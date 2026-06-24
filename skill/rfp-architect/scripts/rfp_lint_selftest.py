#!/usr/bin/env python3
"""Regression tests for rfp_lint.py high-risk rules (rfp_lint-7)."""

from rfp_lint import lint


# ---- Legacy compliance-rule fixtures (price band / weight sum / placeholder) ----
BASE = """
# 測試 RFP
## 執行摘要
summary
## 背景與目標
objective
## 工作範疇
包含與不包含
## 功能需求
必要 應有 加分 use case
## 技術與非功能需求
可用率 99.9 效能 可擴充 可維護 整合架構
## 系統轉換
上線程序 技術移轉
## 資通安全與法規遵循
資安 security 資通安全 資料落地 繁體中文 大陸 禁用
## 服務水準 SLA
服務水準 回應時間
## 商業模式與定價
{pricing_context}
## 評選標準與配分
{evaluation_table}
## 時程
里程碑 等標期
## 契約條款與投標須知
著作權 智財 驗收標準 保固 變更管理 退場 資料返還 提交 釋疑 評選委員會 外聘 委員
"""


def draft(pricing_context: str, evaluation_table: str) -> str:
    return BASE.format(pricing_context=pricing_context, evaluation_table=evaluation_table)


# ---- Section-level fixtures (V6 evidence / negation / conditional severity) ----
# Each section sits on its own line(s) so a single section can be removed or negated
# without disturbing the others. Default build is a clean government 最有利標 case.
_EVAL_TABLE = """## 評選標準與配分
| 評選項目 | 權重 |
|---|---:|
| 技術 | 40% |
| 管理 | 20% |
| 資安 | 10% |
| 價格 | 30% |"""

_SECTIONS = {
    "title": "# 測試 RFP（政府採購 最有利標）",
    "summary": "## 執行摘要\n專案願景 summary",
    "background": "## 背景與目標\n背景 目標 痛點",
    "scope": "## 工作範疇\n包含與不包含 工作說明",
    "functional": "## 功能需求\n必要 應有 加分 use case 功能需求",
    "nonfunc": "## 技術與非功能需求\n非功能 效能 可用率 99.9 可擴充 可維護 整合架構",
    "migration": "## 系統轉換\n上線程序 技術移轉 平行測試",
    "security": "## 資通安全\n資安 資通安全 security SSDLC",
    "locale": "## 在地化\n資料落地 境內 繁體中文 在地化",
    "banlist": "## 禁用清單\n不得使用大陸地區廠牌；大陸地區人民不得參與；禁用清單",
    "sla": "## 服務水準\nSLA 服務水準 可用率 回應時間 罰則",
    "pricing": "## 商業模式與定價\n政府採購 最有利標 報價 總包價 預算",
    "evaluation": _EVAL_TABLE,
    "committee": "## 評選委員會\n評選委員會 5 人以上 外聘 召集人 委員",
    "timeline": "## 時程\n時程 里程碑 等標期 截止",
    "ip": "## 契約：智財\n著作權 著作財產權 智財 授權",
    "acceptance": "## 驗收\n驗收 驗收標準 acceptance",
    "warranty": "## 保固\n保固 維護",
    "change_mgmt": "## 變更管理\n變更管理 變更請求 書面核准",
    "exit": "## 退場\n退場 資料返還 移交 服務移轉",
    "submission": "## 投標須知\n投標須知 釋疑 提交 頁數 格式",
}


def full_draft(**overrides) -> str:
    """Build a complete government RFP fixture; pass section_key="" to remove a section."""
    sections = dict(_SECTIONS)
    sections.update(overrides)
    return "\n".join(v for v in sections.values() if v)


def assert_case(name: str, text: str, expected_pass: bool, **kwargs):
    res = lint(text, **kwargs)
    if res["pass"] != expected_pass:
        raise AssertionError(f"{name}: expected pass={expected_pass}, got pass={res['pass']} "
                             f"(blockers={res['missing_blockers']}, rule_violations={res['rule_violations']})")


def assert_(name: str, cond: bool, detail: str = ""):
    if not cond:
        raise AssertionError(f"{name}: {detail}")


