# Translations

- Every user-facing string goes through `_()` (or `_lt()` at import time) in Python and `__()` in
  JavaScript and Vue. DocType labels and descriptions are picked up from the JSON.
- Wrap whole sentences with placeholders, never concatenated pieces:
  `_("Trip {0} is closed").format(name)`, `__("Trip {0} is closed", [name])`.
- Keep a `__()` call's arguments on one line: build the list first (`const args = [...]`). When prettier
  splits it over lines with a trailing comma, Frappe's extractor reads a third, "context" argument and the
  string silently leaves `main.pot` and its `.po` translation (checked on 16.60.1). The same for a regex
  literal just before a call.
- Each language the project ships is `<app>/locale/<lang>.po` (gettext, like Frappe, ERPNext and
  HRMS; the old `translations/<lang>.csv` format is not used); `locale/main.pot` lists every
  string. Update them with `/translations`. The languages are stated in the project's rules.
- Names of seeded records are data, so nothing extracts them by default: register an extractor
  in the repo-root `babel_extractors.csv` (`frappe/gettext/translate.py: get_method_map`).
- For a string Frappe already translates, use Frappe's wording so a word reads the same across
  the desk. Translations merge in install order, so the app's entry wins: correct a plainly wrong
  Frappe translation in the app and list it in `docs/translations.md`.
- Keep one term per concept across a project's apps; the agreed terms are in the project's
  glossary when it has one. Agree a new domain term with the user and add it there.
- A value that differs by language is a child table with a `Language` link (Frappe's Language,
  named by code: `ar`, `en`) and the text, both required, the language unique per record. Never a
  field per language (`name_ar`, `name_en`).
- Right-to-left languages: layouts mirror through logical CSS properties; numbers, dates and codes keep
  their order inside the text.
