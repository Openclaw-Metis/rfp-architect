# Readiness report

This file is release evidence for the current skill version.
It records mechanical gate results and must be updated whenever `SKILL.md`, scripts, references, or eval assets change.

## Change log — 2026-06-16 revision (verifiability hardening, V3)

Third pass acting on a critical review of a GPT5.5 assessment of V2. Verified each load-bearing claim against the actual files before acting; accepted the real catches, rejected two inaccuracies (the "README inconsistency" — the README is at repo root, not inside the skill folder, so the readiness statement is correct; and the attribution of Healthcare.gov/NPfIT/Queensland/GDS cases "to the research report" — the report contains none of them, verified by grep). Same-day iteration: version stays 2026.6.16; grader_version rfp_lint-3 → rfp_lint-4. Substantive changes:
- `scripts/rfp_lint.py`: upgraded from keyword-only to **keyword completeness (20) + regex compliance rules (4)** — `placeholder` (leftover 【填入】/__% → draft not finished, blocker), `presentation_weight` (簡報/詢答 >20% → major), `price_weight` (價格 outside 20–50% → warning, with fixed-price carve-out), `weight_sum` (評選 table weights ≠ ~100% → warning). This closes the gap GPT5.5 flagged: a keyword-complete RFP with 價格 60% / 簡報 30% now FAILS instead of passing.
- `assets/evals/evals.json`: **fixed eval 4** — its expected_output/expectations no longer require the imprecise "平均總評分 70 分以上者第 1 名"; now states 70 分 is an agency-set qualifying score, not a fixed legal value (aligns with `taiwan-procurement.md`). This was a real V2 self-contradiction the mechanical gates could not catch (they do not check reference↔eval semantic consistency — see manual check below).
- `examples/starter/output.md`: NEW filled reference RFP (no placeholders, weights sum to 100% with price 20%) — makes `example_tests` a real validation (previously fixture-only) and serves as the clean lint self-test fixture.
- `assets/templates/rfp-skeleton.md`: legal-version header (法規版本 / 查核日期 / 待法務確認) + appendix **RTM / 交付驗收 / 付款 gate 三矩陣** (requirement→deliverable→acceptance→payment traceability).
- `references/clause-library.md`: new clause families **M 個資處理與事故通報** and **N 跨境資料與雲端區域揭露**; clause J now also requires 刪除/銷毀 of the vendor's copies (返還 ≠ 刪除).
- `references/taiwan-procurement.md`: §6 gains two **preset weight tables** (固定價格 vs 廠商報價; price 5% only legal in the fixed-price table, 20% floor otherwise — weights verified to sum to 100%).
- `references/case-patterns.md`: NEW failure-mode → RFP-control-point page (honestly sourced as well-known public cases, explicitly NOT from the research report).
- `schemas/*.json`: the four empty-shell schemas fleshed out with real properties/required (lifecycle, release_evidence, skill_spec, run_trace) so they actually validate.
- `SKILL.md`: Step 0 gains a 政府 / 企業 dual-track branch; Step W3 lint validation now covers rule violations + placeholder + legal-version header; Resources updated.

Status note: `skill_lifecycle.yaml` deliberately stays `status: draft` with `last_released_at: null`. Passing the publish gate means **publish-ready**, not **already released** — these are consistent (the `lifecycle_state` audit passes in this exact combination). The skill becomes `published` only when actually cut into a registry.

New manual check (gates cannot catch this class): after any change to reference content that encodes a fact (e.g. the 70-分 wording), grep the eval set for the OLD wording and confirm no eval still rewards it. The eval-4 bug proves the mechanical gates do not verify reference↔eval semantic agreement.

## Change log — 2026-06-16 revision (legal-compliance deepening, V2)

