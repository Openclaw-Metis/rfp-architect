# Source register

This file records source provenance for facts that drive routing, legal compliance, lint severity, and review findings. Update it whenever `taiwan-procurement.md`, `clause-library.md`, `review-rubric.md`, `scripts/rfp_lint.py`, or eval expectations change.

## Freshness policy

- Legal sources: verify against 全國法規資料庫 before each publish gate and at least every 90 days.
- If a law source revision date changes, update the relevant reference file, eval expectations, linter tests, `skill_lifecycle.yaml`, and release evidence in the same change.
- If live web access is unavailable, outputs must say they rely on the embedded source version and require official confirmation before issuance.
- Public case examples are illustrative only; do not cite case details as legal authority without separate verification.

## Legal sources

| Source | URL | Checked | Revision used | Used for |
|---|---|---:|---|---|
| 政府採購法 | https://law.moj.gov.tw/LawClass/LawAll.aspx?pcode=A0030057 | 2026-10-31 | 民國 108 年 05 月 22 日 | 招標與決標原則（§19–§22、§52）、最有利標核准與評選（§56）、規格限制（§26、§37）、保密（§34）、釋疑與異議申訴（§41、§75、§76）、押標金（§30）、契約範本（§63）、轉包分包（§65、§67）、評選委員會（§94） |
| 最有利標評選辦法 | https://law.moj.gov.tw/LawClass/LawAll.aspx?pcode=A0030080 | 2026-10-31 | 民國 114 年 01 月 21 日 | 招標文件應載事項（§4、§16–§18）、評選項目（§5、§6）、固定費用（§9）、簡報（§10）、評定方式（§11–§15-1）、價格權重 20%-50%、評選規則不得變更（§19）、不訂底價原則（§22） |
| 機關委託資訊服務廠商評選及計費辦法 | https://law.moj.gov.tw/LawClass/LawAll.aspx?pcode=A0030078 | 2026-10-31 | 民國 114 年 05 月 23 日 | 適用範圍（§2、§22）、資訊服務範圍（§3）、招標文件得載事項（§5）、整體委外（§4、§6、§8）、評審項目（§7）、評選與議價決標（§9–§12）、計費三法與上限（§13–§20）、智慧財產權（§21） |
| 採購評選委員會組織準則 | https://law.moj.gov.tw/LawClass/LawAll.aspx?pcode=A0030103 | 2026-10-31 | 民國 115 年 05 月 08 日 | 成立時點（§3）、委員 5 人以上與專家學者不少於 1/3（§4）、名單公開（§6）、正副召集人（§7）、工作小組（§8） |
| 招標期限標準 | https://law.moj.gov.tw/LawClass/LawAll.aspx?pcode=A0030093 | 2026-10-31 | 民國 98 年 08 月 31 日 | 等標期下限（§2）、公開評選準用、變更延長、縮短事由（§9） |
| 查核金額、公告金額及中央機關小額採購金額 | https://www.pcc.gov.tw/downloadFile?fpath=YXJ0aWNsZS8xNzM2NzYwODk4MDkwLnBkZg%3D%3D&sname=%E4%BF%AE%E6%AD%A3%E6%A2%9D%E6%96%87%E5%B0%8D%E7%85%A7%E8%A1%A8%281120101%E4%BF%AE%E6%AD%A3%29.pdf | 2026-10-31 | 民國 112 年 01 月 01 日生效 | 公告金額 150 萬元、小額 15 萬元、勞務查核金額 1,000 萬元 |
| 投標廠商資格與特殊或巨額採購認定標準 | https://www.pcc.gov.tw/content/index?eid=2859&type=C | 2026-10-31 | 工程會現行版 | 勞務巨額採購 2,000 萬元 |
| 機關辦理涉及國家安全採購之廠商資格限制條件及審查作業辦法 | https://law.moj.gov.tw/LawClass/LawAll.aspx?pcode=A0030314 | 2026-10-31 | 民國 108 年 11 月 20 日 | 廠商資格限制事項、敘明理由及核准、證明文件 |
| 資通安全管理法 | https://law.moj.gov.tw/LawClass/LawAll.aspx?pcode=A0030297 | 2026-10-31 | 民國 114 年 09 月 24 日（114 年 12 月 1 日施行） | 委外（§10）、危害國家資通安全產品（§3、§11、§27） |
| 資通安全管理法施行細則 | https://law.moj.gov.tw/LawClass/LawAll.aspx?pcode=A0030303 | 2026-10-31 | 民國 115 年 01 月 05 日 | 委外選任及監督事項（§7）、核心資通系統定義、第三方安全性檢測門檻 1,000 萬元 |
| 個人資料保護法 | https://law.moj.gov.tw/LawClass/LawAll.aspx?PCode=I0050021 | 2026-10-31 | 民國 114 年 11 月 11 日修正公布，施行日期由行政院定之，尚未生效 | 受託者視同委託機關（§4）；修正條文只作前瞻提醒 |
| 個人資料保護法施行細則 | https://law.moj.gov.tw/LawClass/LawAll.aspx?pcode=I0050022 | 2026-10-31 | 民國 105 年 03 月 02 日 | 委託監督事項（§8） |
| 人工智慧基本法 | https://law.moj.gov.tw/LawClass/LawAll.aspx?pcode=H0160093 | 2026-10-31 | 民國 115 年 01 月 14 日公布施行 | 政府使用 AI 之風險評估與內控、基本原則 |

