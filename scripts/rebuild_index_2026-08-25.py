#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""2026-08-25 索引同步：以磁盘 381 份报告为权威源。
本批 = 5 份新增（dani-garcia/vaultwarden / tinyhumansai/openhuman / Alishahryar1/free-claude-code / AgriciDaniel/claude-obsidian / rohitg00/ai-engineering-from-scratch）。
计数 376→381。复用 2026-08-23 磁盘权威重建逻辑。STALE = 空（无删除/改名）。
"""
import re, io, glob, os

BASE = r"E:/Lenovo/Documents/coding/github仓库调研"
FA   = f"{BASE}/full-analysis"
IDX  = f"{FA}/GitHub 项目研究 — 全量索引表.md"
OV   = f"{FA}/GitHub 项目研究 — 全量规整后总览.md"
YUAN = f"{FA}/GitHub 项目研究 — 元目录.md"
README = f"{BASE}/README.md"
TOTAL = 381
PREV = 376

def norm(s): return s.lower().replace("/", "-").strip()
def repo_of(ln):
    m = re.search(r"github\.com/([^)\s]+)", ln)
    return m.group(1) if m else None

STALE = []
STALE_N = set(norm(s) for s in STALE)

CURATED = {
 "dani-garcia/vaultwarden": dict(repo="dani-garcia/vaultwarden", file="dani-garcia-vaultwarden-深度调研.md",
    desc="Bitwarden 兼容自托管密码库服务端（Rust 重写，Rocket + Diesel，资源占用极低、协议级兼容官方全平台客户端，AGPL-3.0）",
    stars="66,096", date="2026-08-25", domain="安全 / 运维 / 系统工具"),
 "tinyhumansai/openhuman": dict(repo="tinyhumansai/openhuman", file="tinyhumansai-openhuman-深度调研.md",
    desc="个人 AI 超级智能（大脑+编排器+深度研究员），Rust core 事件总线驱动的 Agent 编队 + 明文 Memory 树 + Obsidian 镜像，local-first 隐私优先",
    stars="37,166", date="2026-08-25", domain="AI Agent / 助手框架"),
 "Alishahryar1/free-claude-code": dict(repo="Alishahryar1/free-claude-code", file="Alishahryar1-free-claude-code-深度调研.md",
    desc="本地代理网关，让 9 个编码 Agent 共用 50 个 ToS-friendly 免费模型（1.3B+ 免费 token/月），FastAPI 协议保留型代理 + 跨客户端故障转移，MIT",
    stars="48,778", date="2026-08-25", domain="AI 编码 / Skill 技能"),
 "AgriciDaniel/claude-obsidian": dict(repo="AgriciDaniel/claude-obsidian", file="AgriciDaniel-claude-obsidian-深度调研.md",
    desc="面向 Claude Code 的 local-first 知识系统，把源材料变成链接的、有出处的 Obsidian 页面（来源/主张账本 + 15+ Agent Skills + 可恢复事务）",
    stars="11,741", date="2026-08-25", domain="RAG / 知识库 / 记忆"),
 "rohitg00/ai-engineering-from-scratch": dict(repo="rohitg00/ai-engineering-from-scratch", file="rohitg00-ai-engineering-from-scratch-深度调研.md",
    desc="511 课/20 阶段/~329 小时的开放 AI 工程课程，每课 ship 可复用 artifact（prompt/skill/agent/MCP），证据驱动 + 课程即 Skill 包，MIT",
    stars="48,185", date="2026-08-25", domain="学习资料 / 方法论"),
}
CURATED_N = {norm(v["repo"]): v for k, v in CURATED.items()}

# ============ 1) 主表重建（磁盘权威）============
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
    return {"repo": rm.group(2) if rm else "", "file": fm.group(1) if fm else "", "desc": cells[3] if len(cells) > 3 else "",
            "stars": cells[4] if len(cells) > 4 else "", "date": cells[5] if len(cells) > 5 else ""}

present_by_file = {}
for ln in table_rows:
    r = parse_row(ln)
    if not r: continue
    if norm(r["repo"]) in STALE_N: continue
    fm = re.search(r"\[([^\]]+\.md)\]", ln)
    if fm: present_by_file[fm.group(1)] = r
curated_by_file = {norm(v["file"]): v for v in CURATED.values()}

def extract_meta(fpath):
    txt = open(fpath, encoding="utf-8").read()
    head = txt[:2000]
    repo = None
    m = re.search(r"#\s+([A-Za-z0-9._\-]+/[A-Za-z0-9._\-]+)\s+深度调研", head, re.M)
    if m: repo = m.group(1)
    if not repo:
        m = re.search(r"github\.com/([A-Za-z0-9._\-]+/[A-Za-z0-9._\-]+)", head)
        if m: repo = m.group(1)
    stars = None
    s = re.search(r"⭐\s*([\d,]+)", head)
    if s: stars = s.group(1)
    date = None
    d = re.search(r"调研日期[：:]\s*([0-9]{4}[年/\-][0-9]{1,2}[月/\-][0-9]{1,2})", head) or re.search(r"(\d{4}-\d{2}-\d{2})", head)
    if d: date = d.group(1)
    return repo, stars, date

disk_files = sorted(glob.glob(f"{FA}/*-深度调研.md"),
                    key=lambda p: norm(os.path.basename(p)[:-len("-深度调研.md")]))
final_rows = []
missing_meta = []
for f in disk_files:
    base = os.path.basename(f)
    if norm(base) in curated_by_file:
        v = curated_by_file[norm(base)]
        final_rows.append({"repo": v["repo"], "file": base, "name": v["repo"], "desc": v["desc"],
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

# ============ 2) 索引 domain 分类重建 ============
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
for i, ln, in enumerate(rest):
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
ov = "\n".join(new_letter)

ov_text = ov
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
ov = ov.replace(f"owner-repo-深度调研.md × {PREV}", f"owner-repo-深度调研.md × {TOTAL}")
io.open(OV, "w", encoding="utf-8").write(ov)
print("[overview] 字母分组 + domain 段 + 计数 完成")

# ============ 4) 校验断链 ============
link_re = re.compile(r"\[([^\]]+\.md)\]\(([^)]+\.md)\)")
alinks = set(m.group(2) for m in link_re.finditer(io.open(IDX, encoding="utf-8").read()))
ovlinks = set(m.group(2) for m in link_re.finditer(io.open(OV, encoding="utf-8").read()))
disk = set(os.path.basename(p) for p in glob.glob(f"{FA}/*-深度调研.md"))
broken = (alinks | ovlinks) - disk
print(f"[verify] 索引链接数={len(alinks|ovlinks)} 磁盘文件={len(disk)} 断链={len(broken)}" + (f" {broken}" if broken else " OK"))

# ============ 5) 元目录 + README 计数 376->381 ============
yuan = io.open(YUAN, encoding="utf-8").read()
yuan = yuan.replace(f"owner-repo-深度调研.md × {PREV}", f"owner-repo-深度调研.md × {TOTAL}")
yuan = yuan.replace(f"| {PREV} |", f"| {TOTAL} |")
io.open(YUAN, "w", encoding="utf-8").write(yuan)
print("[meta] 计数更新")

rd = io.open(README, encoding="utf-8").read()
rd = rd.replace(f"调研报告-{PREV}-blue", f"调研报告-{TOTAL}-blue")
rd = rd.replace(f"| 调研报告总数 | **{PREV}** |", f"| 调研报告总数 | **{TOTAL}** |")
rd = rd.replace(f"| {PREV} |", f"| {TOTAL} |")
rd = rd.replace(f"│   └── owner-repo-深度调研.md × {PREV}", f"│   └── owner-repo-深度调研.md × {TOTAL}")
io.open(README, "w", encoding="utf-8").write(rd)
print("[readme] 计数更新")
print("DONE")
