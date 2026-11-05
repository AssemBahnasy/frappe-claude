# Python endpoints for desk Vue code

Most builders need **no custom endpoint**: `frappe.db.get_doc` + `frappe.client.save`
cover load/save, and `frappe.db.get_list` / Link fields cover lookups. Add an
endpoint only for aggregations, multi-record reads, or server-only computation.

## Permissions — get these right

| Call | Checks the user's permissions? |
|---|---|
| `frappe.get_list(doctype, ...)` | **Yes**, including user permissions and `permission_query_conditions` |
| `frappe.get_all(doctype, ...)` | **No.** It is `get_list(..., ignore_permissions=True)` |
| `frappe.db.get_all` / `frappe.db.get_list` | same as `frappe.get_all` / `frappe.get_list` |
| `frappe.db.get_value`, `frappe.db.sql`, `frappe.qb` | **No** |
| `frappe.get_doc(doctype, name)` | **No.** Call `doc.check_permission("read")` |
| `doc.save()` / `doc.insert()` | **Yes** (write/create), unless `ignore_permissions` |

So for anything that returns data to the browser, use `frappe.get_list`, or
`get_doc` + `check_permission`. Use `get_all` / `db.*` only for data the user
should see regardless of permissions, and say why in a comment.

## Endpoint template

```python
# {app}/{module}/page/{feature}/{feature}.py   (or {app}/api/{feature}.py)
import frappe
from frappe import _


@frappe.whitelist()
def get_summary(name: str) -> dict:
	doc = frappe.get_doc("{DocType}", name)
	doc.check_permission("read")

	rows = frappe.get_list(
		"{Other DocType}",
		filters={"{link_field}": name},
		fields=["name", "status", "modified"],
		order_by="modified desc",
		limit=50,
	)
	return {"count": len(rows), "rows": rows}


@frappe.whitelist(methods=["POST"])
def apply_change(name: str, value: str) -> dict:
	doc = frappe.get_doc("{DocType}", name)
	doc.check_permission("write")
	doc.some_field = value
	doc.save()  # validate() runs; permission re-checked
	return doc.as_dict()
```

- Type hints on whitelisted functions are validated by Frappe (v15+). Keep them accurate.
- Mutating endpoints: `methods=["POST"]`.
- Raise user-facing errors with `frappe.throw(_("..."))`. Don't catch broad
  exceptions just to re-throw them. Frappe already logs and serialises them.
- Endpoint path for the JS side: the dotted module path, e.g.
  `{app}.{module}.page.{feature}.{feature}.get_summary`.
- **Page roles don't protect these methods.** Any logged-in user can call them, so each one
  checks access itself (a permission-aware query, `check_permission`, `frappe.has_permission`,
  or `frappe.only_for`). See permissions.md §1.

## Calling from Vue

Use `frappe.xcall`. It returns a Promise of `r.message`, and rejects on error
after Frappe has already shown the server's message:

```javascript
const loading = ref(false);
const summary = ref(null);

async function refresh() {
	loading.value = true;
	try {
		summary.value = await frappe.xcall("{app}.{module}.page.{feature}.{feature}.get_summary", {
			name: store.name,
		});
	} catch (e) {
		summary.value = null; // message already shown to the user
	} finally {
		loading.value = false;
	}
}
```

Other built-ins that already enforce permissions and are worth using before
writing an endpoint:

- `frappe.db.get_doc(doctype, name)`
- `frappe.db.get_list(doctype, { fields, filters, limit })`
- `frappe.db.get_value(doctype, name, fieldname)`
- `frappe.db.insert(doc)`
- `frappe.xcall("frappe.client.save", { doc })`
- `frappe.xcall("frappe.client.delete", { doctype, name })`

These client-side `frappe.db.*` helpers call whitelisted endpoints
(`frappe.client.*`, `frappe.desk.reportview.get_list`), which check permissions.
The server-side `frappe.db.*` functions above do not.