## Official templates and guidance

Check these when a template version matters; they are not statutes and change without a law revision.

| Source | URL | Checked | Version seen | Used for |
|---|---|---|---|---|
| 資訊服務採購契約範本 | https://www.pcc.gov.tw/content/index?eid=9819&type=C | 2026-10-31 | 1131226 | 政府資訊服務案契約基底 |
| 投標須知範本 | https://www.pcc.gov.tw/content/index?eid=9808&type=C | 2026-10-31 | 修正對照表 1150727 | 投標須知基底 |
| 資訊服務採購評選項目及配分權重範例 | https://www.pcc.gov.tw/downloadFile?fpath=YXJ0aWNsZS8xNzM0MzE0NzUzNTE1LnBkZg%3D%3D&sname=%E8%B3%87%E8%A8%8A%E6%9C%8D%E5%8B%99%E6%8E%A1%E8%B3%BC%E8%A9%95%E9%81%B8%E9%A0%85%E7%9B%AE%E5%8F%8A%E9%85%8D%E5%88%86%E6%AC%8A%E9%87%8D%E7%AF%84%E4%BE%8B-1131216.pdf | 2026-10-31 | 113 年 12 月 | 七類資訊服務之配分起點、評分級距、70 分門檻範例 |
| 資訊服務採購契約範本（含投標須知範本）之資安檢核事項 | https://moda.gov.tw/ACS/laws/guide/rules-guidelines/1331 | 2026-10-31 | 頁面更新 2025-01-08，依投標須知範本 1120630 版制定 | 政府案資安條款檢核；**內容未逐項查核，且早於投標須知範本 1150727 修正**，使用時請以官方檔為準 |
| 資訊服務採購作業指引 / 資通系統籌獲各階段資安強化措施 | 工程會、行政院公開文件 | 2026-10-31 | 僅由工程會範例與函文確認其存在 | 待後續版本納入；目前只作指引名稱 |
| 行政院及所屬機關（構）使用生成式 AI 參考指引 | https://www.nstc.gov.tw/folksonomy/list/c79bf57b-dc94-4aff-8d14-3262b5559cfc?l=ch | 2026-10-31 | 112 年發布 | AI 採購時對照；內容未逐項查核 |

## Linter-backed legal rules

