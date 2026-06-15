# rfp-architect

委外開發建議書徵求說明書（RFP / Request for Proposal）**撰寫**與**審查**的 OpenClaw / Claude Code skill。

A dual-mode skill to **write** and **review** RFPs (建議書徵求說明書 / 需求說明書 / 招標需求規格) for outsourced software & information-system development — anchored in the Taiwan government-procurement context (最有利標、採購評選委員會、序位法、資安分級、資料落地、繁中在地化), and compatible with general enterprise outsourcing.

## 兩種模式 / Two modes

- **write** — 依 11 必備章節產出結構完整、可評選、可驗收的 RFP 草稿（功能／非功能需求、評選配分矩陣、台灣在地條款）。
- **review** — 以 checklist／rubric 逐項審查既有 RFP，依嚴重度（Blocker／Major／Minor）回報缺漏與可貼用的修正建議。

## 安裝 / Install

把整個資料夾放到 skills 目錄（例如 `~/.claude/skills/rfp-architect`）即可被載入。

## 用法 / Usage

用自然語言觸發：

- 「幫我寫一份○○系統的委外開發 RFP」
- 「幫我審查這份 RFP／需求說明書」
- 「委外 RFP 評選怎麼設計／序位法怎麼算」

## 內容 / Contents

| 路徑 | 用途 |
|---|---|
| `SKILL.md` | 主流程（write／review pipeline、決策邊界、輸出契約） |
| `references/rfp-anatomy.md` | 文件家族（RFP/RFI/RFQ/SOW）＋11 必備章節＋需求工程 |
| `references/taiwan-procurement.md` | 招標／決標／最有利標／評選委員會／序位法／等標期 |
| `references/clause-library.md` | 台灣在地條款庫（資安／個資／禁用／資料落地／在地化／智財／保固） |
| `references/review-rubric.md` | 審查清單、嚴重度、八大常見錯誤、failure 根因 |
| `assets/templates/rfp-skeleton.md` | write 模式的填空骨架 |
| `scripts/rfp_lint.py` | RFP 章節／在地條款完整度檢查（write 自審、review 初篩） |
| `assets/evals/` | 觸發與功能 eval（11 題；direct／indirect／negative／near-miss，zh／en／mixed） |
| `release/` | release evidence（draft + publish gate 通過紀錄與 benchmark） |

## 不適用 / Not for

純硬體或標準品比價（用 RFQ）、得標後 SOW／契約逐條談判、營建工程細部規範、一般文章或簡報撰寫。

## License

MIT © 2026 Openclaw-Metis
