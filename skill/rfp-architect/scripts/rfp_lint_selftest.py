#!/usr/bin/env python3
"""Regression tests for rfp_lint.py high-risk rules."""

from rfp_lint import lint


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


def assert_case(name: str, text: str, expected_pass: bool, **kwargs):
    res = lint(text, **kwargs)
    if res["pass"] != expected_pass:
        raise AssertionError(f"{name}: expected pass={expected_pass}, got {res}")


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

    assert_case("clean government", draft("政府採購 報價 總包價", clean_table), True, track="government")
    assert_case("government price over 50", draft("政府採購 報價 總包價", price_over_table), False, track="government")
    assert_case("government price under 20 non-fixed", draft("政府採購 報價 總包價", fixed_low_table), False, track="government")
    assert_case("government fixed price under 20", draft("政府採購 固定價格給付", fixed_low_table), True, track="government")
    assert_case("bad weight sum", draft("政府採購 報價 總包價", bad_sum_table), False, track="government")
    assert_case("presentation over 20", draft("政府採購 報價 總包價", presentation_over_table), False, track="government")
    assert_case("enterprise track skips gov price rule", draft("一般企業 報價", price_over_table), True, track="enterprise")
    assert_case("placeholder blocks", draft("政府採購 報價 【填入】", clean_table), False, track="government")
    print("rfp_lint_selftest: PASS")


if __name__ == "__main__":
    main()
