#!/usr/bin/env python3
"""
rfp_extract.py — read an RFP file as text using only the Python standard library.

Real RFPs arrive as .docx or .odt (the ODF format Taiwan agencies publish) far more
often than as Markdown. This module turns both into Markdown, keeping tables as pipe
tables so rfp_lint.py can read evaluation weights, and decodes plain text in UTF-8,
UTF-16 or Big5 (cp950). PDF and legacy binary formats need a real parser, so they are
refused with an instruction instead of being guessed at.

Input files are untrusted: archive members are read in memory with a size cap, nothing
is written to disk, and any XML carrying a DOCTYPE is rejected before parsing.

Usage:
    python3 scripts/rfp_extract.py <file> > extracted.md
"""
import re
import sys
import xml.etree.ElementTree as ET
import zipfile
from pathlib import Path

MAX_PART_BYTES = 64 * 1024 * 1024
MAX_REPEATED_CELLS = 64
MIN_MANGLED_CHARS = 40
MAX_QUESTION_MARK_SHARE = 0.3
WORD = "{http://schemas.openxmlformats.org/wordprocessingml/2006/main}"
ODF_TEXT = "{urn:oasis:names:tc:opendocument:xmlns:text:1.0}"
ODF_TABLE = "{urn:oasis:names:tc:opendocument:xmlns:table:1.0}"
ODF_OFFICE = "{urn:oasis:names:tc:opendocument:xmlns:office:1.0}"

REFUSED_SUFFIXES = {
    ".pdf": "PDF 需先取出文字：用 host 的 PDF 讀取能力轉成文字後以 stdin（-）傳入；掃描檔須先 OCR。",
    ".doc": "舊版 .doc 無法直接解析：請另存為 .docx 或 .odt。",
    ".rtf": "RTF 無法直接解析：請另存為 .docx、.odt 或純文字。",
    ".xls": "試算表不是 RFP 全文：請提供招標文件本體。",
    ".xlsx": "試算表不是 RFP 全文：請提供招標文件本體。",
}


class InputError(Exception):
    """The input cannot be read as an RFP; the message says what to do instead."""


def decode_bytes(data):
    """Decode plain text, trying the encodings seen in Taiwan government documents."""
    if data.startswith((b"\xff\xfe", b"\xfe\xff")):
        return data.decode("utf-16")
    for encoding in ("utf-8-sig", "cp950"):
        try:
            return data.decode(encoding)
        except UnicodeDecodeError:
            continue
    raise InputError("無法辨識文字編碼（已試 UTF-8、UTF-16、Big5）：請另存為 UTF-8。")


def decode_stdin(data):
    """Decode piped text, refusing what a console has already turned into question marks.

    Windows PowerShell 5.1 pipes through ASCII by default, so every CJK character arrives
    as '?'. Linting that would report sections missing from a document that has them.
    """
    text = decode_bytes(data)
    body = re.sub(r"\s", "", text)
    if len(body) >= MIN_MANGLED_CHARS and body.count("?") / len(body) > MAX_QUESTION_MARK_SHARE:
        raise InputError(
            "stdin 的中文已變成問號，內容在傳入前就損毀。PowerShell 請先執行 "
            "$OutputEncoding = [Text.UTF8Encoding]::new($false)，或改傳檔案路徑。"
        )
    return text


def _read_xml(archive, name):
    try:
        info = archive.getinfo(name)
    except KeyError as exc:
        raise InputError(f"文件結構不完整，缺少 {name}：請確認檔案未損毀。") from exc
    if info.file_size > MAX_PART_BYTES:
        raise InputError(f"{name} 超過 {MAX_PART_BYTES // (1024 * 1024)} MB 上限，拒絕解壓。")
    data = archive.read(name)
    if b"<!DOCTYPE" in data[:4096]:
        raise InputError(f"{name} 含 DOCTYPE 宣告，依不信任輸入規則拒絕解析。")
    try:
        return ET.fromstring(data)
    except ET.ParseError as exc:
        raise InputError(f"{name} 無法解析：{exc}") from exc


def _clean_cell(text):
    return re.sub(r"\s+", " ", text).replace("|", "／").strip()


def _markdown_table(rows):
    """Render rows as a pipe table; a merged title row becomes a paragraph above it."""
    rows = [row for row in rows if any(cell for cell in row)]
    if not rows:
        return []
    width = max(len(row) for row in rows)
    if width == 1:
        return [row[0] for row in rows]
    rows = [row + [""] * (width - len(row)) for row in rows]
    lines = []
    if len(rows) >= 3 and sum(1 for cell in rows[0] if cell) == 1:
        lines.append(next(cell for cell in rows[0] if cell))
        rows = rows[1:]
    lines.append("| " + " | ".join(rows[0]) + " |")
    lines.append("|" + "---|" * width)
    lines.extend("| " + " | ".join(row) + " |" for row in rows[1:])
    return lines


def _docx_heading_styles(archive):
    """Map style ids to heading levels; zh-TW Word names them 標題 1 with bare ids like 1."""
    if "word/styles.xml" not in archive.namelist():
        return {}
    levels = {}
    for style in _read_xml(archive, "word/styles.xml").iter(f"{WORD}style"):
        name_node = style.find(f"{WORD}name")
        name = (name_node.get(f"{WORD}val", "") if name_node is not None else "").lower()
        match = re.match(r"(?:heading|標題)\s*(\d)", name)
        if match:
            levels[style.get(f"{WORD}styleId")] = int(match.group(1))
    return levels