Second optimisation pass acting on a critical review of an external proposal (Copilot V1) plus direct verification against 全國法規資料庫 (web-checked). Version 2026.6.15 → 2026.6.16. Substantive changes (each web-verified against the actual statute, not a report section):
- `references/taiwan-procurement.md`: new §8 《機關委託資訊服務廠商評選及計費辦法》 (pcode A0030078, §3 scope / §5 mandatory items / §7 evaluation items / 準用最有利標); §5 reworked to the three statutory methods (總評分法 §12 / 評分單價法 §13 / 序位法 §15); fixed the "70 分" wording (機關-set qualifying score, NOT a fixed legal value); 五面向 → 八類 (§5 最有利標評選辦法); §6 now states the price weight 20%–50% bound (§16 評分 / §17 序位) **with the fixed-price exception** (固定價格給付 may go below 20%) + simulation ≤20% (§10/§14); version-stamped (114-01-21 / 114-05-23) + 防綁標 guidance.
- `references/clause-library.md`: new clause L 計費方式 (總包價 / 計時 / 服務成本加公費; caps 管理費 ≤100% 直接薪資, 公費 ≤25%, 獎勵 ≤50%/≤10%, 預付款 ≤30%); clause G gains the 分包/轉包著作權鏈條 risk (員工約定 ≠ 分包商約定).
- `references/rfp-anatomy.md`: ch5 + §2 add 系統轉換/技術移轉 requirements (in-contract, explicitly distinguished from exit clause J); §1 法源對照 note to 計費辦法 §5.
- `references/review-rubric.md`: §3 price 20%–50% Blocker (with fixed-price carve-out) + simulation ≤20% Major + 資訊服務 §5/§7 cross-check; §2 system-transition check; §5 subcontractor-IP-chain + 計費 checks.
- `scripts/rfp_lint.py`: 19 → 20 checks (+ `migration` = minor; keywords deliberately exclude bare 資料移轉 to avoid trivial always-hit / overlap with exit); `pricing` keywords expanded with statutory 計費 terms. grader_version rfp_lint-3 → rfp_lint-4 (V3); rfp_lint-2 → rfp_lint-3 (V2).
- `assets/templates/rfp-skeleton.md`: ch5 系統轉換/移轉 field, ch8 法定計費方式, ch9 price 20%–50% prompt (keeps write-mode drafts at 20/20).
- `assets/evals/evals.json`: 11 → 13 evals (+ id 12 review price-weight-60% → Blocker; + id 13 write 成果不確定 → 成本加公費 + 公費25%).
- `SKILL.md`: version 2026.6.16; description, Step W2/R2, Example (lint 20/20), use case 3, Resources updated for price bound / 計費 / sub-law / 分包鏈條.

Decisions taken from my own review of the V1 proposal: (a) added the **fixed-price exception** to the price 20%–50% rule so the rubric does not false-positive on legitimate fixed-price RFPs; (b) sourced all legal content to 全國法規資料庫 條號 (verified), not to non-existent report sections; (c) rated the sub-law gap as **Major**, not Blocker; (d) ran the full mechanical gate set below rather than leaving it as a plan.

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
- Current version reviewed: 2026.6.16
- Overall status: PASS (draft + publish release gates). Publish gate is backed by a single-task smoke benchmark — pass-rate is measured by `rfp_lint` (with-skill 1.0 vs baseline 0.0), while time/token figures are conservative estimates (not per-run instrumented). A fuller multi-eval instrumented benchmark is recommended before wide distribution.
- Blocking issues:
  - None. Draft and publish release gates both PASS; benchmark + evidence archived under `release/`.
- Evidence / commands run:
  - `release_gate.py --stage draft` (skill-creator-advanced toolchain, not a local script) → PASS
  - `stage_gate.py --stage create` (skill-creator-advanced toolchain, not a local script) → PASS
  - Component audits PASS: format, structure, workflow_contract, semantics, semantic_rules, gate_language, lifecycle, lifecycle_state, eval_coverage, eval_quality, golden_trigger_set, wrapper_drift, migration_governance, surface_drift, unreferenced_files, skill_references, healthcheck
  - `python3 scripts/rfp_lint.py` self-test (V3, 20 完整度 + 4 規則): filled `examples/starter/output.md` → 20/20 clean (0 rule findings); raw skeleton → FAIL (placeholder rule, correct — it is a template); RFP with 價格 60% / 簡報 30% → FAIL (presentation>20% major + price warning) — the V2 gap is closed; 評選 weights summing to 80% → sum warning; research report → 19/20 (migration minor expected-absent), 0 Blocker, no placeholder
- Audit date: 2026-06-16
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
- [x] `assets/evals/evals.json` exists (13 evals)
- [x] `assets/evals/regression_gates.json` exists (valid JSON object)
- [x] Trigger eval coverage includes should-trigger / should-not-trigger / near-miss
- [x] Trigger eval coverage includes zh / en / mixed language cases
- [x] Functional eval coverage includes happy path / edge case / failure mode
- [x] Benchmark metadata requirements include skill version, git commit, host, model, timestamp, and grader version
- [x] Version and audit date are not stale (version 2026.6.16, audit 2026-06-16)

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
- [x] Version bumped in top-level version (2026.6.16)
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
