---
paths:
  - "**/doctype/**"
  - "**/report/**"
  - "**/workspace/**"
  - "**/sidebar/**"
  - "**/dock/**"
---

# DocTypes and other synced records

## Creating and changing

- Create DocTypes the Frappe way: in the desk on `<site>` (developer mode is on), or with the
  `/new-doctype` recipe, which writes the same files. Never hand-write a DocType's folder without
  its `__init__.py`, `.py`, `.js` and `test_*.py`.
- When a JSON file is edited by hand, bump its `modified` (to now, never a future date), or
  `bench migrate` skips it.
- Run `bench --site <site> migrate` after every DocType change, and read its output.
- A rename or a change to existing data needs a patch (`/new-patch`), never a manual fix on the
  site.

## Design

- `module` is the app's module; `custom` is 0.
- Naming: choose deliberately (`naming_rule`): naming series `PREFIX-.YYYY.-.#####` for
  transactions, `field:` for masters with a natural unique code, `hash` only for internal rows.
- Use `Link` fields to masters (never `Data` holding a name), `Select` only for a fixed list that
  will not grow; a list the user maintains is a master DocType.
- Transactions that must not change once done are submittable (`is_submittable`) and use
  `docstatus`; add `amended_from` as Frappe generates it.
- Mark `reqd`, `unique`, `in_list_view`, `in_standard_filter`, `search_index` on purpose. Add
  `search_index` to links that lists filter on.
- Values that vary by language are a child table with a `Language` link, never one field per
  language (`translations.md`).
- Quantities have a `uom` link; amounts have a `Currency` field with `options` pointing at a
  currency field.
- Every DocType has role permissions in its JSON. Roles are app-specific (`Fleet Planner`,
  `Fleet Dispatcher`, ...) and created in `install.py` or as fixtures; agree new roles with the
  user.
- Child tables are named after their parent (`Service Visit Stop` for `Service Visit`).

## Before creating a DocType

Propose it first: name, app and module, naming, a fields table (fieldname, type, options, reqd),
permissions. Build it only once the user approves.
