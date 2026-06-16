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
- write：一份依 11 必備章節填實的 RFP 草稿（zh-TW），含功能 / 非功能需求、評選配分、台灣在地條款，且通過 `rfp_lint.py` 無 Blocker 缺漏與無規則違規。
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

3) **RFP 知識諮詢（advise 模式｜輕量）**
- Trigger examples：「委外 RFP 評選怎麼設計」「序位法怎麼算」「資安條款怎麼寫」「RFP 的變更管理 / 退場條款怎麼寫」「價格權重佔比上限是多少」「資訊服務委外怎麼計費」
- Required inputs：具體問題
- Expected result：依 `<output_contract>` advise 五段式回答（結論→白話→政府/企業差異→可貼用條款或配分→法規版本提醒），**不被迫產出完整 RFP 或完整 review findings**；必要時再引導進 write / review

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

<success_criteria>
Quantitative:
- Trigger accuracy：相關 write / review 請求命中率 ≥ 90%，且不誤搶 RFQ / 契約 / 通用寫作。
- write 草稿：`rfp_lint.py` 0 個 Blocker 缺漏、0 個 rule violation。
- review：每個 Blocker / Major finding 都有定位、理由與可貼用修正。

Qualitative:
- 最少使用者來回即可開工。
- 輸出結構可重複（write 依 11 章節；review 依嚴重度）。
- 新使用者第一次就能用。
</success_criteria>

<workflow>
Step 0: 判定模式並蒐集輸入
- Action:先讀對話與附件，判定模式：write（要產出 RFP）、review（要審查既有 RFP）、或 advise（單點知識諮詢，如「價格權重上限多少」「序位法怎麼算」）；若意圖不明，問一題確認。advise 直接依 `<output_contract>` 五段式回答，不進入完整 write / review。write 缺關鍵輸入時走**最小可開工策略**（見下），review 未提供待審文件時請對方貼上或給路徑。**並判定採購軌道**：政府機關 / 公法人 / 受《政府採購法》拘束者走「政府採購軌」（強制檢查最有利標、評選委員會、等標期、價格 20–50% 權重、資訊服務計費辦法）；一般企業走「企業委外軌」（聚焦商業條款、SLA、智財、資安、個資 / 資料處理、付款與退場，不硬套政府採購法術語）。
- 最小可開工策略（少問問題、但明列假設，像顧問而非表單機器）：
  - **標的不明**：才停止補問——沒有標的無法產 RFP。
  - **政府 / 企業軌不明**：不停止；以「待確認：採購軌道」並列政府軌 / 企業軌兩處關鍵差異往下走，請使用者擇定。
  - **預算不明**：不停止；以「未揭露預算」往下走，評選與付款條款先以區間 / 原則撰寫。
  - **資安等級不明**：不停止；先列普 / 中 / 高判斷條件與待確認事項，預設依個資 / 關鍵業務傾向中 / 高。
- Input:使用者請求、附帶檔案、`references/rfp-anatomy.md`（文件家族判定 RFP / RFI / RFQ / SOW）。
- Output:確定模式（write / review / advise）＋採購軌道（政府 / 企業 / 待確認）＋已確認輸入與**明列假設**清單。
- Validation:模式必須為 write / review / advise 其一；一旦標的其實該用 RFQ 或屬契約談判，就停止並改建議正確路徑，不硬產 RFP。所有「待確認」假設須在輸出中明列，不得當成已確認事實。

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
- Action:對草稿執行 `python3 scripts/rfp_lint.py <draft> --track government|enterprise --json`；政府採購案須修正所有 Blocker 章節缺漏**與規則違規（占位符未填、簡報 > 20%、非固定價格案價格不在 20–50%、配分合計非 100%）**，固定價格給付案價格低於 20% 時須於招標文件明載固定價格給付；企業委外案不硬套政府採購價格 / 簡報法定限制，但仍須修正占位符與配分合計錯誤；再以 `references/review-rubric.md` 自審一輪一致性。
- Input:草稿、`scripts/rfp_lint.py`、`references/review-rubric.md`。
- Output:通過 lint（無 Blocker 缺漏、無規則違規）的最終草稿＋一句覆蓋率說明。
- Validation:一旦 lint 回報任何 Blocker 缺漏或 rule_violations > 0（含占位符殘留），就必須補齊 / 修正後再返回，不得交付帶 Blocker 或 rule violation 的草稿。輸出末尾可列「待確認事項」，但草稿正文不得保留 `【填入】`、`__%`、`TODO` 或 `待補` 這類未完成占位符。

