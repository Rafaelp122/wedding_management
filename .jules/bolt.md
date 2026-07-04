# Bolt's Journal - Critical Learnings Only

## 2025-05-15 - Journal Created
**Learning:** Initializing the performance optimization journal.
**Action:** Keep track of critical performance learnings.

## 2025-05-15 - [Django Cartesian Product in Annotations]
**Learning:** Multiple `Count(distinct=True)` in the same QuerySet cause a "Cartesian Product" join explosion, where the DB generates all combinations of related rows before collapsing them. This leads to massive SQL strings and exponentially slower execution as data grows.
**Action:** Use `Subquery` counts wrapped in `Coalesce` to calculate related record counts independently. This keeps the SQL compact and the execution time linear.
