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
   20%–50% band, simulation weight over 20%, weights not summing to 100%, and the
   government items the regulations require the tender documents to state.
   V9 scans every Markdown table in the document instead of one heading-bound
   section, so a table cannot be skipped because of how its heading is worded. A
   table counts as an evaluation table by its heading chain, its header, or a
   priced row; SLA, payment and grading-scale tables stay out. Prose weights are
   read only when no table exists, and only next to a weight word, so formulas
   and abnormally-low-bid sentences are not read as weights.
3) Context-aware signals (V6, refined in V8 and V9):
   - Out-of-scope negation: a keyword that appears only inside a「不處理 / 不適用 /
     另行約定」context is surfaced as an ADVISORY warning (never a hard fail),
     because a keyword linter cannot safely tell prescriptive prohibitions (e.g.
     「不得使用大陸製品」, which is a legitimate clause) from genuine absence. The
     rubric makes the call.
   - Track-specific severity: 評選委員會 / 退場返還 / 禁用清單 / 資料落地 carry far
     more weight in a government 最有利標 / 資訊服務 case (and when 個資 / 雲端 /
     關鍵系統 are in play) than in a generic enterprise RFP, so their MISSING
     severity is escalated accordingly.
   - An explicit exclusion of 政府採購法 selects the enterprise track, except when
     it names a single article. Fixed-price treatment needs a declaration: a negated
     mention or a note explaining the exception is not one.

Used by both modes:
- write mode: self-check a generated draft before returning it.
- review mode: a mechanical first pass before the rubric-based human judgement.

Usage:
    python3 scripts/rfp_lint.py <file.md|.txt|.docx|.odt> [--json] [--track auto|government|enterprise] [--fixed-price]
    cat rfp.md | python3 scripts/rfp_lint.py - [--json] [--track auto|government|enterprise] [--fixed-price]

