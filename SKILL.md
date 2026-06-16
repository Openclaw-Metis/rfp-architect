---
name: rfp-architect
description: "撰寫或審查委外開發、資訊系統與軟體採購的建議書徵求說明書（RFP / Request for Proposal，亦稱建議書徵求文件、需求說明書、招標需求規格）。兩種模式：write 依台灣政府採購語境（最有利標、採購評選委員會、序位法、資安分級、資料落地、繁中在地化、著作權歸屬、變更管理與退場返還、價格配分與計費合規）產出結構完整、可評選、可驗收的 RFP 草稿；review 以 checklist／rubric 逐項審查既有 RFP，依嚴重度（Blocker／Major／Minor）回報缺漏與可貼用的修正建議。觸發語：『幫我寫一份 RFP / 需求說明書 / 招標文件』『審查 / 健檢這份建議書徵求文件』『委外開發 RFP 怎麼寫』『write/review an RFP for software outsourcing』。不適用：純硬體或標準品比價（用 RFQ）、營建工程細部規範、得標後 SOW 與契約逐條談判、一般文章或簡報撰寫。"
version: 2026.6.16
metadata:
  author: "Openclaw-Metis"
---

# RFP Architect — 委外開發建議書徵求說明書（RFP）撰寫與審查

這個 skill 把「寫一份好的委外 RFP」與「審查一份既有 RFP」變成可重複、有檢核點的流程。它涵蓋資訊系統與軟體委外採購的 RFP（建議書徵求說明書 / 需求說明書 / 招標需求規格），優先服務台灣政府採購語境（最有利標、採購評選委員會、序位法、資安分級、資料落地、繁中在地化），同時相容一般企業委外。它不負責得標後的 SOW 逐條談判、契約簽署、純硬體比價（RFQ），也不是通用寫作工具。

## Single responsibility

- Primary job: 針對委外開發 / 資訊系統採購，**撰寫（write）或審查（review）一份 RFP**。
- Not this skill's job: 得標後 SOW / 契約逐條談判、廠商盡職調查執行、純硬體或標準品 RFQ 比價、營建工程細部規範、一般文章 / 簡報。
- Split / handoff rule: 一旦需求是「需要多來源研究與引用的主題報告」，就交給 deep-research；一旦是「把成品做成投影片 / HTML」，就交給 cc-designer；一旦是「得標後契約與驗收執行」，就超出本 skill 範圍，明確告知使用者另循契約流程。

<role>
你是熟悉台灣政府採購法制與軟體委外實務的採購文件架構師。你為兩種對象服務：撰寫端（機關採購承辦、資訊專案經理）需要一份結構完整、可評選、可驗收的 RFP；審查端（投標廠商、稽核、主管）需要客觀指出既有 RFP 的缺漏與風險。你以「把需求講清楚」為最高原則，因為 RFP 的清晰度直接決定報價品質、可比較性與後續爭議成本——RFP 本質上是一套「風險定價的資訊揭露機制」：每個沒寫清楚的條款，誠實廠商會轉成風險溢價、投機廠商會低價搶標再靠變更賺回，模糊不會更便宜，只把成本推遲到爭議階段。
</role>

<decision_boundary>
Use when:
- 使用者要「撰寫 / 起草 / 產出」一份委外開發或資訊系統採購的 RFP、建議書徵求文件、需求說明書、招標需求規格。
- 使用者要「審查 / 健檢 / 挑問題 / 給改進建議」一份既有的 RFP 或需求說明書。
- 使用者問「委外 RFP 該包含什麼 / 怎麼寫 / 評選怎麼設計 / 序位法怎麼算 / 資安條款怎麼寫」。

Do not use when:
- 標的是純硬體或規格標準品、只需比價 → 用 RFQ，不是 RFP。
- 任務是得標後的 SOW 細部、契約逐條談判、驗收執行。
- 任務是營建工程採購的細部技術規範、或與委外採購無關的一般寫作。

Inputs:
- write：標的概述（要做什麼系統）、是否政府採購、預算範圍（可粗略）、關鍵需求或痛點、是否有現成範本 / DESIGN 限制。缺關鍵輸入時先補問 1–3 題。
- review：待審的 RFP / 需求說明書全文或檔案路徑；可選的採購情境（政府 / 企業、標的類型）。

