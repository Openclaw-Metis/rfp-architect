#!/usr/bin/env python3
"""
rfp_lint.py — deterministic linter for an RFP (建議書徵求說明書) draft.

Three layers:
1) Completeness (keyword-based): does the draft mention every mandatory section /
   Taiwan-specific clause? Presence ≠ quality — a HIT still needs rubric review.
   V6 also returns evidence (line number, matched keyword, nearest heading) so a
   review can cite WHERE a section is, not just whether it is present.
2) Compliance rules (regex-based): catches a class of HIGH-RISK errors that a
   keyword check cannot — leftover placeholders, price weight outside the statutory
   20%–50% band, simulation weight over 20%, and 評選 weights not summing to 100%.
   Weight detection is row-aware (V7): the price / simulation rules also read the
   whole eval-table row, so a verbose item label (e.g.「價格合理性與成本效益綜合
   評估」) no longer hides an over-cap weight; and the weight-sum rule skips
   threshold / subtotal rows (門檻 / 及格 / 合計…) that are not weights and would
   otherwise inflate the total.
3) Context-aware signals (V6):
   - Out-of-scope negation: a keyword that appears only inside a「不處理 / 不適用」
     context is surfaced as an ADVISORY warning (never a hard fail), because a
     keyword linter cannot safely tell prescriptive prohibitions (e.g.「不得使用
     大陸製品」, which is a legitimate clause) from genuine absence. The rubric makes
     the call.
   - Track-specific severity: 評選委員會 / 退場返還 / 禁用清單 / 資料落地 carry far
     more weight in a government 最有利標 / 資訊服務 case (and when 個資 / 雲端 /
     關鍵系統 are in play) than in a generic enterprise RFP, so their MISSING
     severity is escalated accordingly.

Used by both modes:
- write mode: self-check a generated draft before returning it.
- review mode: a mechanical first pass before the rubric-based human judgement.

Usage:
    python3 scripts/rfp_lint.py <rfp_file.md|.txt> [--json] [--track auto|government|enterprise] [--fixed-price]
    cat rfp.md | python3 scripts/rfp_lint.py - [--json] [--track auto|government|enterprise] [--fixed-price]

Exit code: 0 if clean or only advisory warnings; 1 if a Blocker section is missing,
a placeholder remains (draft not finished), or a clear rule violation fires.
"""
import argparse
import json
import re
import sys

GRADER_VERSION = "rfp_lint-7"

