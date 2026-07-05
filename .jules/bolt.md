# Bolt's Journal - Critical Learnings Only

## 2025-05-15 - Journal Created
**Learning:** Initializing the performance optimization journal.
**Action:** Keep track of critical performance learnings.

## 2025-05-15 - [Django Cartesian Product in Annotations]
**Learning:** Multiple `Count(distinct=True)` in the same QuerySet cause a "Cartesian Product" join explosion, where the DB generates all combinations of related rows before collapsing them. This leads to massive SQL strings and exponentially slower execution as data grows.
**Action:** Use `Subquery` counts wrapped in `Coalesce` to calculate related record counts independently. This keeps the SQL compact and the execution time linear.

## 2025-05-20 - [Hybrid Properties with Type Hinting]
**Learning:** Using `getattr(self, "_annotated_field", None)` in model properties allows them to use QuerySet annotations if present, avoiding N+1 queries. However, simply returning the value can lose type information or trigger unnecessary `Decimal(val)` re-instantiations if the value is already a Decimal.
**Action:** Use `return cast(Decimal, val)` when returning annotated financial values in properties to satisfy static analysis while avoiding runtime overhead of re-casting.
