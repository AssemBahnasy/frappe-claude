# frappe-claude

Claude Code rules, skills and agents for any development on the Frappe framework, on any bench.
Nothing here belongs to one project: a project keeps its own facts in its own repo
([rules/index.md](rules/index.md), "What a project states for itself").

## Install on a machine

```bash
git clone git@github.com:AssemBahnasy/frappe-claude.git ~/frappe-claude
~/frappe-claude/install.sh
```

The script links `rules/` to `~/.claude/rules/frappe`, each skill to `~/.claude/skills/<name>` and
each agent to `~/.claude/agents/`. Run it again after a pull that adds a skill or an agent.

## Update

```bash
git -C ~/frappe-claude pull
```

Edits made through the links land in this repo: commit and push them to reach the other machine.

## Layout

| Path | Holds |
|---|---|
| `rules/` | Index and rules, loaded in every session (`paths:` rules on matching files) |
| `skills/` | Recipes, invoked as `/<name>` |
| `agents/` | `frappe-reviewer` |
