# Store — Pinia, backed by a real DocType record

Loading rejects cleanly on permission errors, the dirty flag is exact, and saving
applies the server's response.

## Data model first

Before writing the store, decide where each piece of state lives on the DocType:

| State | Where | Why |
|---|---|---|
| Business meaning (states, steps, rules, links) | normal fields + **child tables** | queryable, validated, reportable, usable without the builder |
| Visual-only data (x/y positions, zoom, colours, collapsed panels) | one hidden **`JSON`** field (`{layout_field}`) | the builder needs it; nothing else does |

Server-side `validate()` on the DocType stays the single place where business
rules live.
Records edited in the plain form must still open in the builder: missing layout
entries get default positions.

## Template — `store.js`

```javascript
import { defineStore } from "pinia";
import { ref, computed } from "vue";

const DOCTYPE = "{DocType}";
const LAYOUT_FIELD = "{layout_field}";

export const use{Feature}Store = defineStore("{app}-{feature}", () => {
	const name = ref(null);
	const doc = ref(null); // editable clone, never the object in `locals`
	const layout = ref(null); // parsed {layout_field}
	const meta = ref(null);
	const error = ref(null);
	const saving = ref(false);
	const saved_snapshot = ref(null);

	// exact dirty flag: compares what *would* be saved with what *was* saved
	const payload = computed(() =>
		doc.value ? { ...doc.value, [LAYOUT_FIELD]: JSON.stringify(layout.value ?? {}) } : null
	);
	const dirty = computed(
		() => !!payload.value && JSON.stringify(payload.value) !== saved_snapshot.value
	);
	const can_write = computed(() => !!doc.value && frappe.model.can_write(DOCTYPE));

	function apply(server_doc) {
		const clone = JSON.parse(JSON.stringify(server_doc));
		layout.value = parse_layout(clone[LAYOUT_FIELD]);
		doc.value = clone;
		saved_snapshot.value = JSON.stringify(payload.value);
	}

	async function load(docname) {
		name.value = docname;
		error.value = null;
		try {
			await frappe.model.with_doctype(DOCTYPE);
			meta.value = frappe.get_meta(DOCTYPE);
			// rejects on 403/404 and syncs locals
			apply(await frappe.db.get_doc(DOCTYPE, docname));
		} catch (e) {
			error.value = __("Could not load {0} {1}", [__(DOCTYPE), docname]);
		}
	}

	async function save() {
		if (!dirty.value || saving.value) return;
		saving.value = true;
		frappe.dom.freeze(__("Saving..."));
		try {
			// runs DocType validate() + write permission + modified-timestamp check
			const saved = await frappe.xcall("frappe.client.save", { doc: payload.value });
			frappe.model.sync(saved); // keep `locals` fresh for the form view
			apply(saved); // new `modified`, server-computed fields, child row names
			frappe.show_alert({ message: __("Saved"), indicator: "green" });
		} catch (e) {
			// Frappe already showed the server error (validation / TimestampMismatch).
			// Keep the user's edits; they can fix and retry, or Reset to reload.
		} finally {
			saving.value = false;
			frappe.dom.unfreeze();
		}
	}

	function reset() {
		return load(name.value);
	}

	return {
		name, doc, layout, meta, error, saving, dirty, can_write,
		load, save, reset,
	};
});

function parse_layout(value) {
	if (!value) return {};
	if (typeof value === "object") return value;
	try {
		return JSON.parse(value);
	} catch {
		return {};
	}
}
```

### Notes on the template

- **Pass `pinia` from the class** (`use{Feature}Store(this.pinia)`); components
  call `use{Feature}Store()` with no argument.
- **Store refs are unwrapped on the store object**: `store.dirty` is a boolean,
  `store.doc.some_field` is a value.
- **Edit a clone.** Mutating the object in `locals` leaks unsaved edits into the
  form view of the same record.
- **Child tables** are arrays on `doc` (`store.doc.items`). New rows need
  `{ doctype: "{Child DocType}", parentfield: "items" }`; the server assigns `name`
  and `idx`. Removing a row = removing it from the array.
- **Large documents**: the snapshot compare serialises the payload on each change.
  Fine for builder-sized docs. For very large ones, switch to a `version` counter
  bumped by every mutating action.
- **Concurrent edits**: if someone else saved first, `frappe.client.save` raises
  `TimestampMismatchError` and Frappe shows it. Reset reloads the latest version.

## Mutations

Prefer named actions in the store over components mutating state ad hoc. That
gives one place for validation, history commits and derived updates:

```javascript
function add_step(step) {
	doc.value.steps.push({ doctype: "{Child DocType}", parentfield: "steps", ...step });
	layout.value.positions ??= {};
	layout.value.positions[step.key] = step.position;
	history?.commit();
}
```

## Optional — undo/redo

Use `@vueuse/core` (shipped by Frappe). Create the history inside the store, so
`$dispose()` cleans it up. Create it **once**, not on every load:

```javascript
import { useManualRefHistory } from "@vueuse/core";

const state = computed({
	get: () => ({ doc: doc.value, layout: layout.value }),
	set: (v) => { doc.value = v.doc; layout.value = v.layout; },
});
const history = useManualRefHistory(state, { clone: true, capacity: 100 });
// in apply(): history.clear(); history.commit();
// after each user action: history.commit();
// expose: undo: history.undo, redo: history.redo, can_undo: history.canUndo, can_redo: history.canRedo
```

## Optional — keyboard shortcuts

- **Save:** set `wrapper.save_action` in the page controller (page-host.md).
  Frappe's global Ctrl+S calls it for the visible page only, so there's no listener to leak.
- **Others** (undo, delete): bind inside a **component** with `useMagicKeys` /
  `onKeyStroke` from `@vueuse/core` so `app.unmount()` removes them. Ignore keys
  while typing:

```javascript
import { onKeyStroke, useActiveElement } from "@vueuse/core";
const active = useActiveElement();
const typing = () => ["INPUT", "TEXTAREA", "SELECT"].includes(active.value?.tagName)
	|| active.value?.isContentEditable;

onKeyStroke("z", (e) => {
	if (!(e.ctrlKey || e.metaKey) || typing()) return;
	e.preventDefault();
	e.shiftKey ? store.redo() : store.undo();
});
```

Register listeners once, in setup. Never register them from `load()`: that would
add another listener on every save or reset.
