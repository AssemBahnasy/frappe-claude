# How work is done

- **One step at a time.** Build one step, verify it (`/bench-verify`: migrate, build, tests, the
  browser where it shows), document it, then stop for review before the next. A list of fixes
  approved as a whole is done in one go.
- **Ask before deciding the user's design.** A new DocType, a field that changes a record's
  meaning, a link between two apps, or a new screen is proposed first (fields table or
  mockup) and built only once approved.
- **UI needs an approved mockup** before any implementation code ([ui.md](ui.md)).
- **Verify in Frappe's source** before relying on any hook, desk API or DocType behaviour, and
  cite the file or function in the docs (`/frappe-source`).
- **Docs ship with the change** in the app's `docs/` folder ([docs.md](docs.md)). A change is not
  done until its docs say what it does now.
- **Tests ship with the change** ([testing.md](testing.md)).
- **Stay inside the task's app.** Never edit `frappe/` (core) to make an app work; never edit
  another app in passing — say what it needs and ask.
- **Leave work uncommitted** unless the user says to commit ([git.md](git.md)).
- **Report honestly.** If migrate, a test or the build fails, say so with the output. Never call
  something verified that was not run.
