# Changelog

All notable changes to **rfp-architect** are recorded here. Versions use CalVer (`YYYY.M.D`).

## [2026.10.31] — Published

Legal-accuracy and real-document pass. Rechecks the encoded law against the official text, corrects what it overstated or missed, and upgrades the scorer from `rfp_lint-8` to `rfp_lint-9` after an adversarial replay found that a government draft with price at 60% could pass silently.

### Fixed — legal content
- **§5 is discretionary** — 《機關委託資訊服務廠商評選及計費辦法》§5 says 「得視個案特性及實際需要載明」. The skill called it 法定應載 throughout; findings now separate 得載 items from items with their own 應 basis (§21 intellectual property, §11 negotiation method, 《最有利標評選辦法》§4, §16–§18).
- **Passing score is required** — §16／§17 require the tender documents to state 合格分數 or the pass／fail rule; the skill said an agency 「得另訂」 one.
- **Presentation** — the rubric cited §14, which is the tie-break rule. §10 第 4 項 is now covered: missing a presentation does not affect bid validity, so it cannot exclude a bidder; scoring that item zero stays lawful.
- **Price routes** — fixed-price treatment now cites §9, §12 and §15; the 「price not scored」 route is covered, where the 20–50% band does not apply.
- **Security outsourcing** — clauses follow 《資通安全管理法》(114/09/24) §10, §11 and 施行細則 (115/01/05) §7, including the third-party security test the agency must arrange for core systems or contracts of NT$10 million or more. The former 「大陸廠牌」 clause now rests on 危害國家資通安全產品 and the national-security vendor regulation.
- **Personal data** — clause M follows 施行細則 §8 and marks the 114/11/11 amendment as not yet in force, so 72 hours is a contract term, not a statutory limit.

### Added
- **`scripts/rfp_extract.py`** — reads docx, odt and UTF-8／UTF-16／Big5 text with the standard library, keeping tables as Markdown. PDF and legacy formats are refused with instructions.
- **Bidder-side review** — findings become clarification questions, protest grounds with deadlines (法 §41, §75) and pricing assumptions, with their own verdict wording.
- **Knowledge** — three procurement routes, the 應載事項 checklist, amount thresholds, waiting-period shortening, 整體委外 (§4, §6, §8), the official PCC weighting example for seven service types, clause S, and AI Basic Act duties for government use.
- **Evals** — task evals 22 → 31; trigger evals 10 → 16.

### Changed — `rfp_lint-9`
- **Every table is scanned** — a table cannot be skipped because of its heading wording. Evaluation tables are recognised by heading chain, header or a priced row; SLA, payment and grading-scale tables stay out. Pieces split across a page are merged, and merged cells carry their label down.
- **Prose** — reads 百分之六十 and full-width digits, and only when no table exists; formulas and abnormally-low-bid sentences no longer become weights.
- **New rules** — `evaluation_weights`, `award_method`, `passing_score`, `committee_size`, `presentation_absence`, plus advisory `soft_placeholder`, `track_unknown` and `input_too_short`. Rule findings carry line numbers.
- **Stricter blocker keywords** — bare 必要 no longer satisfies 功能需求 and bare 授權 no longer satisfies 智財.
- **Context** — fixed-price treatment needs a declaration, so 非固定價格 and notes explaining the exception no longer unlock the low-price path. An exclusion of 政府採購法 selects the enterprise track unless it names one article. Unresolved choices such as `【普／中／高】` fail as placeholders. 「另行約定」 raises the out-of-scope advisory.
- **CLI** — exit code 2 with an instruction when input cannot be read, including stdin that Windows PowerShell 5.1 turned into question marks. Tracebacks are gone.

### Packaging
- Frontmatter moves `version` into `metadata`, which the current SkillOps format gate requires, and adds `license`.
- README states the install layout. Installing the whole repository left no root `SKILL.md`, so the host could not discover the skill.

### Upgrade notes
- A government draft that passed `rfp_lint-8` can now fail when it lacks 評定方式 or 合格分數. This is intended.
- JSON output keeps its existing keys and adds `pending_confirmations`, `source_format`, and `line` on rule findings. Exit code 2 is new.

## [2026.8.28] — Published

Modernizes the skill for the current SkillOps contract and upgrades the deterministic scorer from `rfp_lint-7` to `rfp_lint-8`.

### Fixed
- **Evaluation-table parsing** — parses the declared item and weight columns instead of every percentage in a row, preventing formulas such as `最低標價／投標標價 × 100%` from becoming false price weights.
- **Heading coverage** — applies rules under generic or nested Chinese／English evaluation headings instead of silently skipping the table.
- **100-point tables** — treats numeric `配分`／`權重` cells as shares when the matrix uses points without `%`.
- **Track context** — an explicit enterprise statement such as「不適用政府採購法」now controls `--track auto`; a known budget no longer implies fixed-price treatment without explicit fixed-price／fixed-fee wording.