# ---- Layer 1: completeness (key, label, base_severity, [keywords; any match = present]) ----
CHECKS = [
    ("summary",    "執行摘要 / 專案願景",      "minor",   ["執行摘要", "專案願景", "願景", "summary", "vision"]),
    ("background", "業務背景與目標",            "major",   ["背景", "目標", "痛點", "現狀", "objective", "background"]),
    ("scope",      "工作範疇 (含/不含)",        "major",   ["範疇", "範圍", "scope of work", "包含", "不包含", "工作說明"]),
    ("functional", "功能需求 (分級)",           "blocker", ["功能需求", "必要", "應有", "加分", "functional requirement", "use case"]),
    ("nonfunc",    "技術/非功能需求",           "major",   ["非功能", "效能", "可用率", "可擴充", "可維護", "整合架構", "non-functional", "architecture"]),
    ("migration",  "系統轉換 / 技術移轉",       "minor",   ["系統轉換", "技術移轉", "新舊系統", "平行測試", "上線計畫", "上線程序", "system transition"]),
    ("security",   "資通安全分級",              "blocker", ["資安", "資通安全", "防護需求分級", "iso 27001", "ssdlc", "security"]),
    ("locale",     "資料落地 / 繁中在地化",     "major",   ["資料落地", "境內", "繁體中文", "在地化", "localization", "data residency"]),
    ("banlist",    "禁用產品/人員條款",         "minor",   ["大陸", "陸籍", "禁用", "大陸地區人民"]),
    ("sla",        "服務水準 / SLA",            "major",   ["sla", "服務水準", "可用率", "回應時間", "罰則"]),
    ("pricing",    "商業模式與定價/計費方式",   "minor",   ["定價", "報價", "付費", "預算", "總包價", "單價計算", "按月計酬", "按時計酬", "服務成本加公費", "pricing", "budget"]),
    ("evaluation", "評選標準與配分",            "blocker", ["評選", "配分", "權重", "最有利標", "序位法", "評分", "evaluation", "scoring"]),
    ("committee",  "評選委員會 (政府採購)",     "minor",   ["評選委員會", "委員", "外聘", "召集人"]),
    ("timeline",   "時程 / 里程碑 / 等標期",    "major",   ["時程", "里程碑", "等標期", "截止", "milestone", "timeline"]),
    ("ip",         "智財/著作權歸屬",           "blocker", ["著作", "智財", "智慧財產", "著作財產權", "授權", "intellectual property", "copyright"]),
    ("acceptance", "驗收標準",                  "blocker", ["驗收", "acceptance", "驗收標準"]),
    ("warranty",   "保固 / 維護",               "minor",   ["保固", "維護", "保固保證金", "warranty", "maintenance"]),
    ("change_mgmt","變更管理 / 變更請求流程",   "major",   ["變更管理", "變更請求", "變更控制", "變更流程", "change request", "change control", "change management"]),
    ("exit",       "退場 / 資料返還 / 移交",    "minor",   ["退場", "資料返還", "移交", "交接", "服務移轉", "退場計畫", "transition-out", "exit plan"]),
    ("submission", "投標須知 / 釋疑",           "major",   ["投標須知", "釋疑", "提交", "頁數", "submission", "格式"]),
]

SEV_RANK = {"blocker": 0, "major": 1, "minor": 2}

# placeholders that must be gone in a finished draft. "待確認" is intentionally
# allowed because SKILL.md permits a final explicit confirmation list.
_PLACEHOLDERS = ["【填入", "【__", "__%", "待補", "TODO", "xxx%", "XX%"]
# integer percentage, excluding decimals like 99.9% (lookbehind rejects a preceding digit or dot)
_INT_PCT = re.compile(r"(?<![\d.])(\d{1,3})\s*%(?!\.\d)")

# Out-of-scope negation: a section TOPIC declared absent / not handled. Deliberately
# excludes 「不包含」 (a legitimate scope-exclusion keyword) and prescriptive 不得/禁止
# prohibitions (guarded separately) to avoid flagging valid clauses.
_OUT_OF_SCOPE = re.compile(r"(不處理|未處理|不涉及|未涉及|不適用|無需求|無此需求|無相關需求|未規劃|尚未規劃|從缺|無須處理)")
_PROHIBITION = re.compile(r"(不得|禁止|不可|嚴禁)")

# Markers that raise the stakes for data-return / residency / committee clauses.
_SENSITIVE_MARKERS = ("個資", "個人資料", "personal data", "關鍵基礎設施",
                      "關鍵資訊基礎設施", "關鍵系統", "雲端", "cloud")
# Most-advantageous-tender / information-service procurement context.
_MAT_MARKERS = ("最有利標", "資訊服務", "機關委託資訊服務", "評選委員會")
# Eval-table row labels that are thresholds / subtotals, NOT scoring weights; they
# must be excluded from the weight-sum check so they do not inflate the total.
_NON_WEIGHT_ROW = ("門檻", "及格", "合格", "底標", "底價", "總分", "滿分", "合計", "小計", "總計")


def _heading_map(lines):
    """For each line index, the text of the nearest preceding markdown heading."""
    out = []
    current = ""
    for ln in lines:
        if ln.lstrip().startswith("#"):
            current = ln.lstrip("#").strip()
        out.append(current)
    return out


def _find_first(lines, head_map, keywords):
    """Return (line_no_1based, matched_keyword, heading) for the first keyword hit."""
    for i, ln in enumerate(lines):
        low = ln.lower()
        for kw in keywords:
            if kw.lower() in low:
                return (i + 1, kw, head_map[i])
    return None


