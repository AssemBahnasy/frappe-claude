# Separation of concerns and DRY

Two rules shape every change: **each piece of code has one job in one layer**, and **each fact
is written once, in its home**. They apply inside an app (layers, shared homes) and across the
suite (which app owns what, in the project's own rules).

## Layers inside an app

```
 UI          form scripts · list views · desk pages / Vue · print formats
               │  frappe.call / frm.call
 Endpoints   <app>/api/<concern>.py          check access and inputs, then delegate
               │
 Features    <app>/<feature>/*.py            the business rules, plain functions
               │                    ╲
 Records     DocType controllers      Integrations  <app>/integrations/<service>/
             this record's own rules               the only code that talks to an outside service
```

| Layer | Does | Never does |
|---|---|---|
| UI | Shows data, collects input, live feedback | Decides a business rule, checks permissions, computes a value the server stores |
| Endpoint | `@frappe.whitelist`, permission check, argument types, calls one feature function | Business logic, queries beyond loading what it checks |
| Feature | The rules spanning records: calculations, state changes, generating documents | Read `frappe.form_dict`, return HTTP shapes, call an outside service directly |
| Controller | Validation and derived fields of *this* record; calls features for anything wider | Change other DocTypes' records except through their own documents or a feature function |
| Integration | Talk to an outside service behind one interface | Hold business rules |
| `hooks.py` | Declares what runs when (dotted paths only) | Hold logic |

Handlers named in `hooks.py` (`doc_events`, `scheduler_events`) live in the feature they serve
(`<feature>/events.py`, `<feature>/tasks.py`) and are as thin as endpoints.

The server is authoritative: a rule shown live in the browser is still enforced on save in
Python.

## Shared homes (DRY)

| Kind of code | Home | Used as |
|---|---|---|
| Server helpers used by more than one DocType, page or feature | `<app>/utils/<topic>.py` | `from <app>.utils.<topic> import ...` |
| Client helpers used by more than one form or page | `<app>/public/js/utils/<topic>.js` | globals under `<app>.<topic>`, loaded by the app's desk bundle |
| Helpers or rules more than one *app of a suite* needs | the suite's core app, `<core>/utils/<topic>.py` (and `<core>/public/js/utils/`) | imported by the other apps |
| Constants, option lists, defaults | defined once in Python (or as a master DocType / settings field) | read everywhere else |
| Seed data | `<app>/data/<doctype>.json` | read by `install.py` |

How to apply:

1. **Search first.** Before writing a helper, look in the shared homes (this app, then
   the suite's core app).
2. **Second use, shared home.** When code is needed in a second place, move it to its home and
   call it from both; never copy it.
3. **One definition of a rule.** A client-side mirror of a server rule (the same formula in JS,
   for live display) lives in `public/js/utils/` and names the Python function it mirrors.
4. **Data over code.** A rule that varies by case is a setting, a master or a child table, not
   an `if` per case.
5. **Document the home.** A new shared file gets a row in the app's
   `docs/architecture/code-organization.md`.

## Between apps

Each app owns its DocTypes; the ownership table is in the project's own rules.

- **Contracts, not reach-ins.** An app uses another's data only through Link fields and the
  owning app's documented functions. Each contract is a row in the dependent app's
  `docs/architecture/separation-of-concerns.md`.
- **Read upstream, write only your own.** A downstream app reads upstream records and never
  writes them directly. When it must change one (an operation updating a container's status),
  it calls the owning app's function or creates the owning app's document.
- **Reactions go through hooks.** The dependent app declares `doc_events` on the upstream
  DocType in its own `hooks.py`; the upstream app never imports downstream code.