def main():
    clean_table = """| 評選項目 | 權重 |
|---|---:|
| 技術 | 40% |
| 管理 | 20% |
| 資安 | 10% |
| 價格 | 30% |"""

    price_over_table = """| 評選項目 | 權重 |
|---|---:|
| 技術 | 40% |
| 價格 | 60% |"""

    fixed_low_table = """| 評選項目 | 權重 |
|---|---:|
| 技術 | 90% |
| 價格 | 10% |"""

    bad_sum_table = """| 評選項目 | 權重 |
|---|---:|
| 技術 | 30% |
| 功能 | 20% |
| 管理 | 10% |
| 價格 | 20% |"""

    presentation_over_table = """| 評選項目 | 權重 |
|---|---:|
| 技術 | 50% |
| 價格 | 20% |
| 簡報 | 30% |"""

    # --- Layer 2: compliance rules (unchanged behaviour) ---
    assert_case("clean government", draft("政府採購 報價 總包價", clean_table), True, track="government")
    assert_case("government price over 50", draft("政府採購 報價 總包價", price_over_table), False, track="government")
    assert_case("government price under 20 non-fixed", draft("政府採購 報價 總包價", fixed_low_table), False, track="government")
    assert_case("government fixed price under 20", draft("政府採購 固定價格給付", fixed_low_table), True, track="government")
    assert_case("bad weight sum", draft("政府採購 報價 總包價", bad_sum_table), False, track="government")
    assert_case("presentation over 20", draft("政府採購 報價 總包價", presentation_over_table), False, track="government")
    assert_case("enterprise track skips gov price rule", draft("一般企業 報價", price_over_table), True, track="enterprise")
    assert_case("placeholder blocks", draft("政府採購 報價 【填入】", clean_table), False, track="government")

    # --- V6: conditional / track-specific severity ---
    # complete government 最有利標 baseline still passes
    assert_case("v6 clean gov full draft", full_draft(), True, track="government")
    # gov 最有利標 with no 評選委員會 → committee escalates to Blocker
    assert_case("gov mat committee missing → blocker fail", full_draft(committee=""), False, track="government")
    # enterprise with no 評選委員會 → committee stays minor → still passes
    assert_case("enterprise committee missing → pass",
                full_draft(committee="", pricing="## 商業模式與定價\n一般企業 報價 預算 總包價"),
                True, track="enterprise")
    # gov + 個資 (sensitive) with no 退場/資料返還 → exit escalates to Blocker
    assert_case("gov sensitive exit missing → blocker fail",
                full_draft(exit="", security="## 資通安全\n資安 個資 個人資料保護 security"),
                False, track="government")
    # enterprise (non-sensitive) with no exit → exit stays minor → passes
    assert_case("enterprise exit missing non-sensitive → pass",
                full_draft(exit="", committee="", pricing="## 商業模式與定價\n一般企業 報價 預算"),
                True, track="enterprise")

    # --- V6: out-of-scope negation is ADVISORY only (never a hard fail) ---
    neg = lint(full_draft(security="## 資通安全\n本案不處理資安需求，僅就應用層自行處理"), track="government")
    assert_("negation advisory does not fail", neg["pass"] is True,
            f"expected pass=True, got {neg['pass']} blockers={neg['missing_blockers']}")
    assert_("negation produces weak_hit", "資通安全分級" in neg["weak_hits"],
            f"expected security weak_hit, got {neg['weak_hits']}")
    assert_("negation surfaces a warning", neg["rule_warnings"] >= 1,
            f"expected >=1 warning, got {neg['rule_warnings']}")

    # prescriptive 不得 prohibition must NOT be flagged as out-of-scope
    proh = lint(full_draft(), track="government")
    assert_("prohibition not flagged as negation", proh["weak_hits"] == [],
            f"expected no weak_hits (banlist uses 不得), got {proh['weak_hits']}")

    # --- V6: evidence (line + heading) is attached to present checks ---
    ev = lint(full_draft(), track="government")
    acc = next(c for c in ev["checks"] if c["key"] == "acceptance")
    assert_("evidence carries line number", isinstance(acc.get("line"), int) and acc["line"] > 0,
            f"expected acceptance line number, got {acc}")
    assert_("evidence carries heading", "驗收" in (acc.get("heading") or ""),
            f"expected 驗收 heading, got {acc.get('heading')}")
    assert_("evidence carries matched keyword", acc.get("matched") == "驗收",
            f"expected matched=驗收, got {acc.get('matched')}")

    # --- V7: row-aware eval-table parsing ---
    # verbose-price-label-over-50-fails: a verbose price-row label must not hide an
    # over-cap weight (regression for the fixed-width _label_pct window false-negative).
    verbose_price_over = """| 評選項目 | 權重 |
|---|---:|
| 技術能力 | 40% |
| 價格合理性與成本效益綜合評估 | 60% |"""
    assert_case("verbose price label over 50 → blocker",
                draft("政府採購 報價 總包價", verbose_price_over), False, track="government")

    # threshold-row-not-counted-in-weight-sum: a 及格/門檻 row must not inflate the
    # weight total and wrongly fail a valid 100% table (false-positive regression).
    threshold_row_table = """| 評選項目 | 權重 |
|---|---:|
| 技術 | 40% |
| 管理 | 30% |
| 價格 | 30% |
| 評選及格門檻 | 70% |"""
    assert_case("threshold row not counted in weight sum → pass",
                draft("政府採購 報價 總包價", threshold_row_table), True, track="government")

    print("rfp_lint_selftest: PASS")


if __name__ == "__main__":
    main()