def _docx_paragraph_text(node):
    parts = []
    for child in node.iter():
        if child.tag == f"{WORD}t":
            parts.append(child.text or "")
        elif child.tag in (f"{WORD}tab", f"{WORD}br", f"{WORD}cr"):
            parts.append(" ")
    return "".join(parts)


def _docx_table(table):
    rows = []
    for row in table.findall(f"{WORD}tr"):
        cells = []
        for cell in row.findall(f"{WORD}tc"):
            cells.append(_clean_cell(" ".join(
                _docx_paragraph_text(p) for p in cell.iter(f"{WORD}p"))))
            span = cell.find(f"{WORD}tcPr/{WORD}gridSpan")
            if span is not None:
                extra = min(int(span.get(f"{WORD}val", "1")), MAX_REPEATED_CELLS) - 1
                cells.extend([""] * max(extra, 0))
        rows.append(cells)
    return _markdown_table(rows)


def _docx_blocks(node, heading_levels, lines):
    for child in node:
        if child.tag == f"{WORD}p":
            text = _docx_paragraph_text(child).strip()
            if not text:
                continue
            style = child.find(f"{WORD}pPr/{WORD}pStyle")
            level = heading_levels.get(style.get(f"{WORD}val")) if style is not None else None
            lines.append(f"{'#' * level} {text}" if level else text)
        elif child.tag == f"{WORD}tbl":
            lines.extend(_docx_table(child))
        else:
            _docx_blocks(child, heading_levels, lines)


def docx_to_markdown(archive):
    root = _read_xml(archive, "word/document.xml")
    body = root.find(f"{WORD}body")
    if body is None:
        raise InputError("word/document.xml 沒有本文：請確認檔案未損毀。")
    lines = []
    _docx_blocks(body, _docx_heading_styles(archive), lines)
    return "\n".join(lines)


def _odt_text(node):
    parts = [node.text or ""]
    for child in node:
        if child.tag == f"{ODF_TEXT}s":
            parts.append(" " * min(int(child.get(f"{ODF_TEXT}c", "1")), MAX_REPEATED_CELLS))
        elif child.tag in (f"{ODF_TEXT}tab", f"{ODF_TEXT}line-break"):
            parts.append(" ")
        else:
            parts.append(_odt_text(child))
        parts.append(child.tail or "")
    return "".join(parts)


def _odt_table(table):
    rows = []
    for row in table.iter(f"{ODF_TABLE}table-row"):
        cells = []
        for cell in row:
            # ODF writes a covered cell for each spanned column, so spans need no padding here.
            if cell.tag == f"{ODF_TABLE}covered-table-cell":
                cells.append("")
            elif cell.tag == f"{ODF_TABLE}table-cell":
                cells.append(_clean_cell(" ".join(
                    _odt_text(p) for p in cell.iter(f"{ODF_TEXT}p"))))
        rows.append(cells)
    return _markdown_table(rows)


def _odt_blocks(node, lines):
    for child in node:
        if child.tag == f"{ODF_TEXT}h":
            level = int(child.get(f"{ODF_TEXT}outline-level", "1"))
            lines.append(f"{'#' * min(level, 6)} {_odt_text(child).strip()}")
        elif child.tag == f"{ODF_TEXT}p":
            text = _odt_text(child).strip()
            if text:
                lines.append(text)
        elif child.tag == f"{ODF_TABLE}table":
            lines.extend(_odt_table(child))
        else:
            _odt_blocks(child, lines)


def odt_to_markdown(archive):
    body = _read_xml(archive, "content.xml").find(f"{ODF_OFFICE}body/{ODF_OFFICE}text")
    if body is None:
        raise InputError("content.xml 沒有文字本文：請確認這是文字文件（.odt）。")
    lines = []
    _odt_blocks(body, lines)
    return "\n".join(lines)


def read_document(src):
    """Return (text, format). `src` is a path, or '-' for bytes on stdin."""
    if src == "-":
        return decode_stdin(sys.stdin.buffer.read()), "stdin"
    path = Path(src)
    if not path.is_file():
        raise InputError(f"找不到檔案：{src}")
    suffix = path.suffix.lower()
    if suffix in REFUSED_SUFFIXES:
        raise InputError(REFUSED_SUFFIXES[suffix])
    if suffix in (".docx", ".odt"):
        convert = docx_to_markdown if suffix == ".docx" else odt_to_markdown
        try:
            with zipfile.ZipFile(path) as archive:
                return convert(archive), suffix[1:]
        except zipfile.BadZipFile as exc:
            raise InputError(f"{path.name} 不是有效的 {suffix} 檔案。") from exc
    return decode_bytes(path.read_bytes()), "text"


def main():
    if len(sys.argv) != 2:
        print("usage: rfp_extract.py <file>", file=sys.stderr)
        return 2
    sys.stdout.reconfigure(encoding="utf-8")
    try:
        text, _ = read_document(sys.argv[1])
    except InputError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2
    print(text)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
