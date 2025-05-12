from src.indexing.predicates import create_predicate_index
from src.sql_parsers.parse_predicates import parse_predicates

query = """
        SELECT o.*, c.name
        FROM orders o
                 JOIN customers c ON o.customer_id = c.id AND c.active = TRUE
        WHERE o.status = 'completed' \
        """
result = parse_predicates(query)

print(result)
