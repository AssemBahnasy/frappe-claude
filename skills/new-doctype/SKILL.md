---
name: new-doctype
description: Recipe for adding a new DocType (master, transaction, child table or single settings) to a Frappe app, the Frappe v16 way - propose, create with Frappe's own exporter so the JSON, controller, form script and test are generated, then migrate, test and document. Use when the user asks for a new DocType, master, child table, settings page or record type.
argument-hint: "<app> <DocType Name>"
---

# New DocType

Read first: `~/.claude/rules/frappe/doctypes.md`, `~/.claude/rules/frappe/doctype-layout.md` and the project's rules (which app it belongs to).

## 1. Propose and wait for approval

Write the proposal in chat:

- name, app, module, kind (master / submittable
  transaction / child table / single);
- naming rule (series `PREFIX-.YYYY.-.#####`, `field:<code>`, ...);
- a fields table: fieldname | label | type | options | reqd | in list / filter;
- permissions: role → read / write / create / submit / cancel / delete;
- links to other DocTypes and which app owns them;
- two or three similar DocTypes in Frappe, ERPNext, HRMS or CRM whose pattern it follows;
- a sketch of the form: tabs, sections and columns, with each field in its place.

Do not create anything until the user approves.

## 2. Create it through Frappe

Either the user creates it in the desk (`/desk/doctype/new`, developer mode is on), or create it
from a script so Frappe exports the files exactly as the desk would
(`DocType.on_update` → `export_doc` + `make_controller_template`,
`frappe/core/doctype/doctype/doctype.py`). Save the script in the session scratchpad:

```python
import frappe

frappe.init("<site>", sites_path="<bench>/sites")
frappe.connect()
doc = frappe.get_doc({
	"doctype": "DocType",
	"name": "Service Visit",
	"module": "<Module>",
	"custom": 0,
	"naming_rule": "By \"Naming Series\" field",
	"autoname": "naming_series:",
	"is_submittable": 1,
	"track_changes": 1,
	"fields": [
		{"fieldname": "naming_series", "fieldtype": "Select", "label": "Series", "options": "TRIP-.YYYY.-.#####", "reqd": 1},
		{"fieldname": "vehicle", "fieldtype": "Link", "label": "Vehicle", "options": "Vehicle", "reqd": 1, "in_list_view": 1},
	],
	"permissions": [{"role": "System Manager", "read": 1, "write": 1, "create": 1, "submit": 1, "cancel": 1, "delete": 1}],
})
doc.insert()
frappe.db.commit()
frappe.destroy()
```

```bash
cd <bench>/sites && ../env/bin/python <scratchpad>/create_doctype.py
```

Child tables: `"istable": 1`, no permissions. Settings: `"issingle": 1`.

**Check the `permissions` in the generated JSON.** A script's `doc.insert()` fills every permission
field with DocPerm's default, so a row written as `{"role": "X", "select": 1}` comes out with read,
write, create, delete, report, export, share, print and email too. Correct the JSON by hand, bump `modified`, and test that the role
can't write. Checked on v16.55: a `select`-only row in the JSON stays select-only on migrate.

## 3. Fill in the generated files

In `<app>/<app>/<module_folder>/doctype/<doctype>/`:

- `<doctype>.py`: controller logic only for this record (`validate`, `before_submit`, ...).
  Frappe regenerates the type-hint block on migrate; leave it.
- `<doctype>.js`: form behaviour per `rules/form-scripts.md`.
- `test_<doctype>.py`: tests for the behaviour you added.
- `<doctype>_list.js` if the list needs indicators.

## 4. Verify, document, stop

- `/bench-verify <app> "<DocType>"` (migrate, tests, open the form in each language).
- New strings → `/translations <app>`.
- Document it with `/app-docs <app> doctype "<DocType>"`: its doc in the feature folder, a row in
  `docs/doctypes/README.md`, and any cross-app link in `docs/architecture/separation-of-concerns.md`.
- Add it to the app's sidebar/workspace if users need it (`/app-navigation`).
- Stop for review.
