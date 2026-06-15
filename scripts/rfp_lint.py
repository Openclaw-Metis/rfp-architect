#!/usr/bin/env python3
"""
rfp_lint.py — deterministic completeness linter for an RFP (建議書徵求說明書) draft.

Used by both modes:
- write mode: self-check a generated draft before returning it.
- review mode: a mechanical first pass that flags missing mandatory sections /
  Taiwan-specific clauses before the rubric-based human judgement.

It is keyword-based, not a grader: presence ≠ quality. A MISS is a strong signal;
a HIT still needs human/rubric review for adequacy.

Usage:
    python3 scripts/rfp_lint.py <rfp_file.md|.txt> [--json]
    cat rfp.md | python3 scripts/rfp_lint.py - [--json]

Exit code: 0 if no Blocker-severity sections are missing, else 1.
"""
import sys, json, re

# (key, label, severity, [keywords - any match counts as present])
CHECKS = [
    ("summary",    "執行摘要 / 專案願景",      "minor",   ["執行摘要", "專案願景", "願景", "summary", "vision"]),
    ("background", "業務背景與目標",            "major",   ["背景", "目標", "痛點", "現狀", "objective", "background"]),
    ("scope",      "工作範疇 (含/不含)",        "major",   ["範疇", "範圍", "scope of work", "包含", "不包含", "工作說明"]),
    ("functional", "功能需求 (分級)",           "blocker", ["功能需求", "必要", "應有", "加分", "functional requirement", "use case"]),
    ("nonfunc",    "技術/非功能需求",           "major",   ["非功能", "效能", "可用率", "可擴充", "可維護", "整合架構", "non-functional", "architecture"]),
    ("security",   "資通安全分級",              "blocker", ["資安", "資通安全", "防護需求分級", "iso 27001", "ssdlc", "security"]),
    ("locale",     "資料落地 / 繁中在地化",     "major",   ["資料落地", "境內", "繁體中文", "在地化", "localization", "data residency"]),
    ("banlist",    "禁用產品/人員條款",         "minor",   ["大陸", "陸籍", "禁用", "大陸地區人民"]),
    ("sla",        "服務水準 / SLA",            "major",   ["sla", "服務水準", "可用率", "回應時間", "罰則"]),
    ("pricing",    "商業模式與定價",            "minor",   ["定價", "報價", "付費", "預算", "pricing", "budget"]),
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


def lint(text: str):
    low = text.lower()
    present, missing = [], []
    for key, label, sev, kws in CHECKS:
        hit = any(k.lower() in low for k in kws)
        (present if hit else missing).append({"key": key, "label": label, "severity": sev})
    missing.sort(key=lambda m: SEV_RANK[m["severity"]])
    blockers = [m for m in missing if m["severity"] == "blocker"]
    score = round(100 * len(present) / len(CHECKS))
    return {
        "total_checks": len(CHECKS),
        "present": len(present),
        "coverage_pct": score,
        "missing": missing,
        "missing_blockers": [m["label"] for m in blockers],
        "pass": len(blockers) == 0,
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
        print(f"RFP 完整度：{res['present']}/{res['total_checks']} 章節 ({res['coverage_pct']}%)  "
              f"{'PASS' if res['pass'] else 'FAIL (有 Blocker 缺漏)'}")
        if res["missing"]:
            print("缺漏：")
            for m in res["missing"]:
                print(f"  [{m['severity'].upper()}] {m['label']}")
        else:
            print("所有必備章節關鍵字皆命中（仍須以 review-rubric.md 判定品質）。")
    sys.exit(0 if res["pass"] else 1)


if __name__ == "__main__":
    main()