| Rule | Severity | Source basis | Notes |
|---|---|---|---|
| `placeholder` | blocker | Skill output contract | Finished drafts must not contain `【填入】`, `__%`, `TODO`, `TBD`, `待補`, or an unresolved choice such as `【普／中／高】`; items still open are written as `待確認：<項目>`. |
| `soft_placeholder` | warning (advisory) | Skill quality rule | V9: `○○`, `＿＿`, and bracketed defaults such as `【99.9%】`; annexed forms keep these legitimately. |
| `presentation_weight` | major | 最有利標評選辦法 §10 | Applies to government-track RFPs only. |
| `presentation_absence` | major | 最有利標評選辦法 §10 第 4 項 | V9: excluding a bidder for missing the presentation; scoring that item zero stays lawful. |
| `price_weight` > 50% | blocker | 最有利標評選辦法 §16 / §17 | Applies to government-track RFPs when price is included in scoring or ranking. |
| `price_weight` < 20% | blocker unless fixed-price | 最有利標評選辦法 §16 / §17; fixed-price route §9, §12, §15 | Fixed-price government cases may be below 20% only when the RFP declares fixed-price / fixed-fee treatment; negated mentions and notes explaining the exception do not count. |
| `weight_sum` | major | 評選矩陣 completeness rule | Applies to the declared weight / score column of evaluation tables; pieces split at a page break are merged first. |
| `evaluation_weights` | blocker | 最有利標評選辦法 §16 / §17 / §18 | V9: government scored tender with no weights in any table or sentence. |
| `award_method` | major | 最有利標評選辦法 §4 / §11 | V9: 總評分法、評分單價法或序位法 not stated. Skipped for 最低標 cases. |
| `passing_score` | major | 最有利標評選辦法 §16 / §17 | V9: 合格分數 or an equivalent sentence not stated. Skipped for 最低標 cases. |
| `committee_size` | blocker | 政府採購法 §94；採購評選委員會組織準則 §4 | V9: stated size under 5, or stated experts under 1/3. Quorum and 工作小組 sentences are excluded. |
| `track_unknown` / `input_too_short` | warning (advisory) | Skill quality rule | V9: says when statutory rules were not applied, or when extraction likely failed. |
| `out_of_scope_mention` | warning (advisory) | Skill quality rule | V6, extended in V9: a mandatory-section keyword found in a「不處理／不適用／另行約定」context; advisory only, prescriptive 不得／禁止 prohibitions are excluded. |
| missing `committee` (escalated) | blocker on gov 最有利標/資服, else major (gov) | 採購評選委員會組織準則 | V6 conditional severity: a government most-advantageous-tender / information-service case with no 評選委員會/評選方式 is a legality Blocker. |
| missing `exit` (escalated) | blocker when 個資/雲端/關鍵系統 present | 個資法委託處理 + CLM exit best practice | V6 conditional severity: outsourced sensitive data with no return/erase clause. |
| missing `locale` (escalated) | blocker on gov + sensitive | 資料落地 / 跨境揭露 | V6 conditional severity. |
| missing `banlist` (escalated) | major on government track | 公部門禁用陸製/陸籍實務 | V6 conditional severity; enterprise stays minor. |

Linter `rfp_lint-9` reads the declared item and weight columns of every evaluation table in the document, so percentages inside scoring formulas or notes do not alter price, presentation, or total-weight findings. It also requires a declaration of fixed-price / fixed-fee treatment (or `--fixed-price`) before applying the below-20% exception; a known budget alone is not sufficient evidence.

> **2026-06-16 live verification**: the three legal sources above were re-fetched from 全國法規資料庫 and their 修正日期 confirmed (114/01/21, 114/05/23, 115/05/08); page text also confirmed the 20%–50% price band, ≤20% simulation cap, §5 應載事項 (13 款), 公費 ≤25% / 管理費 ≤100% / 預付 ≤30%, and committee composition (5+ 人、外聘 ≥1/3、召集人一級主管以上). Linter grader at this check: `rfp_lint-6`.

> **2026-08-28 live verification**: 全國法規資料庫再次確認《最有利標評選辦法》修正日期仍為民國 114/01/21，§10 簡報 / 詢答上限與 §16/§17 價格 20%–50% 規則未變；《機關委託資訊服務廠商評選及計費辦法》修正日期仍為民國 114/05/23，§5 招標文件 13 款事項、§13 計費三法及現行費用上限未變；《採購評選委員會組織準則》修正日期仍為民國 115/05/08，委員 5 人以上與專家學者至少 1/3 規則未變。三個來源下次 90 日定期查核日為 2026-11-26；若發布晚於該日，須先重新查核。

> **2026-10-31 live verification**: 全國法規資料庫全文核對上列法規，修正日期與本表一致。本輪修正內建內容與條文不符之處：《資訊服務辦法》§5 為「得視個案特性及實際需要載明」而非應載；§16、§17 要求招標文件載明合格判定而非「得另訂」；§14 是同分處理而非簡報；§10 第 4 項未出席不影響投標文件有效性；§21 智慧財產權歸屬與侵權責任為應載。另新增委外資安（資安法 §10、細則 §7）、委託監督（個資法細則 §8）與金額級距來源。《個人資料保護法》114 年修正條文尚未生效。工程會研議《政府採購法》修法（含查核與巨額額度），截至查核日未生效，下次查核須確認。下次 90 日定期查核日為 2027-01-29。

## Public case examples

`case-patterns.md` uses widely discussed public IT project examples only to illustrate failure modes. It must not be treated as a sourced research report. If a final report needs case citations, hand off to a research workflow and verify each case independently.