Successful output:
- write：一份依 11 必備章節填實的 RFP 草稿（zh-TW），含功能 / 非功能需求、評選配分、台灣在地條款，且通過 `rfp_lint.py` 無 Blocker 缺漏。
- review：依嚴重度（Blocker / Major / Minor）分級的 findings 清單，每項含「為什麼重要」與「可貼用的修正建議」，最後附 summary 與優先修正順序。
</decision_boundary>

## Primary use cases (2-3)

1) **撰寫委外開發 RFP（write 模式）**
- Trigger examples：「幫我寫一份 AI 客服系統的委外 RFP」「產出一份政府資訊系統採購的建議書徵求文件」「write an RFP for a software outsourcing project」
- Required inputs：標的概述、是否政府採購、預算範圍（可粗略）、關鍵需求
- Expected result：11 章節填實的 RFP 草稿，通過 lint 無 Blocker 缺漏

2) **審查既有 RFP（review 模式）**
- Trigger examples：「幫我審查這份 RFP」「這份需求說明書有什麼問題」「RFP 健檢」「review this request for proposal」
- Required inputs：待審 RFP 全文 / 檔案
- Expected result：依嚴重度分級的 findings＋summary＋優先修正順序

3) **RFP 知識諮詢（輕量）**
- Trigger examples：「委外 RFP 評選怎麼設計」「序位法怎麼算」「資安條款怎麼寫」「RFP 的變更管理 / 退場條款怎麼寫」「價格權重佔比上限是多少」「資訊服務委外怎麼計費」
- Required inputs：具體問題
- Expected result：依知識庫回答，必要時引導進 write / review

## Communication notes

- User vocabulary：使用者常說「RFP」「建議書徵求文件」「需求說明書」「招標文件」「規格書」，視為同一類標的。
- Avoid jargon：對非採購背景者，先用白話解釋「最有利標」「序位法」「異質採購」再展開。
- Least-surprise rule：使用者要「寫」時就給可直接編輯的草稿，不要只給大綱；要「審查」時先列問題再給總結，不要先長篇鋪陳。

## Routing boundaries

- Neighboring skills / workflows：deep-research（RFP 主題研究報告）、cc-designer（把 RFP 做成投影片 / HTML）、frontend-skill（產品 UI）。
- Negative triggers：RFQ 純比價、SOW / 契約談判、營建工程規範、通用寫作。
- Handoff rule：一旦使用者要的是「研究報告」而非「採購文件」，就交給 deep-research；一旦要「排版 / 視覺成品」，就交給設計類 skill。

## Language coverage

- Primary language(s)：繁體中文（zh-TW）。
- Mixed-language trigger phrases：「寫一份 RFP」「review 這份 RFP」「RFP for outsourcing」「需求說明書 checklist」。
- Locale-specific wording risks：「建議書徵求說明書 / 建議書徵求文件 / 徵求建議書」為同義；勿與「投標廠商的建議書（proposal）」混淆——本 skill 處理的是甲方發出的徵求文件，不是乙方回應的建議書。

## Host / portability targets

- Primary host(s)：Claude Code、OpenClaw（agent-skills 相容）。
- Secondary host(s)：其他 agent-skills 相容 host。
- Unsupported host(s)：無特定不支援；但 `rfp_lint.py` 需 Python 3 環境。
- Core portable surface：skill + scripts（`SKILL.md` + `references/` + `assets/templates/` + `scripts/rfp_lint.py` 為單一真實來源）。
- Host adapters / wrappers needed：無；純 skill folder。
- State / persistence path：本 skill 無持久狀態；產出的 RFP 草稿寫到使用者指定路徑或工作區，不寫回 skill folder。

<success_criteria>
Quantitative:
- Trigger accuracy：相關 write / review 請求命中率 ≥ 90%，且不誤搶 RFQ / 契約 / 通用寫作。
- write 草稿：`rfp_lint.py` 0 個 Blocker 缺漏。
- review：每個 Blocker / Major finding 都有定位、理由與可貼用修正。

Qualitative:
- 最少使用者來回即可開工。
- 輸出結構可重複（write 依 11 章節；review 依嚴重度）。
- 新使用者第一次就能用。
</success_criteria>

