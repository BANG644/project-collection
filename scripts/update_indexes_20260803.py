# -*- coding: utf-8 -*-
import io, sys

BASE = r"E:\Lenovo\Documents\coding\github仓库调研"
IDX = f"{BASE}/full-analysis/GitHub 项目研究 — 全量索引表.md"
OV  = f"{BASE}/full-analysis/GitHub 项目研究 — 全量规整后总览.md"
META= f"{BASE}/full-analysis/GitHub 项目研究 — 元目录.md"
README = f"{BASE}/README.md"

def read(p):
    with io.open(p, encoding="utf-8") as f:
        return f.read()

def write(p, s):
    with io.open(p, "w", encoding="utf-8") as f:
        f.write(s)

def repl_once(s, old, new, label):
    n = s.count(old)
    if n != 1:
        raise SystemExit(f"[FAIL] {label}: expected exactly 1 match, found {n}\nOLD={old!r}")
    return s.replace(old, new, 1)

# ---------------- 全量索引表.md ----------------
t = read(IDX)

# 1) rewrite rows
t = repl_once(t,
    "| 34 | [`anthropics/skills`](https://github.com/anthropics/skills) | — | — | 2026-06-19 | [anthropics-skills-深度调研.md](anthropics-skills-深度调研.md) |",
    "| 34 | [`anthropics/skills`](https://github.com/anthropics/skills) | Anthropic 官方 Agent Skills 公共仓库（18 技能 + marketplace 分发，Apache-2.0） | 165,791 | 2026-08-03 | [anthropics-skills-深度调研.md](anthropics-skills-深度调研.md) |",
    "idx:rewrite anthropics/skills")
t = repl_once(t,
    "| 72 | [`CyC2018/CS-Notes`](https://github.com/CyC2018/CS-Notes) | — | — | 2026-06-19 | [CyC2018-CS-Notes-深度调研.md](CyC2018-CS-Notes-深度调研.md) |",
    "| 72 | [`CyC2018/CS-Notes`](https://github.com/CyC2018/CS-Notes) | CS 面试八股文笔记合集（Java/网络/OS/DB/分布式），已停更 | 184,937 | 2026-08-03 | [CyC2018-CS-Notes-深度调研.md](CyC2018-CS-Notes-深度调研.md) |",
    "idx:rewrite CS-Notes")
t = repl_once(t,
    "| 135 | [`koala73/worldmonitor`](https://github.com/koala73/worldmonitor) | 实时全球情报仪表盘 | 58,000 | — | [koala73-worldmonitor-深度调研.md](koala73-worldmonitor-深度调研.md) |",
    "| 135 | [`koala73/worldmonitor`](https://github.com/koala73/worldmonitor) | 实时全球情报仪表盘（AI 新闻聚合+地缘监控+双地图引擎，AGPL-3.0） | 78,069 | 2026-08-03 | [koala73-worldmonitor-深度调研.md](koala73-worldmonitor-深度调研.md) |",
    "idx:rewrite worldmonitor")

# 2) append 2 new rows after MiroThinker (#300)
anchor = "| 300 | [`MiroMindAI/MiroThinker`](https://github.com/MiroMindAI/MiroThinker) | 深度研究 Agent——interactive scaling + 近因上下文，BrowseComp SOTA，配套训练数据闭环 | 8,361 | 2026-08-01 | [MiroMindAI-MiroThinker-深度调研.md](MiroMindAI-MiroThinker-深度调研.md) |"
newrows = anchor + "\n" + \
"| 301 | [`gsd-build/get-shit-done`](https://github.com/gsd-build/get-shit-done) | 多 Agent 规格驱动开发系统（meta-prompting/上下文工程），已归档→gsd-core | 64,778 | 2026-08-03 | [gsd-build-get-shit-done-深度调研.md](gsd-build-get-shit-done-深度调研.md) |\n" + \
"| 302 | [`666ghj/BettaFish`](https://github.com/666ghj/BettaFish) | 纯 Python 零框架多 Agent 舆情分析助手（日志文件消息总线） | 41,920 | 2026-08-03 | [666ghj-BettaFish-深度调研.md](666ghj-BettaFish-深度调研.md) |"
t = repl_once(t, anchor, newrows, "idx:append new rows 301/302")

