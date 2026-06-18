#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Audit Markdown research reports in project-collection.

Detects reports that are likely unusable in the browser/reader:
- collapsed into one giant line / no Markdown structure
- mojibake / replacement chars
- excessive English/raw README dumps
- shallow reports missing key research sections
- truncated/generated placeholders

Outputs JSON + Markdown reports for follow-up repair batches.
"""
from __future__ import annotations

import json
import math
import re
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Iterable

ROOT = Path(__file__).resolve().parents[1]
TARGET_DIRS = [ROOT / "full-analysis", ROOT / "latest-reports", ROOT / "quick-reports"]
OUT_DIR = ROOT / "audit-results"

CORE_SECTIONS = [
    "一句话定位",
    "项目全景",
    "核心架构",
    "源码深度解读",
    "社区口碑",
    "全网口碑",
    "竞品对比",
    "核心研判",
    "关键文件路径速查",
]

MOJIBAKE_PATTERNS = [
    "�", "Ã", "Â", "æ", "ç", "å", "ä", "ö", "ü", "姣忔", "宸℃", "涓", "鍙", "鐮", "璋", "乱码"
]

RAW_DUMP_MARKERS = [
    "...[truncated]",
    "comments=[{",
    "reactionGroups",
    "includesCreatedEdit",
    "authorAssociation",
    "SECURITY NOTICE",
]

PLACEHOLDER_MARKERS = [
    "数据不可用",
    "通常意味着",
    "该项目试图把 README 中描述的能力产品化/脚本化",
    "通用方案学习成本更高",
    "若外部搜索数据不可用",
    "作者驱动、文档深度可能不足",
]

ASCII_RE = re.compile(r"[A-Za-z]")
CJK_RE = re.compile(r"[\u4e00-\u9fff]")
HEADING_RE = re.compile(r"^#{1,6}\s+", re.M)
TABLE_RE = re.compile(r"^\|.+\|$", re.M)
CODE_FENCE_RE = re.compile(r"^```", re.M)
URL_RE = re.compile(r"https?://")

@dataclass
class AuditResult:
    path: str
    directory: str
    bytes: int
    chars: int
    lines: int
    max_line_len: int
    avg_line_len: float
    headings: int
    tables: int
    code_fences: int
    urls: int
    cjk_chars: int
    ascii_letters: int
    english_ratio: float
    mojibake_hits: int
    raw_dump_hits: int
    placeholder_hits: int
    core_section_hits: int
    score: int
    severity: str
    reasons: list[str]


def read_text(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        # Replacement read lets us count decoding damage instead of crashing.
        return path.read_text(encoding="utf-8", errors="replace")


def count_hits(text: str, markers: Iterable[str]) -> int:
    return sum(text.count(m) for m in markers)


def audit_file(path: Path) -> AuditResult:
    text = read_text(path)
    lines = text.splitlines() or [""]
    line_lengths = [len(x) for x in lines]
    cjk = len(CJK_RE.findall(text))
    ascii_letters = len(ASCII_RE.findall(text))
    english_ratio = ascii_letters / max(1, ascii_letters + cjk)
    headings = len(HEADING_RE.findall(text))
    tables = len(TABLE_RE.findall(text))
    code_fences = len(CODE_FENCE_RE.findall(text))
    urls = len(URL_RE.findall(text))
    mojibake = count_hits(text, MOJIBAKE_PATTERNS)
    raw_dump = count_hits(text, RAW_DUMP_MARKERS)
    placeholders = count_hits(text, PLACEHOLDER_MARKERS)
    core_hits = sum(1 for s in CORE_SECTIONS if s in text)

    score = 0
    reasons: list[str] = []

    def add(points: int, reason: str):
        nonlocal score
        score += points
        reasons.append(reason)

    if len(lines) <= 3 and len(text) > 2000:
        add(40, "整篇几乎没有换行，Markdown 会退化成超长段落")
    if max(line_lengths) > 3000:
        add(30, f"存在超长行 max_line_len={max(line_lengths)}")
    if len(text) > 4000 and headings < 5:
        add(25, f"标题层级过少 headings={headings}")
    if len(text) > 4000 and core_hits < 5:
        add(22, f"核心章节缺失 core_section_hits={core_hits}")
    if english_ratio > 0.62 and len(text) > 2500:
        add(20, f"英文占比过高 english_ratio={english_ratio:.2f}")
    if mojibake > 0:
        add(min(35, 8 + mojibake * 3), f"疑似乱码/错误转码命中 {mojibake} 次")
    if raw_dump > 0:
        add(min(30, raw_dump * 6), f"含原始抓取/JSON/截断残留 {raw_dump} 处")
    if placeholders >= 3:
        add(min(25, placeholders * 3), f"模板化/浅层占位句过多 {placeholders} 处")
    if "README / 说明文档要点" in text and english_ratio > 0.48:
        add(12, "疑似直接搬运 README 英文原文")
    if code_fences % 2 == 1:
        add(10, "代码围栏数量为奇数，可能破坏后续 Markdown 渲染")
    if "Manual verification checklist" in text:
        # This itself is not a flaw, but it is the exact area the user called out.
        add(4, "包含 Manual verification checklist，需检查是否被代码块吞掉或未中文讲解")

    if score >= 70:
        severity = "critical"
    elif score >= 45:
        severity = "high"
    elif score >= 25:
        severity = "medium"
    else:
        severity = "low"

    return AuditResult(
        path=str(path.relative_to(ROOT)).replace("\\", "/"),
        directory=path.parent.name,
        bytes=path.stat().st_size,
        chars=len(text),
        lines=len(lines),
        max_line_len=max(line_lengths),
        avg_line_len=round(sum(line_lengths) / max(1, len(lines)), 1),
        headings=headings,
        tables=tables,
        code_fences=code_fences,
        urls=urls,
        cjk_chars=cjk,
        ascii_letters=ascii_letters,
        english_ratio=round(english_ratio, 3),
        mojibake_hits=mojibake,
        raw_dump_hits=raw_dump,
        placeholder_hits=placeholders,
        core_section_hits=core_hits,
        score=score,
        severity=severity,
        reasons=reasons,
    )


def main() -> int:
    OUT_DIR.mkdir(exist_ok=True)
    files: list[Path] = []
    for d in TARGET_DIRS:
        if d.exists():
            files.extend(sorted(d.glob("*.md")))

    results = [audit_file(p) for p in files]
    results.sort(key=lambda x: (x.score, x.max_line_len, x.english_ratio), reverse=True)

    (OUT_DIR / "quality-audit.json").write_text(
        json.dumps([asdict(r) for r in results], ensure_ascii=False, indent=2),
        encoding="utf-8",
    )

    counts = {sev: sum(1 for r in results if r.severity == sev) for sev in ["critical", "high", "medium", "low"]}
    md: list[str] = []
    md.append("# Project Collection 调研报告质量审计\n")
    md.append(f"- 扫描文件数：{len(results)}")
    md.append(f"- Critical：{counts['critical']}")
    md.append(f"- High：{counts['high']}")
    md.append(f"- Medium：{counts['medium']}")
    md.append(f"- Low：{counts['low']}\n")
    md.append("## 判定维度\n")
    md.append("- Markdown 结构：换行、标题、表格、代码围栏")
    md.append("- 内容语言：英文原文占比、中文讲解是否不足")
    md.append("- 数据污染：乱码、抓取截断、JSON/Issue 原始 dump")
    md.append("- 调研完整性：核心章节是否齐全、是否模板化/过浅\n")
    md.append("## 高风险清单（按分数倒序）\n")
    md.append("| 严重级别 | 分数 | 文件 | 行数 | 最长行 | 英文占比 | 核心章节 | 原因 |")
    md.append("|---|---:|---|---:|---:|---:|---:|---|")
    for r in results:
        if r.severity in {"critical", "high", "medium"}:
            reason = "<br>".join(r.reasons[:4]).replace("|", "\\|")
            md.append(f"| {r.severity} | {r.score} | `{r.path}` | {r.lines} | {r.max_line_len} | {r.english_ratio:.3f} | {r.core_section_hits} | {reason} |")
    md.append("\n## 建议修复优先级\n")
    md.append("1. Critical：先修；通常是完全不可读/一整行/乱码/原始 dump。")
    md.append("2. High：再修；通常可读但英文搬运、模板化、章节缺失明显。")
    md.append("3. Medium：批量润色；补中文解释、修 checklist/table/code fence。")
    md.append("4. Low：暂不动，除非人工点名。\n")

    (OUT_DIR / "quality-audit.md").write_text("\n".join(md), encoding="utf-8")

    print(json.dumps({"total": len(results), "counts": counts, "top10": [asdict(r) for r in results[:10]]}, ensure_ascii=False, indent=2))
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
