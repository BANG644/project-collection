# Project Collection 调研报告质量审计

- 扫描文件数：156
- Critical：0
- High：0
- Medium：2
- Low：154

## 判定维度

- Markdown 结构：换行、标题、表格、代码围栏
- 内容语言：英文原文占比、中文讲解是否不足
- 数据污染：乱码、抓取截断、JSON/Issue 原始 dump
- 调研完整性：核心章节是否齐全、是否模板化/过浅

## 高风险清单（按分数倒序）

| 严重级别 | 分数 | 文件 | 行数 | 最长行 | 英文占比 | 核心章节 | 原因 |
|---|---:|---|---:|---:|---:|---:|---|
| medium | 42 | `full-analysis/GitHub 项目研究 — 全量索引表.md` | 364 | 193 | 0.835 | 1 | 核心章节缺失 core_section_hits=1<br>英文占比过高 english_ratio=0.83 |
| medium | 42 | `full-analysis/addyosmani-agent-skills-深度调研.md` | 173 | 141 | 0.625 | 2 | 核心章节缺失 core_section_hits=2<br>英文占比过高 english_ratio=0.63 |

## 建议修复优先级

1. Critical：先修；通常是完全不可读/一整行/乱码/原始 dump。
2. High：再修；通常可读但英文搬运、模板化、章节缺失明显。
3. Medium：批量润色；补中文解释、修 checklist/table/code fence。
4. Low：暂不动，除非人工点名。