### Changed
- **SkillOps governance** — frontmatter metadata now uses compact JSON with discovery fields; lifecycle archetype is `general`; all runtime and governance assets have point-of-use references (`orphan 35 → 0`).
- **Frozen benchmark** — adds an 8-case development／held-out accuracy benchmark and a reusable stdlib-only runner. On identical cases, baseline `rfp_lint-7` scored 0/8 and candidate `rfp_lint-8` scored 8/8.
- **Regression suite** — 17 → 21 deterministic selftests; regression gates now include the eight newly proven defects and guards.
- **Lifecycle** — version moves to published `2026.8.28`; `2026.6.25` remains the prior rollback release.

### Validation
- SkillOps evaluate／revise／optimize／package／publish + security gates — PASS
- `rfp_lint_selftest.py` — 21 cases PASS
- frozen linter benchmark — development 4/4 and first held-out run 4/4 PASS
- starter output — 20/20, 0 rule violations; raw skeleton — EXPECTED FAIL
- legal-rule official check — all three sources were re-fetched on 2026-08-28; current text still supports §10 20% and §16/§17 20%–50%, the information-service §5／計費 rules, and the committee composition rules

## [2026.6.25] — Published

A SkillOpt-style optimization pass on the deterministic scorer: reproduce the 2026.6.16 baseline → adversarial rollout against `rfp_lint.py` → two bounded fixes → held-out validation + final-test gate. Linter `rfp_lint-6 → rfp_lint-7`. No `SKILL.md` / routing / reference / task-eval change — only the eval-table compliance rules now parse weights correctly.

