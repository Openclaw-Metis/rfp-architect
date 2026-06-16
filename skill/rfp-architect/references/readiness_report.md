# Readiness report

This file is release evidence for the current skill version. It records mechanical gate results and must be updated whenever `SKILL.md`, scripts, references, eval assets, or release artifacts change.

## Change log - 2026-06-16 local hardening

Current version reviewed: `2026.6.16`

Audit date: 2026-06-16

Primary objective: fix release-blocking mismatches found in the prior review: linter severity drift, untraceable release evidence, missing source freshness registry, README/package boundary ambiguity, and missing regression coverage.

Substantive changes:
- `scripts/rfp_lint.py`: upgraded to `rfp_lint-5`; added `--track auto|government|enterprise` and `--fixed-price`; government non-fixed price `<20%` or `>50%` now fails as `blocker`; fixed-price `<20%` is informational only when fixed-price treatment is explicit; enterprise track no longer applies Taiwan government price-weight law; `weight_sum` is now a failing `major`; `待確認` is no longer treated as an unfinished placeholder.
- `scripts/rfp_lint_selftest.py`: added deterministic regression tests for price upper/lower bounds, fixed-price exception, enterprise track, presentation cap, weight-sum failure, and placeholder failure.
- `scripts/audit_release_evidence.py`: added traceability audit for benchmark hash, embedded summary consistency, and git commit metadata.
- `references/source-register.md`: added legal and case provenance register with official URLs, checked dates, revision dates, and linter-backed rule mapping.
- `references/taiwan-procurement.md`: added `採購評選委員會組織準則` as a tracked freshness source; checked 2026-06-16, revision 民國 115 年 05 月 08 日.
- `assets/evals/evals.json`: expanded from 13 to 16 task evals, adding regressions for government price `>50%`, fixed-price `<20%`, and enterprise-track non-government handling.
- `assets/evals/trigger_evals.json`: added a separate pure routing / description trigger set.
- `README.md`: clarified that README is repo-level documentation and should be excluded from packaged skill runtime when the host disallows README in skill folders.
- `release/*`: regenerated local benchmark summary and evidence with matching SHA-256 and traceable commit metadata.

## Final gate

- Overall status: PASS for local draft/smoke readiness.
- Publish status: NOT CLAIMED. Before registry publication, commit the optimized working tree and run a full paired with-skill/baseline benchmark across `assets/evals/evals.json`.
- Blocking issues for local draft use:
  - None found after this pass.
- Remaining publish requirements:
  - The release benchmark is a local smoke benchmark, not a full instrumented paired benchmark; baseline figures are carried from the prior smoke benchmark for gate compatibility and were not rerun in this pass. Source commit: `86b7c52ca2ec957445a36f340fe0adcefd36eb9c`.

## Evidence / commands run

- `python -m json.tool assets/evals/evals.json`
  - PASS
- `python -m json.tool assets/evals/trigger_evals.json`
  - PASS
- `python scripts/rfp_lint_selftest.py`
  - PASS
- `python scripts/rfp_lint.py examples/starter/output.md --track government --json`
  - PASS, 20/20, 0 rule violations, `grader_version: rfp_lint-5`
- `python scripts/rfp_lint.py assets/templates/rfp-skeleton.md --track government --json`
  - EXPECTED FAIL, placeholder blocker; confirms raw template cannot be mistaken for a finished RFP.
- `python scripts/audit_release_evidence.py . --json`
  - PASS; benchmark source hash and embedded summary match; no `local-only` / `local working tree` markers remain.
- `python -m json.tool release/benchmark-smoke-20260616.json`
  - PASS
- `python -m json.tool release/benchmark-summary-2026.6.16.json`
  - PASS
- `python -m json.tool release/evidence-20260616.json`
  - PASS

## Mechanical check summary

- Format: PASS
- Structure: PASS by inspection; core semantic blocks remain present (`<role>`, `<decision_boundary>`, `<workflow>`, `<output_contract>`, `<default_follow_through_policy>`)
- Workflow contract: PASS by inspection; changed linter invocation now includes track selection
- Eval JSON: PASS
- Trigger eval JSON: PASS
- Linter regression: PASS
- Release evidence traceability: PASS
- Source freshness register: PASS for checked sources on 2026-06-16
- Package boundary: PASS by documentation; README is repo-level and excluded from packaged runtime

## Common error checks

- [x] No README exists inside the packaged skill folder.
- [x] No release-blocking `TODO` placeholders remain in user-facing instructions.
- [x] Finished output placeholders are blocked by `rfp_lint.py`; raw templates fail as expected.
- [x] Government and enterprise procurement tracks are explicitly separated.
- [x] Fixed-price exception no longer weakens the government non-fixed price gate.
- [x] Release evidence hash matches the local benchmark source.
- [x] Release metadata no longer uses `local-only` or `local working tree` markers.
- [x] New references and scripts are listed in `SKILL.md`, README, or `skill_lifecycle.yaml`.

## Eval and lifecycle checks

- `assets/evals/evals.json` exists with 16 task evals.
- `assets/evals/trigger_evals.json` exists with 10 pure trigger evals.
- Coverage includes direct, indirect, negative, near-miss, zh, en, mixed, government track, enterprise track, fixed-price exception, and rule-regression cases.
- `assets/evals/regression_gates.json` includes required rule regressions.
- `skill_lifecycle.yaml` references new scripts and `references/source-register.md`.

## Manual review notes

- Primary job remains coherent: write or review an RFP for outsourced software / information-system procurement.
- The two-mode design remains acceptable because write and review share the same anatomy, law references, clause library, and linter.
- Government and enterprise tracks are now explicitly separated.
- `rfp_lint.py` remains an initial mechanical screen; review quality still requires rubric-based judgment.

## Residual risk

- Legal freshness cannot be permanently guaranteed by embedded files; official legal sources must be rechecked before a real procurement release.
- The current benchmark is smoke-level. Public distribution should use a full paired benchmark with real timing/token instrumentation and archived outputs; do not treat the carried baseline numbers as fresh publication evidence.