def _negation_hit(lines, keywords):
    """If a keyword appears on a line that declares the topic out-of-scope (and is not a
    prescriptive 不得/禁止 prohibition), return (line_no_1based, evidence_excerpt)."""
    for i, ln in enumerate(lines):
        low = ln.lower()
        if not any(kw.lower() in low for kw in keywords):
            continue
        if _OUT_OF_SCOPE.search(ln) and not _PROHIBITION.search(ln):
            excerpt = ln.strip()
            if len(excerpt) > 60:
                excerpt = excerpt[:57] + "…"
            return (i + 1, excerpt)
    return None


def _effective_severity(key, base, track, sensitive, mat_context):
    """Escalate MISSING severity for clauses that matter more in government / sensitive cases."""
    if key == "committee":
        if track == "government":
            return "blocker" if mat_context else "major"
        return base  # enterprise: a 評選委員會 is not required
    if key == "exit":
        if sensitive:
            return "blocker"  # outsourced data with no return/erase clause is a real trap
        if track == "government":
            return "major"
        return base
    if key == "banlist":
        return "major" if track == "government" else base
    if key == "locale":
        if track == "government" and sensitive:
            return "blocker"
        return base  # already major
    return base


def _eval_section(text):
    """Return the 評選/配分 section (heading contains 評選 + 配分/權重/標準) up to the next heading."""
    lines = text.splitlines()
    start = None
    for i, ln in enumerate(lines):
        if ln.lstrip().startswith("#") and "評選" in ln and any(k in ln for k in ("配分", "權重", "標準")):
            start = i
            break
    if start is None:
        return ""
    out = [lines[start]]
    for ln in lines[start + 1:]:
        if ln.lstrip().startswith("#"):
            break
        out.append(ln)
    return "\n".join(out)


def _label_pct(blob, label_re):
    """First integer percentage appearing right after a label within the same line/run."""
    vals = []
    for m in re.finditer(label_re + r"[^%\d\n]{0,12}?(\d{1,3})\s*%", blob):
        vals.append(int(m.group(1)))
    return vals


def _row_label_pct(blob, keywords):
    """Integer percentages from eval-table rows whose FIRST cell (the item label)
    contains any keyword. Row-aware, so it catches verbose item labels such as
    『價格合理性與成本效益綜合評估』that the fixed-width _label_pct window misses,
    while ignoring keyword mentions that only appear in a description cell."""
    vals = []
    for ln in blob.splitlines():
        if "|" not in ln:
            continue
        cells = [c.strip() for c in ln.split("|") if c.strip()]
        if not cells:
            continue
        label = cells[0].lower()
        if any(kw.lower() in label for kw in keywords):
            vals += [int(x) for x in _INT_PCT.findall(ln)]
    return vals


def _detect_track(text, requested):
    """Infer whether Taiwan government procurement rules should apply."""
    if requested != "auto":
        return requested
    government_markers = (
        "政府採購", "政府機關", "公法人", "受採購法", "採購法", "最有利標",
        "等標期", "評選委員會", "採購評選委員會", "機關委託資訊服務",
    )
    enterprise_markers = ("一般企業", "企業委外", "公司採購", "民間企業")
    gov_hits = sum(1 for k in government_markers if k in text)
    ent_hits = sum(1 for k in enterprise_markers if k in text)
    if gov_hits:
        return "government"
    if ent_hits:
        return "enterprise"
    return "unknown"


def _detect_fixed_price(text, forced):
    if forced:
        return True
    return any(k in text for k in ("固定價格", "固定費用", "固定服務費用", "固定費率", "預算已定案", "預算確定"))


