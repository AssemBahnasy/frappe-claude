---
paths:
  - "**/doctype/**"
---

# DocType form layout

Every DocType's form is designed, never a list of fields in one column. A field's place on the form
is part of the DocType's design, and is proposed and approved with its fields.

## Before designing

1. **Find the pattern.** Read the JSON of two or three DocTypes doing a similar job in Frappe,
   ERPNext, HRMS or CRM (a master like a master, a transaction like a transaction), and name them
   in the proposal. Take their logic, not blindly their layout: some are poor.
2. **Show the layout** in the proposal as a small sketch of tabs, sections and columns.
3. **A copied DocType is not exempt.** A DocType taken from another app is checked against this
   rule too, and layout changes are listed for review.

## How much structure

What Frappe's own apps do, by number of real fields (measured on the forms of Frappe, ERPNext, HRMS
and CRM). Breaks are not counted.

| Fields | Columns | Sections | Tabs |
|---|---|---|---|
| 1–3 | One column is right | None | None |
| 4–6 | Two, as most ERPNext, HRMS and CRM forms do | One, when the fields split by topic | None |
| 7–10 | Two | One or two | None |
| 11–20 | Two, in most sections | About three | Rarely |
| 21–40 | Two, in most sections | Four or five | When topics are distinct |
| 41 or more | Two, in most sections | Six or more; usually ten or more | Yes, four or more |

A section has one or two columns; three when its fields are short and belong side by side; more
is rare. A column usually holds two to six fields. Keep columns of a section roughly even.

## Where each field goes

- **Group by topic.** A section is one topic a user thinks of as one thing (Identity, Dates,
  Pricing, Contact). If it has no clear name, the grouping is wrong.
- **Most important first.** What identifies the record and is filled in first goes at the top
  left. Secondary facts (status, dates, flags) sit in the column beside it.
- **Keep pairs together.** From and To, start and end, a quantity and its unit sit side by side or
  one under the other, never split across sections.
- **Full width alone.** A `Table`, `Text Editor`, `Code` or `HTML` field takes the whole width: it
  gets its own section, with no column break beside it.
- **Rare things out of the way.** Optional or seldom-used sections are `collapsible`.
- **Conditional fields stay with their trigger**, in the same section (`depends_on`). A column that
  can end up empty is a sign the fields belong elsewhere.
- **System fields last**: `amended_from`, `lft`, `rgt` and other hidden or read-only bookkeeping.

## Tabs and breaks

- A tab is a large distinct topic (More Info, Terms, Address & Contact). Fields before the first
  `Tab Break` go in a tab Frappe adds, "Details" (`frappe/public/js/frappe/form/layout.js`).
- Links to related records use a last `Tab Break` labelled "Connections", with `show_dashboard` on.
- A section has a label and a fieldname named for its topic (`pricing_section`). The first section,
  or one holding a single self-explaining field, needs no label. Column breaks have no label.

Check the rendered form in the browser, not only the JSON: light and dark, narrow width, and right
to left when the project ships such a language.
