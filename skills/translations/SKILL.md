---
name: translations
description: Update a Frappe app's translations after adding or changing user-facing strings - regenerate main.pot, sync locale/<lang>.po, translate the new entries with the project's terms, compile and check. Use when strings were added or changed, or the user asks to translate, add Arabic, or fix a translation.
argument-hint: "<app>"
---

# Update translations

Read first: `~/.claude/rules/frappe/translations.md` (and the project's glossary, if it has one).

```bash
cd <bench>
bench generate-pot-file --app <app>
# first time only, if <app>/locale/<lang>.po does not exist:
bench create-po-file <lang> --app <app>
bench update-po-files --app <app> --locale <lang>
```

Then edit `<app>/<app>/locale/<lang>.po`:

- Fill every empty `msgstr` for this change. Keep placeholders (`{0}`, `%s`) and HTML tags
  exactly as in `msgid`.
- Use the project's terms from the rule; for a string Frappe already translates, reuse Frappe's
  wording (`grep -n 'msgid "<text>"' <bench>/apps/frappe/frappe/locale/<lang>.po`)..
- Remove nothing that other code still uses; leave `#, fuzzy` entries only after checking them.

```bash
bench compile-po-to-mo --app <app> --locale <lang>
bench build --app <app>
bench --site <site> clear-cache
```

Check a changed screen in that language (`/bench-verify`). If a Frappe translation was corrected, list
it in the app's `docs/translations.md`.
