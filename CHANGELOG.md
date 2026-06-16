# Changelog

All notable changes to **rfp-architect** are recorded here. Versions use CalVer (`YYYY.M.D`).

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
