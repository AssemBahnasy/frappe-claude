# Real Frappe controls inside Vue; metadata-driven property panels

Builders need property panels: "edit the selected node's fields". Don't hand-build
inputs. Render **real Frappe controls** (Link autocomplete, Date pickers, Select,
Check, Code…) from **DocType meta**. Labels, options, `depends_on`-like
filtering and translations then come from the DocType, not from Vue code.

## `FrappeControl.vue` — wrap `frappe.ui.form.make_control`

`make_control` is the public API behind every form, dialog and FieldGroup.

```vue
<script setup>
import { ref, onMounted, onBeforeUnmount, watch } from "vue";

const props = defineProps({
	df: { type: Object, required: true }, // a docfield: { fieldname, fieldtype, label, options, ... }
	modelValue: { default: null },
	readOnly: { type: Boolean, default: false },
});
const emit = defineEmits(["update:modelValue"]);

const el = ref(null);
let control = null;

function same(a, b) {
	return (a ?? "") === (b ?? "");
}

onMounted(() => {
	control = frappe.ui.form.make_control({
		parent: el.value,
		df: {
			...props.df,
			read_only: props.readOnly || props.df.read_only ? 1 : 0,
			change() {
				if (!control) return; // Link controls can fire after unmount
				const value = control.get_value();
				if (!same(value, props.modelValue)) emit("update:modelValue", value);
			},
		},
		render_input: true,
	});
	control.set_value(props.modelValue ?? "");
	control.refresh();
});

watch(
	() => props.modelValue,
	(value) => {
		if (control && !same(value, control.get_value())) control.set_value(value ?? "");
	}
);

watch(
	() => props.readOnly,
	(ro) => {
		if (!control) return;
		control.df.read_only = ro ? 1 : 0;
		control.refresh();
	}
);

onBeforeUnmount(() => {
	control?.$wrapper?.remove();
	control = null;
});
</script>

<template>
	<div ref="el" class="frappe-control-host"></div>
</template>
```

- `change` fires from `set_value` too. The `same()` guard stops the
  emit → watch → set_value loop. Don't remove it.
- Link filters: pass `df.get_query: () => ({ filters: {...} })`.
- Don't mount controls for layout-only fieldtypes (`Section Break`, `Column Break`,
  `Tab Break`). Filter them out with `frappe.model.layout_fields`.

## Metadata-driven panel

Each field gets the same access a form would give it: hidden, read-only or editable,
from the user's permission level, mask, hidden/read-only flags and docstatus
(see permissions.md §4).

```vue
<script setup>
import { computed } from "vue";
import FrappeControl from "./FrappeControl.vue";
import { use{Feature}Store } from "../store";

const store = use{Feature}Store();

const HIDDEN = ["{layout_field}"];
const SKIP = [...frappe.model.layout_fields, "Table", "Table MultiSelect"];

const target = computed(() => store.selected || store.doc);
const perm = computed(() => frappe.perm.get_perm("{DocType}", store.doc)); // parent rules, also for child rows

function access(df) {
	const status = frappe.perm.get_field_display_status(df, target.value, perm.value);
	const masked = df.mask && !frappe.perm.has_perm("{DocType}", df.permlevel || 0, "mask");
	return masked && status === "Write" ? "Read" : status; // "Write" | "Read" | "None"
}

// fields of the selected child row's DocType, or of the parent DocType
const fields = computed(() =>
	frappe
		.get_meta(target.value?.doctype || "{DocType}")
		.fields.filter((df) => !HIDDEN.includes(df.fieldname) && !SKIP.includes(df.fieldtype))
		.map((df) => ({ df, access: access(df) }))
		.filter((field) => field.access !== "None")
);
</script>

<template>
	<div v-if="target" class="properties">
		<FrappeControl
			v-for="{ df, access } in fields"
			:key="`${target.name || target.idx}-${df.fieldname}`"
			:df="df"
			:read-only="access !== 'Write'"
			:model-value="target[df.fieldname]"
			@update:model-value="(v) => (target[df.fieldname] = v)"
		/>
	</div>
</template>
```

Call `frappe.model.with_doctype(childDocType)` in the store's `load()` for every
child DocType the panel renders, so `frappe.get_meta()` is populated.

The `:key` includes the record identity, so switching selection re-creates the
controls. That's simpler and safer than re-pointing a live control.

Never offer an editable input for a field whose access isn't "Write". On save, the server
silently resets fields above the user's permission level, so the edit would just vanish.
