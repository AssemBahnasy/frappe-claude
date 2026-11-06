---
name: new-patch
description: Recipe for a data migration patch in a Frappe app - when a rename, field change, default or data fix must reach every site. Covers patches.txt sections, idempotent patch code and testing with migrate. Use when the user asks for a patch, migration, data fix, renaming a field or DocType, or backfilling values.
argument-hint: "<app> <short description>"
---

# New patch

A patch is how a change to existing data reaches every site. Never fix data by hand on the site
instead.

1. **File**: `<app>/<app>/patches/v16_0/<what_it_does>.py` (create `__init__.py` in each new
   folder) with one `execute()`:

   ```python
   import frappe


   def execute():
   	"""Copy the old free-text driver into the new Crew Member link."""
   	if not frappe.db.has_column("Service Visit", "driver_name"):
   		return
   	...
   ```

   - **Idempotent**: safe to run twice; check before changing.
   - Bulk updates with `frappe.qb` / `frappe.db.set_value` over loops of `doc.save()` when no
     controller logic must run; use `doc.save()` when it must.
   - **Dropping a removed field's column with `trim_table`:** clear the local column list first, with
     `frappe.client_cache.delete_value(f"table_columns::tab{doctype}")`. `trim_table` clears it through
     `frappe.cache`, leaving the process's own copy to a background thread, so a second trim of the table in the
     same migrate can fail now and then with `Can't DROP COLUMN` (MariaDB 1091). Checked on v16.55:
     `frappe/model/meta.py: trim_table`, `frappe/utils/redis_wrapper.py: ClientCache`. Keep the two lines in one
     helper when more than one patch needs them.
   - Reload a DocType the patch reads with its new schema in `pre_model_sync`:
     `frappe.reload_doc("<module>", "doctype", "<doctype>")`.
2. **Register** it in `<app>/<app>/patches.txt` under the right section
   (`frappe/modules/patch_handler.py`):
   - `[pre_model_sync]`: needs the **old** schema (before DocType JSON is synced), e.g. renames.
   - `[post_model_sync]`: needs the **new** schema, e.g. filling a new field.

   Line: `<app>.patches.v16_0.<what_it_does>`. A patch line runs once per site; to re-run, change
   the line (append `# 2`).
3. **Run**: `cd <bench> && bench --site <site> migrate`; read the output, then check
   the data.
4. Add a test if the transformation has logic worth guarding; note the patch in the feature's
   docs if it changes behaviour users see.
5. Stop for review.
