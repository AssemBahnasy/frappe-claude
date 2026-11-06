---
paths:
  - "**/*.py"
---

# Python

- Tabs, double quotes, line length 110, the bench's Python (`[tool.ruff]` in each app's
  `pyproject.toml`). Lint only what you changed: `ruff check <files> && ruff format <files>`.
- Type hints on public functions and whitelisted endpoints (Frappe validates whitelisted
  argument types).
- Docstrings and comments are brief: **two sentences at most**, saying *why*, never a paragraph. No
  comment that restates the code; a longer explanation belongs in the app's `docs/`.
- User-facing text through `_()` (or `_lt()` at import time); `frappe.throw(_("..."))` for
  validation errors, with `title=` when it helps.
- No `print`; use `frappe.logger("<app>")` or `frappe.log_error` for failures worth keeping.
- `frappe.db.commit()` only in background jobs, patches or after an irreversible external call,
  never inside a controller or endpoint (Frappe commits the request).
- Queries through `frappe.qb`, `frappe.get_all`/`get_list` or `frappe.db.get_value`; `get_list`
  when the user's permissions must apply. Never build SQL with f-strings from input.
- v16 rejects SQL functions as strings in `fields` (`"count(name)"`); use the dict form
  `{"COUNT": "*", "as": "total"}` (`frappe/database/query.py`).

## Where code goes

Layers, shared homes and app boundaries are in [architecture.md](architecture.md). Install code
is `<app>/install.py` (`after_install`), with its data in `<app>/data/*.json`.
