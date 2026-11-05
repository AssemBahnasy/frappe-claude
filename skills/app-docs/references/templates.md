# Doc templates

Replace `<...>`. Delete a section that has nothing in it yet rather than writing "TBD".

Each template is one concern's file. When a DocType or feature has more than a little to say,
its sections (Fields, Rules, Status, Who uses it, Form) become separate files in its folder,
with a `README.md` index, instead of one long file.

## docs/README.md

````markdown
# <App Title>

<One paragraph: what the app does, for whom, and where it sits among its sibling apps, if any.>

Requires Frappe <version> <and any required app>.

## Docs

| Folder | Read it to |
|---|---|
| [architecture/](architecture/separation-of-concerns.md) | Know what the app owns, its layers, its contracts with other apps |
| [doctypes/](doctypes/README.md) | See every DocType and how they relate |
| [<feature>/](<feature>/README.md) | <Change or explain one feature> |
| [api/](api/README.md) | Call the whitelisted endpoints |
| [setup/](setup/README.md) | Install, settings, roles |
| [tests/](tests/README.md) | Write and run the tests |

## Where to start for a task

| Task | Read first |
|---|---|
| Any change | `~/.claude/rules/frappe/index.md`, then [architecture/](architecture/separation-of-concerns.md) |
| <A new ...> | <doc> |
````

## architecture/separation-of-concerns.md

````markdown
# Separation of concerns

## Owns

- <the DocTypes and rules this app is the only owner of>

## Does not own

- <thing> (<owning app>)

## Layers

```
 UI         <forms, pages>
 Endpoints  api/<files>
 Features   <feature packages>
 Records    <module>/doctype/*
```

## Contracts with other apps

| From (this app) | To (app · DocType or function) | Contract |
|---|---|---|
| <Service Visit.vehicle> | <core app> · Vehicle | Link, read only |

## Invariants

1. <This app never writes to ... ; it changes ... only through ...>
````

## architecture/code-organization.md

````markdown
# Code organization

Shared code lives once, in its home (rule: `~/.claude/rules/frappe/architecture.md`).
A helper needed a second time moves here; it is never copied.

## Server: `utils/`

| Module | Holds |
|---|---|
| `<topic>.py` | <what, and who calls it> |

## Client: `public/js/utils/`

| File | Namespace | Holds |
|---|---|---|
| `<topic>.js` | `<app>.<topic>` | <what; "mirrors `utils/<topic>.py`" when it repeats a server rule> |
````

## architecture/data-flow.md

````markdown
# Data flow

```
<upstream record> ──▶ <this app's record> ──▶ <downstream record>
```

| Step | Record | Created by | Then |
|---|---|---|---|
| 1 | <DocType> | <role, on what event> | <what happens next, which function> |
````

## doctypes/README.md

````markdown
# DocTypes

| DocType | Kind | Naming | What it is | Doc |
|---|---|---|---|---|
| <Service Visit> | Submittable | `TRIP-.YYYY.-.#####` | <one line> | [<feature>/<file>.md](../<feature>/<file>.md) |
````

## A DocType doc (in its feature folder)

````markdown
# <DocType>

**Module:** <Module> · **<Master | Submittable | Child of X | Single>** · **Naming:** `<rule>`

<What it is and why it exists, in two or three sentences. Link the records it belongs to.>

## Fields that matter

| Field | Type | Meaning |
|---|---|---|
| `<fieldname>` | Link → <DocType> | <...> |

## Rules

| Rule | Where |
|---|---|
| <what must hold> | `<function>`, on <validate / submit> |

## Status

<Draft → ... ; what moves it, which function>

## Who uses it

| Role | Can |
|---|---|
| <Role> | read / create / submit |

<Which other DocTypes, apps or reports read it, through which function.>
````

## A feature folder README.md

````markdown
# <Feature>

<One paragraph: what the feature does for the user.>

| Doc | Covers |
|---|---|
| [<file>.md](<file>.md) | <one concern> |

## Code

| Path | Job |
|---|---|
| `<app>/<feature>/<module>.py` | <...> |
````

## api/<concern>.md

````markdown
# <concern> endpoints

## `<app>.api.<concern>.<method>`

**POST** · callers need <permission on DocType>

| Argument | Type | Meaning |
|---|---|---|
| `<arg>` | str | <...> |

Returns `{<shape>}`. Delegates to `<feature function>`.
````