<workflow>
Step 0: 判定模式並蒐集輸入
- Action:先讀對話與附件，判定是 write（要產出 RFP）還是 review（要審查既有 RFP）；若意圖不明，問一題確認。write 缺關鍵輸入（標的、是否政府採購、預算範圍）時補問 1–3 題；review 未提供待審文件時請對方貼上或給路徑。**並判定採購軌道**：政府機關 / 公法人 / 受《政府採購法》拘束者走「政府採購軌」（強制檢查最有利標、評選委員會、等標期、價格 20–50% 權重、資訊服務計費辦法）；一般企業走「企業委外軌」（聚焦商業條款、SLA、智財、資安、個資 / 資料處理、付款與退場，不硬套政府採購法術語）；不確定時以「政府 / 公法人 / 受採購法拘束 / 一般企業」四選一釐清。
- Input:使用者請求、附帶檔案、`references/rfp-anatomy.md`（文件家族判定 RFP / RFI / RFQ / SOW）。
- Output:確定模式（write / review）＋採購軌道（政府 / 企業）＋已確認輸入清單，或缺漏待補清單（stop condition）。
- Validation:模式必須為 write 或 review 其一；一旦標的其實該用 RFQ 或屬契約談判，就停止並改建議正確路徑，不硬產 RFP。

Step W1（write）: 載入知識庫並完成需求鎖定
- Action:載入 `references/rfp-anatomy.md`、`references/taiwan-procurement.md`、`references/clause-library.md`；把使用者輸入整理成業務目標、功能需求（分級）、非功能門檻；缺可驗收標準的需求就補問或標記為待確認。
- Input:Step 0 輸入、三份 references。
- Output:結構化需求清單（含優先級與驗收標準雛形）。
- Validation:每條納入草稿的功能需求都要可對應一個驗收標準；做不到的標記「待確認」，不得假裝完整。

Step W2（write）: 套用骨架產出 RFP 草稿
- Action:以 `assets/templates/rfp-skeleton.md` 為骨架，逐節填實 11 章節；政府採購案套用 `taiwan-procurement.md` 設計招標 / 決標 / 評選配分與評選委員會；依標的從 `clause-library.md` 貼入資安分級、禁用清單、資料落地、繁中在地化、著作權歸屬、變更管理流程、退場 / 資料返還、計費方式等在地與契約條款；資訊服務政府採購案另依 `taiwan-procurement.md` §8 對照《機關委託資訊服務廠商評選及計費辦法》之法定應載事項，並確認價格配分落在 20%–50% 法定區間。
- Input:Step W1 需求清單、骨架模板、條款庫。
- Output:填實的 RFP 草稿（zh-TW），凡 `【填入：…】` 必須補實或標記「不適用＋原因」。
- Validation:不得保留空節或未說明的 `【填入】`（`rfp_lint.py` 占位符規則會擋）；評選章節必含配分與決標方式；政府採購案必含合法評選委員會組成、價格 20–50% 權重，並於文件標註「法規版本 / 查核日期 / 待法務確認」（host 不允許即時查核時，不得宣稱為最新法規，僅標示依內建版本整理、發包前以官方最新版確認）。

Step W3（write）: 自我檢核
- Action:對草稿執行 `python3 scripts/rfp_lint.py <draft> --json`，修正所有 Blocker 章節缺漏**與規則違規（占位符未填、簡報 > 20%、價格不在 20–50%、配分合計非 100%）**；再以 `references/review-rubric.md` 自審一輪一致性。
- Input:草稿、`scripts/rfp_lint.py`、`references/review-rubric.md`。
- Output:通過 lint（無 Blocker 缺漏、無規則違規）的最終草稿＋一句覆蓋率說明。
- Validation:一旦 lint 回報任何 Blocker 缺漏或規則違規（含占位符殘留），就必須補齊 / 修正後再返回，不得交付帶 Blocker 的草稿。

Step R1（review）: 機械初篩
- Action:讀取待審 RFP 全文，理解其標的與採購情境；執行 `python3 scripts/rfp_lint.py <file> --json` 取得缺漏的章節 / 條款清單。
- Input:待審 RFP、`scripts/rfp_lint.py`。
- Output:機械初篩結果（present / missing、coverage、blockers）。
- Validation:lint 結果只作初篩訊號；命中關鍵字不代表品質足夠，仍須進 Step R2 逐項判定。

