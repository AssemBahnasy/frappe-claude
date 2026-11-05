---
name: new-endpoint
description: Recipe for adding a whitelisted API method to a Frappe app - thin endpoint in <app>/api/, logic in the feature package, server-side permission checks, tests and an api doc. Use when the user asks for an API, endpoint, whitelisted method, or a server call for a form, page or mobile client.
argument-hint: "<app> <concern> <method>"
---

# New endpoint

Read first: `~/.claude/rules/frappe/api.md`.

1. **Logic first**, in the feature package (`<app>/<feature>/<module>.py`), as a plain function
   that takes typed arguments and returns plain data. It knows nothing about requests.
2. **Endpoint** in `<app>/api/<concern>.py` (create `api/__init__.py` if missing):

   ```python
   import frappe


   @frappe.whitelist(methods=["POST"])
   def close_trip(trip: str) -> dict:
   	"""Close a collection trip once every stop has proof of service."""
   	doc = frappe.get_doc("Service Visit", trip)
   	doc.check_permission("write")
   	return trips.close(doc)
   ```

   - `GET` (default) for reads, `POST` for writes.
   - Access checked here: `doc.check_permission(...)`, `frappe.has_permission(...,
     throw=True)`, or reads through `frappe.get_list`.
   - Guest access only when the user asks, with `@rate_limit(...)`.
3. **Call it** from JS with `frappe.call({method: "<app>.api.<concern>.<method>", args})` or
   `frm.call` for a controller method.
4. **Test** the logic and the permission check (a user without the role gets
   `frappe.PermissionError`) in `<app>/tests/test_<concern>.py`.
5. **Document** in `docs/api/<concern>.md`: method path, HTTP verb, arguments table, return shape,
   who may call it.
6. `/bench-verify <app>`, then stop for review.
