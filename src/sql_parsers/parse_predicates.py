import sqlglot
from sqlglot import parse_one, exp


def parse_predicates(sql):
    """
    Enhanced parser that handles JOIN conditions properly.
    Returns predicates in structured format:
    {
        "where": [list of where predicates],
        "joins": [list of join predicates],
        "having": [list of having predicates]
    }
    """

    def parse_expression(expression):
        if isinstance(expression, exp.Column):
            return expression.sql(dialect='postgres')

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
            # Fallback for unsupported expressions
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

    # Extract WHERE clause
    where_clause = parsed.find(exp.Where)
    if where_clause:
        result["where"] = flatten_conditions(where_clause.this)

    # Extract JOIN ON clauses
    for join in parsed.find_all(exp.Join):
        if join.args.get("on"):
            result["joins"].extend(flatten_conditions(join.args["on"]))

    # Extract HAVING clause
    having_clause = parsed.find(exp.Having)
    if having_clause:
        result["having"] = flatten_conditions(having_clause.this)

    return result
