# Maintainer guide（非 runtime；維護、測試、發版用）

本檔收錄**維護者導向**內容：測試計畫、eval workflow、發版政策、troubleshooting、完整資源目錄、host / portability 細節。把它從 `SKILL.md` 抽出，是為了讓 runtime 載入的 `SKILL.md` 只保留操作契約（trigger / role / 模式 / workflow / output contract / tool rules），降低維護資訊干擾交付物的機率。使用本 skill 寫 / 審 RFP **不需**讀本檔；只有要修改、測試或發版 skill 時才需要。

## Host / portability targets

- Primary host(s)：Claude Code、OpenClaw（agent-skills 相容）。
- Secondary host(s)：其他 agent-skills 相容 host。
- Unsupported host(s)：無特定不支援；但 `rfp_lint.py` 需 Python 3 環境（無 Python 3 時改以 `review-rubric.md` 人工檢核，見 SKILL.md `<tool_rules>`）。
- Core portable surface：skill + scripts（`SKILL.md` + `references/` + `assets/templates/` + `scripts/rfp_lint.py` 為單一真實來源）。
- Host adapters / wrappers needed：無；純 skill folder。
- State / persistence path：本 skill 無持久狀態；產出的 RFP 草稿寫到使用者指定路徑或工作區，不寫回 skill folder。

## Success criteria（量化發版門檻）

Quantitative:
- Trigger accuracy：相關 write / review 請求命中率 ≥ 90%，且不誤搶 RFQ / 契約 / 通用寫作。
- write 草稿：`rfp_lint.py` 0 個 Blocker 缺漏、0 個 rule violation。
- review：每個 Blocker / Major finding 都有定位、理由與可貼用修正。

Qualitative:
- 最少使用者來回即可開工（見 SKILL.md 最小可開工策略）。
- 輸出結構可重複（write 依 11 章節；review 依嚴重度；advise 依五段式）。
- 新使用者第一次就能用。

## Testing plan

### Triggering tests
- Golden trigger set:
  - Direct:
    - 「幫我寫一份委外開發的 RFP」
    - 「審查這份建議書徵求說明書」
  - Indirect:
    - 「我要發包一個系統，需求說明書怎麼起草」
    - 「這份招標需求規格幫我挑問題」
  - Negative:
    - 「幫我寫一篇部落格文章介紹 RFP」（通用寫作 → 不觸發）
    - 「幫我比價三家筆電報價」（RFQ → 不觸發）
- Should trigger：委外 / 資訊系統 RFP 的撰寫或審查、RFP 結構 / 評選 / 條款諮詢。
- Should NOT trigger：RFQ 比價、SOW / 契約談判、營建規範、一般文章 / 簡報。
- Near-miss / confusing cases：「幫我寫投標建議書」（乙方 proposal，非甲方徵求文件）→ 釐清後再決定是否適用。
- Should ask before acting：write 缺標的、review 無待審文件、需寫入檔案時（預算 / 採購軌 / 資安等級不明時改列假設往下走，不硬停——見 SKILL.md）。

### Functional tests
- Test case: write 政府採購 RFP
  - Given：標的＋政府採購＋預算範圍
  - When：執行 write 流程
  - Then：產出 11 章節草稿，rfp_lint 0 Blocker，含評選配分與資安分級
- Test case: review 缺評選配分的 RFP
  - Given：一份未載明評選配分的 RFP
  - When：執行 review 流程
  - Then：回報 [Blocker] 評選配分未載明，並給可貼用修正
- Test case: advise 單點諮詢
  - Given：「政府案價格權重上限是多少」
  - When：執行 advise 流程
  - Then：五段式回答（結論→白話→政府/企業差異→可貼用條款或配分→法規版本提醒），不被迫產出完整 RFP

### Performance comparison (optional)
- Baseline (no skill)：模型自由發揮，常漏台灣在地條款（資安分級 / 禁陸製 / 資料落地）與評選合法性。
- With skill：固定 11 章節 + 在地條款庫 + 評選合法性檢查 + lint 把關。

### ROI guardrail
- Quality gain must justify extra:
  - Time：多一次 lint 與 rubric 自審，數十秒內完成。
  - Tokens：references 為 on-demand 載入，未膨脹常駐 context（SKILL.md 已瘦身，維護內容移至本檔）。
  - Maintenance burden：法規更新時只需維護 `taiwan-procurement.md`、`clause-library.md`、`source-register.md`。

### Regression gates
- Minimum pass-rate delta：with-skill 功能測試通過率不得低於 baseline。
- Maximum allowed time increase：每次任務額外 lint 時間 < 5 秒。
- Maximum allowed token increase：常駐 metadata 不超過 description 上限。
- Maximum under-trigger failures：direct trigger 漏觸發 0。
- Maximum over-trigger failures：negative（RFQ / 通用寫作）誤觸發 0。
- Government compliance regression：非固定價格政府案價格 <20% 或 >50% 必須 fail；固定價格給付案價格 <20% 可通過但須提示文件明載固定價格；政府案簡報 / 詢答 >20% 必須 fail；配分合計非 100% 必須 fail；政府案缺評選委員會 / 退場（涉個資 / 雲端）必須升級為 Blocker。

