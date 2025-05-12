from src.indexing.predicates import create_predicate_index
from src.sql_parsers.parse_predicates import parse_predicates

queries = {
    "query1": """
              SELECT *
              FROM engine
              WHERE ship_id = 'A-CS'
                AND sog >= 15
              """,
    "query2": """
              SELECT *
              FROM engine
              WHERE (ship_id = 'A-CS')
                AND (sog >= 15)
              """,
    "query3": """
              SELECT *
              FROM (SELECT *
                    FROM engine
                    WHERE sog >= 15) AS sub
              WHERE sub.ship_id = 'A-CS'
              """,
    "query4": """
              SELECT *
              FROM (SELECT *
                    FROM engine
                    WHERE ship_id = 'A-CS') AS sub
              WHERE sub.sog >= 15
              """,
    "query5": """
              SELECT e.*
              FROM engine AS e
              WHERE e.sog >= 15
                AND e.ship_id = 'A-CS'
              """,
    "query6": """
              SELECT *
              FROM (SELECT ship_id, sog
                    FROM engine) AS sub
              WHERE ship_id = 'A-CS'
                AND sog >= 15
              """,
    "query7": """
              SELECT *
              FROM (SELECT *
                    FROM (SELECT *
                          FROM engine
                          WHERE ship_id = 'A-CS') AS innermost
                    WHERE sog >= 15) AS x
              """
}

for name, q in queries.items():
    predicates = parse_predicates(q)
    index = create_predicate_index(predicates)
    print(f"{name} index: {index}")

"""
All these queries are semantically equivalent (same predicates in different forms),
so they should generate identical predicate indexes.
"""
