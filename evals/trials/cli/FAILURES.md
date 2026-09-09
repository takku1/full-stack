# Observed execution failures

Initial sandbox invocation `python evals/trials/cli/test_cli.py initial` exited 1 before its first CLI call: PermissionError [Errno 13] writing tmpk7iajnaw/valid.csv, followed by WinError 5 during temporary-directory cleanup. Reran with escalation as required by the host.

The escalated initial invocation completed all 26 CLI calls and behavioral assertions, then exited 1 with WinError 32 removing tmplzwxwyuw/inventory.sqlite3. Diagnosis: the test harness used sqlite3 connection context managers, which manage transactions but do not close connections. Application storage already explicitly closes connections. Fixed the two test trigger connections using contextlib.closing. The transcript of assertions before this cleanup failure is retained as initial-before-cleanup-fix.json; its internal outcome predates failed cleanup and is not a successful whole-run result. Initial successful rerun is recorded separately.
