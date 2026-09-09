# Trial evidence and limits

Environment: Windows PowerShell in Z:/full-stack; Python 3.12.10. Date supplied by host: 2026-09-09. Agent identified by host as Codex based on GPT-6; exact backend model version/settings were not exposed. No external libraries, tool installations, network, service, or mocks used.

Input is retained verbatim in ../INPUT.md. Baseline files retain literal supplied behavior. cap50/ retains initial implementation, tests, README and design before follow-up; ../app.py, ../pricing.py, ../test_checkout.py and ../docs/design/checkout.md are final output.

Executed command/result record (all exited 0):
1. Get-Content skills/full-stack/SKILL.md; read portable skill.
2. Get-Content skills/full-stack/references/existing-projects.md; Get-Content skills/full-stack/references/implementation.md; Get-Content skills/full-stack/references/terminology.md; read only portable references.
3. New-Item created trial/baseline, docs/design, evidence directories; Set-Content established baseline pricing.py, app.py, test_checkout.py; Copy-Item preserved them in baseline/. No preexisting subject application was inferred.
4. python --version => Python 3.12.10.
5. python -m unittest discover -s evals/trials/existing -v => Ran 1 test in 0.000s; OK (test_existing_checkout).
6. Get-Content skills/full-stack/references/artifacts.md; read handoff/work package pattern.
7. Set-Content wrote INPUT.md, design/handoff, ROADMAP.md, README.md and initial application/test changes. Exact written implementation is retained in cap50/; initial requirements in cap50/design.md.
8. python -m unittest discover -s evals/trials/existing -v => Ran 9 tests in 0.000s; OK.
9. New-Item created evidence/cap50; Copy-Item preserved initial output; Get-Content/Replace/Set-Content changed MAX_DISCOUNT_PERCENT 50 to 30, test inputs/expectations and R2 acceptance text.
10. python -m unittest discover -s evals/trials/existing -v => Ran 9 tests in 0.000s; OK.
11. Get-FileHash evals/trials/existing/app.py, evals/trials/existing/evidence/cap50/app.py => identical SHA256 60BA96C6E9A195BA4348E71430B8573FA97B6B51CEC39E367BC6773B68F8CA3D.
12. Read README with Get-Content -Raw; replace Checkout example with Checkout usage; WriteAllText; assert exact equality to that replacement => PASS: README exact label replacement only. Updated registry and this evidence document afterward.

Nine named test methods: test_existing_checkout, test_zero_empty_and_zero_prices, test_discount_boundaries, test_floor_after_sum, test_large_integer_precision, test_discount_errors, test_price_errors, test_iterable_and_no_mutation, test_existing_pricing_call. Individual subtests cover negative and above-cap percentages; both bool values; float, string and None percentages/prices; negative prices; inclusive cap and zero; empty and generator inputs. Final tests explicitly reject former valid cap 50, as well as 31. Rounding example [1,1] at 30 returns 1 (per-item rounding would return 0). Old checkout and provider call forms survive. All integration tests import actual app and pricing modules.

Boundary diagnostic: inspection of snapshots and final output shows only pricing's MAX_DISCOUNT_PERCENT changed in production code. Domain-policy acceptance and tests changed to reflect the requested range; checkout source hash is unchanged. This supports the chosen responsibility boundary for this particular policy change, not a general maintainability result. README label step performed no architecture work and did not rerun unrelated tests.

Self-review: requirements, provider ownership, migration compatibility, integer arithmetic and errors were assessed by the implementing agent. Runtime evidence: locally executed unittest results described above, with no test doubles. Independent evaluation: none within this trial; a parent evaluator may assess retained artifacts separately. This single synthetic task and small test suite do not establish broad skill effectiveness, exhaustive correctness, academic validation, production behavior, performance targets, or behavior on other Python versions. Error classes, iterable preservation and integer-subclass acceptance are disclosed implementation conventions, not invented stakeholder requirements.
