#!/usr/bin/env python3
"""Regression tests for rfp_lint.py high-risk rules and rfp_extract.py inputs (rfp_lint-9)."""

import tempfile
import zipfile
from pathlib import Path

from rfp_extract import InputError, decode_stdin, read_document
from rfp_lint import lint

PASSING_LINE = "總滿分 100 分，合格分數 70 分。"

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
評定方式：序位法。
總滿分 100 分，合格分數 70 分。
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
    "committee": "## 評選委員會\n評選委員會 5 人以上 外聘 召集人 委員\n評定方式：序位法。\n總滿分 100 分，合格分數 70 分。",
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


# ---- File-format fixtures (V9): minimal documents built in a temporary folder ----
WORD_NS = 'xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main"'
DOCX_STYLES = f"""<w:styles {WORD_NS}><w:style w:type="paragraph" w:styleId="2">
<w:name w:val="heading 2"/></w:style></w:styles>"""
DOCX_BODY = f"""<w:document {WORD_NS}><w:body>
<w:p><w:pPr><w:pStyle w:val="2"/></w:pPr><w:r><w:t>評選標準與配分</w:t></w:r></w:p>
<w:tbl>
<w:tr><w:tc><w:tcPr><w:gridSpan w:val="2"/></w:tcPr><w:p><w:r><w:t>評選項目及配分表</w:t></w:r></w:p></w:tc></w:tr>
<w:tr><w:tc><w:p><w:r><w:t>評選項目</w:t></w:r></w:p></w:tc><w:tc><w:p><w:r><w:t>配分</w:t></w:r></w:p></w:tc></w:tr>
<w:tr><w:tc><w:p><w:r><w:t>技術</w:t></w:r></w:p></w:tc><w:tc><w:p><w:r><w:t>40</w:t></w:r></w:p></w:tc></w:tr>
<w:tr><w:tc><w:p><w:r><w:t>價格</w:t></w:r></w:p></w:tc><w:tc><w:p><w:r><w:t>60</w:t></w:r></w:p></w:tc></w:tr>
</w:tbl></w:body></w:document>"""
ODT_BODY = """<office:document-content xmlns:office="urn:oasis:names:tc:opendocument:xmlns:office:1.0"
 xmlns:text="urn:oasis:names:tc:opendocument:xmlns:text:1.0"
 xmlns:table="urn:oasis:names:tc:opendocument:xmlns:table:1.0"><office:body><office:text>
<text:h text:outline-level="2">評選標準與配分</text:h>
<table:table>
<table:table-row><table:table-cell><text:p>評選項目</text:p></table:table-cell><table:table-cell><text:p>配分</text:p></table:table-cell></table:table-row>
<table:table-row><table:table-cell><text:p>技術</text:p></table:table-cell><table:table-cell><text:p>40</text:p></table:table-cell></table:table-row>
<table:table-row><table:table-cell><text:p>價格</text:p></table:table-cell><table:table-cell><text:p>60</text:p></table:table-cell></table:table-row>
</table:table></office:text></office:body></office:document-content>"""


def write_zip(path, parts):
    with zipfile.ZipFile(path, "w") as archive:
        for name, content in parts.items():
            archive.writestr(name, content)


def severities(text, track="government"):
    return {(f["rule"], f["severity"]) for f in lint(text, track=track)["rule_findings"]}


