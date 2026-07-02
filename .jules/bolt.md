# Bolt's Journal - Critical Learnings

## 2025-05-14 - Initializing Bolt's Journal
**Learning:** Bolt is active and ready to optimize.
**Action:** Keep an eye out for performance bottlenecks in the Wedding Management System.

## 2025-05-14 - Python Eager Default Evaluation Anti-pattern
**Learning:** Using `getattr(obj, "attr", obj.related.count())` is a major performance anti-pattern in Python. Because Python evaluates all arguments before calling the function, `obj.related.count()` (the default value) is executed even if the attribute exists, causing N+1 queries during list serialization.
**Action:** Always use conditional checks (e.g., `if (val := getattr(obj, "attr", None)) is not None: return val`) to ensure expensive fallbacks are only executed when absolutely necessary.

## 2025-05-14 - Reverse OneToOne and Serialization Cache
**Learning:** Reverse OneToOne relationships in Django are particularly tricky for serialization. Accessing them triggers a query if they aren't pre-fetched, and they don't behave like Forward foreign keys (where the ID is on the model itself). When creating objects in a service, manual cache population (`obj.related = child`) is necessary to avoid queries during the immediate response serialization.
**Action:** Manually populate the object cache in the service layer after creation to ensure the ensuing serialization is query-free.
