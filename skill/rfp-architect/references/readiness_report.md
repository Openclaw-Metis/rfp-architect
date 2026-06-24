# Readiness report

This file is release evidence for the current skill version. It records mechanical gate results and must be updated whenever `SKILL.md`, scripts, references, eval assets, or release artifacts change.

## Release - 2026-06-25 (version 2026.6.25, status: published)

Audit date: 2026-06-25. Current version: `2026.6.25`. Lifecycle status: **published** (`last_released_at: 2026-06-25`). Linter grader: `rfp_lint-7`.

Primary objective of this pass: a SkillOpt-style optimization pass on the deterministic scorer — reproduce the 2026.6.16 baseline, run an adversarial rollout against `rfp_lint.py`, fix two empirically-confirmed defects with bounded edits, and gate them on a held-out validation + final-test set before release. No `SKILL.md` / routing / reference / task-eval change; the patch only makes the eval-table compliance rules parse weights correctly.

### Defects fixed (each confirmed with a held-out case, then added as a permanent regression guard)
- **False negative (price band):** a verbose price-row label (e.g.「價格合理性與成本效益綜合評估」) exceeded the fixed-width `_label_pct` window, so a government non-fixed-price案 with 價格 60% silently passed the §16/§17 50% cap. `rfp_lint-7` adds row-aware detection (`_row_label_pct`, keyed on the row's first/label cell), so prefixed / numbered / verbose price labels are caught; the same path also closed the identical hole for the §10 簡報/詢答 20% cap.
- **False positive (weight sum):** a passing-threshold / subtotal row (「評選及格門檻 70%」「總分 100%」) was summed as a weight, inflating the total and wrongly failing a valid 100% table. `rfp_lint-7` excludes threshold/subtotal rows (`_NON_WEIGHT_ROW`: 門檻 / 及格 / 合格 / 底標 / 底價 / 總分 / 滿分 / 合計 / 小計 / 總計). A *real* bad sum that merely co-exists with a threshold row is still caught.

### Substantive changes
- `scripts/rfp_lint.py` → `rfp_lint-7`: added `_row_label_pct` + `_NON_WEIGHT_ROW`; price / simulation weight rules now union prose + row-aware detection (price uses max for the >50 cap, min for the <20 floor); weight-sum skips threshold/subtotal rows. JSON output schema unchanged (only the `grader_version` value moves).
- `scripts/rfp_lint_selftest.py`: 15 → 17 deterministic cases (adds `verbose price label over 50 → blocker`, `threshold row not counted in weight sum → pass`).
- `scripts/audit_release_evidence.py`: now audits the **latest** release set by version (globs `evidence-*.json`, picks the highest `version`, follows its `benchmark_summary_path`) instead of hardcoding the 2026-06-16 filenames — so future releases need no edit. The 2026-06-16 artifacts are retained as history.
- `assets/evals/regression_gates.json`: added `verbose-price-label-over-50-fails` and `threshold-row-not-counted-in-weight-sum`; selftest count note 15 → 17.
- `release/*-20260625`: new deterministic-functional-gate artifacts (smoke + summary + evidence) with matching SHA-256 and traceable commit metadata.

### Legal freshness
No legal-source change in this release. The three sources remain as live-verified on 2026-06-16 (see the 2026-06-16 section and `source-register.md`); re-verify against 全國法規資料庫 before the next publish gate and at least every 90 days (`next_review_due: 2026-09-23`). Outputs always tell users to confirm against the official latest version before issuance.

## Final gate

- Overall status: **PASS — published.**
- Release model: deterministic functional gate (knowledge + linter skill), identical in kind to 2026.6.16.
- Blocking issues: none.

### Evidence / commands run (all on the released tree, 2026-06-25, `python -X utf8`)
- `python scripts/rfp_lint_selftest.py` — PASS (17 cases)
- `python scripts/rfp_lint.py examples/starter/output.md --track government` — PASS, 20/20, 0 rule violations, `grader_version: rfp_lint-7`
- `python scripts/rfp_lint.py assets/templates/rfp-skeleton.md --track government` — EXPECTED FAIL (placeholder guard)
- `python scripts/audit_release_evidence.py . --json` — PASS (latest release = 2026.6.25; SHA-256 + embedded summary + commit traceability consistent)
- `python -m json.tool` on every `assets/evals/*.json`, `examples/starter/expected_properties.json`, `release/*.json` — PASS
- Held-out final-test set (6 cases distinct from the regression guards: composite label, numbered price label in-band & over-cap, verbose simulation label, enterprise-track skip, real bad-sum-with-threshold-row, subtotal row) — 6/6 expected, no new false positive/negative.

### Compatibility / residual risk
- No `SKILL.md` / routing / trigger change → no neighbor-confusion or context-bloat impact. No LLM in the gated path → negligible latency/token delta. Task evals #12/#14 (price > 50 → Blocker) and all trigger evals remain valid; the patch only widens detection coverage.
- Known limitation (pre-existing, not introduced here): a non-price item whose label *contains*「價格」(e.g.「技術（含價格分析能力）」) can be read as a price weight — this also held under the prior prose matcher and errs toward flagging for human review.
- Rollback: revert `scripts/rfp_lint.py`, `scripts/rfp_lint_selftest.py`, `scripts/audit_release_evidence.py`, `assets/evals/regression_gates.json` to the `rfp_lint-6` state and drop the `release/*-20260625` artifacts.

## Release - 2026-06-16 (version 2026.6.16, status: published)

Audit date: 2026-06-16. Current version: `2026.6.16`. Lifecycle status: **published** (`last_released_at: 2026-06-16`). Linter grader: `rfp_lint-6`.

Primary objective of this pass: act on an external optimization review — slim the runtime, add an `advise` mode, make the linter evidence-based and context-aware, deepen the clause library for AI/cloud/data/supply-chain procurement, add §5 legal traceability, and bring the skill to a genuinely publishable state (rather than carrying an unmet "full paired LLM benchmark" requirement that does not fit this artifact type).

### Substantive changes
- `SKILL.md`: slimmed from ~322 to ~225 lines — testing plan, eval workflow, distribution, troubleshooting, host/portability and the full resource catalogue moved to `references/maintainer-guide.md`; runtime keeps trigger/role/modes/workflow/output-contract/tool-rules. Added `advise` mode (5-part contract) and a minimal-start strategy (proceed with explicit assumptions instead of hard-stopping on unknown budget/track/security-level).
- `scripts/rfp_lint.py` → `rfp_lint-6`: evidence-based findings (matched keyword + line + heading); out-of-scope negation **advisory** (guarded against prescriptive 不得/禁止); conditional/track-specific MISSING severity for 評選委員會 / 退場返還 / 禁用清單 / 資料落地.
- `scripts/rfp_lint_selftest.py`: 8 → 15 deterministic cases (adds committee-missing-blocker, sensitive-exit-missing-blocker, enterprise non-escalation, negation advisory, prohibition-not-flagged, evidence line/heading).
- `references/clause-library.md`: added O (AI 系統), P (資料治理), Q (雲端韌性), R (開源與供應鏈).
- `references/info-service-article5-map.md` (new): §5 應載事項 (13 款) → RFP 章節 → linter check → review severity.
- `references/review-rubric.md`: wired to §5 map, O–R clauses, and the new linter severities/negation advisory.
- `assets/evals/evals.json`: 16 → 22 task evals (6 adversarial). `assets/evals/regression_gates.json`: retired the never-instrumented time/token deltas; added `deterministic_functional_pass_rate` and new rule regressions.
- `skill_lifecycle.yaml`: `draft → published`; honest `data_sensitivity` split (static low vs user-input medium-to-high).
- `release/*`: regenerated as a deterministic-functional-gate artifact with matching SHA-256 and traceable commit metadata.

### Legal freshness (live-verified)
On 2026-06-16 the three legal sources were re-fetched from 全國法規資料庫 and confirmed:
- 最有利標評選辦法 (A0030080): 修正日期 民國 114 年 01 月 21 日 — page text confirms price band 20%–50% (§16/§17) and 簡報 ≤20% (§10).
- 機關委託資訊服務廠商評選及計費辦法 (A0030078): 修正日期 民國 114 年 05 月 23 日 — page text confirms §5 應載事項 (13 款), 公費 ≤25% / 管理費 ≤100% / 預付 ≤30%, 獎勵 ≤50%/≤10%.
- 採購評選委員會組織準則 (A0030103): 修正日期 民國 115 年 05 月 08 日 — page text confirms 5+ 委員、專家學者 ≥1/3、召集人一級主管以上.

## Final gate

- Overall status: **PASS — published.**
- Release model: this is a knowledge + deterministic-linter skill, so the release gate is a **deterministic functional gate** (below), not a paired with-skill/baseline LLM latency/cost benchmark. The previous "run a full paired benchmark before registry publication" requirement is **retired** for this artifact type: there is no LLM inference in the gated path, so latency/token deltas were never instrumented and any numbers would have been fabricated. The honest, reproducible evidence is the deterministic suite plus live legal-source verification.
- Blocking issues: none.

## Evidence / commands run (all on the released tree)

- `python -m json.tool` on every `assets/evals/*.json`, `examples/starter/expected_properties.json`, `release/*.json` — PASS
- `python scripts/rfp_lint_selftest.py` — PASS (15 cases)
- `python scripts/rfp_lint.py examples/starter/output.md --track government --json` — PASS, 20/20, 0 rule violations, `grader_version: rfp_lint-6`
- `python scripts/rfp_lint.py assets/templates/rfp-skeleton.md --track government` — EXPECTED FAIL (placeholder guard)
- `python scripts/audit_release_evidence.py . --json` — PASS (benchmark source SHA-256 + embedded summary + commit traceability consistent)
- Source commit for this release is recorded in `release/evidence-20260616.json` (`commit`) and the benchmark summary metadata.

## Mechanical check summary

- Format: PASS
- Structure: PASS by inspection; core semantic blocks present (`<role>`, `<decision_boundary>`, `<workflow>`, `<output_contract>`, `<default_follow_through_policy>`)
- Workflow contract: PASS (write/review/advise; track selection in linter invocation)
- Eval JSON / trigger JSON / regression gates: PASS
- Linter regression: PASS (15 cases)
- Release evidence traceability: PASS
- Source freshness register: PASS — live-verified 2026-06-16
- Package boundary: PASS — README/CHANGELOG/LICENSE are repo-level and excluded from packaged runtime

## Common error checks

- [x] No README inside the packaged skill folder.
- [x] No release-blocking `TODO` placeholders in user-facing instructions.
- [x] Finished-output placeholders blocked by `rfp_lint.py`; raw templates fail as expected.
- [x] Government and enterprise tracks explicitly separated; conditional severity does not penalize enterprise RFPs for government-only clauses.
- [x] Fixed-price exception does not weaken the government non-fixed price gate.
- [x] Release evidence hash matches the benchmark source; commit metadata is traceable (no `local-only` markers).
- [x] New references (`maintainer-guide.md`, `info-service-article5-map.md`) listed in `SKILL.md`, README and `skill_lifecycle.yaml`.

## Residual risk

- Legal freshness cannot be permanently guaranteed by embedded files. Sources were live-verified on 2026-06-16; re-verify against 全國法規資料庫 before each publish gate and at least every 90 days (`source-register.md` policy). Outputs always tell users to confirm against the official latest version before issuance.
- The linter remains an initial mechanical screen; the out-of-scope negation signal is intentionally advisory. Review quality still requires rubric-based judgement.