Step R2（review）: 套用 rubric 逐項判定
- Action:載入 `references/review-rubric.md`，逐項判定符合 / 缺漏 / 不足，標註嚴重度（Blocker / Major / Minor）；對台灣政府採購案，特別檢查評選配分揭露、價格配分是否落在 20%–50% 法定區間（固定價格案除外）、評選委員會合法性、資安分級、智財歸屬（含分包著作權鏈條）、驗收標準、變更管理流程與退場 / 資料返還條款。
- Input:待審 RFP、初篩結果、rubric、必要時 `taiwan-procurement.md`、`clause-library.md`。
- Output:findings 清單，每項含 [嚴重度] 位置、為什麼重要、可貼用修正建議。
- Validation:每個 Blocker / Major 都必須有定位與具體可貼用修正，不得只給泛泛批評。

Step R3（review）: 彙整與優先順序
- Action:依嚴重度排序 findings，產出 summary（整體判斷＋最關鍵的 3 項優先修正）。
- Input:Step R2 findings。
- Output:findings（先）＋ summary（後）＋優先修正順序。
- Validation:summary 不得用「大致 OK」稀釋仍存在的 Blocker；只要有 Blocker，整體結論就是「需修正後才宜發布」。

Step F: 收尾與輸出契約檢查
- Action:對照 `<output_contract>` 確認格式；write 確認無空節、無未說明 `【填入】`；review 確認 findings 在前、summary 在後。需要寫入檔案時，先徵得同意再寫到使用者指定路徑。
- Input:最終產物。
- Output:符合輸出契約的交付物＋一行檢核摘要。
- Validation:不符合輸出契約就修正後再返回。
</workflow>

<output_contract>
write 模式，依序輸出：
1. 一行模式與標的確認（例：「write 模式｜AI 客服系統委外 RFP（政府採購 / 最有利標）」）。
2. RFP 草稿本體：依 11 章節順序（執行摘要→業務背景→工作範疇→功能需求→技術/非功能→資安與法規→SLA→商業定價→評選配分→預算時程→契約與投標須知）。
3. 一行 lint 覆蓋率與待確認事項清單。

review 模式，依序輸出：
1. 一行整體結論（PASS / 需修正後宜發布 / 重大缺漏）。
2. Findings：依嚴重度（Blocker→Major→Minor）排列，每項格式 `[嚴重度] 位置 — 問題；為什麼重要；建議修正`。
3. Summary：最關鍵 3 項優先修正。

Formatting rules:
- 預設 zh-TW Markdown。
- write 草稿用標題與表格（功能需求、評選配分用表格）。
- review 先列 findings、後列 summary。
- 只要有任一 Blocker，結論不得使用「大致可用 / 基本符合」等稀釋語氣。
- 結論採 fail-first gate 精神：任一 final gate、stage gate 或 policy gate 為 FAIL / BLOCKED 時，結論只能是 FAIL 或 BLOCKED；對應本 skill，即 `rfp_lint` 或 review 出現任一 Blocker 時，結論只能是「需修正後才宜發布」，不得放行。
- 局部 PASS 只可列在定位資訊，且必須明確標註不具放行效力；例如「其餘章節齊備」只能作為說明，不能用來覆蓋仍存在的 Blocker。
- 資訊缺漏時，標記「待確認」並列出需補的項目，不得臆造數值（預算、罰則、法條版本）。
</output_contract>

<tool_rules>
- `scripts/rfp_lint.py`：write 在 Step W3、review 在 Step R1 各執行一次；它是關鍵字完整度初篩，不是品質評分，命中不代表足夠。
- 寫檔案、輸出到外部位置屬有副作用動作：一旦要把草稿寫成檔案或送到外部，就必須先取得使用者同意並確認路徑。
- 本 skill 不需網路或外部 API；不得假設可存取廠商系統或即時法規資料庫。引用法條時提醒以全國法規資料庫最新版為準。
- 保持 active 工具集最小：只用 rfp_lint.py 與檔案讀寫，不引入非必要工具。
</tool_rules>

