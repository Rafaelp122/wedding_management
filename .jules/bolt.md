# Bolt's Journal - Critical Learnings Only

## 2025-05-15 - Journal Created
**Learning:** Initializing the performance optimization journal.
**Action:** Keep track of critical performance learnings.

## 2025-05-15 - [Django Cartesian Product in Annotations]
**Learning:** Multiple `Count(distinct=True)` in the same QuerySet cause a "Cartesian Product" join explosion, where the DB generates all combinations of related rows before collapsing them. This leads to massive SQL strings and exponentially slower execution as data grows.
**Action:** Use `Subquery` counts wrapped in `Coalesce` to calculate related record counts independently. This keeps the SQL compact and the execution time linear.

## 2025-05-15 - [N+1 in Django Ninja Schema Resolvers]
**Learning:** Accessing reverse OneToOne relationships (like `obj.expense` on `Contract`) in schema resolvers triggers a query if not pre-fetched. Even `hasattr(obj, 'expense')` triggers a query. Data integrity is paramount, so we cannot simply return defaults; however, checking `obj.__dict__` for cached relations and using `getattr(obj, 'annotated_field', None)` for annotated values avoids N+1 during serialization while maintaining correctness via a final fallback.
**Action:** Always check `obj.__dict__` or pre-annotated fields before accessing related objects in list serialization contexts. When creating related objects, manually populate the parent's cache to avoid N+1 in the immediate response.
