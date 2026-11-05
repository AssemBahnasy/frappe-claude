# Form host — a Vue widget inside a DocType form

For interactive UI tied to the open record: a preview, a small visual editor, a
chart, a map. The form stays in charge: it owns loading, the dirty state and
saving. The widget reads `frm.doc` and writes back only through `frm.set_value`.

## Files

```
{app}/{app}/{module}/doctype/{doctype}/{doctype}.js       ← form script: lifecycle only
{app}/{app}/public/js/{feature}/{app}_{feature}.bundle.js ← widget class
{app}/{app}/public/js/{feature}/{Feature}Widget.vue
```

## 1. Host field

Add an **HTML** field (e.g. `{feature}_html`) to the DocType where the widget
should appear. **Leave its `options` empty.** `ControlHTML.refresh_input()`
rewrites the wrapper whenever `options` has content, which wipes the mounted app
on every refresh. With empty options it leaves the wrapper alone.

The field gives a stable wrapper, a position you choose in the layout, and
`depends_on` support.

## 2. Form script

```javascript
frappe.ui.form.on("{DocType}", {
	refresh(frm) {
		render_{feature}(frm);
	},
});

function render_{feature}(frm) {
	// frm is reused for every record of this DocType: keep the instance on frm
	frm._{feature}_token = (frm._{feature}_token || 0) + 1;
	const token = frm._{feature}_token;
	frm._{feature}?.destroy();
	frm._{feature} = null;

	const field = frm.get_field("{feature}_html");
	field.$wrapper.empty();
	if (frm.is_new()) return; // or render a "save first" hint

	frappe.require("{app}_{feature}.bundle.js").then(() => {
		if (token !== frm._{feature}_token) return; // refreshed again / switched record
		frm._{feature} = new {app}.ui.{Feature}Widget({ wrapper: field.$wrapper, frm });
	});
}
```

`refresh` fires on load, after save, after reload and when switching records.
Re-mounting each time is cheap and avoids stale state. `frm.set_value` does
**not** trigger `refresh`, so the widget isn't remounted while the user is editing.

## 3. Widget class — `{app}_{feature}.bundle.js`

```javascript
import { createApp, reactive } from "vue";
import {Feature}Widget from "./{Feature}Widget.vue";

class {Feature}WidgetHost {
	constructor({ wrapper, frm }) {
		// plain snapshot of what the widget needs; frm.doc itself is not reactive
		this.state = reactive({
			doc: JSON.parse(JSON.stringify(frm.doc)),
			read_only: !frm.perm?.[0]?.write || frm.doc.docstatus !== 0,
		});
		this.app = createApp({Feature}Widget, {
			state: this.state,
			onChange: (fieldname, value) => frm.set_value(fieldname, value), // form owns dirty + save
		});
		SetVueGlobals(this.app);
		this.app.mount($(wrapper).get(0));
	}

	destroy() {
		this.app?.unmount();
		this.app = null;
	}
}

frappe.provide("{app}.ui");
{app}.ui.{Feature}Widget = {Feature}WidgetHost;
export default {Feature}WidgetHost;
```

A widget with more than a couple of components can use Pinia exactly as the page
host does: `createPinia()` in the constructor, plus `store.$dispose()` in `destroy()`.

## 4. Widget component — `{Feature}Widget.vue`

```vue
<script setup>
import { computed } from "vue";

const props = defineProps({ state: Object, onChange: Function });

const layout = computed(() => {
	try {
		return JSON.parse(props.state.doc.{layout_field} || "{}");
	} catch {
		return {};
	}
});

function update_layout(next) {
	if (props.state.read_only) return;
	const value = JSON.stringify(next);
	props.state.doc.{layout_field} = value; // local echo
	props.onChange("{layout_field}", value); // marks the form dirty; user saves normally
}
</script>

<template>
	<div class="{feature}-widget">
		<!-- render from props.state.doc / layout -->
	</div>
</template>

<style scoped>
.{feature}-widget {
	min-height: 200px;
	border: 1px solid var(--border-color);
	border-radius: var(--border-radius);
	background: var(--fg-color);
}
</style>
```

## Rules

- **Never call `frappe.client.save` on the form's own record from the widget.**
  It races the form's own save and causes `TimestampMismatchError`. Use
  `frm.set_value` (or `frappe.model.set_value` for child rows) and let the user save.
- For **read-only data from elsewhere** (stats, related records), call a
  whitelisted method from the widget (`frappe.xcall`). Do it in the widget, not
  in the form script.
- To react to other field changes without a remount, add a field trigger in the
  form script that updates the instance:
  `some_field(frm) { if (frm._{feature}) frm._{feature}.state.doc.some_field = frm.doc.some_field; }`.
- The form stays in the DOM when you navigate away; the widget stays mounted but
  hidden. That's fine as long as the widget registers no `window`/`document` listeners.