# 3) 按领域分类 AI Agent: bump 79->81 and prepend 2 entries
t = repl_once(t,
    "### AI Agent / 助手框架（79）",
    "### AI Agent / 助手框架（81）\n\n- [`gsd-build/get-shit-done`](https://github.com/gsd-build/get-shit-done) — [gsd-build-get-shit-done-深度调研.md](gsd-build-get-shit-done-深度调研.md)\n- [`666ghj/BettaFish`](https://github.com/666ghj/BettaFish) — [666ghj-BettaFish-深度调研.md](666ghj-BettaFish-深度调研.md)",
    "idx:domain AI Agent bump+insert")
write(IDX, t)

# ---------------- 全量规整后总览.md ----------------
o = read(OV)
# count
o = repl_once(o, "owner-repo-深度调研.md × 314", "owner-repo-深度调研.md × 316", "ov:count 314->316")
# new "6" group before "### A（23 个）"
o = repl_once(o,
    "| [`AlexsJones/llmfit`](https://github.com/AlexsJones/llmfit) | [AlexsJones-llmfit-深度调研.md](AlexsJones-llmfit-深度调研.md) |\n\n### A（23 个）",
    "| [`AlexsJones/llmfit`](https://github.com/AlexsJones/llmfit) | [AlexsJones-llmfit-深度调研.md](AlexsJones-llmfit-深度调研.md) |\n\n### 6（1 个）\n\n| owner/repo | 报告文件 |\n|------------|----------|\n| [`666ghj/BettaFish`](https://github.com/666ghj/BettaFish) | [666ghj-BettaFish-深度调研.md](666ghj-BettaFish-深度调研.md) |\n\n### A（23 个）",
    "ov:new 6 group")
# G group bump + insert gsd-build
o = repl_once(o,
    "### G（17 个）\n| owner/repo | 报告文件 |\n|------------|----------|\n| [`github/gh-aw`](https://github.com/github/gh-aw) | [github-gh-aw-深度调研.md](github-gh-aw-深度调研.md) |",
    "### G（18 个）\n| owner/repo | 报告文件 |\n|------------|----------|\n| [`gsd-build/get-shit-done`](https://github.com/gsd-build/get-shit-done) | [gsd-build-get-shit-done-深度调研.md](gsd-build-get-shit-done-深度调研.md) |\n| [`github/gh-aw`](https://github.com/github/gh-aw) | [github-gh-aw-深度调研.md](github-gh-aw-深度调研.md) |",
    "ov:G group bump+insert")
# 按领域分类 AI Agent: insert 2 entries after header
o = repl_once(o,
    "### AI Agent / 助手框架\n\n- [`chatwoot/chatwoot`](https://github.com/chatwoot/chatwoot) — [chatwoot-chatwoot-深度调研.md](chatwoot-chatwoot-深度调研.md)",
    "### AI Agent / 助手框架\n\n- [`gsd-build/get-shit-done`](https://github.com/gsd-build/get-shit-done) — [gsd-build-get-shit-done-深度调研.md](gsd-build-get-shit-done-深度调研.md)\n- [`666ghj/BettaFish`](https://github.com/666ghj/BettaFish) — [666ghj-BettaFish-深度调研.md](666ghj-BettaFish-深度调研.md)\n- [`chatwoot/chatwoot`](https://github.com/chatwoot/chatwoot) — [chatwoot-chatwoot-深度调研.md](chatwoot-chatwoot-深度调研.md)",
    "ov:domain AI Agent insert")
write(OV, o)

# ---------------- 元目录.md ----------------
m = read(META)
m = repl_once(m, "owner-repo-深度调研.md × 314", "owner-repo-深度调研.md × 316", "meta:count1")
# | 314 | appears on lines 39, 40, 113 (all count refs) -> global replace
n314 = m.count("| 314 |")
if n314 != 3:
    raise SystemExit(f"[FAIL] meta:count2 expected 3 matches, found {n314}")
m = m.replace("| 314 |", "| 316 |")
write(META, m)

# ---------------- README.md ----------------
r = read(README)
r = repl_once(r, "| 调研报告总数 | **314** |", "| 调研报告总数 | **316** |", "readme:count")
write(README, r)

print("ALL INDEX UPDATES APPLIED OK")
