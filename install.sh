#!/bin/sh
# Install the portable Full Stack skill for Claude Code and/or Codex.
# Usage: ./install.sh [--target claude|codex|both] [--home DIR] [--preview]
set -eu

target=both
home_dir=${HOME:-}
preview=0
while [ $# -gt 0 ]; do
    case $1 in
        --target) target=$2; shift 2 ;;
        --home) home_dir=$2; shift 2 ;;
        --preview) preview=1; shift ;;
        *) echo "Unknown argument: $1" >&2; exit 2 ;;
    esac
done
case $target in claude|codex|both) ;; *) echo "--target must be claude, codex, or both" >&2; exit 2 ;; esac
[ -n "$home_dir" ] || { echo "Supply --home for the target user." >&2; exit 2; }

if command -v sha256sum >/dev/null 2>&1; then hash() { sha256sum "$1" | cut -d' ' -f1; }
elif command -v shasum >/dev/null 2>&1; then hash() { shasum -a 256 "$1" | cut -d' ' -f1; }
else echo "sha256sum or shasum is required." >&2; exit 1; fi

script_dir=$(cd "$(dirname "$0")" && pwd -P)
source_dir=$script_dir/skill/full-stack
# The source must be ordinary files; a symlink would install content from outside this checkout.
[ -d "$source_dir" ] && [ ! -L "$source_dir" ] || { echo "Package source must be an ordinary directory: $source_dir" >&2; exit 1; }
if [ -n "$(find "$source_dir" -type l)" ]; then echo "Redirected package entry under $source_dir" >&2; exit 1; fi
files=$(cd "$source_dir" && find . -type f | sed 's|^\./||' | sort)
count=$(printf '%s\n' "$files" | wc -l | tr -d ' ')

roots=
[ "$target" = claude ] || roots="$roots .agents/skills/full-stack"
[ "$target" = codex ] || roots="$roots .claude/skills/full-stack"

# Preflight every destination before changing any.
plan=
for root in $roots; do
    dest=$home_dir/$root
    cursor=$dest
    while [ "$cursor" != / ] && [ "$cursor" != . ]; do
        if [ -L "$cursor" ] || { [ -e "$cursor" ] && [ ! -d "$cursor" ]; }; then
            echo "Install path must be an ordinary directory: $cursor" >&2; exit 1
        fi
        cursor=$(dirname "$cursor")
    done
    state=new
    differs=
    if [ -d "$dest" ]; then
        if [ -n "$(find "$dest" -type l)" ]; then echo "Redirected install entry under $dest" >&2; exit 1; fi
        for installed in $(cd "$dest" && find . -type f | sed 's|^\./||'); do
            printf '%s\n' "$files" | grep -qx "$installed" || {
                echo "Unexpected installed file; preserve or relocate it before reinstalling: $dest/$installed" >&2; exit 1; }
        done
        state=unchanged
        for f in $files; do
            if [ ! -f "$dest/$f" ] || [ "$(hash "$dest/$f")" != "$(hash "$source_dir/$f")" ]; then
                state=update
                differs="$differs  differs from source (local edit or older package): $f
"
            fi
        done
    fi
    echo "$state: $dest"
    printf '%s' "$differs"
    plan="$plan $state:$root"
done
if [ "$preview" = 1 ]; then echo "Preview only; nothing was copied."; exit 0; fi

stamp=$(date +%Y%m%d-%H%M%S)
for entry in $plan; do
    state=${entry%%:*}; root=${entry#*:}
    [ "$state" = unchanged ] && continue
    dest=$home_dir/$root
    parent=$(dirname "$dest")
    mkdir -p "$parent"
    # Stage beside the destination so the final move stays on one filesystem.
    staging=$parent/.full-stack.staging-$$
    trap 'rm -rf "$staging"' EXIT
    for f in $files; do
        mkdir -p "$(dirname "$staging/$f")"
        cp "$source_dir/$f" "$staging/$f"
        [ "$(hash "$staging/$f")" = "$(hash "$source_dir/$f")" ] || { echo "Staged file differs from source: $staging/$f" >&2; exit 1; }
    done
    backup=
    if [ "$state" = update ]; then
        # Backups live outside every skills directory so hosts never load them.
        mkdir -p "$home_dir/.full-stack-backups"
        host=${root%%/*}
        backup=$home_dir/.full-stack-backups/${host#.}-$stamp
        mv "$dest" "$backup"
    fi
    if ! mv "$staging" "$dest"; then
        [ -n "$backup" ] && mv "$backup" "$dest"
        echo "Install failed; previous copy restored: $dest" >&2; exit 1
    fi
    echo "Installed and SHA256-verified $count files: $dest"
    [ -z "$backup" ] || echo "  previous copy kept at: $backup"
done
