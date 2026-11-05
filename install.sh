#!/usr/bin/env bash
# Link this repo's rules, skills and agents into ~/.claude. Safe to run again; never overwrites a
# real file or folder, it stops and names it instead.
set -euo pipefail

repo="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
home="${CLAUDE_CONFIG_DIR:-$HOME/.claude}"
mkdir -p "$home/rules" "$home/skills" "$home/agents"

link() {
	local target="$1" path="$2"
	if [ -e "$path" ] && [ ! -L "$path" ]; then
		echo "Stopped: $path already exists and is not a link. Move it away and run again." >&2
		exit 1
	fi
	ln -sfn "$target" "$path"
	echo "linked $path"
}

link "$repo/rules" "$home/rules/frappe"
for skill in "$repo"/skills/*/; do
	link "${skill%/}" "$home/skills/$(basename "$skill")"
done
for agent in "$repo"/agents/*.md; do
	link "$agent" "$home/agents/$(basename "$agent")"
done

# remove links to skills or agents this repo no longer has
for path in "$home"/skills/* "$home"/agents/*; do
	if [ -L "$path" ] && [ ! -e "$path" ] && [[ "$(readlink "$path")" == "$repo"/* ]]; then
		rm "$path"
		echo "removed stale link $path"
	fi
done
