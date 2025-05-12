from src.sql_parsers.parse_predicates import parse_predicates


def test_basic_comparisons():
    query = """
            SELECT *
            FROM foo
            WHERE id > 100
              AND rating < 4.5
              AND name <> 'test' \
            """
    result = parse_predicates(query)
    assert result == {
        'where': [
            {'type': 'comparison', 'column': 'id', 'operator': '>', 'value': '100'},
            {'type': 'comparison', 'column': 'rating', 'operator': '<', 'value': '4.5'},
            {'type': 'comparison', 'column': 'name', 'operator': '<>', 'value': "'test'"}
        ],
        'joins': [],
        'having': []
    }


def test_in_clause():
    query = "SELECT * FROM products WHERE category IN ('electronics', 'books')"
    result = parse_predicates(query)
    assert result == {
        'where': [{
            'type': 'in',
            'column': 'category',
            'values': ["'electronics'", "'books'"]
        }],
        'joins': [],
        'having': []
    }


def test_between_clause():
    query = "SELECT * FROM orders WHERE order_date BETWEEN '2023-01-01' AND '2023-12-31'"
    result = parse_predicates(query)
    assert result == {
        'where': [{
            'type': 'between',
            'column': 'order_date',
            'low': "'2023-01-01'",
            'high': "'2023-12-31'"
        }],
        'joins': [],
        'having': []
    }


def test_null_checks():
    query = """
            SELECT *
            FROM users
            WHERE email IS NULL
              AND phone IS NOT NULL \
            """
    result = parse_predicates(query)
    assert result == {'where': [{'type': 'is_null', 'column': 'email', 'negation': ''},
                                {'type': 'raw', 'expression': 'NOT phone IS NULL'}], 'joins': [], 'having': []}


def test_having_clause():
    query = """
            SELECT department, COUNT(*)
            FROM employees
            GROUP BY department
            HAVING COUNT(*) > 5
               AND AVG(salary) < 100000 \
            """
    result = parse_predicates(query)
    assert result == {'where': [], 'joins': [],
                      'having': [{'type': 'comparison', 'column': 'COUNT(*)', 'operator': '>', 'value': '5'},
                                 {'type': 'comparison', 'column': 'AVG(salary)', 'operator': '<', 'value': '100000'}]}


def test_nested_conditions():
    query = """
            SELECT *
            FROM inventory
            WHERE (quantity < 10 OR supplier_id = 5)
              AND (category = 'perishable' OR discontinued = TRUE) \
            """
    result = parse_predicates(query)
    assert result == {'where': [{'type': 'raw', 'expression': '(quantity < 10 OR supplier_id = 5)'},
                                {'type': 'raw', 'expression': "(category = 'perishable' OR discontinued = TRUE)"}],
                      'joins': [], 'having': []}


def test_no_predicates():
    query = "SELECT * FROM logs"
    result = parse_predicates(query)
    assert result == {
        'where': [],
        'joins': [],
        'having': []
    }