### Feedback loop
- Common failure signals：產出漏掉台灣在地條款、或 review 只給泛泛建議。
- Likely fix：補強 `clause-library.md` / `review-rubric.md`，或在 workflow 加明確 gate。

### Model / routing checks
- GPT-style prompt pass：逐章節 / 逐 rubric 明確執行。
- Reasoning-model pass：給目標與約束即可穩定產出。
- Neighbor-skill confusion：與 deep-research（研究報告）、cc-designer（排版）界線清楚。

### Host compatibility checks
- Primary host smoke tests：Claude Code / OpenClaw 載入後可執行 write 與 review。
- Wrapper / manifest / config drift review：無 host wrapper，免漂移。
- Auth / approval / persistence checks：無祕鑰；寫檔案需 approval；無持久狀態。
- Known unsupported hosts：無 Python 3 時 `rfp_lint.py` 不可用，需改人工以 rubric 檢核。

## Eval workflow

- Save approved task prompts to `assets/evals/evals.json`
- Save pure routing / description prompts to `assets/evals/trigger_evals.json`
- Define release thresholds in `assets/evals/regression_gates.json`
- 觸發與功能 eval 以 direct / indirect / negative / near-miss、zh / en / mixed 覆蓋
- 比較 baseline（無 skill）以確認在地條款與評選合法性的增益

## Distribution notes

- Packaging：以 skill-creator-advanced 工具鏈的打包腳本封裝為 .skill（封裝工具不在本 skill folder 內）
- 核心 skill folder 為單一真實來源；不要為單一 host fork 內容
- 支援 host、權限、approval 邊界記錄在 skill folder 外
- repo-level `README.md` 放本 skill folder 之外；packaged runtime 不含 README

## Troubleshooting

- Symptom：write 草稿漏掉台灣在地條款。
  - Cause：未載入或未套用 `clause-library.md`。
  - Fix：Step W2 強制依標的逐項對照條款庫（含 AI / 資料治理 / 雲端 / 供應鏈 O–R 節）。
- Symptom：review 只給泛泛建議、無定位。
  - Cause：未套用 `review-rubric.md` 的 finding 格式。
  - Fix：每項 finding 套 `[嚴重度] 位置 — 問題 / 理由 / 修正`，並引用 `rfp_lint.py` 回傳的行號 / 證據片段。
- Symptom：linter 命中關鍵字但內容其實是「不處理 / 不適用」。
  - Cause：keyword presence 不等於品質；v6 已加 out-of-scope 否定語**警示**（advisory），但不硬性 fail。
  - Fix：review 時依 `weak_hit` 警示人工複核該章節是否真的具備。

## Resources（完整資源目錄）

- `scripts/rfp_lint.py`：RFP 章節 / 在地條款完整度初篩（write 與 review 共用；v6 含證據定位、否定語警示、政府軌條件式嚴重度）。
- `scripts/rfp_lint_selftest.py`：linter 高風險規則回歸測試。
- `scripts/audit_release_evidence.py`：release evidence traceability 檢查。
- `references/rfp-anatomy.md`：文件家族與 11 必備章節、需求工程、撰寫流程。
- `references/taiwan-procurement.md`：招標 / 決標 / 異質採購 / 最有利標 / 評選委員會 / 三種評定方式 / 序位法 / 等標期 / 價格 20–50% 區間 / 資訊服務委外專法（§8）。
- `references/clause-library.md`：台灣在地與契約條款庫（A–N 在地 / 契約條款；O–R AI / 資料治理 / 雲端韌性 / 供應鏈）。
- `references/info-service-article5-map.md`：《機關委託資訊服務廠商評選及計費辦法》§5 應載事項 → RFP 章節 → linter check → review 嚴重度對照。
- `references/review-rubric.md`：審查心法、審查清單、嚴重度、八大常見錯誤、失敗根因、finding 格式。
- `references/case-patterns.md`：委外失敗模式 → RFP 控制點對照（公開案例，非報告內容）。
- `references/source-register.md`：法規、案例與數值規則來源登錄（URL、查核日、版本與 freshness policy）。
- `assets/templates/rfp-skeleton.md`：write 模式的填空骨架（含法規版本標頭與 RTM / 交付 / 付款管理矩陣）。
- `references/readiness_report.md`：發版證據（必備）。
- `references/checklist_template.md`：人工 review notes 模板（非 release gate）。
- `references/migration-governance.md`：rename / deprecate / merge / split 相容性規則。
- `skill_lifecycle.yaml`：生命週期、擁有者、審查週期、支援矩陣、風險、依賴。
- `schemas/`：機器可讀契約。
- `policies/`：release / portability / retirement 政策。
- `examples/`：example-as-test fixtures。
- `assets/`：模板與 eval fixtures。