def rule_checks(text, track="auto", fixed_price=False):
    """Layer 2: regex compliance rules. Returns list of findings."""
    findings = []
    effective_track = _detect_track(text, track)

    # placeholder_rule — a finished RFP must not contain template placeholders
    low = text.lower()
    hits = sorted({p for p in _PLACEHOLDERS if p.lower() in low})
    if hits:
        findings.append({
            "rule": "placeholder", "severity": "blocker",
            "message": f"草稿仍含未填占位符 {hits}；write 模式不得宣稱完成（這是模板而非完稿）。"
        })

    sec = _eval_section(text)
    if sec:
        # Taiwan government procurement compliance rules.
        if effective_track == "government":
            # presentation_weight_rule — 簡報/現場詢答 weight must be ≤20% (no statutory exception).
            # Union of prose detection and row-aware detection (verbose labels).
            pres_vals = set(_label_pct(sec, r"(?:簡報|現場詢答|詢答)")) | set(
                _row_label_pct(sec, ["簡報", "現場詢答", "詢答"]))
            if pres_vals and max(pres_vals) > 20:
                findings.append({
                    "rule": "presentation_weight", "severity": "major",
                    "message": f"簡報 / 詢答配分 {max(pres_vals)}% 逾《最有利標評選辦法》§10 之 20% 上限。"
                })
            # price_weight_rule — price 20%–50% unless fixed-price案 only for the lower bound.
            # Union of prose detection and row-aware detection so a verbose price-row
            # label cannot hide an over-cap weight.
            is_fixed_price = _detect_fixed_price(text, fixed_price)
            price_vals = set(_label_pct(sec, r"價格")) | set(_row_label_pct(sec, ["價格", "報價"]))
            if price_vals and max(price_vals) > 50:
                findings.append({
                    "rule": "price_weight", "severity": "blocker",
                    "message": f"價格配分 {max(price_vals)}% 逾《最有利標評選辦法》§16/§17 之 50% 上限。"
                })
            elif price_vals and min(price_vals) < 20:
                lo = min(price_vals)
                if is_fixed_price:
                    findings.append({
                        "rule": "price_weight", "severity": "info",
                        "message": f"固定價格給付案價格配分 {lo}% 低於 20%；此為固定價格例外，仍應於招標文件明載固定價格給付。"
                    })
                else:
                    findings.append({
                        "rule": "price_weight", "severity": "blocker",
                        "message": f"非固定價格案價格配分 {lo}% 低於《最有利標評選辦法》§16/§17 之 20% 下限。"
                    })
        # weight_sum_rule — 評選 weights should sum to ~100% (count table-row %, not prose).
        # Skip threshold / subtotal rows (門檻 / 及格 / 合計…), which are not weights.
        row_pcts = []
        for ln in sec.splitlines():
            if "|" not in ln:
                continue
            cells = [c.strip() for c in ln.split("|") if c.strip()]
            if cells and any(m in cells[0] for m in _NON_WEIGHT_ROW):
                continue
            row_pcts += [int(x) for x in _INT_PCT.findall(ln)]
        if len(row_pcts) >= 3:
            total = sum(row_pcts)
            if not (98 <= total <= 102):
                findings.append({
                    "rule": "weight_sum", "severity": "major",
                    "message": f"評選配分合計約 {total}%（偵測 {len(row_pcts)} 項表格配分），應修正為 100%。"
                })

    return findings


