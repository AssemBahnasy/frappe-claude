---
name: seed-data
description: Ship default records with a Frappe app - roles, default masters (types, units, statuses), settings and custom fields - via install.py and data/*.json, or Frappe fixtures. Use when the user asks for default data, seed data, fixtures, initial records, roles, or "every site should have".
argument-hint: "<app> <what to seed>"
---

# Seed data and fixtures

Pick the mechanism by who owns the record after install:

| Record | Mechanism |
|---|---|
| Defaults users may edit or delete (types, units, sample zones) | `after_install` reading `<app>/data/<doctype>.json`; insert only if missing |
| Roles the app's permissions use | `after_install` (and `after_migrate` if new roles are added later) |
| Records the app controls and must stay identical (Custom Field / Property Setter on another app's DocType, Workflow) | `fixtures` in `hooks.py`, exported with `bench --site <site> export-fixtures --app <app>` |

## install.py pattern

```python
import json
from pathlib import Path

import frappe

DATA = Path(__file__).parent / "data"


def after_install():
	seed("Service Type")


def seed(doctype: str):
	"""Insert the app's default records once; never overwrite what the site changed."""
	for row in json.loads((DATA / f"{frappe.scrub(doctype)}.json").read_text()):
		if not frappe.db.exists(doctype, row.get("name")):
			frappe.get_doc({"doctype": doctype, **row}).insert(ignore_permissions=True)
```

`hooks.py`: `after_install = "<app>.install.after_install"`.

- One JSON file per DocType in `<app>/data/`; Python only reads them (one source per fact).
- Labels in the JSON are English; they are translated by `_()` where shown.
- Fixtures need a filter (`{"dt": "Custom Field", "filters": [["module", "=", "<Module>"]]}`) so
  the app never exports other apps' records.
- Test: `bench --site <site> execute <app>.install.after_install` twice (it must be
  idempotent), then a test in `<app>/tests/test_install.py`.
