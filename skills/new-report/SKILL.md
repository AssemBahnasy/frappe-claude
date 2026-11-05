---
name: new-report
description: Recipe for a report in a Frappe app - choose Report Builder, Query Report or Script Report, generate it through Frappe, write the execute() with permissions and filters, chart and summary, then test and document. Use when the user asks for a report, KPI, summary, analytics, dashboard numbers, or an export of records.
argument-hint: "<app> <Report Name>"
---

# New report

1. **Choose the kind** (and propose it with columns and filters before building):
   - Report Builder (saved list view): one DocType, no computation; the user can make it.
   - Script Report: anything computed, grouped, or across DocTypes. The usual default.
   - Query Report: only for a fixed SQL the user wants to maintain as SQL.
2. **Create** in the desk (`/desk/report/new`, Is Standard = Yes, module = the app's module,
   reference DocType = the main DocType) so Frappe exports
   `<app>/<module_folder>/report/<report>/` with `.json`, `.py`, `.js`.
3. **`<report>.py`**:

   ```python
   import frappe
   from frappe import _


   def execute(filters: dict | None = None):
   	filters = frappe._dict(filters or {})
   	columns = [
   		{"fieldname": "vehicle", "label": _("Vehicle"), "fieldtype": "Link", "options": "Vehicle", "width": 160},
   		{"fieldname": "trips", "label": _("Trips"), "fieldtype": "Int", "width": 100},
   	]
   	data = frappe.get_list(  # get_list applies the user's permissions
   		"Service Visit",
   		filters={"docstatus": 1, "trip_date": ["between", [filters.from_date, filters.to_date]]},
   		fields=["vehicle", {"COUNT": "*", "as": "trips"}],
   		group_by="vehicle",
   	)
   	return columns, data
   ```

   Optional returns: `columns, data, message, chart, report_summary`. Keep heavy logic in the
   feature package and call it from `execute`.
4. **`<report>.js`**: filters (`from_date`/`to_date` with defaults, links with `get_query`), every
   label in `__()`.
5. **Roles** in the report JSON (`roles`), matching who may read the DocTypes.
6. **Test** `execute()` with a few records in `test_<report>.py`; add it to the app's sidebar
   (`/app-navigation`); document it in the feature's docs; `/bench-verify`; stop for review.
