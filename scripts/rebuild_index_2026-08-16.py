#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""2026-08-16 索引同步：以磁盘 354 份报告为权威源，追加 5 个新仓库
（tmux/tmux、langbot-app/LangBot、simular-ai/Agent-S、
MakazhanAlpamys/Soup、cursor/plugins），计数 349→354。
复用 2026-08-15 磁盘权威重建逻辑。STALE = 空（纯新增，无删除/改名）。
"""
import re, io, glob, os

BASE = r"E:/Lenovo/Documents/coding/github仓库调研"
FA   = f"{BASE}/full-analysis"
IDX  = f"{FA}/GitHub 项目研究 — 全量索引表.md"
OV   = f"{FA}/GitHub 项目研究 — 全量规整后总览.md"
YUAN = f"{FA}/GitHub 项目研究 — 元目录.md"
README = f"{BASE}/README.md"
TOTAL = 354
PREV = 349

def norm(s): return s.lower().replace("/", "-").strip()
def repo_of(ln):
    m = re.search(r"github\.com/([^)\s]+)", ln)
    return m.group(1) if m else None

STALE = []
STALE_N = set(norm(s) for s in STALE)

CURATED = {
 "tmux/tmux": dict(repo="tmux/tmux", file="tmux-tmux-深度调研.md",
    desc="终端复用器的事实标准（GNU screen 现代继任者）——client-server 架构、会话持久化、窗格/窗口/会话三层抽象、历史与可视分离 grid、pledge 沙箱，可脚本化驱动",
    stars="48,637", date="2026-08-16", domain="安全 / 运维 / 系统工具"),
 "langbot-app/LangBot": dict(repo="langbot-app/LangBot", file="langbot-app-LangBot-深度调研.md",
    desc="生产级多平台智能机器人（Agentic IM Bot）开发平台——一套 Agent 逻辑同时部署 10+ IM（企微/飞书/钉钉/QQ/Discord 等），Pipeline 责任链+生成器分叉，v4.10.7 Workspace 多租户",
    stars="17,419", date="2026-08-16", domain="AI Agent / 助手框架"),
 "simular-ai/Agent-S": dict(repo="simular-ai/Agent-S", file="simular-ai-Agent-S-深度调研.md",
    desc="开源 GUI Agent（Computer-Use）框架——像人一样操作电脑，标志性 bBoN 行为边界用前后截图对比校验动作，S1→S3 多代扁平化降低推理时延",
    stars="12,159", date="2026-08-16", domain="AI Agent / 助手框架"),
 "MakazhanAlpamys/Soup": dict(repo="MakazhanAlpamys/Soup", file="MakazhanAlpamys-Soup-深度调研.md",
    desc="一条 YAML 一条命令完成 LLM 微调——Layer Streaming 把冻结基座驻留 CPU RAM/NVMe 逐层流式进 VRAM，8B+NF4 在 4GB 显卡 3.32GB 峰值训练（BETA）",
    stars="1,572", date="2026-08-16", domain="机器学习 / 科学计算"),
 "cursor/plugins": dict(repo="cursor/plugins", file="cursor-plugins-深度调研.md",
    desc="Cursor 官方插件规范 + 官方插件市场——manifest 定义 skills/rules/hooks/mcp 四件套，30+ 官方插件 + 第三方 MCP 集成，ajv schema + CI 强制校验防腐化",
    stars="2,922", date="2026-08-16", domain="AI 编码 / Skill 技能"),
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

# ============ 4) 元目录 + README 计数 349->354 ============
yuan = io.open(YUAN, encoding="utf-8").read()
yuan = yuan.replace(f"owner-repo-深度调研.md × {PREV}", f"owner-repo-深度调研.md × {PREV}")
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
