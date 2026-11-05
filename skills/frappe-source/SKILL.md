---
name: frappe-source
description: How to verify a Frappe v16 mechanism (hook, DocType behaviour, desk JS API, CLI command, permission rule) in the bench's own Frappe source before relying on it, and how to borrow patterns from ERPNext, HRMS and CRM. Use before using any hook or framework API you have not checked in this session, or when the user asks "how does Frappe do X", "is there a hook for", "where does Frappe".
argument-hint: "<mechanism>"
---

# Look it up in Frappe's source

The truth is the code on this bench, `<bench>/apps/frappe` (check its version), not memory or older docs.

| Looking for | Where |
|---|---|
| A hook and what it does | `apps/frappe/hooks.md`, then `grep -rn "get_hooks(\"<hook>\"" frappe/` |
| DocType save/submit lifecycle | `frappe/model/document.py` (`run_method`, `_validate`, `insert`, `save`, `submit`) |
| DocType JSON options | `frappe/core/doctype/doctype/doctype.json`, `docfield/docfield.json` |
| File sync on migrate | `frappe/model/sync.py`, `frappe/modules/import_file.py` |
| Patches | `frappe/modules/patch_handler.py` |
| Permissions | `frappe/permissions.py`, `frappe/model/db_query.py` |
| Whitelisting, rate limits | `frappe/__init__.py` (`whitelist`), `frappe/rate_limiter.py` |
| Desk navigation (dock, sidebar, workspace) | `frappe/desk/doctype/{dock,sidebar,workspace}/`, `frappe/public/js/frappe/ui/sidebar/` |
| Form JS API (`frm.*`) | `frappe/public/js/frappe/form/form.js`, `script_manager.js` |
| CLI commands | `frappe/commands/*.py` (`@click.command`) |
| Tests base classes | `frappe/tests/classes/` |
| Boilerplate for new files | `frappe/core/doctype/doctype/boilerplate/`, `frappe/utils/boilerplate.py` |

```bash
cd <bench>/apps/frappe
grep -rn "<name>" frappe --include=*.py | grep -v /tests/ | head
grep -rn "<name>" frappe/public/js | head
```

## Patterns from other Frappe apps (read only)

`~/frappe-bench/apps/` has `erpnext`, `hrms`, `crm` (if present) and earlier custom apps
(`naqel`, `pestcontrol`). Read them for how a problem is
usually solved; never import from them, and never edit them.

## Record what you found

Cite the file and function in the docs you write (`frappe/model/sync.py`,
`APP_ROOTED_DOCTYPES`), so the next reader can check it too.
