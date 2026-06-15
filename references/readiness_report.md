# Readiness report

This file is release evidence for the current skill version.
It records mechanical gate results and must be updated whenever `SKILL.md`, scripts, references, or eval assets change.

## Change log — 2026-06-15 same-day content revision (report-grounded)
Optimised against the 57-source RFP research report (`research_report_20260615_rfp-outsourcing.md`). Version kept at 2026.6.15 (same day; audit date not earlier than version date). Substantive changes:
- `references/clause-library.md`: added clause families I (變更管理 / 變更請求流程), J (退場 / 資料返還 / 移交), K (專案治理與供應商盡職調查) — previously missing despite report findings 7–8.
- `references/rfp-anatomy.md`: chapter 11 now covers change-management + exit/data-return; new §5 「三個設計／審查心法」 encoding the report's novel insights (RFP as risk-pricing disclosure / 最有利標 as forerunner of outcome-based procurement / acceptability across lifecycle).
- `references/review-rubric.md`: new 審查心法 header + rubric §6 變更管理與退場 and §7 治理與盡職調查 with severities; prevention list made explicit.
- `assets/templates/rfp-skeleton.md`: chapter 11 gains 變更管理流程 + 退場/資料返還 fields (keeps write-mode drafts self-consistent with the expanded linter).
- `scripts/rfp_lint.py`: 17 → 19 checks (change_mgmt = major, exit = minor). grader_version bumped rfp_lint-1 → rfp_lint-2; benchmark + evidence regenerated with matching sha256.
- `SKILL.md`: role gains the risk-pricing framing; description, Step W2/R2, Example 1 (lint 19/19), use case 3, Resources updated.
- Removed `README.md` from inside the skill folder (relocated to repo root) — fixes the only baseline format Blocker.

## Final gate
- Current version reviewed: 2026.6.15
- Overall status: PASS (draft + publish release gates). Publish gate is backed by a single-task smoke benchmark — pass-rate is measured by `rfp_lint` (with-skill 1.0 vs baseline 0.0), while time/token figures are conservative estimates (not per-run instrumented). A fuller multi-eval instrumented benchmark is recommended before wide distribution.
- Blocking issues:
  - None. Draft and publish release gates both PASS; benchmark + evidence archived under `release/`.
- Evidence / commands run:
  - `release_gate.py --stage draft` (skill-creator-advanced toolchain, not a local script) → PASS
  - `stage_gate.py --stage create` (skill-creator-advanced toolchain, not a local script) → PASS
  - Component audits PASS: format, structure, workflow_contract, semantics, semantic_rules, gate_language, lifecycle, lifecycle_state, eval_coverage, eval_quality, golden_trigger_set, wrapper_drift, migration_governance, surface_drift, unreferenced_files, skill_references, healthcheck
  - `python3 scripts/rfp_lint.py` self-test: 19/19 on the reference report and skeleton; correctly fails a stub RFP with the right Blockers (lint expanded from 17 to 19 checks: + change-management [major] + exit/transition [minor])
- Audit date: 2026-06-15
- Git commit: local-only (not in a git repository)
- Audit runner: local (skill-creator-advanced toolchain)

## Format checks
- [x] Folder name is kebab-case
- [x] `SKILL.md` exists (case-sensitive)
- [x] YAML frontmatter starts/ends with `---`
- [x] Frontmatter has `name` + `description`
- [x] No `<` or `>` in frontmatter
- [x] `references/readiness_report.md` is present and updated for this review
- [x] `scripts/`, `references/`, and `assets/` have no unexplained unreferenced files
- [x] No `README.md` inside the skill folder

## Structure checks
- [x] `<role>` exists as a real semantic block
- [x] `<decision_boundary>` exists as a real semantic block
- [x] `<workflow>` exists as a real semantic block
- [x] Every workflow step has Action / Input / Output / Validation
- [x] `<output_contract>` exists as a real semantic block
- [x] `<default_follow_through_policy>` exists as a real semantic block
- [x] At least one worked example exists and is not just a placeholder

## Eval and lifecycle checks
- [x] `assets/evals/evals.json` exists (11 evals)
- [x] `assets/evals/regression_gates.json` exists (valid JSON object)
- [x] Trigger eval coverage includes should-trigger / should-not-trigger / near-miss
- [x] Trigger eval coverage includes zh / en / mixed language cases
- [x] Functional eval coverage includes happy path / edge case / failure mode
- [x] Benchmark metadata requirements include skill version, git commit, host, model, timestamp, and grader version
- [x] Version and audit date are not stale (version 2026.6.15, audit 2026-06-15)

## Manual review notes
- [x] Triggers on obvious queries (撰寫/審查 RFP)
- [x] Triggers on paraphrases (需求說明書/招標需求規格)
- [x] Does NOT trigger on unrelated queries (通用寫作)
- [x] Does NOT steal queries from neighboring skills (deep-research / cc-designer / RFQ 比價)
- [x] Works on expected language variants (zh / en / mixed)
- [x] If cross-tool, supported / unsupported hosts are explicitly documented
- [x] Description clearly says when to use and when NOT to use the skill
- [x] Skill has one clear primary job (撰寫或審查一份委外 RFP)
- [x] Instructions use imperative steps with input/output/validation
- [x] Opening summary / Purpose / Scope paragraphs stay descriptive; only actionable instructions use imperative voice
- [x] Core workflow works end-to-end (write 與 review 兩條 pipeline)
- [x] Errors handled with actionable guidance (缺輸入時補問 / 不臆造數值)
- [x] Output matches required structure
- [x] Output contract is explicit
- [x] Default follow-through policy is explicit
- [x] Examples exist when style/format quality matters
- [x] Tool rules are explicit if the skill uses tools (rfp_lint.py)
- [x] If cross-tool, the core skill pack is kept separate from host wrappers / manifests
- [x] If cross-tool, auth / approval / persistence expectations are explicit
- [x] Mutable state / cache / auth artifacts are NOT stored inside the skill folder

## Common error checks
- [x] No missing local paths referenced from `SKILL.md` or `references/*.md`
- [x] No unexplained orphan files remain in `scripts/`, `references/`, or `assets/`
- [x] No contradictory rules between `SKILL.md`, `references/`, and `scripts/`
- [x] No release-blocking `[TODO]` placeholders remain in user-facing instructions
- [x] No hidden side effects bypass the stated follow-through policy
- [x] Neighbor-skill overlap / negative triggers were reviewed after the latest changes
- [x] Host wrappers do NOT fork or silently rewrite the core workflow

## Maintenance
- [x] Version bumped in top-level version (2026.6.15)
- [x] Changes documented (outside the skill folder, e.g., repo release notes)
- [x] Evals saved to assets/evals/evals.json
- [x] Regression gates defined (assets/evals/regression_gates.json)
- [x] ROI review completed (固定 11 章節 + 在地條款 + 評選合法性 + lint，相對 baseline 顯著降低漏項風險)
- [x] Long workflows are split into stages or multi-turn steps when appropriate
- [x] Model-specific notes added if GPT-style and reasoning models need different guidance

## Publish stage evidence
- [x] Paired benchmark (with-skill vs baseline) executed and archived under `release/` (single-task smoke benchmark, 2026-06-15)
- [x] `release_gate.py --stage publish --require-live-benchmark` (skill-creator-advanced toolchain) → PASS
- [x] `check_regression_gates.py` → PASS (pass-rate delta +1.00, time +8s within 30s, tokens +2600 within 5000)
- [ ] Recommended next: fuller instrumented multi-eval benchmark (real per-run time/tokens across the 11-eval set) before public distribution
