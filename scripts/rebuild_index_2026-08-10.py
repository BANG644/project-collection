#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""2026-08-10 索引同步：以磁盘 329 份报告为权威源，追加 5 个 Trending 新仓库
（Comfy-Org/ComfyUI、pranshuparmar/witr、vitali87/code-graph-rag、pingdotgg/t3code、
msitarzewski/agency-agents），计数 324→329。复用 2026-08-09 磁盘权威重建逻辑。
STALE = 空（无删除/改名）。
"""
import re, io, glob, os

BASE = r"E:/Lenovo/Documents/coding/github仓库调研"
IDX = f"{BASE}/full-analysis/GitHub 项目研究 — 全量索引表.md"
OV  = f"{BASE}/full-analysis/GitHub 项目研究 — 全量规整后总览.md"
YUAN= f"{BASE}/full-analysis/GitHub 项目研究 — 元目录.md"
README = f"{BASE}/README.md"
TOTAL = 327
PREV = 324

def norm(s): return s.lower().replace("/", "-").strip()
def repo_of(ln):
    m = re.search(r"github\.com/([^)\s]+)", ln)
    return m.group(1) if m else None

STALE = []
STALE_N = set(norm(s) for s in STALE)

CURATED = {
 "comfy-org/comfyui": dict(repo="Comfy-Org/ComfyUI", file="Comfy-Org-ComfyUI-深度调研.md",
    desc="节点式 AI 内容生成引擎——图像/视频/3D/音频的数据流图工作流，局部重算 + 显存精算，100+ 模型原生支持，GPL-3.0",
    stars="125,347", date="2026-08-10", domain="视频 / 音频 / 多媒体"),
 "pranshuparmar/witr": dict(repo="pranshuparmar/witr", file="pranshuparmar-witr-深度调研.md",
    desc="Go 单文件静态二进制——把进程/端口/容器/文件「为什么在跑」收敛成一条人类可读祖先因果链（CLI+TUI），Apache-2.0",
    stars="20,489", date="2026-08-10", domain="开发工具 / CLI"),
 "vitali87/code-graph-rag": dict(repo="vitali87/code-graph-rag", file="vitali87-code-graph-rag-深度调研.md",
    desc="多语言 monorepo 代码 RAG——Tree-sitter 抽结构进 Memgraph 统一图 Schema，自然语言查询 + AST 级编辑，可作 MCP server，MIT",
    stars="2,875", date="2026-08-10", domain="RAG / 知识库 / 记忆"),
 "pingdotgg/t3code": dict(repo="pingdotgg/t3code", file="pingdotgg-t3code-深度调研.md",
    desc="Theo 的开源 Agent 工作台控制面——Web/桌面/移动三端统一 GUI 收编 Claude Code/Codex/Cursor 等，BYO 订阅 + git 原生一键 PR，MIT",
    stars="17,577", date="2026-08-10", domain="AI 编码 / Skill 技能"),
 "msitarzewski/agency-agents": dict(repo="msitarzewski/agency-agents", file="msitarzewski-agency-agents-深度调研.md",
    desc="「虚拟 AI 公司」人设库——200+ 结构化 agent 角色 Markdown，按 16-21 部门组织，一键装进十余种工具 + 原生 App，MIT",
    stars="140,498", date="2026-08-10", domain="AI Agent / 助手框架"),
}
CURATED_N = {norm(v["repo"]): v for k, v in CURATED.items()}

# ============ 1) 主表重建 ============
lines = io.open(IDX, encoding="utf-8").read().split("\n")
sep_i = next(i for i, ln in enumerate(lines) if re.match(r"^\|[\-:\s|]+\|$", ln))
end_i = sep_i + 1
while end_i < len(lines) and not lines[end_i].startswith("## "): end_i += 1
header_block = lines[:sep_i + 1]
table_rows = lines[sep_i + 1:end_i]
tail = lines[end_i:]

def parse_row(ln):
    m = re.match(r"^\|\s*(\d+)\s*\|", ln)
    if not m: return None
    rm = re.search(r"\[`([^`]+)`\]\(https://github\.com/([^)]+)\)", ln)
    fm = re.search(r"\[([^\]]+\.md)\]", ln)
    cells = [c.strip() for c in ln.split("|")]
    return {"repo": rm.group(2) if rm else "", "file": fm.group(1) if fm else "",
            "desc": cells[3] if len(cells) > 3 else "", "stars": cells[4] if len(cells) > 4 else "",
            "date": cells[5] if len(cells) > 5 else ""}

present_by_file = {}
for ln in table_rows:
    r = parse_row(ln)
    if not r: continue
    if norm(r["repo"]) in STALE_N: continue
    if r["file"]:
        present_by_file[r["file"]] = r
curated_by_file = {norm(v["file"]): v for v in CURATED.values()}

def extract_meta(fpath):
    txt = open(fpath, encoding="utf-8").read()
    head = txt[:2000]
    repo = None
    m = re.search(r"#\s+([A-Za-z0-9._\-]+/[A-Za-z0-9._\-]+)\s+深度调研", head, re.M)
    if m: repo = m.group(1)
    if not repo:
        m = re.search(r"调研仓库[：:]\s*`([^`]+)`", head)
        if m: repo = m.group(1)
    if not repo:
        m = re.search(r"github\.com/([A-Za-z0-9._\-]+/[A-Za-z0-9._\-]+)", head)
        if m: repo = m.group(1)
    stars = None
    s = re.search(r"⭐\s*([\d,]+)", head) or re.search(r"[Ss]tars[：:]\s*([\d,]+)", head)
    if s: stars = s.group(1)
    date = None
    d = re.search(r"调研日期[：:]\s*([0-9]{4}[年/\-][0-9]{1,2}[月/\-][0-9]{1,2})", head) or re.search(r"(\d{4}-\d{2}-\d{2})", head)
    if d: date = d.group(1)
    return repo, stars, date

disk_files = sorted(glob.glob("full-analysis/*-深度调研.md"),
                    key=lambda p: norm(os.path.basename(p)[:-len("-深度调研.md")]))
final_rows = []
missing_meta = []
for f in disk_files:
    base = os.path.basename(f)
    if norm(base) in curated_by_file:
        v = curated_by_file[norm(base)]
        final_rows.append({"repo": v["repo"], "file": base, "desc": v["desc"],
                           "stars": v["stars"], "date": v["date"]})
    elif base in present_by_file:
        final_rows.append(present_by_file[base])
    else:
        repo, stars, date = extract_meta(f)
        final_rows.append({"repo": repo or base[:-len("-深度调研.md")], "file": base,
                           "desc": "—", "stars": stars or "—", "date": date or "—"})
        missing_meta.append(base)
assert len(final_rows) == TOTAL, f"主表 {len(final_rows)} != {TOTAL}"
new_table = [f"| {n} | [`{r['repo']}`](https://github.com/{r['repo']}) | {r['desc']} | {r['stars']} | {r['date']} | [{r['file']}]({r['file']}) |"
             for n, r in enumerate(final_rows, 1)]
io.open(IDX, "w", encoding="utf-8").write("\n".join(header_block + new_table + tail))
print(f"[index] 主表={len(final_rows)} OK" + (f" | 回退提取 {len(missing_meta)} 份: {missing_meta}" if missing_meta else ""))

SUF = "-深度调研.md"
for _r in final_rows:
    if not _r["repo"]:
        _r["repo"] = _r["file"][:-len(SUF)] if _r["file"].endswith(SUF) else _r["file"]

# ============ 2) 索引 domain 分类重建（以 329 为权威源）============
idx_text = io.open(IDX, encoding="utf-8").read()
sec_start = idx_text.index("## 🏷️ 按技术领域分类")
domain_of_present = {}
L = idx_text[sec_start:].split("\n")
curD = None
for ln in L[1:]:
    if re.match(r"^### ", ln):
        curD = re.sub(r"\s*[（(]\d+[)）]\s*🆕?$", "", ln[4:].strip()).strip()
        continue
    if re.match(r"^## ", ln): break
    if ln.strip().startswith("- "):
        fm = re.search(r"\[([^\]]+\.md)\]", ln)
        if fm: domain_of_present[norm(fm.group(1))] = curD

full_domain = {}
for r in final_rows:
    n = norm(r["repo"])
    if n in CURATED_N:
        full_domain[n] = CURATED_N[n]["domain"]
    elif norm(r["file"]) in domain_of_present:
        full_domain[n] = domain_of_present[norm(r["file"])]
    else:
        full_domain[n] = "其他"

groups = {}
for r in final_rows:
    n = norm(r["repo"])
    d = full_domain[n]
    bullet = f"- [`{r['repo']}`](https://github.com/{r['repo']}) — [{r['file']}]({r['file']})"
    groups.setdefault(d, []).append(bullet)
for d in groups:
    groups[d].sort(key=lambda b: norm(repo_of(b) or b))

orig_domains = []
seen = set()
for ln in L:
    if re.match(r"^### ", ln):
        name = re.sub(r"\s*[（(]\d+[)）]\s*🆕?$", "", ln[4:].strip()).strip()
        if name not in seen:
            seen.add(name); orig_domains.append(name)
for d in groups:
    if d not in seen:
        orig_domains.append(d)

out = idx_text[:sec_start].split("\n")
out.append("## 🏷️ 按技术领域分类")
for d in orig_domains:
    bullets = groups.get(d, [])
    out.append(f"### {d}（{len(bullets)}）")
    out.extend(bullets)
rest = idx_text[sec_start:].split("\n")
endi = 0
for i, ln in enumerate(rest):
    if i > 0 and re.match(r"^## ", ln):
        endi = i; break
out.extend(rest[endi:])
io.open(IDX, "w", encoding="utf-8").write("\n".join(out))
print(f"[index] domain 段重建完成，domain 数={len(orig_domains)}")

# ============ 3) 总览 字母分组 + domain 段重建 ============
ov = io.open(OV, encoding="utf-8").read().split("\n")
letter_sec_i = next(i for i, ln in enumerate(ov) if ln.startswith("## 📚 按字母分组索引"))
letter_end = letter_sec_i + 1
while letter_end < len(ov) and not ov[letter_end].startswith("## "): letter_end += 1
letter_groups = {}
for r in final_rows:
    L0 = r["repo"][0].upper()
    bullet = f"- [`{r['repo']}`](https://github.com/{r['repo']}) — [{r['file']}]({r['file']})"
    letter_groups.setdefault(L0, []).append(bullet)
for L0 in letter_groups:
    letter_groups[L0].sort(key=lambda b: norm(repo_of(b) or b))
orig_letters = []
seen = set()
for ln in ov[letter_sec_i:letter_end]:
    m = re.match(r"^### ([A-Za-z0-9])（\d+ 个）$", ln)
    if m and m.group(1) not in seen:
        seen.add(m.group(1)); orig_letters.append(m.group(1))
for L0 in letter_groups:
    if L0 not in seen: orig_letters.append(L0)
new_letter = ov[:letter_sec_i + 1]
for L0 in orig_letters:
    bullets = letter_groups.get(L0, [])
    new_letter.append(f"### {L0}（{len(bullets)} 个）")
    new_letter.extend(bullets)
new_letter.extend(ov[letter_end:])
ov = new_letter

ov_text = "\n".join(ov)
dsec = ov_text.index("## 🏷️ 按技术领域分类")
ov_domains = []
seen = set()
for ln in ov_text[dsec:].split("\n"):
    if re.match(r"^### ", ln):
        name = ln[4:].strip()
        if name not in seen:
            seen.add(name); ov_domains.append(name)
for d in groups:
    if d not in seen: ov_domains.append(d)
out2 = ov_text[:dsec].split("\n")
out2.append("## 🏷️ 按技术领域分类")
for d in ov_domains:
    out2.extend(groups.get(d, []))
out2.extend(ov_text[dsec:].split("\n")[1:])
ov = "\n".join(out2)
# 计数 324->329
ov = ov.replace(f"owner-repo-深度调研.md × {PREV}", f"owner-repo-深度调研.md × {TOTAL}")
io.open(OV, "w", encoding="utf-8").write(ov)
print("[overview] 字母分组 + domain 段 + 计数 完成")

# ============ 4) 元目录 + README 计数 324->329 ============
yuan = io.open(YUAN, encoding="utf-8").read()
yuan = yuan.replace(f"owner-repo-深度调研.md × {PREV}", f"owner-repo-深度调研.md × {TOTAL}")
yuan = yuan.replace("| [`GitHub 项目研究 — 全量规整后总览.md`](GitHub%20项目研究%20—%20全量规整后总览.md) | 🎯 权威总览（按字母分组索引 + 按领域分类 + 仓库结构 + 调研方法） | 315 |".replace("315", str(PREV)),
                    f"| [`GitHub 项目研究 — 全量规整后总览.md`](GitHub%20项目研究%20—%20全量规整后总览.md) | 🎯 权威总览（按字母分组索引 + 按领域分类 + 仓库结构 + 调研方法） | {TOTAL} |")
yuan = yuan.replace("| [`GitHub 项目研究 — 全量索引表.md`](GitHub%20项目研究%20—%20全量索引表.md) | 📋 全量索引表，所有项目的表格索引（owner/repo + 定位 + Stars + 报告链接） | 315 |".replace("315", str(PREV)),
                    f"| [`GitHub 项目研究 — 全量索引表.md`](GitHub%20项目研究%20—%20全量索引表.md) | 📋 全量索引表，所有项目的表格索引（owner/repo + 定位 + Stars + 报告链接） | {TOTAL} |")
yuan = yuan.replace(f"| 调研报告总数 | {PREV} |", f"| 调研报告总数 | {TOTAL} |")
io.open(YUAN, "w", encoding="utf-8").write(yuan)
print("[meta] 计数更新")

rd = io.open(README, encoding="utf-8").read()
rd = rd.replace(f"调研报告-{PREV}-blue", f"调研报告-{TOTAL}-blue")
rd = rd.replace(f"| 调研报告总数 | **{PREV}** |", f"| 调研报告总数 | **{TOTAL}** |")
rd = rd.replace(f"| [🎯 全量规整后总览](full-analysis/GitHub%20项目研究%20—%20全量规整后总览.md) | 全量维护后权威总览（按字母分组索引 + 按领域分类） | {PREV} |",
                f"| [🎯 全量规整后总览](full-analysis/GitHub%20项目研究%20—%20全量规整后总览.md) | 全量维护后权威总览（按字母分组索引 + 按领域分类） | {TOTAL} |")
rd = rd.replace(f"| [📚 全量索引表](full-analysis/GitHub%20项目研究%20—%20全量索引表.md) | 所有项目的表格索引（项目名 / 定位 / Stars / 报告链接） | {PREV} |",
                f"| [📚 全量索引表](full-analysis/GitHub%20项目研究%20—%20全量索引表.md) | 所有项目的表格索引（项目名 / 定位 / Stars / 报告链接） | {TOTAL} |")
rd = rd.replace(f"│   └── owner-repo-深度调研.md × {PREV}", f"│   └── owner-repo-深度调研.md × {TOTAL}")
io.open(README, "w", encoding="utf-8").write(rd)
print("[readme] 计数更新")
print("DONE")
