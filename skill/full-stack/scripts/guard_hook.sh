#!/usr/bin/env sh
# Host hook entry for run_guard.py. Picks a working Python (python3, python,
# or the Windows py launcher; skips stubs that fail to run) and passes the
# hook event on stdin through unchanged. With no Python, does nothing (exit 0),
# so the host never blocks edits because the guard could not start.
here=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
for py in python3 python "py -3"; do
  if $py -c "import sys; sys.exit(0 if sys.version_info >= (3, 8) else 1)" >/dev/null 2>&1; then
    exec $py "$here/run_guard.py" hook "$@"
  fi
done
exit 0