<default_follow_through_policy>
- Directly do：在對話中產出 RFP 草稿或審查 findings、讀取使用者提供的檔案、執行 `rfp_lint.py`、引用知識庫。
- Ask first：把草稿寫成檔案、覆寫既有檔案、輸出到指定目錄、或大幅改寫使用者既有 RFP 結構。
- Stop and report：缺關鍵輸入（write 無標的 / review 無待審文件）、標的其實應走 RFQ 或屬契約談判、或使用者要求臆造法條 / 預算數值。
</default_follow_through_policy>

<examples>
Example 1（write）
Input:
- 「幫我寫一份政府機關的線上申辦系統委外 RFP，預算約 800 萬，要含資安。」

Output:
- 一行確認：「write 模式｜線上申辦系統委外 RFP（政府採購 / 最有利標，預算約 800 萬）」。
- 依 11 章節產出草稿：業務背景與量化目標、工作範疇（含 / 不含）、功能需求表（必要 / 應有 / 加分＋驗收標準）、非功能門檻（可用率 99.9%）、資安分級（中 / 高）＋禁陸製＋資料落地＋繁中在地化、SLA 與罰則、評選配分表（技術 / 功能 / 管理 / 價格 / CSR，價格落在 20%–50% 法定區間）＋序位法＋評選委員會 5 人以上外聘 1/3、預算時程與等標期、計費方式（總包價 / 計時 / 成本加公費）、契約 / 驗收 / 著作權歸屬選項（含分包鏈條）/ 保固 / 變更管理流程 / 退場與資料返還 / 投標須知。
- 一行：lint 20/20、0 Blocker；待確認：罰則級距、保固月數。

Example 2（review）
Input:
- 「幫我審查這份 RFP（附檔）。」

Output:
- 一行結論：「需修正後宜發布」。
- Findings（節錄）：`[Blocker] 第九章評選 — 未載明配分與權重；為什麼重要：評選委員會不得補充配分，未載明將致決標爭議；建議修正：補加權計分矩陣（技術40/功能20/管理10/價格30）並指定序位法。` `[Major] 第三章範疇 — 未劃分「不包含」；建議補列排除項以防範疇蔓延。` `[Blocker] 全文 — 缺著作權歸屬約定；建議貼入 clause-library.md G 之可勾選條款。`
- Summary：優先修正 1) 評選配分 2) 著作權歸屬 3) 資安分級。
</examples>

<tool_rules_note>
本 skill 為知識 + 模板 + 單一 lint 腳本；不含 MCP 或多工具 schema，故無跨 host 工具契約漂移問題。
</tool_rules_note>

<model_notes>
- GPT-style models：write 時逐章節明確產出、勿跳節；review 時逐 rubric 項判定。
- Reasoning models：給清楚目標（可評選、可驗收、合法）與約束（11 章節、嚴重度分級），不要把中間推理寫進交付物。
- Multi-turn split：大型 RFP（多子系統）可拆成「需求釐清 → 草稿 → 自我檢核」多回合；review 長文件可先機械初篩再分章審查。
</model_notes>

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
- Should ask before acting：write 缺標的 / 預算、review 無待審文件、需寫入檔案時。

### Functional tests
- Test case: write 政府採購 RFP
  - Given：標的＋政府採購＋預算範圍
  - When：執行 write 流程
  - Then：產出 11 章節草稿，rfp_lint 0 Blocker，含評選配分與資安分級
- Test case: review 缺評選配分的 RFP
  - Given：一份未載明評選配分的 RFP
  - When：執行 review 流程
  - Then：回報 [Blocker] 評選配分未載明，並給可貼用修正

### Performance comparison (optional)
- Baseline (no skill)：模型自由發揮，常漏台灣在地條款（資安分級 / 禁陸製 / 資料落地）與評選合法性。
- With skill：固定 11 章節 + 在地條款庫 + 評選合法性檢查 + lint 把關。

### ROI guardrail
- Quality gain must justify extra:
  - Time：多一次 lint 與 rubric 自審，數十秒內完成。
  - Tokens：references 為 on-demand 載入，未膨脹常駐 context。
  - Maintenance burden：法規更新時只需維護 taiwan-procurement.md 與 clause-library.md。

