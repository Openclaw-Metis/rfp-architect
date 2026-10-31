#!/usr/bin/env python3
"""Run frozen deterministic accuracy cases against an rfp_lint module."""

from __future__ import annotations

import argparse
import importlib.util
import json
from pathlib import Path


BASE_DRAFT = """# 測試 RFP（{title}）
## 執行摘要
專案願景 summary
## 背景與目標
背景 目標 痛點
## 工作範疇
包含與不包含 工作說明
## 功能需求
必要 應有 加分 use case 功能需求
## 技術與非功能需求
非功能 效能 可用率 99.9 可擴充 可維護 整合架構
## 系統轉換
上線程序 技術移轉 平行測試
## 資通安全
資安 資通安全 security SSDLC
## 在地化
資料落地 境內 繁體中文 在地化
## 禁用清單
不得使用大陸地區廠牌；大陸地區人民不得參與；禁用清單
## 服務水準
SLA 服務水準 可用率 回應時間 罰則
## 商業模式與定價
{pricing}
{evaluation}
## 評選委員會
評選委員會 5 人以上 外聘 召集人 委員
評定方式：序位法。
總滿分 100 分，合格分數 70 分。
## 時程
時程 里程碑 等標期 截止
## 契約：智財
著作權 著作財產權 智財 授權
## 驗收
驗收 驗收標準 acceptance
## 保固
保固 維護
## 變更管理
變更管理 變更請求 書面核准
## 退場
退場 資料返還 移交 服務移轉
## 投標須知
投標須知 釋疑 提交 頁數 格式
"""


AWARD_LINE = "評定方式：序位法。\n"
PASSING_LINE = "總滿分 100 分，合格分數 70 分。\n"
COMMITTEE_LINE = "評選委員會 5 人以上 外聘 召集人 委員"
IP_LINE = "著作權 著作財產權 智財 授權"

# Each mode rewrites the shared draft the same way for baseline and candidate.
DOCUMENT_MODES = {
    "neutral": ((COMMITTEE_LINE, "內部審查小組"), ("## 評選委員會", "## 審查小組"), ("等標期", "報價期")),
    "ip_deferred": ((IP_LINE, "智財事項另行約定"),),
    "ip_after_award": ((IP_LINE, "著作權歸屬於決標後另議"),),
    "committee_three": ((COMMITTEE_LINE, "評選委員會由 3 人組成，外聘 召集人"),),
    "committee_three_zh": ((COMMITTEE_LINE, "評選委員會置委員三人，外聘專家學者一人，召集人"),),
    "committee_share": ((COMMITTEE_LINE, "評選委員會委員 7 人，其中外聘專家學者 2 人，召集人"),),
    "committee_two_of_nine": ((COMMITTEE_LINE, "評選委員會委員 9 人，外聘專家學者 2 人，召集人"),),
    "working_group": ((COMMITTEE_LINE, COMMITTEE_LINE + "\n工作小組 3 人協助評選作業"),),
    "no_award_method": ((AWARD_LINE, ""),),
    "no_passing_score": ((PASSING_LINE, ""),),
    "lowest_bid": ((AWARD_LINE, ""), (PASSING_LINE, "")),
}


def build_document(fixture: dict) -> str:
    text = BASE_DRAFT.format(**fixture)
    for old, new in DOCUMENT_MODES.get(fixture.get("document_mode"), ()):
        text = text.replace(old, new)
    if fixture.get("strip_headings"):
        text = text.replace("## ", "").replace("# ", "")
    return text


def load_linter(path: Path):
    spec = importlib.util.spec_from_file_location("rfp_lint_benchmark_target", path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load linter module: {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def evaluate_case(module, case: dict) -> dict:
    text = build_document(case["fixture"])
    actual = module.lint(text, track=case.get("track", "auto"))
    expected = case["expected"]
    checks = {
        "pass": actual["pass"] == expected["pass"],
    }
    if "effective_track" in expected:
        checks["effective_track"] = actual["effective_track"] == expected["effective_track"]

    actual_rules = {}
    for finding in actual["rule_findings"]:
        actual_rules.setdefault(finding["rule"], set()).add(finding["severity"])
    for rule, severity in expected.get("rule_severities", {}).items():
        checks[f"rule:{rule}:{severity}"] = severity in actual_rules.get(rule, set())
    for rule in expected.get("forbidden_rules", []):
        checks[f"forbidden_rule:{rule}"] = rule not in actual_rules

    return {
        "id": case["id"],
        "split": case["split"],
        "status": "PASS" if all(checks.values()) else "FAIL",
        "checks": checks,
        "actual": {
            "pass": actual["pass"],
            "effective_track": actual["effective_track"],
            "rules": [
                {"rule": finding["rule"], "severity": finding["severity"]}
                for finding in actual["rule_findings"]
            ],
        },
    }


def run(benchmark_path: Path, module_path: Path, split: str) -> dict:
    benchmark = json.loads(benchmark_path.read_text(encoding="utf-8"))
    module = load_linter(module_path)
    cases = [
        case for case in benchmark["cases"]
        if split == "all" or case["split"] == split
    ]
    results = [evaluate_case(module, case) for case in cases]
    passed = sum(result["status"] == "PASS" for result in results)
    return {
        "benchmark_id": benchmark["benchmark_id"],
        "benchmark_version": benchmark["version"],
        "benchmark_metadata": benchmark["metadata"],
        "split": split,
        "module": str(module_path),
        "grader_version": getattr(module, "GRADER_VERSION", "unknown"),
        "status": "PASS" if passed == len(results) else "FAIL",
        "pass_rate": passed / len(results) if results else 0.0,
        "passed": passed,
        "total": len(results),
        "results": results,
    }


def main() -> int:
    root = Path(__file__).resolve().parent.parent
    parser = argparse.ArgumentParser(description="Run frozen rfp_lint accuracy cases")
    parser.add_argument(
        "--benchmark",
        type=Path,
        default=root / "assets" / "evals" / "linter_benchmark.json",
    )
    parser.add_argument("--module", type=Path, default=root / "scripts" / "rfp_lint.py")
    parser.add_argument("--split", choices=["development", "held_out", "all"], default="all")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()
    result = run(args.benchmark.resolve(), args.module.resolve(), args.split)
    if args.json:
        print(json.dumps(result, ensure_ascii=False, indent=2))
    else:
        print(
            f"linter benchmark ({result['split']}): {result['status']} "
            f"{result['passed']}/{result['total']} ({result['pass_rate']:.0%})"
        )
        for item in result["results"]:
            if item["status"] != "PASS":
                print(f"- FAIL {item['id']}: {item['checks']}")
    return 0 if result["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
