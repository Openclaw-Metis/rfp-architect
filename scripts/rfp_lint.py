#!/usr/bin/env python3
"""
rfp_lint.py — deterministic linter for an RFP (建議書徵求說明書) draft.

Two layers:
1) Completeness (keyword-based): does the draft mention every mandatory section /
   Taiwan-specific clause? Presence ≠ quality — a HIT still needs rubric review.
2) Compliance rules (regex-based, V3): catches a class of HIGH-RISK errors that a
   keyword check cannot — leftover placeholders, price weight outside the statutory
   20%–50% band, simulation weight over 20%, and評選 weights not summing to 100%.

Used by both modes:
- write mode: self-check a generated draft before returning it.
- review mode: a mechanical first pass before the rubric-based human judgement.

Usage:
    python3 scripts/rfp_lint.py <rfp_file.md|.txt> [--json]
    cat rfp.md | python3 scripts/rfp_lint.py - [--json]

Exit code: 0 if clean or only advisory warnings; 1 if a Blocker section is missing,
a placeholder remains (draft not finished), or a clear rule violation fires.
"""
import sys, json, re

# ---- Layer 1: completeness (key, label, severity, [keywords; any match = present]) ----
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

# placeholders that must be gone in a finished draft
_PLACEHOLDERS = ["【填入", "【__", "__%", "待補", "待確認", "TODO", "xxx%", "XX%"]
# integer percentage, excluding decimals like 99.9% (lookbehind rejects a preceding digit or dot)
_INT_PCT = re.compile(r"(?<![\d.])(\d{1,3})\s*%(?!\.\d)")


def _eval_section(text: str) -> str:
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


def _label_pct(blob: str, label_re: str):
    """First integer percentage appearing right after a label within the same line/run."""
    vals = []
    for m in re.finditer(label_re + r"[^%\d\n]{0,12}?(\d{1,3})\s*%", blob):
        vals.append(int(m.group(1)))
    return vals


def rule_checks(text: str):
    """Layer 2: regex compliance rules. Returns list of findings."""
    findings = []

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
        # presentation_weight_rule — 簡報/現場詢答 weight must be ≤20% (no statutory exception)
        for v in _label_pct(sec, r"(?:簡報|現場詢答|詢答)"):
            if v > 20:
                findings.append({
                    "rule": "presentation_weight", "severity": "major",
                    "message": f"簡報 / 詢答配分 {v}% 逾《最有利標評選辦法》20% 上限。"
                })
                break
        # price_weight_rule — price 20%–50% unless fixed-price案 → advisory (warning)
        fixed_price = any(k in text for k in ("固定價格", "固定費用", "預算已定案", "預算確定"))
        for v in _label_pct(sec, r"價格"):
            if v < 20 or v > 50:
                note = "；惟若為固定價格給付案則得低於 20%，請確認" if (v < 20 and fixed_price) else ""
                findings.append({
                    "rule": "price_weight", "severity": "warning",
                    "message": f"價格配分 {v}% 不在《最有利標評選辦法》§16/§17 之 20%–50%；"
                               f"非固定價格案即違規{note}。"
                })
                break
        # weight_sum_rule — 評選 weights should sum to ~100% (only count table-row %, not prose)
        row_pcts = []
        for ln in sec.splitlines():
            if "|" in ln:
                row_pcts += [int(x) for x in _INT_PCT.findall(ln)]
        if len(row_pcts) >= 3:
            total = sum(row_pcts)
            if not (98 <= total <= 102):
                findings.append({
                    "rule": "weight_sum", "severity": "warning",
                    "message": f"評選配分合計約 {total}%（偵測 {len(row_pcts)} 項表格配分），宜為 100%，請確認。"
                })

    return findings


def lint(text: str):
    low = text.lower()
    present, missing = [], []
    for key, label, sev, kws in CHECKS:
        hit = any(k.lower() in low for k in kws)
        (present if hit else missing).append({"key": key, "label": label, "severity": sev})
    missing.sort(key=lambda m: SEV_RANK[m["severity"]])
    blockers = [m for m in missing if m["severity"] == "blocker"]
    rules = rule_checks(text)
    rule_block = [r for r in rules if r["severity"] in ("blocker", "major")]
    score = round(100 * len(present) / len(CHECKS))
    ok = (len(blockers) == 0) and (len(rule_block) == 0)
    return {
        "total_checks": len(CHECKS),
        "present": len(present),
        "coverage_pct": score,
        "missing": missing,
        "missing_blockers": [m["label"] for m in blockers],
        "rule_findings": rules,
        "rule_violations": len(rule_block),
        "rule_warnings": len([r for r in rules if r["severity"] == "warning"]),
        "pass": ok,
    }


def main():
    args = [a for a in sys.argv[1:] if a != "--json"]
    as_json = "--json" in sys.argv
    if not args:
        print("usage: rfp_lint.py <rfp_file|-> [--json]", file=sys.stderr)
        sys.exit(2)
    src = args[0]
    text = sys.stdin.read() if src == "-" else open(src, encoding="utf-8").read()
    res = lint(text)
    if as_json:
        print(json.dumps(res, ensure_ascii=False, indent=2))
    else:
        verdict = "PASS" if res["pass"] else "FAIL"
        tail = ""
        if res["pass"] and res["rule_warnings"]:
            tail = f"｜⚠ {res['rule_warnings']} 項合規風險待確認"
        print(f"RFP 完整度：{res['present']}/{res['total_checks']} 章節 ({res['coverage_pct']}%)  {verdict}{tail}")
        if res["missing"]:
            print("章節缺漏：")
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