def lint(text, track="auto", fixed_price=False):
    lines = text.splitlines()
    low = text.lower()
    eff_track = _detect_track(text, track)
    sensitive = any(m.lower() in low for m in _SENSITIVE_MARKERS)
    mat_context = any(m in text for m in _MAT_MARKERS)
    head_map = _heading_map(lines)

    checks_out, missing, weak_hits = [], [], []
    present_count = 0
    for key, label, base_sev, kws in CHECKS:
        eff_sev = _effective_severity(key, base_sev, eff_track, sensitive, mat_context)
        loc = _find_first(lines, head_map, kws)
        if loc:
            present_count += 1
            line_no, matched, heading = loc
            entry = {"key": key, "label": label, "status": "present", "severity": eff_sev,
                     "line": line_no, "matched": matched, "heading": heading}
            neg = _negation_hit(lines, kws)
            if neg:
                entry["status"] = "weak_hit"
                entry["evidence_line"] = neg[0]
                entry["evidence"] = neg[1]
                weak_hits.append({"key": key, "label": label, "line": neg[0], "evidence": neg[1]})
            checks_out.append(entry)
        else:
            missing.append({"key": key, "label": label, "severity": eff_sev})
            checks_out.append({"key": key, "label": label, "status": "missing", "severity": eff_sev})

    missing.sort(key=lambda m: SEV_RANK[m["severity"]])
    blockers = [m for m in missing if m["severity"] == "blocker"]

    rules = rule_checks(text, track=track, fixed_price=fixed_price)
    for w in weak_hits:
        rules.append({
            "rule": "out_of_scope_mention", "severity": "warning", "key": w["key"], "line": w["line"],
            "message": f"『{w['label']}』關鍵字出現在疑似『不處理 / 不適用』語境（第 {w['line']} 行：{w['evidence']}）；命中不代表章節具備，請人工複核。"
        })
    rule_block = [r for r in rules if r["severity"] in ("blocker", "major")]

    score = round(100 * present_count / len(CHECKS))
    ok = (len(blockers) == 0) and (len(rule_block) == 0)
    return {
        "total_checks": len(CHECKS),
        "present": present_count,
        "coverage_pct": score,
        "checks": checks_out,
        "missing": missing,
        "missing_blockers": [m["label"] for m in blockers],
        "weak_hits": [w["label"] for w in weak_hits],
        "rule_findings": rules,
        "rule_violations": len(rule_block),
        "rule_warnings": len([r for r in rules if r["severity"] == "warning"]),
        "rule_infos": len([r for r in rules if r["severity"] == "info"]),
        "effective_track": eff_track,
        "sensitive_context": sensitive,
        "grader_version": GRADER_VERSION,
        "pass": ok,
    }


def main():
    parser = argparse.ArgumentParser(description="Lint an outsourced software/system RFP draft.")
    parser.add_argument("src", help="RFP file path, or '-' for stdin")
    parser.add_argument("--json", action="store_true", help="emit JSON")
    parser.add_argument("--track", choices=["auto", "government", "enterprise"], default="auto",
                        help="apply Taiwan government procurement rules, enterprise rules, or infer from text")
    parser.add_argument("--fixed-price", action="store_true",
                        help="treat the RFP as a fixed-price/fixed-fee government procurement case")
    ns = parser.parse_args()
    src = ns.src
    text = sys.stdin.read() if src == "-" else open(src, encoding="utf-8").read()
    res = lint(text, track=ns.track, fixed_price=ns.fixed_price)
    if ns.json:
        print(json.dumps(res, ensure_ascii=False, indent=2))
    else:
        verdict = "PASS" if res["pass"] else "FAIL"
        tail = ""
        if res["pass"] and res["rule_warnings"]:
            tail = f"｜⚠ {res['rule_warnings']} 項合規風險待確認"
        if res["pass"] and res["rule_infos"]:
            tail += f"｜ℹ {res['rule_infos']} 項說明"
        print(f"RFP 完整度：{res['present']}/{res['total_checks']} 章節 ({res['coverage_pct']}%)  軌道={res['effective_track']}  {verdict}{tail}")
        if res["missing"]:
            print("章節缺漏（嚴重度已依採購軌道 / 敏感度調整）：")
            for m in res["missing"]:
                print(f"  [{m['severity'].upper()}] {m['label']}")
        if res["rule_findings"]:
            print("規則檢查（合規風險）：")
            for r in res["rule_findings"]:
                print(f"  [{r['severity'].upper()}] {r['message']}")
        if not res["missing"] and not res["rule_findings"]:
            print("章節完整、規則檢查無異常（仍須以 review-rubric.md 判定品質）。")
    sys.exit(0 if res["pass"] else 1)


if __name__ == "__main__":
    main()
