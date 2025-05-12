import sqlglot
from sqlglot import parse_one, exp


def parse_predicates(sql):
    """
    Recursively parses predicates from top-level and subqueries.
    """

    def parse_expression(expression):
        if isinstance(expression, exp.Column):
            # Strip table/alias prefix, keep only column name
            return expression.name  # avoids alias or table prefix

        if isinstance(expression, exp.EQ):
            return {
                "type": "comparison",
                "column": parse_expression(expression.left),
                "operator": "=",
                "value": parse_expression(expression.right)
            }
        elif isinstance(expression, exp.NEQ):
            return {
                "type": "comparison",
                "column": parse_expression(expression.left),
                "operator": "<>",
                "value": parse_expression(expression.right)
            }
        elif isinstance(expression, (exp.GT, exp.GTE, exp.LT, exp.LTE)):
            return {
                "type": "comparison",
                "column": parse_expression(expression.left),
                "operator": expression.key,
                "value": parse_expression(expression.right)
            }
        elif isinstance(expression, exp.In):
            return {
                "type": "in",
                "column": parse_expression(expression.this),
                "values": [parse_expression(v) for v in expression.expressions]
            }
        elif isinstance(expression, exp.Between):
            return {
                "type": "between",
                "column": parse_expression(expression.this),
                "low": parse_expression(expression.args["low"]),
                "high": parse_expression(expression.args["high"])
            }
        elif isinstance(expression, exp.Is):
            return {
                "type": "is_null",
                "column": parse_expression(expression.this),
                "negation": "NOT " if expression.args.get("not") else ""
            }
        elif isinstance(expression, exp.Paren):
            return parse_expression(expression.this)
        else:
            try:
                return {
                    "type": "raw",
                    "expression": expression.sql(dialect='postgres')
                }
            except AttributeError:
                return {
                    "type": "unsupported",
                    "expression": str(expression)
                }

    def flatten_conditions(expression):
        predicates = []
        if expression is None:
            return predicates

        if isinstance(expression, (exp.And, exp.Or)):
            predicates.extend(flatten_conditions(expression.left))
            predicates.extend(flatten_conditions(expression.right))
        else:
            parsed = parse_expression(expression)
            if parsed:
                predicates.append(parsed)
        return predicates

    def collect_from_select(select_expr, result):
        # WHERE
        where_clause = select_expr.args.get("where")
        if where_clause:
            result["where"].extend(flatten_conditions(where_clause.this))

        # JOIN
        for join in select_expr.find_all(exp.Join):
            if join.args.get("on"):
                result["joins"].extend(flatten_conditions(join.args["on"]))

        # HAVING
        having_clause = select_expr.args.get("having")
        if having_clause:
            result["having"].extend(flatten_conditions(having_clause.this))

    result = {
        "where": [],
        "joins": [],
        "having": []
    }

    try:
        parsed = parse_one(sql, read='postgres')
    except sqlglot.errors.ParseError as e:
        print(f"Parse error: {e}")
        return result

    # Traverse all SELECT expressions, including subqueries
    for select_expr in parsed.find_all(exp.Select):
        collect_from_select(select_expr, result)

    return result
