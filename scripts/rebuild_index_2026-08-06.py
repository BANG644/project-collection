#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""2026-08-06 索引全量重建：以磁盘 316 份报告为权威源，重建主表/字母组/领域分类。
- 删除 8 个陈旧索引行（5 占位删除 + 3 改名孤儿：maxkbstar/skyvernstar/github.com-tencentcloud）
- 补录 23 个磁盘有报告但未进主表的仓库
- 最终主表 = 316 行，与磁盘一致
"""
import re, io, glob, os

BASE = r"E:/Lenovo/Documents/coding/github仓库调研"
IDX = f"{BASE}/full-analysis/GitHub 项目研究 — 全量索引表.md"
OV  = f"{BASE}/full-analysis/GitHub 项目研究 — 全量规整后总览.md"
YUAN= f"{BASE}/full-analysis/GitHub 项目研究 — 元目录.md"
README = f"{BASE}/README.md"
TOTAL = 316

def norm(s): return s.lower().replace("/", "-").strip()
def repo_of(ln):
    m = re.search(r"github\.com/([^)\s]+)", ln)
    return m.group(1) if m else None

# 8 个陈旧索引行（磁盘已删除/改名）
STALE = ["1panel-dev/maxkbstar","bang644/ai-workflow-optimizer","bang644/docx-svg-to-pdf",
         "github.com/tencentcloud","liyue-aigc/female-portrait-dataset",
         "qiuqiubuchongle/cloud-chokepoint-atlas","skyvern-ai/skyvernstar",
         "xw7872081123/wallpaper-engine-steam"]
STALE_N = set(norm(s) for s in STALE)

# 23 个磁盘有报告但未进主表的仓库（curated 元数据，来自报告头 + 历史调研记忆）
CURATED = {
 "1panel-dev/maxkb": dict(repo="1Panel-dev/MaxKB", file="1panel-dev-maxkb-深度调研.md",
    desc="1Panel 开源企业 AI 知识库问答系统——RAG + Agent 工作流，对接主流 LLM 与向量库",
    stars="21,928", date="2026-07-07", domain="RAG / 知识库 / 记忆"),
 "automattic/harper": dict(repo="Automattic/harper", file="automattic-harper-深度调研.md",
    desc="Rust 本地优先语法检查器——手写规则引擎（expr DSL）非 ML，WASM 可嵌，20 crate workspace",
    stars="12,923", date="2026-07-26", domain="开发工具 / CLI"),
 "composiohq/awesome-claude-skills": dict(repo="ComposioHQ/awesome-claude-skills", file="composiohq-awesome-claude-skills-深度调研.md",
    desc="1000+ Claude Skills 策展清单——界定 Skills≠MCP≠Tools，渐进式加载（~100 token 名称常驻，命中才载正文）",
    stars="69,947", date="2026-07-26", domain="AI 编码 / Skill 技能"),
 "coreybutler/nvm-windows": dict(repo="coreybutler/nvm-windows", file="coreybutler-nvm-windows-深度调研.md",
    desc="Go 编写的 Node 版本管理器——symlink-in-PATH 切换 + 进程隔离",
    stars="47,040", date="2026-07-13", domain="开发工具 / CLI"),
 "davila7/claude-code-templates": dict(repo="davila7/claude-code-templates", file="davila7-claude-code-templates-深度调研.md",
    desc="Claude Code 配置模板分发平台（npx 一键拉取）",
    stars="29,187", date="2026-07-13", domain="AI 编码 / Skill 技能"),
 "farion1231/cc-switch": dict(repo="farion1231/cc-switch", file="farion1231-cc-switch-深度调研.md",
    desc="Tauri 2 桌面端 AI 编码工具管理器——SQLite SSOT + 原子写 + 双向同步，统管 7 款 Coding Agent",
    stars="116,295", date="2026-07-13", domain="AI 编码 / Skill 技能"),
 "firecrawl/anydoc": dict(repo="firecrawl/anydoc", file="firecrawl-anydoc-深度调研.md",
    desc="Firecrawl Rust 文档转 Markdown 库——9 类 Office/PDF 统一 model + 单序列化器，Rust/Node/Python/WASM 四端同构",
    stars="4,343", date="2026-08-03", domain="AI 编码 / Skill 技能"),
 "gastownhall/beads": dict(repo="gastownhall/beads", file="gastownhall-beads-深度调研.md",
    desc="Go + Dolt 驱动的 Agent 记忆/Issue 追踪器——单元格级版本化",
    stars="25,249", date="2026-07-13", domain="AI Agent / 助手框架"),
 "genspark-ai/genoffice": dict(repo="genspark-ai/genoffice", file="genspark-ai-genoffice-深度调研.md",
    desc="GenSpark 开源 AI-native 办公套件（mac/Win）——Electron 壳 + 共享 *-engine 做 OOXML 往返保真，内嵌 agent 生成/改写",
    stars="1,732", date="2026-07-31", domain="前端 / 设计 / UI"),
 "grafana/grafana": dict(repo="grafana/grafana", file="grafana-grafana-深度调研.md",
    desc="Grafana —— 开源可观测性平台（指标/日志/追踪统一仪表盘与告警），运维标配",
    stars="74,940", date="2026-06-27", domain="安全 / 运维 / 系统工具"),
 "icewhaletech/casaos": dict(repo="IceWhaleTech/CasaOS", file="icewhaletech-casaos-深度调研.md",
    desc="CasaOS —— 轻量家庭云/NAS 操作系统，Web UI 一键管理 Docker 应用与设备",
    stars="35,420", date="2026-06-27", domain="安全 / 运维 / 系统工具"),
 "justvugg/colibri": dict(repo="JustVugg/colibri", file="justvugg-colibri-深度调研.md",
    desc="纯 C 实现 744B GLM-5.2 MoE 推理于 25GB RAM——LFRU 分层缓存 + MTP 投机解码",
    stars="16,030", date="2026-07-19", domain="LLM / 推理框架"),
 "langchain-ai/openwiki": dict(repo="langchain-ai/openwiki", file="langchain-ai-openwiki-深度调研.md",
    desc="LangChain DeepAgents 文档写作 CLI——后端写护栏 + SHA-256 快照门禁",
    stars="12,272", date="2026-07-19", domain="AI 编码 / Skill 技能"),
 "lordog/dive-into-llms": dict(repo="Lordog/dive-into-llms", file="lordog-dive-into-llms-深度调研.md",
    desc="上交大《动手学大模型》中文教程——11 章课件+教程+notebook，覆盖水印/隐写/越狱/对齐",
    stars="44,960", date="2026-07-26", domain="学习资料 / 方法论"),
 "nanmicoder/mediacrawler": dict(repo="NanmiCoder/MediaCrawler", file="nanmicoder-mediacrawler-深度调研.md",
    desc="MediaCrawler —— 小红书/抖音/B站/微博等社媒数据爬虫，支持登录态与多平台，AI 训练数据采集",
    stars="53,397", date="2026-06-27", domain="AI Agent / 助手框架"),
 "oomol-lab/open-connector": dict(repo="oomol-lab/open-connector", file="oomol-lab-open-connector-深度调研.md",
    desc="Composio 开源替代——Agent SaaS 连接器网关，guarded-fetch 安全校验",
    stars="2,913", date="2026-07-19", domain="开发工具 / CLI"),
 "ottermind/chat2db": dict(repo="OtterMind/Chat2DB", file="ottermind-chat2db-深度调研.md",
    desc="开源 AI 数据库客户端——Spring Boot+React，BYO 模型 text2sql，AES-256-GCM 本地加密",
    stars="26,261", date="2026-07-26", domain="开发工具 / CLI"),
 "skyvern-ai/skyvern": dict(repo="Skyvern-AI/skyvern", file="skyvern-ai-skyvern-深度调研.md",
    desc="Skyvern —— 用 LLM + 计算机视觉驱动的浏览器自动化 Agent，自然语言工作流替代脆弱 XPath 脚本",
    stars="22,129", date="2026-07-07", domain="AI Agent / 助手框架"),
 "tencentcloud": dict(repo="TencentCloud/TencentDB-Agent-Memory", file="tencentcloud-深度调研.md",
    desc="TencentCloud 开源组织深度调研——聚焦 TencentDB-Agent-Memory（Agent 记忆层）+ CubeSandbox（代码沙箱）",
    stars="—", date="2026-06-07", domain="AI Agent / 助手框架"),
 "trycompai/crm": dict(repo="trycompai/crm", file="trycompai-crm-深度调研.md",
    desc="Agentic-first 开源 CRM——耐久研究 agent 是产品本体，API 零智能 + 租约队列 + deny-all 沙箱 + 证据账本",
    stars="6,016", date="2026-07-31", domain="AI Agent / 助手框架"),
 "xai-org/grok-build": dict(repo="xai-org/grok-build", file="xai-org-grok-build-深度调研.md",
    desc="xAI 的 Rust 编码 Agent——ACP 协议三入口（TUI/headless/ACP），DeepAgents 风格 code graph",
    stars="18,477", date="2026-07-19", domain="AI 编码 / Skill 技能"),
 "yorukot/superfile": dict(repo="yorukot/superfile", file="yorukot-superfile-深度调研.md",
    desc="Go+bubbletea v2 现代 TUI 文件管理器——单 Model 编排多面板，内建压缩包/PDF/图预览",
    stars="19,408", date="2026-07-26", domain="开发工具 / CLI"),
 "zai-org/open-autoglm": dict(repo="zai-org/Open-AutoGLM", file="zai-org-open-autoglm-深度调研.md",
    desc="智谱开源手机 GUI Agent——VLM + ADB/HDC 执行闭环",
    stars="25,756", date="2026-07-13", domain="AI Agent / 助手框架"),
}
CURATED_N = {norm(v["repo"]): v for k, v in CURATED.items()}  # 用 repo 归一化做键，兼容 tencentcloud 这种 key≠repo 的特殊项

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

# 构建 present_by_file（非陈旧行，按文件键）
present_by_file = {}
for ln in table_rows:
    r = parse_row(ln)
    if not r: continue
    if norm(r["repo"]) in STALE_N: continue
    if r["file"]:
        present_by_file[r["file"]] = r
curated_by_file = {norm(v["file"]): v for v in CURATED.values()}  # 按归一化文件名匹配，避免大小写错位

# 回退：从报告文件提取 repo/stars/date
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

# 遍历磁盘 316 份报告，构建最终主表（每文件一行，无孤儿/重复/幻影）
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

# 归一化：保证 repo 非空（用文件名兜底），避免字母分组 r["repo"][0] 越界
SUF = "-深度调研.md"
for _r in final_rows:
    if not _r["repo"]:
        _r["repo"] = _r["file"][:-len(SUF)] if _r["file"].endswith(SUF) else _r["file"]

# ============ 2) 索引 domain 分类重建（以 316 为权威源）============
# 先从当前索引 domain 段解析 present 的 domain（按文件键，避免 repo 归一化错位）
idx_text = io.open(IDX, encoding="utf-8").read()
sec_start = idx_text.index("## 🏷️ 按技术领域分类")
domain_of_present = {}
L = idx_text[sec_start:].split("\n")
curD = None
for ln in L[1:]:   # 跳过首个 "## 🏷️ 按技术领域分类" 自身，否则会立即 break
    if re.match(r"^### ", ln):
        curD = re.sub(r"\s*[（(]\d+[)）]\s*🆕?$", "", ln[4:].strip()).strip()
        continue
    if re.match(r"^## ", ln): break
    if ln.strip().startswith("- "):
        fm = re.search(r"\[([^\]]+\.md)\]", ln)
        if fm: domain_of_present[norm(fm.group(1))] = curD

# 构建完整 316 的 domain 映射
full_domain = {}
for r in final_rows:
    n = norm(r["repo"])
    if n in CURATED_N:                                 # curated 权威领域优先，覆盖历史陈旧 domain_of_present
        full_domain[n] = CURATED_N[n]["domain"]
    elif norm(r["file"]) in domain_of_present:          # 大小写无关匹配，避免非 curated 仓库漏判 domain
        full_domain[n] = domain_of_present[norm(r["file"])]
    else:
        full_domain[n] = "其他"

# 按 domain 分组 bullet
groups = {}
for r in final_rows:
    n = norm(r["repo"])
    d = full_domain[n]
    bullet = f"- [`{r['repo']}`](https://github.com/{r['repo']}) — [{r['file']}]({r['file']})"
    groups.setdefault(d, []).append(bullet)
for d in groups:
    groups[d].sort(key=lambda b: norm(repo_of(b) or b))

# 重新写 domain 段：保留原有 domain 顺序（去重），新 domain 追加在末尾
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
# 追加原段之后的内容（维护规则等）
rest = idx_text[sec_start:].split("\n")
# 找到原段结束（下一个 ## ）
endi = 0
for i, ln in enumerate(rest):
    if i > 0 and re.match(r"^## ", ln):
        endi = i; break
out.extend(rest[endi:])
io.open(IDX, "w", encoding="utf-8").write("\n".join(out))
print(f"[index] domain 段重建完成，domain 数={len(orig_domains)}")

# ============ 3) 总览 字母分组 + domain 段重建 ============
ov = io.open(OV, encoding="utf-8").read().split("\n")
# 字母分组
letter_sec_i = next(i for i, ln in enumerate(ov) if ln.startswith("## 📚 按字母分组索引"))
# 找到字母段结束（下一个 ## ）
letter_end = letter_sec_i + 1
while letter_end < len(ov) and not ov[letter_end].startswith("## "): letter_end += 1
letter_groups = {}
for r in final_rows:
    L0 = r["repo"][0].upper()
    bullet = f"- [`{r['repo']}`](https://github.com/{r['repo']}) — [{r['file']}]({r['file']})"
    letter_groups.setdefault(L0, []).append(bullet)
for L0 in letter_groups:
    letter_groups[L0].sort(key=lambda b: norm(repo_of(b) or b))
# 保留原有字母顺序
orig_letters = []
seen = set()
for ln in ov[letter_sec_i:letter_end]:
    m = re.match(r"^### ([A-Za-z0-9])（\d+ 个）$", ln)
    if m and m.group(1) not in seen:
        seen.add(m.group(1)); orig_letters.append(m.group(1))
for L0 in letter_groups:
    if L0 not in seen: orig_letters.append(L0)
# 数字字母排在前面更符合原序；这里简单按出现+追加
new_letter = ov[:letter_sec_i + 1]
for L0 in orig_letters:
    bullets = letter_groups.get(L0, [])
    new_letter.append(f"### {L0}（{len(bullets)} 个）")
    new_letter.extend(bullets)
new_letter.extend(ov[letter_end:])
ov = new_letter

# 总览 domain 段
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
# 计数 318->316
ov = ov.replace("owner-repo-深度调研.md × 318", "owner-repo-深度调研.md × 316")
ov = ov.replace("| 🎯 本文件 | 权威总览（仓库结构 + 按字母分组索引 + 按领域分类 + 调研方法） | 318 |",
                "| 🎯 本文件 | 权威总览（仓库结构 + 按字母分组索引 + 按领域分类 + 调研方法） | 316 |")
io.open(OV, "w", encoding="utf-8").write(ov)
print("[overview] 字母分组 + domain 段 + 计数 完成")

# ============ 4) 元目录 + README 计数 318->316 ============
yuan = io.open(YUAN, encoding="utf-8").read()
yuan = yuan.replace("owner-repo-深度调研.md × 318", "owner-repo-深度调研.md × 316")
yuan = yuan.replace("| [`GitHub 项目研究 — 全量规整后总览.md`](GitHub%20项目研究%20—%20全量规整后总览.md) | 🎯 权威总览（按字母分组索引 + 按领域分类 + 仓库结构 + 调研方法） | 318 |",
                    "| [`GitHub 项目研究 — 全量规整后总览.md`](GitHub%20项目研究%20—%20全量规整后总览.md) | 🎯 权威总览（按字母分组索引 + 按领域分类 + 仓库结构 + 调研方法） | 316 |")
yuan = yuan.replace("| [`GitHub 项目研究 — 全量索引表.md`](GitHub%20项目研究%20—%20全量索引表.md) | 📋 全量索引表，所有项目的表格索引（owner/repo + 定位 + Stars + 报告链接） | 318 |",
                    "| [`GitHub 项目研究 — 全量索引表.md`](GitHub%20项目研究%20—%20全量索引表.md) | 📋 全量索引表，所有项目的表格索引（owner/repo + 定位 + Stars + 报告链接） | 316 |")
yuan = yuan.replace("| 调研报告总数 | 318 |", "| 调研报告总数 | 316 |")
io.open(YUAN, "w", encoding="utf-8").write(yuan)
print("[meta] 318->316")

rd = io.open(README, encoding="utf-8").read()
rd = rd.replace("调研报告-318-blue", "调研报告-316-blue")
rd = rd.replace("| 调研报告总数 | **318** |", "| 调研报告总数 | **316** |")
rd = rd.replace("| [🎯 全量规整后总览](full-analysis/GitHub%20项目研究%20—%20全量规整后总览.md) | 全量维护后权威总览（按字母分组索引 + 按领域分类） | 318 |",
                "| [🎯 全量规整后总览](full-analysis/GitHub%20项目研究%20—%20全量规整后总览.md) | 全量维护后权威总览（按字母分组索引 + 按领域分类） | 316 |")
rd = rd.replace("| [📚 全量索引表](full-analysis/GitHub%20项目研究%20—%20全量索引表.md) | 所有项目的表格索引（项目名 / 定位 / Stars / 报告链接） | 318 |",
                "| [📚 全量索引表](full-analysis/GitHub%20项目研究%20—%20全量索引表.md) | 所有项目的表格索引（项目名 / 定位 / Stars / 报告链接） | 316 |")
rd = rd.replace("│   └── owner-repo-深度调研.md × 318", "│   └── owner-repo-深度调研.md × 316")
io.open(README, "w", encoding="utf-8").write(rd)
print("[readme] 318->316")
print("DONE")
