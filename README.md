# rfp-architect

委外開發建議書徵求說明書（RFP / Request for Proposal）**撰寫**與**審查**的 OpenClaw / Claude Code skill。

A skill to **write**, **review** and **advise on** RFPs (建議書徵求說明書 / 需求說明書 / 招標需求規格) for outsourced software & information-system development — anchored in the Taiwan government-procurement context (最有利標、公開評選、採購評選委員會、序位法、資安與委外、資料落地、繁中在地化、價格配分與計費合規), and compatible with general enterprise outsourcing.

> 版本 / Version：`2026.10.31`　·　狀態 / Status：**Published**　·　授權 / License：MIT
>
> 法規查核日 / Legal check：2026-10-31。詳見 `skill/rfp-architect/references/readiness_report.md`、`skill/rfp-architect/references/source-register.md` 與 `CHANGELOG.md`。本 skill 提供起草與審查輔助，不構成法律意見；發包前請以全國法規資料庫最新版及機關法務確認為準。

## 三種模式 / Three modes

- **write** — 依 11 必備章節產出結構完整、可評選、可驗收的 RFP 草稿（功能／非功能需求、評選配分矩陣、價格 20–50% 法定區間、計費方式、台灣在地條款），交付前以內建 linter 自審。
- **review** — 以 checklist／rubric 逐項審查既有 RFP，依嚴重度（Blocker／Major／Minor）回報缺漏與可貼用的修正建議。可直接讀 docx、odt 與文字檔；投標廠商立場改為輸出釋疑問題、異議期限與報價假設。
- **advise** — 回答配分、序位法、條款、計費等單點問題，不被迫產出整份文件。

撰寫前先判定**採購軌道**：政府機關、公立學校、公營事業與受《政府採購法》拘束者走「政府採購軌」（強制檢查招標與決標路徑、應載事項、評選委員會、等標期、價格 20–50% 權重、資訊服務計費辦法、委外資安）；一般企業走「企業委外軌」（聚焦商業條款、SLA、智財、資安、個資、付款與退場）。

## 安裝 / Install

把 `skill/rfp-architect/` 資料夾的**內容**放到 skills 目錄下的 `rfp-architect/`，使 `SKILL.md` 位於 `~/.claude/skills/rfp-architect/SKILL.md`。這個子資料夾才是 packaged skill runtime；把整個 repo 放進去時根目錄沒有 `SKILL.md`，host 不會發現這個 skill。

```bash
git clone https://github.com/Openclaw-Metis/rfp-architect.git
cp -r rfp-architect/skill/rfp-architect ~/.claude/skills/rfp-architect
```

`README.md` 是 repo-level 說明，不在 packaged skill runtime 內；root `LICENSE` 保留在 repo 層。

## 用法 / Usage

用自然語言觸發：

- 「幫我寫一份○○系統的委外開發 RFP」
- 「幫我審查這份 RFP／需求說明書」
- 「委外 RFP 評選怎麼設計／序位法怎麼算」
- 「價格權重佔比上限是多少／資訊服務委外怎麼計費」

## 內容 / Contents

| 路徑 | 用途 |
|---|---|
| `skill/rfp-architect/SKILL.md` | 主流程（write／review／advise、採購軌道與立場判定、決策邊界、輸出契約） |
| `skill/rfp-architect/references/rfp-anatomy.md` | 文件家族（RFP/RFI/RFQ/SOW）＋11 必備章節＋需求工程 |
| `skill/rfp-architect/references/taiwan-procurement.md` | 招標與決標路徑／最有利標／評選委員會／評定方式／序位法／金額級距與等標期／釋疑異議／價格 20–50% 區間／工程會配分範例／資訊服務辦法／應載事項清單 |
| `skill/rfp-architect/references/clause-library.md` | 台灣在地與契約條款庫（A–N：資安／個資／禁用／資料落地／在地化／智財含分包鏈條／保固／變更管理／退場返還／計費方式／治理盡職調查；**O–R：AI 系統／資料治理／雲端韌性／開源供應鏈；S：資通系統委外資安事項**） |
| `skill/rfp-architect/references/info-service-article5-map.md` | 《機關委託資訊服務廠商評選及計費辦法》§5 得載事項 → RFP 章節 → linter check → review 嚴重度與獨立法源對照 |
| `skill/rfp-architect/references/review-rubric.md` | 審查心法、審查清單、嚴重度、投標廠商立場、八大常見錯誤、failure 根因 |
| `skill/rfp-architect/references/maintainer-guide.md` | 維護者導向：測試計畫、eval workflow、發版政策、troubleshooting、host／portability（非 runtime；SKILL.md 已瘦身，維護內容移此） |
| `skill/rfp-architect/references/case-patterns.md` | 委外失敗模式 → RFP 控制點對照（公開個案示例，強化 review finding 的「為什麼重要」） |
| `skill/rfp-architect/assets/templates/rfp-skeleton.md` | write 模式的填空骨架（含法規版本標頭與 RTM／交付／付款管理矩陣） |
| `skill/rfp-architect/examples/starter/` | 範例輸入 `input.md` ＋ 通過 lint 的完整範例輸出 `output.md` |
| `skill/rfp-architect/scripts/rfp_lint.py` | RFP 章節／在地條款／配分規則完整度檢查（`rfp_lint-9`，20 章節項；掃描全文評選表，支援跨頁表格、合併儲存格、百分之六十與全形數字，並檢查政府案應載事項） |
| `skill/rfp-architect/scripts/rfp_extract.py` | 以標準函式庫讀取 docx、odt 與 UTF-8／UTF-16／Big5 文字，表格轉成 Markdown |
| `skill/rfp-architect/scripts/rfp_lint_selftest.py` | linter 高風險規則與檔案輸入回歸測試 |
| `skill/rfp-architect/scripts/run_linter_benchmark.py` | 對 frozen development／held-out cases 比較 linter baseline 與 candidate |
| `skill/rfp-architect/scripts/audit_release_evidence.py` | release evidence traceability 檢查 |
| `skill/rfp-architect/references/source-register.md` | 法規、案例與數值規則來源登錄（URL、查核日、版本與 freshness policy） |
| `skill/rfp-architect/assets/evals/` | 觸發與功能 eval（含 direct／indirect／negative／near-miss，zh／en／mixed；trigger eval 與 task eval 分檔） |
| `skill/rfp-architect/release/` | release evidence（draft + publish gate 通過紀錄與 benchmark） |

## 不適用 / Not for

純硬體或標準品比價（用 RFQ）、得標後 SOW／契約逐條談判、營建工程細部規範、一般文章或簡報撰寫。

## License

MIT © 2026 Openclaw-Metis
