QUERY_1 = """
          SELECT o.order_id, c.customer_name, p.product_name
          FROM orders o
                   JOIN customers c ON o.customer_id = c.customer_id
                   JOIN order_items oi ON o.order_id = oi.order_id
                   JOIN products p ON oi.product_id = p.product_id AND p.discontinued = FALSE
          WHERE o.order_date BETWEEN '2023-01-01' AND '2023-12-31'
            AND (c.membership_level = 'GOLD' OR c.total_purchases > 1000)
            AND o.status IN ('completed', 'shipped')
          HAVING COUNT(oi.item_id) > 1 \
          """

QUERY_2 = """
          SELECT d.department_name,
                 AVG(e.salary)                                          as avg_salary,
                 COUNT(CASE WHEN e.hire_date > '2020-01-01' THEN 1 END) as new_hires
          FROM employees e
                   JOIN departments d ON e.department_id = d.department_id AND d.budget > 1000000
                   LEFT JOIN performance_reviews pr ON e.employee_id = pr.employee_id
          WHERE e.active = TRUE
            AND (e.salary > 80000 OR e.bonus_eligible = TRUE)
            AND EXISTS (SELECT 1
                        FROM projects
                        WHERE lead_employee_id = e.employee_id
                          AND deadline > CURRENT_DATE)
          GROUP BY d.department_name
          HAVING AVG(e.salary) > 70000
             AND COUNT(pr.review_id) > 0 \
          """

from src.indexing.predicates import create_predicate_index

from src.sql_parsers.parse_predicates import parse_predicates

# Parse both complex queries
predicates1 = parse_predicates(QUERY_1)
predicates2 = parse_predicates(QUERY_2)

# Generate indexes
index1 = create_predicate_index(predicates1)
index2 = create_predicate_index(predicates2)

print(f"E-commerce query index: {index1}")
print(f"Analytics query index: {index2}")
