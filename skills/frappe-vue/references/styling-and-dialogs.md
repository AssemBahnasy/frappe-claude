# Styling, sizing, and Vue inside Frappe dialogs

## Styling rules

1. **`<style scoped>` on every component.** `lang="scss"` works (Frappe's esbuild
   compiles it). Use `:deep(.x)` to style child elements you don't render
   (Frappe controls, third-party components).
2. **Use Frappe's CSS variables, not hex colours.** Light and dark mode then
   work without extra code, and the UI matches the desk.
3. **Use Bootstrap 4 utility/component classes** that Frappe already ships:
   `btn btn-default btn-sm`, `btn-primary`, `text-muted`, `form-control`,
   `d-flex`, `mr-2`, `small`, `indicator-pill`, `frappe-card`.
4. **No global stylesheets from components.** Unscoped CSS and injected `<link>`
   tags apply to the whole document and restyle the desk.
5. **Prefix any class that must be unscoped** with `{app}-{feature}-`.
6. **SFC styles ship inside the JS bundle.** Frappe's `frappe-vue-style` esbuild
   plugin inlines them as `frappe.dom.set_style(...)`. The build log lists a
   `.css` file, but it isn't written or needed. Don't `frappe.require` a CSS file
   for Vue styles.

### Frequently used variables (verified in Frappe v16 SCSS)

| Purpose | Variables |
|---|---|
| Surfaces | `--fg-color` (cards/panels), `--bg-color` (page), `--card-bg`, `--control-bg` |
| Text | `--text-color`, `--heading-color`, `--text-muted` |
| Lines | `--border-color` |
| Accent | `--primary-color`, `--highlight-color` |
| Spacing | `--padding-sm`, `--padding-md`, `--padding-lg`, `--margin-md` |
| Shape | `--border-radius`, `--border-radius-lg`, `--shadow-sm` |
| Type | `--text-sm`, `--text-md`, `--text-lg` |
| Layout | `--page-head-height` (`--navbar-height` exists but v16 shows no top navbar) |
| Palette | `--gray-50` … `--gray-900`, `--blue-500`, `--green-500`, `--red-500`, … |

### Full-height canvas on a page

Don't hardcode offsets: v16's desk has no top navbar (`--navbar-height` is still 48px), so
`calc(100vh - var(--navbar-height) - …)` leaves a gap. Measure where the root starts instead:

```vue
<script setup>
import { onMounted, ref } from "vue";
import { useEventListener } from "@vueuse/core";

const root = ref(null);
const top = ref(0);
const measure = () => (top.value = root.value?.getBoundingClientRect().top || 0);
onMounted(measure);
useEventListener(window, "resize", measure); // removed automatically on unmount
</script>

<template>
	<div ref="root" :style="{ height: `calc(100vh - ${top}px - var(--margin-md))` }">…</div>
</template>
```

A Leaflet (or any canvas) child must also re-measure itself:
`useResizeObserver(el, () => map?.invalidateSize())`.

## Modals and overlays

**Prefer Frappe dialogs** (`frappe.ui.Dialog`, `frappe.prompt`, `frappe.confirm`,
`frappe.msgprint`) over custom Vue modals. They handle z-index, focus, Esc,
mobile layout, and the desk's look. Use `frappe.show_alert` for toasts.

If you must render an overlay yourself (`<Teleport to="body">`): scoped styles
don't reach teleported nodes, so use an unscoped, prefixed class and
`z-index: 1050`+ (Bootstrap modal backdrop is 1040, modal 1050).

## Vue inside a `frappe.ui.Dialog`

Use Frappe's dialog chrome (title, primary action, footer) with Vue content in
the body.

```javascript
import { createApp } from "vue";
import ConfigurePanel from "./ConfigurePanel.vue";

export function open_configure_dialog({ value, on_apply }) {
	let app = null;
	const state = { value: structuredClone(value) };

	const dialog = new frappe.ui.Dialog({
		title: __("Configure"),
		size: "large",
		fields: [{ fieldtype: "HTML", fieldname: "vue_area" }],
		primary_action_label: __("Apply"),
		primary_action() {
			on_apply(state.value);
			dialog.hide();
		},
		on_page_show() {
			// dialog hook: fires after the dialog is shown
			app = createApp(ConfigurePanel, { state });
			SetVueGlobals(app);
			app.mount(dialog.get_field("vue_area").$wrapper.get(0));
		},
		on_hide() {
			app?.unmount();
			app = null;
		},
	});
	dialog.show();
}
```

Pass a plain object and let the component mutate a `reactive()` copy, or pass
callbacks. Don't pass the parent's Pinia store into a second app. If the dialog
needs it, register the same pinia: `app.use(parentPinia)`.
