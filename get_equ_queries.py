from src.indexing.predicates import create_predicate_index
from src.sql_parsers.parse_predicates import parse_predicates

query = """
        select *
        from engine
        where ship_id = 'A-CS'
          and sog >= 15 \
        """

query2 = """
         SELECT *
         FROM engine
         WHERE (ship_id = 'A-CS')
           AND (sog >= 15)
         """

query3 = """
         SELECT *
         FROM (SELECT *
               FROM engine
               WHERE sog >= 15) AS sub
         WHERE sub.ship_id = 'A-CS' \
         """

# Parse both complex queries
predicates1 = parse_predicates(query)
predicates2 = parse_predicates(query2)
predicates3 = parse_predicates(query3)

print("P1: {predicate1}".format(predicate1=predicates1))
print("P2: {predicate2}".format(predicate2=predicates2))
print("P3: {predicate3}".format(predicate3=predicates3))

index1 = create_predicate_index(predicates1)
index2 = create_predicate_index(predicates2)
index3 = create_predicate_index(predicates3)

print(f"Q1: {index1}")
print(f"Q2: {index2}")
print(f"Q3: {index3}")

""" Provides same indexes, for 3 data-wise equivalent, but syntactically different queries"""
""" Helps to identify, if the active/running queries are fundamentally the same and if they should be shared """
