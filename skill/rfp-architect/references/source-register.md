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
| 最有利標評選辦法 | https://law.moj.gov.tw/LawClass/LawAll.aspx?pcode=A0030080 | 2026-06-16 | 民國 114 年 01 月 21 日 | 評選項目、評定方式、價格權重 20%-50%、簡報 / 詢答 20% 上限、評選規則公告後不得變更 |
| 機關委託資訊服務廠商評選及計費辦法 | https://law.moj.gov.tw/LawClass/LawAll.aspx?pcode=A0030078 | 2026-06-16 | 民國 114 年 05 月 23 日 | 資訊服務範圍、招標文件應載事項、資訊服務評審項目、計費三法、公費 / 管理費 / 預付款上限 |
| 採購評選委員會組織準則 | https://law.moj.gov.tw/LawClass/LawAll.aspx?pcode=A0030103 | 2026-06-16 | 民國 115 年 05 月 08 日 | 評選委員會 5 人以上、專家學者不少於 1/3、外聘委員限制、召集人資格 |

## Linter-backed legal rules

| Rule | Severity | Source basis | Notes |
|---|---|---|---|
| `placeholder` | blocker | Skill output contract | Finished drafts must not contain `【填入】`, `__%`, `TODO`, or `待補`; final confirmation lists may use `待確認` outside the draft body. |
| `presentation_weight` | major | 最有利標評選辦法 §10 | Applies to government-track RFPs only. |
| `price_weight` > 50% | blocker | 最有利標評選辦法 §16 / §17 | Applies to government-track RFPs when price is included in scoring or ranking. |
| `price_weight` < 20% | blocker unless fixed-price | 最有利標評選辦法 §16 / §17 and fixed-price exception | Fixed-price government cases may be below 20% only when the RFP explicitly states fixed-price / fixed-fee treatment. |
| `weight_sum` | major | 評選矩陣 completeness rule | Applies whenever an evaluation table has percentage weights. |
| `out_of_scope_mention` | warning (advisory) | Skill quality rule | V6: a mandatory-section keyword found only in a「不處理／不適用」context; advisory only, prescriptive 不得／禁止 prohibitions are excluded. |
| missing `committee` (escalated) | blocker on gov 最有利標/資服, else major (gov) | 採購評選委員會組織準則 | V6 conditional severity: a government most-advantageous-tender / information-service case with no 評選委員會/評選方式 is a legality Blocker. |
| missing `exit` (escalated) | blocker when 個資/雲端/關鍵系統 present | 個資法委託處理 + CLM exit best practice | V6 conditional severity: outsourced sensitive data with no return/erase clause. |
| missing `locale` (escalated) | blocker on gov + sensitive | 資料落地 / 跨境揭露 | V6 conditional severity. |
| missing `banlist` (escalated) | major on government track | 公部門禁用陸製/陸籍實務 | V6 conditional severity; enterprise stays minor. |

> **2026-06-16 live verification**: the three legal sources above were re-fetched from 全國法規資料庫 and their 修正日期 confirmed (114/01/21, 114/05/23, 115/05/08); page text also confirmed the 20%–50% price band, ≤20% simulation cap, §5 應載事項 (13 款), 公費 ≤25% / 管理費 ≤100% / 預付 ≤30%, and committee composition (5+ 人、外聘 ≥1/3、召集人一級主管以上). Linter grader at this check: `rfp_lint-6`.

## Public case examples

`case-patterns.md` uses widely discussed public IT project examples only to illustrate failure modes. It must not be treated as a sourced research report. If a final report needs case citations, hand off to a research workflow and verify each case independently.