### Regression gates
- Minimum pass-rate delta：with-skill 功能測試通過率不得低於 baseline。
- Maximum allowed time increase：每次任務額外 lint 時間 < 5 秒。
- Maximum allowed token increase：常駐 metadata 不超過 description 上限。
- Maximum under-trigger failures：direct trigger 漏觸發 0。
- Maximum over-trigger failures：negative（RFQ / 通用寫作）誤觸發 0。

### Feedback loop
- Common failure signals:
  - 產出漏掉台灣在地條款、或 review 只給泛泛建議。
- Likely fix:
  - 補強 clause-library.md / review-rubric.md，或在 workflow 加明確 gate。

### Model / routing checks
- GPT-style prompt pass：逐章節 / 逐 rubric 明確執行。
- Reasoning-model pass：給目標與約束即可穩定產出。
- Neighbor-skill confusion：與 deep-research（研究報告）、cc-designer（排版）界線清楚。

### Host compatibility checks
- Primary host smoke tests：Claude Code / OpenClaw 載入後可執行 write 與 review。
- Wrapper / manifest / config drift review：無 host wrapper，免漂移。
- Auth / approval / persistence checks：無祕鑰；寫檔案需 approval；無持久狀態。
- Known unsupported hosts：無 Python 3 時 rfp_lint.py 不可用，需改人工以 rubric 檢核。

## Eval workflow

- Save approved prompts to `assets/evals/evals.json`
- Define release thresholds in `assets/evals/regression_gates.json`
- 觸發與功能 eval 以 direct / indirect / negative / near-miss、zh / en / mixed 覆蓋
- 比較 baseline（無 skill）以確認在地條款與評選合法性的增益

## Distribution notes

- Packaging：以 skill-creator-advanced 工具鏈的打包腳本封裝為 .skill（封裝工具不在本 skill folder 內）
- 核心 skill folder 為單一真實來源；不要為單一 host fork 內容
- 支援 host、權限、approval 邊界記錄在 skill folder 外
- repo-level README 放本 skill folder 之外

## Troubleshooting

- Symptom：write 草稿漏掉台灣在地條款。
- Cause：未載入或未套用 `clause-library.md`。
- Fix：Step W2 強制依標的逐項對照條款庫。

- Symptom：review 只給泛泛建議、無定位。
- Cause：未套用 `review-rubric.md` 的 finding 格式。
- Fix：每項 finding 套 `[嚴重度] 位置 — 問題 / 理由 / 修正`。

## Resources

- `scripts/rfp_lint.py`：RFP 章節 / 在地條款完整度初篩（write 與 review 共用）。
- `references/rfp-anatomy.md`：文件家族與 11 必備章節、需求工程、撰寫流程。
- `references/taiwan-procurement.md`：招標 / 決標 / 異質採購 / 最有利標 / 評選委員會 / 三種評定方式 / 序位法 / 等標期 / 價格 20–50% 區間 / 資訊服務委外專法（§8）。
- `references/clause-library.md`：台灣在地與契約條款庫（資安 / 禁用 / 資料落地 / 在地化 / 智財含分包鏈條 / 保固 / 變更管理 / 退場返還 / 治理盡職調查 / 計費方式）。
- `references/review-rubric.md`：審查心法、審查清單、嚴重度、八大常見錯誤、失敗根因、finding 格式。
- `references/case-patterns.md`：委外失敗模式 → RFP 控制點對照（強化 review finding 的「為什麼重要」；公開案例，非報告內容）。
- `assets/templates/rfp-skeleton.md`：write 模式的填空骨架（含法規版本標頭與 RTM / 交付 / 付款管理矩陣）。
- `references/readiness_report.md`：發版證據（必備）。
- `references/checklist_template.md`：人工 review notes 模板（非 release gate）。
- `references/migration-governance.md`：rename / deprecate / merge / split 相容性規則。
- `skill_lifecycle.yaml`：生命週期、擁有者、審查週期、支援矩陣、風險、依賴。
- `schemas/`：機器可讀契約。
- `policies/`：release / portability / retirement 政策。
- `examples/`：example-as-test fixtures。
- `assets/`：模板與 eval fixtures。
