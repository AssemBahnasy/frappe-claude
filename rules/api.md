---
paths:
  - "**/api/**"
  - "**/hooks.py"
---

# Endpoints, hooks and permissions

## Whitelisted endpoints

- They live in `<app>/api/<concern>.py`, one file per concern, and only check access and inputs,
  then call the feature package. No business logic in an endpoint.
- `@frappe.whitelist()` with type-hinted arguments; `methods=["POST"]` for anything that writes.
  `allow_guest=True` only when the user asks, with `rate_limit`.
- Check access on the server, every time: `frappe.has_permission(doctype, ptype, doc,
  throw=True)` or read through `frappe.get_list` (permissions applied). Never trust a role check
  done in JavaScript.
- Never `ignore_permissions=True` on data the caller chose; when it is needed (system records),
  say why in a one-line comment.
- Return plain dicts and lists; document them in `docs/api/<concern>.md`.

## hooks.py

- Every hook is a dotted path to a function in the app; keep `hooks.py` declarative.
- `required_apps` lists every app this one links to or imports from; the direction between apps
  is agreed first (the project's rules).
- Check each hook's behaviour in `apps/frappe/hooks.md` and Frappe's source before relying on it.
- After changing `hooks.py`: `bench --site <site> clear-cache` (and `migrate` if it adds
  fixtures or `after_migrate`).
