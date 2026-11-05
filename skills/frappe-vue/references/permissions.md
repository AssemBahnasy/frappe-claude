# Permissions

Admins manage everything below without code, in **Role Permissions Manager**
(`/desk/permission-manager`) or the **Roles** tab of a DocType's Settings dialog (v16.51+).
Both write *Custom DocPerm* rows. Because the architecture reads and writes only through
permission-aware APIs, the page follows their changes automatically. This file covers what
the code must do so that holds.

## Three layers

| Layer | Decides | Enforced where |
|---|---|---|
| **Page roles** (`{feature}.json` → `roles`) | Who can **open** the page | Only when the page loads (`frappe/desk/desk_page.py`). **Not** on the page's Python methods |
| **DocType rights** (per role: read, write, create, delete, submit…, at permission levels 0–9, optionally "Only if Creator", narrowed by User Permissions) | What each user may do with **the data** | Server, on every `get_list`, `get_doc` + `check_permission`, `insert`, `save` |
| **Custom Permission Types** (v16) | App-specific **actions** beyond CRUD ("Publish", "Snap Routes", …) | Wherever your code checks them, on the server and in the UI |

A Page has no Read/Write/Create of its own. To control what a user may *do* on a page,
use DocType rights or a custom Permission Type, never extra page roles.

## 1. Every endpoint checks its own access

A page method call is just a dotted command (`frappe/public/js/frappe/request.js`), so any
logged-in user can call it whatever the page roles say. Each whitelisted method must do one of:

```python
rows = frappe.get_list("{DocType}", ...)            # permission-aware query
doc = frappe.get_doc("{DocType}", name)
doc.check_permission("write")                       # one record
frappe.has_permission("{DocType}", ptype="snap_routes", throw=True)   # custom right
frappe.only_for(("System Manager",))                # role gate, as core's permission manager does
```

## 2. Show only the tools a user can use

```javascript
const can = (ptype, doc) => frappe.perm.has_perm("{DocType}", 0, ptype, doc);
// can("create"), can("write", store.doc), can("delete"), can("snap_routes")
```

- **Don't use `frappe.model.can_create(doctype)`** on DocTypes with *User Cannot Create*
  (`in_create`). It always returns false there, even for roles that have Create.
  `frappe.perm.has_perm` reads the role rules directly.
- Hiding a button is a convenience only. The server checks again (§1).

## 3. Custom Permission Types

Use one when a page action doesn't map to read/write/create/delete. Typical cases are an
action on many records, an external call, or a step that only some writers should take.

- **Create:** in developer mode, add a *Permission Type* with **Doc Type** = `{DocType}`
  and **Perm Type** = `snap_routes` (scrubbed; standard right names are rejected). Frappe:
  - adds the checkbox to the permission rule tables;
  - exports `{module}/permission_type/{doctype}_{perm_type}/….json`;
  - on migrate, syncs it **before** DocTypes, so DocType JSON can grant it.
- **Grant:** tick it per role in Role Permissions Manager, or in the DocType's `permissions`.
- **Check:** `frappe.has_permission("{DocType}", ptype="snap_routes")` on the server,
  and `frappe.perm.has_perm("{DocType}", 0, "snap_routes")` in the browser.
  Both include custom rights (`frappe/permissions.py`, `frappe.perm.get_rights`).

## 4. Field-level access in property panels

Fields at **permission level > 0** need that level's read/write right. Fields marked
**mask** come back masked unless the role has the *mask* right at that level. If a user
edits a field they can't write, the server **silently resets it on save**, with no error
(`Document.validate_higher_perm_levels`), so the edit just disappears. Decide each field's
access the way forms do:

```javascript
const perm = frappe.perm.get_perm("{DocType}", store.doc); // parent rules, even for child rows

function access(df, row) {
	const status = frappe.perm.get_field_display_status(df, row, perm); // "Write" | "Read" | "None"
	const masked = df.mask && !frappe.perm.has_perm("{DocType}", df.permlevel || 0, "mask");
	return masked && status === "Write" ? "Read" : status;
}
// "None" → don't render · "Read" → render read-only · "Write" → editable
```

`get_field_display_status` also applies `hidden`, `read_only`, submitted-document rules
and `allow_on_submit`, so panels behave like the standard form. See controls.md.

## 5. Ownership and record restrictions

"Only if Creator" and *User Permissions* narrow which records a role sees. `frappe.get_list`
already applies them. Never "fix" a missing record by switching to `frappe.get_all`, which
bypasses them (see python-api.md).