### Fixed
- **Price-band false negative** — a verbose price-row label (e.g.「價格合理性與成本效益綜合評估」) exceeded the fixed-width `_label_pct` window, so a government non-fixed-price案 with 價格 60% silently passed the《最有利標評選辦法》§16/§17 50% cap. Added row-aware detection (`_row_label_pct`, keyed on the row's first/label cell) so prefixed / numbered / verbose price labels are caught; the same path also closed the identical hole for the §10 簡報/詢答 20% cap.
- **Weight-sum false positive** — a passing-threshold / subtotal row (「評選及格門檻 70%」「總分 100%」) was summed as a weight, inflating the total and wrongly failing a valid 100% table. Added `_NON_WEIGHT_ROW` exclusion (門檻 / 及格 / 合格 / 底標 / 底價 / 總分 / 滿分 / 合計 / 小計 / 總計). A real bad sum that co-exists with a threshold row is still caught.

### Changed
- **`rfp_lint.py` → `rfp_lint-7`**: price / simulation weight rules union prose + row-aware detection (price uses max for the >50 cap, min for the <20 floor); weight-sum skips threshold/subtotal rows. JSON output schema unchanged (only the `grader_version` value moves).
- **`rfp_lint_selftest.py`**: 15 → 17 deterministic cases (`verbose price label over 50 → blocker`, `threshold row not counted in weight sum → pass`).
- **`audit_release_evidence.py`**: now audits the latest release set by version (globs `evidence-*.json`, follows its `benchmark_summary_path`) instead of hardcoding the 2026-06-16 filenames; older dated artifacts retained as history.
- **`regression_gates.json`**: added `verbose-price-label-over-50-fails` and `threshold-row-not-counted-in-weight-sum`.

### Release gate (all green)
- `rfp_lint_selftest.py` — 17 deterministic cases PASS
- starter `examples/starter/output.md` — lint PASS (20/20, 0 rule violations, `rfp_lint-7`)
- `assets/templates/rfp-skeleton.md` — lint EXPECTED-FAIL (placeholder guard)
- `scripts/audit_release_evidence.py` — release-evidence traceability PASS (latest = 2026.6.25)
- held-out final-test set (6 cases) — 6/6 expected, no new false positive/negative
- all eval / config JSON valid

### Note
- Legal sources unchanged this release; they remain as live-verified against 全國法規資料庫 on 2026-06-16 (see readiness report and `source-register.md`). `next_review_due: 2026-09-23`.

## [2026.6.16] — Published

First formally **published** release (prior `2026.6.16` working tree was draft / local smoke-ready). This release is gated by a deterministic functional gate rather than a paired LLM benchmark — see "Release gate" below.

### Added
- **`advise` mode** — a third, lightweight Q&A contract (5-part: conclusion → plain-language → government/enterprise difference → paste-ready clause/weights → legal-version reminder) so single-point questions ("what's the price-weight cap?") no longer force a full RFP or full review.
- **`clause-library.md` O–R** — 2026 information-procurement clauses absent from traditional RFP templates:
  - **O. AI 系統條款** — model version & change notice, eval metrics & test sets, hallucination/error-rate measurement, human-in-the-loop, training-data use, prompt/log retention, fairness/explainability, structured PoC.
  - **P. 資料治理** — data dictionary, lineage, data-quality SLA, access matrix, de-identification.
  - **Q. 雲端韌性** — RTO/RPO, BCP/DR drills, key management (KMS/BYOK/HYOK), backup immutability.
  - **R. 開源與供應鏈** — SBOM, license compliance, dependency-vulnerability SLA, container/image scanning.
- **`references/info-service-article5-map.md`** — maps 《機關委託資訊服務廠商評選及計費辦法》§5 應載事項 (13 款) → RFP chapter → linter check → review severity, giving government information-service reviews legal traceability ("§5 第 N 款 缺漏（嚴重度）").
- **`references/maintainer-guide.md`** — testing plan, eval workflow, release policy, troubleshooting, host/portability and the full resource catalogue, moved out of the runtime `SKILL.md`.
- **`CHANGELOG.md`** (this file).
- Six **adversarial evals** (ids 17–22): gov-committee-missing, gov-sensitive-exit-missing, security out-of-scope negation, IP-keyword-without-attribution, functional-without-acceptance, AI-system-RFP-needs-PoC.

### Changed
- **`SKILL.md` slimmed** (~322 → ~225 lines): testing/eval/distribution/troubleshooting/host/resources moved to `maintainer-guide.md`; runtime now carries only trigger, role, modes, workflow, output contract, tool rules, and a compact knowledge-base pointer.
- **`rfp_lint.py` → `rfp_lint-6`**:
  - Evidence-based findings: every present check now returns the matched keyword, line number and nearest heading.
  - Out-of-scope negation: a keyword appearing only inside a「不處理／不適用」context is surfaced as an **advisory warning** (never a hard fail); prescriptive 不得／禁止 prohibitions are explicitly guarded so legitimate ban clauses are not flagged.
  - Conditional / track-specific severity: missing 評選委員會 (government 最有利標/資服 → Blocker), 退場返還 (sensitive 個資/雲端/關鍵系統 → Blocker), 禁用清單 (government → Major) and 資料落地 (government + sensitive → Blocker) escalate beyond their base severity; enterprise track is unaffected.
- **Minimal-start strategy** in `SKILL.md`: unknown budget / procurement-track / security-level no longer hard-stop the workflow — the skill proceeds with explicitly-listed assumptions instead of acting like a form.
- **`review-rubric.md`** wired to the §5 map and the O–R clauses, and to the linter's new conditional severities and negation advisory.
- **`regression_gates.json`** retired `max_time_increase_seconds` / `max_token_increase` (they assumed a paired LLM latency benchmark that was never instrumented for this artifact type) in favour of a `deterministic_functional_pass_rate` gate and the new rule regressions.
- **`skill_lifecycle.yaml`**: `status: draft → published`; `last_released_at: 2026-06-16`; `data_sensitivity` split into honest `skill_static_data_sensitivity: low` vs `user_input_data_sensitivity: medium_to_high_possible`.

### Verified
- **Legal sources re-checked live against 全國法規資料庫 on 2026-06-16**: 最有利標評選辦法 (民國 114/01/21), 機關委託資訊服務廠商評選及計費辦法 (民國 114/05/23), 採購評選委員會組織準則 (民國 115/05/08). Page text confirmed the 20%–50% price band, ≤20% simulation cap, §5 應載事項, and committee composition rules the skill encodes.

### Release gate
This is a knowledge + linter skill: its release evidence is a **deterministic functional gate**, not a paired LLM latency/cost benchmark. The previous "full paired benchmark before publication" requirement is retired as not applicable to this artifact type. Gate (all green):
- `rfp_lint_selftest.py` — 15 deterministic cases PASS
- starter `examples/starter/output.md` — lint PASS (20/20, 0 rule violations)
- `assets/templates/rfp-skeleton.md` — lint EXPECTED-FAIL (placeholder guard)
- `scripts/audit_release_evidence.py` — release-evidence traceability PASS
- all eval / config JSON valid

## [Unreleased history]
- `2026.6.16` (draft) — government/enterprise track separation, `rfp_lint-5` price/weight rules, source register, release-evidence audit, expanded evals (local smoke-ready, not published).
- `2026.6.15` — initial dual-mode (write/review) RFP skill: 11-section anatomy, Taiwan procurement references, clause library, deterministic linter.