Exit code: 0 if clean or only advisory warnings; 1 if a Blocker section is missing,
a placeholder remains (draft not finished), or a clear rule violation fires; 2 if
the input could not be read, in which case nothing was checked.
"""
import argparse
import json
import re
import sys

GRADER_VERSION = "rfp_lint-9"

# ---- Layer 1: completeness (key, label, base_severity, [keywords; any match = present]) ----
CHECKS = [
    ("summary",    "執行摘要 / 專案願景",      "minor",   ["執行摘要", "專案願景", "願景", "summary", "vision"]),
    ("background", "業務背景與目標",            "major",   ["背景", "目標", "痛點", "現狀", "objective", "background"]),
    ("scope",      "工作範疇 (含/不含)",        "major",   ["範疇", "範圍", "scope of work", "包含", "不包含", "工作說明"]),
    ("functional", "功能需求 (分級)",           "blocker", ["功能需求", "功能規格", "功能項目", "功能說明", "系統功能", "需求規格", "服務項目", "functional requirement", "use case"]),
    ("nonfunc",    "技術/非功能需求",           "major",   ["非功能", "效能", "可用率", "可擴充", "可維護", "整合架構", "non-functional", "architecture"]),
    ("migration",  "系統轉換 / 技術移轉",       "minor",   ["系統轉換", "技術移轉", "新舊系統", "平行測試", "上線計畫", "上線程序", "system transition"]),
    ("security",   "資通安全分級",              "blocker", ["資安", "資通安全", "防護需求分級", "iso 27001", "ssdlc", "security"]),
    ("locale",     "資料落地 / 繁中在地化",     "major",   ["資料落地", "境內", "繁體中文", "在地化", "localization", "data residency"]),
    ("banlist",    "禁用產品/人員條款",         "minor",   ["大陸", "陸籍", "陸資", "禁用", "危害國家資通安全"]),
    ("sla",        "服務水準 / SLA",            "major",   ["sla", "服務水準", "可用率", "回應時間", "罰則"]),
    ("pricing",    "商業模式與定價/計費方式",   "minor",   ["定價", "報價", "付費", "預算", "總包價", "單價計算", "按月計酬", "按時計酬", "服務成本加公費", "pricing", "budget"]),
    ("evaluation", "評選標準與配分",            "blocker", ["評選", "配分", "權重", "最有利標", "序位法", "評分", "evaluation", "scoring"]),
    ("committee",  "評選委員會 (政府採購)",     "minor",   ["評選委員", "評審委員", "外聘", "召集人", "專家學者"]),
    ("timeline",   "時程 / 里程碑 / 等標期",    "major",   ["時程", "里程碑", "等標期", "截止", "milestone", "timeline"]),
    ("ip",         "智財/著作權歸屬",           "blocker", ["著作", "智財", "智慧財產", "intellectual property", "copyright"]),
    ("acceptance", "驗收標準",                  "blocker", ["驗收", "acceptance", "驗收標準"]),
    ("warranty",   "保固 / 維護",               "minor",   ["保固", "維護", "保固保證金", "warranty", "maintenance"]),
    ("change_mgmt","變更管理 / 變更請求流程",   "major",   ["變更管理", "變更請求", "變更控制", "變更流程", "change request", "change control", "change management"]),
    ("exit",       "退場 / 資料返還 / 移交",    "minor",   ["退場", "資料返還", "移交", "交接", "服務移轉", "退場計畫", "transition-out", "exit plan"]),
    ("submission", "投標須知 / 釋疑",           "major",   ["投標須知", "釋疑", "提交", "頁數", "submission", "格式"]),
]

SEV_RANK = {"blocker": 0, "major": 1, "minor": 2}

# placeholders that must be gone in a finished draft. "待確認" is intentionally
# allowed because SKILL.md permits a final explicit confirmation list.
_PLACEHOLDERS = ["【填入", "【__", "__%", "待補", "TODO", "TBD", "xxx%", "XX%"]
# An unresolved choice such as【普／中／高】is left over from the template or clause library.
_CHOICE_BRACKET = re.compile(r"【[^】\n]{1,40}[／/][^】\n]{0,40}】")
# Annexed forms legitimately keep these, so they advise instead of failing the draft.
_SOFT_PLACEHOLDER = re.compile(r"○○|〇〇|＿＿|_{4,}|【\d[^】\n]{0,12}】")
_MIN_DOCUMENT_CHARS = 300

# integer percentage, excluding decimals like 99.9% (lookbehind rejects a preceding digit or dot)
_INT_PCT = re.compile(r"(?<![\d.])(\d{1,3})\s*%(?!\.\d)")
_NUMBER = re.compile(r"(?<![\d.])(\d{1,3}(?:\.\d+)?)(?![\d.])")

# Official documents write weights as 百分之六十 or ６０％, which every rule below must read.
_FULLWIDTH_DIGITS = str.maketrans("０１２３４５６７８９％．", "0123456789%.")
_CN_NUMERAL = "零〇一二兩三四五六七八九十百"
_CN_PERCENT = re.compile(rf"百分之\s*(\d+(?:\.\d+)?|[{_CN_NUMERAL}]+)")

# Out-of-scope negation: a section TOPIC declared absent / not handled. Deliberately
# excludes 「不包含」 (a legitimate scope-exclusion keyword) and prescriptive 不得/禁止
# prohibitions (guarded separately) to avoid flagging valid clauses.
_OUT_OF_SCOPE = re.compile(r"(不處理|未處理|不涉及|未涉及|不適用|無需求|無此需求|無相關需求|未規劃|尚未規劃|從缺|無須處理)")
_PROHIBITION = re.compile(r"(不得|禁止|不可|嚴禁)")
# Deferral: 「另行約定」leaves the clause as undecided as declaring it out of scope.
_DEFERRED = re.compile(r"另行(?:約定|協議|議定|討論|商議|訂定)|另案(?:處理|約定)|另議|(?:決標|得標|簽約)後[^,，。；;\n]{0,4}(?:約定|協議|議定|討論|確定)")

# Markers that raise the stakes for data-return / residency / committee clauses.
_SENSITIVE_MARKERS = ("個資", "個人資料", "personal data", "關鍵基礎設施",
                      "關鍵資訊基礎設施", "關鍵系統", "雲端", "cloud")
# Most-advantageous-tender / information-service procurement context.
_MAT_MARKERS = ("最有利標", "資訊服務", "機關委託資訊服務", "評選委員會", "公開評選")
# Eval-table row labels that are thresholds / subtotals, NOT scoring weights; they
# must be excluded from the weight-sum check so they do not inflate the total.
_NON_WEIGHT_ROW = ("門檻", "及格", "合格", "底標", "底價", "總分", "滿分", "合計", "小計", "總計")
_ITEM_HEADER = ("評選項目", "評比項目", "評審項目", "評分項目", "項目", "內容", "名稱", "面向", "criterion", "criteria", "item")
_SEQUENCE_HEADER = ("項次", "序號", "編號", "no.")
_WEIGHT_HEADER = ("權重", "配分", "比重", "占比", "佔比", "占分", "佔分", "分數", "百分比", "比例", "weight", "score", "points")
_PRICE_LABEL = ("價格", "標價", "報價", "price")
_PRESENTATION_LABEL = ("簡報", "現場詢答", "詢答", "presentation", "briefing", "q&a")
# A heading or header with these words marks a table as an evaluation table.
_EVAL_TOPIC = ("評選", "評分", "評審", "評比", "配分", "權重", "evaluation", "scoring")
_EVAL_HEADER = ("評選", "評比", "評審", "評分項目", "配分", "criteria", "criterion")
# 等第 / 級距 tables convert grades to scores; their values are not weights.
_SCALE_HEADER = ("等第", "等級", "級距", "區間", "評語", "序位", "名次")

_PLAIN_HEADINGS = (
    (1, re.compile(r"^\s*(?:\*\*)?第[一二三四五六七八九十百\d]+[章節篇]")),
    (2, re.compile(r"^\s*(?:\*\*)?[一二三四五六七八九十]+[、.]")),
    (3, re.compile(r"^\s*(?:\*\*)?[(（][一二三四五六七八九十]+[)）]")),
)
_MAX_PLAIN_HEADING_CHARS = 40
# PDF extraction splits a long table at page breaks; pieces this close are one table.
_PAGE_SPLIT_GAP = 8

_WEIGHT_WORD = r"(?:配分|權重|比率|比重|占比|佔比|所占|所佔|占|佔|為|weight)"
_PROSE_GAP = r"[^%\d\n,，。；;]{0,8}?"
# Sentences stating the legal band or a limit are not this document's weights.
_PROSE_RULE_TEXT = re.compile(r"不得|落在|區間|法定|上限|下限|得低於|介於|以上|以下")
_GENERIC_WEIGHT = re.compile(r"(?:配分|權重|占|佔|比率)[^。\n]{0,10}?\d{1,3}\s*(?:%|分)|\S{1,10}[:：\s]\d{1,3}\s*(?:%|分)(?![\d/])")

_ENTERPRISE_EXCLUSION = re.compile(
    r"(?:不適用|不受)(?:本?政府)?採購法(?!\s*第)|非政府採購|not subject to (?:the )?government procurement",
    re.IGNORECASE,
)
_FIXED_PRICE = re.compile(r"固定(?:價格|費用|服務費用|費率)|fixed[- ](?:price|fee|rate)", re.IGNORECASE)
_FIXED_NEGATION = re.compile(r"(?:非|不採|不以|未採|未訂明?|無|不屬|not)\s*(?:本案)?\s*$", re.IGNORECASE)
_FIXED_EXPLANATION = re.compile(r"得低於|例外|除外|不在此限|unless", re.IGNORECASE)

_AWARD_METHODS = ("總評分法", "評分單價法", "序位法", "序位評比", "總評分")
_PASSING_MARKERS = ("合格分數", "及格分數", "合格門檻", "及格門檻", "合格標準", "及格標準", "及格分", "合格分")
# 不合格 alone also describes 資格 or 標價; it counts only beside a score.
_PASSING_SENTENCE = re.compile(r"未達\s*\d{1,3}\s*分|(?:總評分|平均|總分|序位評比)[^。；;\n]{0,12}不合格|不合格[^。；;\n]{0,12}(?:總評分|平均)")

_COUNT = rf"(\d{{1,2}}|[{_CN_NUMERAL}]{{1,3}})\s*(?:人|位|名)"
_COMMITTEE_TOTAL = re.compile(rf"評選委員(?:會)?[^。；;\n]{{0,14}}?{_COUNT}")
_COMMITTEE_EXTERNAL = re.compile(rf"(?:外聘|專家、?學者)[^。；;\n]{{0,10}}?{_COUNT}")
_ABSENCE = re.compile(r"(?:未出席|未到場|未參加|缺席)[^。；;\n]{0,10}簡報|簡報[^。；;\n]{0,10}(?:未出席|未到場|未參加|缺席)")
_ABSENCE_PENALTY = re.compile(r"不予評選|不予評比|喪失|取消[^。；;\n]{0,6}資格|(?:視同|視為)放棄(?:投標|評選|資格|本案)|棄權|投標無效|不得參與")
# Scoring the presentation item zero is lawful; only excluding the bidder is not.
_ABSENCE_ZERO = re.compile(r"0\s*分|零分|不予計分|不給分")
# 審議規則 quorum sentences and the 工作小組 use the same words with other headcounts.
_COMMITTEE_OTHER_BODY = re.compile(r"工作小組|出席|會議|開會|列席|初審")


def _cn_to_int(value):
    """Convert 六十 / 二十五 / 一百 style numerals; plain digits pass through."""
    if value.isdigit():
        return int(value)
    digits = {"零": 0, "〇": 0, "一": 1, "二": 2, "兩": 2, "三": 3, "四": 4,
              "五": 5, "六": 6, "七": 7, "八": 8, "九": 9}
    total = current = 0
    for ch in value:
        if ch in digits:
            current = digits[ch]
        elif ch == "十":
            total += (current or 1) * 10
            current = 0
        elif ch == "百":
            total += (current or 1) * 100
            current = 0
    return total + current


def normalize_text(text):
    """Fold full-width digits and 百分之N to ASCII; line numbers stay the same."""
    def percent(match):
        value = match.group(1)
        return f"{value}%" if value[0].isdigit() else f"{_cn_to_int(value)}%"
    return _CN_PERCENT.sub(percent, text.translate(_FULLWIDTH_DIGITS))


def _markdown_level(line):
    match = re.match(r"^\s*(#{1,6})\s+", line)
    return len(match.group(1)) if match else None


def _plain_level(line):
    """Headings of text extracted from PDF or unstyled documents carry no Markdown marker."""
    stripped = line.strip()
    if len(stripped) > _MAX_PLAIN_HEADING_CHARS or "|" in stripped:
        return None
    for level, pattern in _PLAIN_HEADINGS:
        if pattern.match(stripped):
            return level
    return None


def _heading_context(lines):
    """For each line: the nearest heading, and the chain of headings above it.

    Numbered paragraphs inside a Markdown section are often 一、二、 lists, so the
    plain patterns apply only when the document has no Markdown headings at all.
    """
    use_markdown = any(_markdown_level(ln) for ln in lines)
    nearest, chains = [], []
    stack = []
    for ln in lines:
        level = _markdown_level(ln) if use_markdown else _plain_level(ln)
        if level:
            stack = [item for item in stack if item[0] < level]
            stack.append((level, ln.strip().lstrip("#* ").rstrip("* ")))
        nearest.append(stack[-1][1] if stack else "")
        chains.append(" / ".join(item[1] for item in stack))
    return nearest, chains


def _find_first(lines, head_map, keywords):
    """Return (line_no_1based, matched_keyword, heading) for the first keyword hit."""
    for i, ln in enumerate(lines):
        low = ln.lower()
        for kw in keywords:
            if kw.lower() in low:
                return (i + 1, kw, head_map[i])
    return None


def _first_line(lines, predicate):
    return next((i + 1 for i, ln in enumerate(lines) if predicate(ln)), None)


def _negation_hit(lines, keywords):
    """If a keyword appears on a line that declares the topic out-of-scope or defers it
    (and is not a prescriptive 不得/禁止 prohibition), return (line_no_1based, excerpt)."""
    for i, ln in enumerate(lines):
        low = ln.lower()
        if not any(kw.lower() in low for kw in keywords):
            continue
        if (_OUT_OF_SCOPE.search(ln) or _DEFERRED.search(ln)) and not _PROHIBITION.search(ln):
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


def _table_cells(line):
    if "|" not in line:
        return []
    return [cell.strip() for cell in line.strip().strip("|").split("|")]


def _separator_row(cells):
    return bool(cells) and all(re.fullmatch(r":?-{3,}:?", cell.replace(" ", "")) for cell in cells)


def _weight_value(cell):
    """Read one declared table weight, never percentages from description cells."""
    match = _INT_PCT.search(cell)
    if match:
        return float(match.group(1))
    match = _NUMBER.search(cell)
    return float(match.group(1)) if match else None


def _column_of(lowered, markers, skip=None):
    return next(
        (idx for idx, cell in enumerate(lowered)
         if idx != skip and any(marker in cell for marker in markers)),
        None,
    )


def _label_column(lowered, weight_idx):
    idx = _column_of(lowered, _ITEM_HEADER, skip=weight_idx)
    if idx is not None:
        return idx
    return next(
        (i for i, cell in enumerate(lowered)
         if i != weight_idx and not any(marker in cell for marker in _SEQUENCE_HEADER)),
        0,
    )


def _is_evaluation_table(lowered, label_idx, weight_idx, chain, rows):
    if any(marker in lowered[idx] for idx in (label_idx, weight_idx) for marker in _SCALE_HEADER):
        return False
    low_chain = chain.lower()
    if any(topic in low_chain for topic in _EVAL_TOPIC):
        return True
    if any(marker in cell for cell in lowered for marker in _EVAL_HEADER):
        return True
    return any(marker in row["label"].lower() for row in rows for marker in _PRICE_LABEL)


def _weight_rows(table):
    return [row for row in table if not any(marker in row["label"] for marker in _NON_WEIGHT_ROW)]


def _table_end(lines, start):
    end = start
    while end < len(lines) and _table_cells(lines[end]):
        end += 1
    return end


def _rows_from(lines, numbers, label_idx, weight_idx):
    rows = []
    label = ""
    for number in numbers:
        cells = _table_cells(lines[number])
        if len(cells) <= max(label_idx, weight_idx):
            continue
        # A vertically merged item cell repeats its label on continuation rows.
        label = cells[label_idx] or label
        value = _weight_value(cells[weight_idx])
        if value is not None:
            rows.append({"label": label, "value": value, "line": number + 1})
    return rows


def _is_page_split(last, header, weight_idx, line):
    """A nearby piece with the same columns continues a table still short of 100."""
    if last is None or len(header) != len(last["header"]) or line - last["end"] > _PAGE_SPLIT_GAP:
        return False
    if weight_idx is not None and header != last["header"]:
        return False
    return not 98 <= sum(row["value"] for row in _weight_rows(last["rows"])) <= 102


def _eval_tables(lines, chains):
    """Parse every Markdown table, keeping those that hold evaluation weights."""
    tables = []
    last = None
    i = 0
    while i + 1 < len(lines):
        header = _table_cells(lines[i])
        separator = _table_cells(lines[i + 1])
        if not header or not _separator_row(separator) or len(header) != len(separator):
            i += 1
            continue
        end = _table_end(lines, i + 2)
        body = list(range(i + 2, end))
        lowered = [cell.lower() for cell in header]
        weight_idx = _column_of(lowered, _WEIGHT_HEADER)
        if _is_page_split(last, header, weight_idx, i):
            # A piece without a repeated header has a data row in the header position.
            numbers = body if header == last["header"] else [i] + body
            last["rows"].extend(_rows_from(lines, numbers, last["label_idx"], last["weight_idx"]))
            last["end"] = end
        elif weight_idx is not None:
            label_idx = _label_column(lowered, weight_idx)
            rows = _rows_from(lines, body, label_idx, weight_idx)
            if rows and _is_evaluation_table(lowered, label_idx, weight_idx, chains[i], rows):
                tables.append(rows)
                last = {"header": header, "label_idx": label_idx, "weight_idx": weight_idx,
                        "rows": rows, "end": end}
        i = max(end, i + 1)
    return tables


def _labelled_shares(tables, keywords):
    """Per table, the summed share of rows carrying a label, so sub-items add up."""
    shares = []
    for table in tables:
        rows = [row for row in _weight_rows(table)
                if any(keyword.lower() in row["label"].lower() for keyword in keywords)]
        if rows:
            shares.append((sum(row["value"] for row in rows), rows[0]["line"]))
    return shares


def _prose_pattern(labels):
    label = "|".join(re.escape(item) for item in labels)
    return re.compile(
        rf"(?:{label})(?:項目|部分|之)?{_PROSE_GAP}{_WEIGHT_WORD}{_PROSE_GAP}(\d{{1,3}})\s*(?:%|分)"
        rf"|(?:{label})\s*[:：(（]?\s*(\d{{1,3}})\s*(?:%|分)(?![\d/])",
        re.IGNORECASE,
    )


def _prose_shares(lines, line_numbers, labels):
    pattern = _prose_pattern(labels)
    shares = []
    for i in line_numbers:
        for match in pattern.finditer(lines[i]):
            if not _PROSE_RULE_TEXT.search(match.group(0)):
                shares.append((float(match.group(1) or match.group(2)), i + 1))
    return shares


def _eval_line_numbers(lines, chains):
    """Lines under an evaluation heading, or every line when no such heading exists."""
    numbers = [i for i, chain in enumerate(chains)
               if any(topic in chain.lower() for topic in _EVAL_TOPIC)]
    return numbers or list(range(len(lines)))


def _display_number(value):
    return int(value) if float(value).is_integer() else value


def _detect_track(text, requested):
    """Infer whether Taiwan government procurement rules should apply."""
    if requested != "auto":
        return requested
    government_markers = (
        "政府採購", "政府機關", "公法人", "受採購法", "採購法", "最有利標",
        "等標期", "評選委員會", "採購評選委員會", "機關委託資訊服務",
        "招標機關", "本機關", "公開評選", "限制性招標", "政府電子採購網",
    )
    enterprise_markers = ("一般企業", "企業委外", "公司採購", "民間企業", "本公司", "private enterprise")
    if _ENTERPRISE_EXCLUSION.search(text):
        return "enterprise"
    if any(k in text for k in government_markers):
        return "government"
    low = text.lower()
    if any(k.lower() in low for k in enterprise_markers):
        return "enterprise"
    return "unknown"


def _detect_fixed_price(text, forced):
    """Accept only a declaration; 非固定價格 and 固定價格案得低於 20% do not declare it."""
    if forced:
        return True
    for sentence in re.split(r"[。；;\n]", text):
        for match in _FIXED_PRICE.finditer(sentence):
            if _FIXED_NEGATION.search(sentence[:match.start()]):
                continue
            if _FIXED_EXPLANATION.search(sentence):
                continue
            return True
    return False


def _placeholder_findings(lines, low):
    findings = []
    hits = sorted({p for p in _PLACEHOLDERS if p.lower() in low})
    choices = sorted({m.group(0) for ln in lines for m in _CHOICE_BRACKET.finditer(ln)})
    if hits or choices:
        line = _first_line(lines, lambda ln: _CHOICE_BRACKET.search(ln)
                           or any(p.lower() in ln.lower() for p in hits))
        findings.append({
            "rule": "placeholder", "severity": "blocker", "line": line,
            "message": f"草稿仍含未填占位符 {hits + choices}；write 模式不得宣稱完成（這是模板而非完稿）。"
        })
    soft = sorted({m.group(0) for ln in lines for m in _SOFT_PLACEHOLDER.finditer(ln)})
    if soft:
        findings.append({
            "rule": "soft_placeholder", "severity": "warning",
            "line": _first_line(lines, _SOFT_PLACEHOLDER.search),
            "message": f"含疑似未定內容 {soft[:6]}；確認是附件範本或尚待填寫。"
        })
    return findings


def _committee_findings(lines):
    findings = []
    for number, ln in enumerate(lines, 1):
        total = _COMMITTEE_TOTAL.search(ln)
        if not total or _COMMITTEE_OTHER_BODY.search(ln):
            continue
        size = _cn_to_int(total.group(1))
        if size < 5:
            findings.append({
                "rule": "committee_size", "severity": "blocker", "line": number,
                "message": f"評選委員會 {size} 人，少於《政府採購法》§94 與《採購評選委員會組織準則》§4 之 5 人下限。"
            })
            break
        external = _COMMITTEE_EXTERNAL.search(ln)
        if external and _cn_to_int(external.group(1)) * 3 < size:
            count = _cn_to_int(external.group(1))
            findings.append({
                "rule": "committee_size", "severity": "blocker", "line": number,
                "message": f"專家學者 {count} 人占委員 {size} 人，低於《採購評選委員會組織準則》§4 之 1/3 下限。"
            })
            break
    return findings


def _statutory_findings(lines, text, eval_lines, tables, weighted_prose):
    """Items the regulations require a most-advantageous-tender document to state."""
    findings = []
    has_weights = bool(tables or weighted_prose) or sum(
        len(_GENERIC_WEIGHT.findall(lines[i])) for i in eval_lines
        if not any(marker in lines[i] for marker in _NON_WEIGHT_ROW)) >= 2
    if not has_weights:
        findings.append({
            "rule": "evaluation_weights", "severity": "blocker",
            "message": "未載明評選項目之配分或權重（《最有利標評選辦法》§16、§17、§18）。"
        })
    if not any(method in text for method in _AWARD_METHODS):
        findings.append({
            "rule": "award_method", "severity": "major",
            "message": "未載明評定最有利標之方式：總評分法、評分單價法或序位法（《最有利標評選辦法》§4、§11）。"
        })
    if not any(marker in text for marker in _PASSING_MARKERS) and not _PASSING_SENTENCE.search(text):
        findings.append({
            "rule": "passing_score", "severity": "major",
            "message": "未載明合格分數或合格判定（《最有利標評選辦法》§16、§17 要求招標文件載明）。"
        })
    return findings


def rule_checks(text, track="auto", fixed_price=False):
    """Layer 2: regex compliance rules. Returns list of findings."""
    text = normalize_text(text)
    lines = text.splitlines()
    findings = _placeholder_findings(lines, text.lower())
    effective_track = _detect_track(text, track)
    if effective_track == "unknown":
        findings.append({
            "rule": "track_unknown", "severity": "warning",
            "message": "無法判定採購軌道，政府採購法定規則未套用；請以 --track government 或 enterprise 重跑。"
        })
    if len(text.strip()) < _MIN_DOCUMENT_CHARS:
        findings.append({
            "rule": "input_too_short", "severity": "warning",
            "message": "文字量過少，疑似掃描檔或擷取失敗；本次結果不代表全文。"
        })

    _, chains = _heading_context(lines)
    tables = _eval_tables(lines, chains)
    eval_lines = _eval_line_numbers(lines, chains)

    # Taiwan government procurement compliance rules.
    if effective_track == "government":
        # Tables are authoritative; prose is read only when the document has none.
        price_shares = _labelled_shares(tables, _PRICE_LABEL)
        presentation_shares = _labelled_shares(tables, _PRESENTATION_LABEL)
        if not tables:
            price_shares = _prose_shares(lines, eval_lines, _PRICE_LABEL)
            presentation_shares = _prose_shares(lines, eval_lines, _PRESENTATION_LABEL)

        # presentation_weight_rule — 簡報/現場詢答 weight must be ≤20% (no statutory exception).
        over = [share for share in presentation_shares if share[0] > 20]
        if over:
            value, line = max(over)
            findings.append({
                "rule": "presentation_weight", "severity": "major", "line": line,
                "message": f"簡報 / 詢答配分 {_display_number(value)}% 逾《最有利標評選辦法》§10 之 20% 上限。"
            })
        # price_weight_rule — price 20%–50% unless fixed-price案 only for the lower bound.
        is_fixed_price = _detect_fixed_price(text, fixed_price)
        if price_shares and max(price_shares)[0] > 50:
            value, line = max(price_shares)
            findings.append({
                "rule": "price_weight", "severity": "blocker", "line": line,
                "message": f"價格配分 {_display_number(value)}% 逾《最有利標評選辦法》§16/§17 之 50% 上限。"
            })
        elif price_shares and min(price_shares)[0] < 20:
            value, line = min(price_shares)
            lo = _display_number(value)
            if is_fixed_price:
                findings.append({
                    "rule": "price_weight", "severity": "info", "line": line,
                    "message": f"固定價格給付案價格配分 {lo}% 低於 20%；此為固定價格例外，仍應於招標文件明載固定價格給付。"
                })
            else:
                findings.append({
                    "rule": "price_weight", "severity": "blocker", "line": line,
                    "message": f"非固定價格案價格配分 {lo}% 低於《最有利標評選辦法》§16/§17 之 20% 下限。"
                })

        findings.extend(_committee_findings(lines))
        absence = _first_line(lines, lambda ln: _ABSENCE.search(ln) and _ABSENCE_PENALTY.search(ln)
                              and not _ABSENCE_ZERO.search(ln))
        if absence:
            findings.append({
                "rule": "presentation_absence", "severity": "major", "line": absence,
                "message": "未出席簡報不影響投標文件有效性（《最有利標評選辦法》§10 第 4 項），不得據以排除廠商；簡報項目可不給分。"
            })
        scored_tender = any(marker in text for marker in _MAT_MARKERS)
        lowest_bid = "最低標" in text and "最有利標" not in text and "公開評選" not in text
        if scored_tender and not lowest_bid:
            weighted_prose = price_shares or presentation_shares
            findings.extend(_statutory_findings(lines, text, eval_lines, tables, weighted_prose))

    # weight_sum_rule — sum only the declared weight column, never formulas or notes.
    for table in tables:
        rows = _weight_rows(table)
        if len(rows) < 2:
            continue
        total = sum(row["value"] for row in rows)
        if not (98 <= total <= 102):
            findings.append({
                "rule": "weight_sum", "severity": "major", "line": rows[0]["line"],
                "message": f"評選配分合計約 {_display_number(total)}%（偵測 {len(rows)} 項表格配分），應修正為 100%。"
            })

    return findings


def lint(text, track="auto", fixed_price=False):
    text = normalize_text(text)
    lines = text.splitlines()
    low = text.lower()
    eff_track = _detect_track(text, track)
    sensitive = any(m.lower() in low for m in _SENSITIVE_MARKERS)
    mat_context = any(m in text for m in _MAT_MARKERS)
    head_map, _ = _heading_context(lines)

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
            "message": f"『{w['label']}』關鍵字出現在疑似『不處理 / 不適用 / 另行約定』語境（第 {w['line']} 行：{w['evidence']}）；命中不代表章節具備，請人工複核。"
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
        "pending_confirmations": sum("待確認" in ln for ln in lines),
        "effective_track": eff_track,
        "sensitive_context": sensitive,
        "grader_version": GRADER_VERSION,
        "pass": ok,
    }


def main():
    # Imported here so that loading this file as a module needs nothing beside it.
    from rfp_extract import InputError, read_document

    parser = argparse.ArgumentParser(description="Lint an outsourced software/system RFP draft.")
    parser.add_argument("src", help="RFP file path (.md, .txt, .docx, .odt), or '-' for stdin")
    parser.add_argument("--json", action="store_true", help="emit JSON")
    parser.add_argument("--track", choices=["auto", "government", "enterprise"], default="auto",
                        help="apply Taiwan government procurement rules, enterprise rules, or infer from text")
    parser.add_argument("--fixed-price", action="store_true",
                        help="treat the RFP as a fixed-price/fixed-fee government procurement case")
    ns = parser.parse_args()
    # A zh-TW Windows console defaults to cp950, which cannot print every character used here.
    sys.stdout.reconfigure(encoding="utf-8")
    try:
        text, source_format = read_document(ns.src)
    except InputError as exc:
        if ns.json:
            print(json.dumps({"pass": False, "error": str(exc), "grader_version": GRADER_VERSION},
                             ensure_ascii=False, indent=2))
        else:
            print(f"無法讀取輸入，未執行任何檢查：{exc}")
        sys.exit(2)
    res = lint(text, track=ns.track, fixed_price=ns.fixed_price)
    res["source_format"] = source_format
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
        if res["pending_confirmations"]:
            print(f"待確認：{res['pending_confirmations']} 處")
        if res["missing"]:
            print("章節缺漏（嚴重度已依採購軌道 / 敏感度調整）：")
            for m in res["missing"]:
                print(f"  [{m['severity'].upper()}] {m['label']}")
        if res["rule_findings"]:
            print("規則檢查（合規風險）：")
            for r in res["rule_findings"]:
                where = f"第 {r['line']} 行 " if r.get("line") else ""
                print(f"  [{r['severity'].upper()}] {where}{r['message']}")
        if not res["missing"] and not res["rule_findings"]:
            print("章節完整、規則檢查無異常（仍須以 review-rubric.md 判定品質）。")
    sys.exit(0 if res["pass"] else 1)


if __name__ == "__main__":
    main()