def rules_of(text, rule, track="government"):
    return [f for f in lint(text, track=track)["rule_findings"] if f["rule"] == rule]


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

    # --- V8: context and table-column accuracy ---
    # An explicit enterprise exclusion must beat a negated mention of 採購法.
    enterprise_auto = lint(full_draft(
        title="# 測試 RFP（一般企業委外）",
        pricing="## 商業模式與定價\n一般企業 CRM 委外，廠商須報價。\n本案不適用政府採購法。",
        evaluation="""## 評選標準與配分
| 評選項目 | 權重 |
|---|---:|
| 技術 | 40% |
| 價格 | 60% |""",
    ), track="auto")
    assert_("explicit enterprise exclusion controls auto track",
            enterprise_auto["effective_track"] == "enterprise" and enterprise_auto["pass"] is True,
            f"expected enterprise/pass, got {enterprise_auto['effective_track']}/{enterprise_auto['pass']}")

    # A known budget is not the same as an explicitly fixed price or fee.
    assert_case("known budget is not fixed price",
                draft("政府採購 預算已定案 廠商仍須報價", fixed_low_table), False,
                track="government")

    # Generic evaluation headings must still activate the statutory rules.
    generic_heading = clean_table.replace("| 價格 | 30% |", "| 價格 | 60% |").replace(
        "| 技術 | 40% |", "| 技術 | 40% |")
    assert_case("generic 評選方式 heading still parses table",
                draft("政府採購 報價", generic_heading).replace("## 評選標準與配分", "## 評選方式"),
                False, track="government")

    # Formula percentages live in their own column and must not become weights.
    formula_table = """| 評選項目 | 權重 | 計分方式 |
|---|---:|---|
| 技術 | 70% | 依內容評分 |
| 價格 | 30% | 最低標價／投標標價 × 100% |"""
    formula_result = lint(draft("政府採購 報價", formula_table), track="government")
    assert_("formula percentage is not parsed as weight",
            formula_result["pass"] is True and not formula_result["rule_findings"],
            f"unexpected findings: {formula_result['rule_findings']}")

    # --- V9: every table is scanned and real-document forms hold ---
    split_repeated = """| 項次 | 評選項目 | 配分 |
|---|---|---|
| 一 | 技術 | 50 |

| 項次 | 評選項目 | 配分 |
|---|---|---|
| 二 | 管理 | 20 |
| 三 | 價格 | 30 |"""
    assert_("repeated header across pages is one table",
            not rules_of(draft("政府採購 報價", split_repeated), "weight_sum"),
            "page-split table summed separately")

    split_bare = """| 評選項目 | 子項 | 配分 |
|---|---|---|
| 團隊能力 | 主持人 | 20 |
| 執行能力 | 工作計畫 | 20 |

| 企業社會責任 | 指標 | 0 |
|---|---|---|
| 價格 | 標價合理性 | 60 |"""
    assert_("continuation piece keeps its first data row",
            ("price_weight", "blocker") in severities(draft("政府採購 報價", split_bare)),
            "price row on the next page missed")

    two_stages = """| 評選項目 | 配分 |
|---|---|
| 技術 | 70 |
| 價格 | 30 |

| 評選項目 | 配分 |
|---|---|
| 技術 | 60 |
| 價格 | 40 |"""
    assert_("two complete tables stay separate",
            not rules_of(draft("政府採購 報價", two_stages), "weight_sum"), "complete tables were merged")

    scale_table = clean_table + """

| 等第 | 分數 |
|---|---|
| 優 | 90 |
| 甲 | 80 |"""
    assert_("grade scale is not a weight table",
            not rules_of(draft("政府採購 報價", scale_table), "weight_sum"), "grade scale summed as weights")

    notes_column = """| 評選項目 | 配分 | 評語 |
|---|---|---|
| 技術 | 40 | 說明 |
| 價格 | 60 | 說明 |"""
    assert_("a notes column does not hide the weights",
            ("price_weight", "blocker") in severities(draft("政府採購 報價", notes_column)),
            "table with a 評語 column skipped")

    no_score_line = draft("政府採購 報價", clean_table).replace(PASSING_LINE, "")
    assert_("資格不合格 alone is not a passing score",
            rules_of(no_score_line + "\n資格不合格者不予評選。", "passing_score"), "passing score wrongly satisfied")
    assert_("未達分數 sentence states the passing score",
            not rules_of(no_score_line + "\n平均總評分未達 70 分者不得列為協商及決標對象。", "passing_score"),
            "official wording not recognised")

    zero_score = draft("政府採購 報價", clean_table) + "\n廠商唱名未到場，視同放棄簡報，簡報項目以零分計算。"
    assert_("zero score for absence is lawful", not rules_of(zero_score, "presentation_absence"),
            "lawful zero score flagged")

    quorum = draft("政府採購 報價", clean_table) + "\n評選委員會會議應有委員二分之一以上出席，專家、學者至少 2 人。"
    assert_("quorum sentence is not the committee size", not rules_of(quorum, "committee_size"),
            "quorum read as committee size")

    pdf_text = draft("政府採購 報價", "技術（40%）架構 40\n價格（60%）標價合理性 60")
    assert_("pipe-less PDF text is read as prose",
            ("price_weight", "blocker") in severities(pdf_text), "price in brackets missed")

    over_draft = draft("政府採購 報價", price_over_table)
    price_finding = next(f for f in lint(over_draft, track="government")["rule_findings"]
                         if f["rule"] == "price_weight")
    assert_("rule findings carry a line number",
            "| 價格 | 60% |" in over_draft.splitlines()[price_finding["line"] - 1],
            f"wrong line {price_finding.get('line')}")

    pending = lint(draft("政府採購 報價 待確認：罰則", clean_table), track="government")
    assert_("pending confirmations are counted",
            pending["pending_confirmations"] == 1 and pending["pass"] is True,
            f"got {pending['pending_confirmations']}")

    # --- V9: real file formats reach the same rules ---
    assert_("stdin text passes through", decode_stdin("政府採購".encode("utf-8")) == "政府採購", "stdin decode")
    assert_("a short answer with question marks is not mangled",
            decode_stdin("是否?".encode("utf-8")) == "是否?", "short input rejected")
    try:
        decode_stdin(("# ??? RFP\n" + "?" * 80).encode("ascii"))
    except InputError:
        pass
    else:
        raise AssertionError("stdin mangled into question marks should raise InputError")

    with tempfile.TemporaryDirectory() as folder:
        root = Path(folder)
        docx = root / "rfp.docx"
        write_zip(docx, {"word/document.xml": DOCX_BODY, "word/styles.xml": DOCX_STYLES})
        text, kind = read_document(str(docx))
        assert_("docx heading style becomes Markdown", "## 評選標準與配分" in text and kind == "docx", text)
        assert_("docx merged title row leaves the header in place", "| 評選項目 | 配分 |" in text, text)
        assert_("docx table reaches the price rule",
                ("price_weight", "blocker") in severities(draft("政府採購 報價", text)), text)

        odt = root / "rfp.odt"
        write_zip(odt, {"content.xml": ODT_BODY})
        text, kind = read_document(str(odt))
        assert_("odt heading becomes Markdown", "## 評選標準與配分" in text and kind == "odt", text)
        assert_("odt keeps its column count", "| 評選項目 | 配分 |\n|---|---|" in text, text)
        assert_("odt table reaches the price rule",
                ("price_weight", "blocker") in severities(draft("政府採購 報價", text)), text)

        for name, payload in (("big5.txt", "政府採購".encode("cp950")),
                              ("bom.txt", "政府採購".encode("utf-8-sig")),
                              ("utf16.txt", "政府採購".encode("utf-16"))):
            path = root / name
            path.write_bytes(payload)
            assert_(f"{name} decodes", read_document(str(path))[0] == "政府採購", name)

        doctype = root / "doctype.odt"
        write_zip(doctype, {"content.xml": '<!DOCTYPE lolz [<!ENTITY a "a">]><root/>'})
        pdf = root / "rfp.pdf"
        pdf.write_bytes(b"%PDF-1.7")
        broken = root / "broken.docx"
        broken.write_bytes(b"not a zip")
        for label, path in (("DOCTYPE", doctype), ("PDF", pdf), ("bad zip", broken), ("missing", root / "none.md")):
            try:
                read_document(str(path))
            except InputError:
                continue
            raise AssertionError(f"{label} input should raise InputError")

    print("rfp_lint_selftest: PASS")


if __name__ == "__main__":
    main()