Step R1（review）: 機械初篩
- Action:讀取待審 RFP 全文，理解其標的與採購情境；依採購軌道執行 `python3 scripts/rfp_lint.py <file> --track government|enterprise --json` 取得缺漏的章節 / 條款清單與規則違規。固定價格給付政府案可加 `--fixed-price`，但文件本身仍應明載固定價格給付。
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
3. 一行 lint 覆蓋率、rule violation 數與待確認事項清單。

review 模式，依序輸出：
1. 一行整體結論（PASS / 需修正後宜發布 / 重大缺漏）。
2. Findings：依嚴重度（Blocker→Major→Minor）排列，每項格式 `[嚴重度] 位置 — 問題；為什麼重要；建議修正`。
3. Summary：最關鍵 3 項優先修正。

advise 模式（單點知識諮詢，輕量），依序輸出五段：
1. 一句結論（直接回答問題）。
2. 白話解釋（對非採購背景者展開「最有利標 / 序位法 / 資安分級」等術語）。
3. 政府採購軌 vs 企業委外軌的差異（同一問題在兩軌的不同答案；不適用則註明）。
4. 可貼用條款或評選配分（指向 `clause-library.md` / `taiwan-procurement.md` 的具體條款或配分表）。
5. 法規版本與「發包前以官方最新版確認」提醒（涉法定數值時必附）。
- advise 不產出完整 RFP、不跑 11 章節、不列完整 review findings；問題擴大為「要寫 / 要審整份」時，再引導切換 write / review。

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
- `scripts/rfp_lint.py`：write 在 Step W3、review 在 Step R1 各執行一次；政府案使用 `--track government`，企業案使用 `--track enterprise`，採購軌道未明時可用 `--track auto` 但不得用 auto 的推論取代人工判斷。它是關鍵字完整度與高風險規則初篩，不是完整品質評分，命中不代表足夠。
- `scripts/rfp_lint_selftest.py`：release / 修改 linter 後必跑，守住政府價格上下限、固定價格例外、企業軌、簡報上限、配分合計與占位符規則。
- `scripts/audit_release_evidence.py`：release evidence 修改後必跑，確認 benchmark hash、embedded summary 與 git commit traceability 一致。
- 寫檔案、輸出到外部位置屬有副作用動作：一旦要把草稿寫成檔案或送到外部，就必須先取得使用者同意並確認路徑。
- 本 skill 不需網路或外部 API；不得假設可存取廠商系統或即時法規資料庫。引用法條時提醒以全國法規資料庫最新版為準。
- 保持 active 工具集最小：只用 rfp_lint.py 與檔案讀寫，不引入非必要工具。
</tool_rules>

<default_follow_through_policy>
- Directly do：在對話中產出 RFP 草稿、審查 findings 或 advise 五段式回答、讀取使用者提供的檔案、執行 `rfp_lint.py`、引用知識庫。預算 / 採購軌 / 資安等級不明時，依最小可開工策略**明列假設往下走**，不卡住。
- Ask first：把草稿寫成檔案、覆寫既有檔案、輸出到指定目錄、或大幅改寫使用者既有 RFP 結構。
- Stop and report：僅在缺**無可替代**的關鍵輸入時停止——write 無標的、review 無待審文件、標的其實應走 RFQ 或屬契約談判、或使用者要求臆造法條 / 預算 / 罰則數值。預算 / 軌道 / 資安等級不明**不是**停止條件（改列假設）。
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

## Knowledge base（runtime 按需載入）

- `references/rfp-anatomy.md` — 文件家族（RFP/RFI/RFQ/SOW）＋11 必備章節＋需求工程。
- `references/taiwan-procurement.md` — 招標 / 決標 / 最有利標 / 評選委員會 / 序位法 / 等標期 / 價格 20–50% 區間 / 資訊服務委外專法（§8）。
- `references/clause-library.md` — 台灣在地與契約條款庫（A–N 在地 / 契約；**O–R AI 系統 / 資料治理 / 雲端韌性 / 供應鏈**）。
- `references/info-service-article5-map.md` — 《機關委託資訊服務廠商評選及計費辦法》§5 應載事項 → RFP 章節 → linter check → review 嚴重度對照（政府資訊服務案 review 用）。
- `references/review-rubric.md` — 審查心法、審查清單、嚴重度、八大常見錯誤、finding 格式。
- `references/case-patterns.md` — 委外失敗模式 → RFP 控制點對照（公開案例）。
- `references/source-register.md` — 法規 / 案例 / 數值規則來源登錄（URL、查核日、freshness policy）。
- `assets/templates/rfp-skeleton.md` — write 模式填空骨架（含法規版本標頭與 RTM / 交付 / 付款矩陣）。

> 維護者導向內容（測試計畫、eval workflow、發版政策、troubleshooting、host / portability、完整資源目錄、量化發版門檻）見 `references/maintainer-guide.md`；runtime 寫 / 審 / 諮詢 RFP 不需載入。
