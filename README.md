# rfp-architect

委外開發建議書徵求說明書（RFP / Request for Proposal）**撰寫**與**審查**的 OpenClaw / Claude Code skill。

A dual-mode skill to **write** and **review** RFPs (建議書徵求說明書 / 需求說明書 / 招標需求規格) for outsourced software & information-system development — anchored in the Taiwan government-procurement context (最有利標、採購評選委員會、序位法、資安分級、資料落地、繁中在地化、價格配分與計費合規), and compatible with general enterprise outsourcing.

> 版本 / Version：`2026.6.16`　·　授權 / License：MIT

## 兩種模式 / Two modes

- **write** — 依 11 必備章節產出結構完整、可評選、可驗收的 RFP 草稿（功能／非功能需求、評選配分矩陣、價格 20–50% 法定區間、計費方式、台灣在地條款），交付前以內建 linter 自審。
- **review** — 以 checklist／rubric 逐項審查既有 RFP，依嚴重度（Blocker／Major／Minor）回報缺漏與可貼用的修正建議。

撰寫前先判定**採購軌道**：政府機關／公法人／受《政府採購法》拘束者走「政府採購軌」（強制檢查最有利標、評選委員會、等標期、價格 20–50% 權重、資訊服務計費辦法）；一般企業走「企業委外軌」（聚焦商業條款、SLA、智財、資安、個資、付款與退場）。

## 安裝 / Install

把 `skill/rfp-architect/` 這個資料夾放到 skills 目錄（例如 `~/.claude/skills/rfp-architect`）即可被載入。此子資料夾才是 packaged skill runtime。

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
| `skill/rfp-architect/SKILL.md` | 主流程（write／review pipeline、採購軌道判定、決策邊界、輸出契約） |
| `skill/rfp-architect/references/rfp-anatomy.md` | 文件家族（RFP/RFI/RFQ/SOW）＋11 必備章節＋需求工程 |
| `skill/rfp-architect/references/taiwan-procurement.md` | 招標／決標／最有利標／評選委員會／三種評定方式／序位法／等標期／價格 20–50% 區間／資訊服務委外計費辦法（§8） |
| `skill/rfp-architect/references/clause-library.md` | 台灣在地與契約條款庫（資安／個資／禁用／資料落地／在地化／智財含分包鏈條／保固／變更管理／退場返還／計費方式／治理盡職調查） |
| `skill/rfp-architect/references/review-rubric.md` | 審查心法、審查清單、嚴重度、八大常見錯誤、failure 根因 |
| `skill/rfp-architect/references/case-patterns.md` | 委外失敗模式 → RFP 控制點對照（公開個案示例，強化 review finding 的「為什麼重要」） |
| `skill/rfp-architect/assets/templates/rfp-skeleton.md` | write 模式的填空骨架（含法規版本標頭與 RTM／交付／付款管理矩陣） |
| `skill/rfp-architect/examples/starter/` | 範例輸入 `input.md` ＋ 通過 lint 的完整範例輸出 `output.md` |
| `skill/rfp-architect/scripts/rfp_lint.py` | RFP 章節／在地條款／配分規則完整度檢查（20 項；含占位符殘留、政府案簡報配分 >20%、政府非固定價格案價格不在 20–50%、配分合計非 100%；write 自審、review 初篩） |
| `skill/rfp-architect/scripts/rfp_lint_selftest.py` | linter 高風險規則回歸測試 |
| `skill/rfp-architect/scripts/audit_release_evidence.py` | release evidence traceability 檢查 |
| `skill/rfp-architect/references/source-register.md` | 法規、案例與數值規則來源登錄（URL、查核日、版本與 freshness policy） |
| `skill/rfp-architect/assets/evals/` | 觸發與功能 eval（含 direct／indirect／negative／near-miss，zh／en／mixed；trigger eval 與 task eval 分檔） |
| `skill/rfp-architect/release/` | release evidence（draft + publish gate 通過紀錄與 benchmark） |

## 不適用 / Not for

純硬體或標準品比價（用 RFQ）、得標後 SOW／契約逐條談判、營建工程細部規範、一般文章或簡報撰寫。

## License

MIT © 2026 Openclaw-Metis
