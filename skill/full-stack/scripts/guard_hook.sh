#!/usr/bin/env sh
# Host hook entry for run_guard.py. Picks a working Python (python3, python,
# or the Windows py launcher; skips stubs that fail to run) and passes the
# hook event on stdin through unchanged.
#
# With no Python the guard cannot run. Edits are then allowed (exit 0) so a
# missing interpreter never blocks work, but the loss of enforcement is made
# visible as a host system message at session start and stop (FS-023 defect D4).
# FULL_STACK_GUARD_PYTHONS (comma-separated commands) overrides the candidates.
self=$(printf '%s' "$0" | tr '\\' '/')
here=${self%/*}
[ "$here" = "$self" ] && here=.
event=$(cat)
candidates=${FULL_STACK_GUARD_PYTHONS:-python3,python,py -3}
old_ifs=$IFS
IFS=,
for py in $candidates; do
  IFS=$old_ifs
  if $py -c "import sys; sys.exit(0 if sys.version_info >= (3, 8) else 1)" >/dev/null 2>&1; then
    printf '%s' "$event" | $py "$here/run_guard.py" hook "$@"
    exit $?
  fi
  IFS=,
done
IFS=$old_ifs
case $event in
  *SessionStart*|*'"Stop"'*)
    printf '%s\n' '{"systemMessage": "Full Stack guard inactive: no Python 3.8+ found (tried python3, python, py -3). Edits are not checked against the write set."}'
    ;;
esac
exit 0
