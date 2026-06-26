"""生成全量索引表 markdown + 更新轻量元目录。"""
import json

with open(r'E:\Lenovo\Documents\coding\github仓库调研\scripts\index_data_v2.json', 'r', encoding='utf-8') as fp:
    results = json.load(fp)

# ========== 1. 全量索引表 ==========
md = []
md.append('# 📚 GitHub 项目研究 — 全量索引表')
md.append('')
md.append('> 本文件是 `full-analysis/` 下所有调研报告的全量索引。')
md.append(f'> 生成时间：2026-06-26 | 收录项目：**{len(results)}** 个')
md.append('')
md.append('## 阅读指引')
md.append('')
md.append('- 本表为**全量索引**，只列项目名/定位/Stars/日期/报告文件名，详情请打开对应报告。')
md.append('- 另有 [`github项目研究_元目录_20260616_v3.md`](github项目研究_元目录_20260616_v3.md) 为**精选深度详录**（16 个标杆项目，含核心发现摘要）。')
md.append('- 所有报告文件统一命名为 `owner-repo-深度调研.md`，位于 `full-analysis/` 目录。')
md.append('- Stars/日期标注「—」表示历史报告格式不统一未提取到，不代表项目无数据。')
md.append('')
md.append('## 📋 全量项目索引')
md.append('')
md.append('| # | owner/repo | 一句话定位 | Stars | 调研日期 | 报告文件 |')
md.append('|---|-----------|-----------|-------|---------|---------|')
for i, r in enumerate(results, 1):
    owner_repo = r['owner_repo'].replace('|', '\\|')
    desc = r['desc'][:80].replace('|', '\\|').replace('\n', ' ') if r['desc'] != '（详见报告）' else '—'
    stars = r['stars'] if r['stars'] != '—' else '—'
    date = r['date'] if r['date'] != '未知' else '—'
    fname = r['file'].replace('|', '\\|')
    md.append(f'| {i} | `{owner_repo}` | {desc} | {stars} | {date} | {fname} |')

md.append('')
md.append('---')
md.append('')
md.append(f'**统计**：共 {len(results)} 个项目 | 有描述 {len([r for r in results if r["desc"] != "（详见报告）"])} | 有 Stars {len([r for r in results if r["stars"] != "—"])} | 有日期 {len([r for r in results if r["date"] != "未知"])}')
md.append('')

# 技术领域分类（简单关键词分类）
categories = {
    'AI Agent / 助手框架': [],
    'AI 编码 / Skill 技能': [],
    'RAG / 知识库 / 记忆': [],
    '开发工具 / CLI': [],
    '前端 / 设计 / UI': [],
    '视频 / 音频 / 多媒体': [],
    '安全 / 运维 / 系统工具': [],
    '学习资料 / 方法论': [],
    '其他': [],
}
for r in results:
    o = r['owner_repo'].lower()
    d = r['desc'].lower() if r['desc'] != '（详见报告）' else ''
    f = r['file'].lower()
    if any(k in o+d+f for k in ['agent', 'openclaw', 'copilot', 'goose', 'nezha', 'superpowers', 'skill', 'ui-tars', 'skyvern']):
        categories['AI Agent / 助手框架'].append(r)
    elif any(k in o+d+f for k in ['skill', 'claude', 'cursor', 'coding', 'code', 'codex']):
        categories['AI 编码 / Skill 技能'].append(r)
    elif any(k in o+d+f for k in ['rag', 'graphrag', 'maxkb', 'knowledge', 'memory', 'recall', 'supermemory', 'cognee']):
        categories['RAG / 知识库 / 记忆'].append(r)
    elif any(k in o+d+f for k in ['cli', 'tool', 'mcp', 'opencli', 'crawl4ai', 'reader', 'jina']):
        categories['开发工具 / CLI'].append(r)
    elif any(k in o+d+f for k in ['figma', 'lottie', 'design', 'frontend', 'chart', 'infographic', 'remotion', 'excalidraw', 'penpot']):
        categories['前端 / 设计 / UI'].append(r)
    elif any(k in o+d+f for k in ['video', 'audio', 'voice', 'tts', 'lottie', 'vtuber', 'diffusion', 'stable-diffusion', 'fooocus', 'cosmos', 'triposplat']):
        categories['视频 / 音频 / 多媒体'].append(r)
    elif any(k in o+d+f for k in ['security', 'audit', 'win11', 'debloat', 'edge', 'firewall', 'cloudflare', 'remove']):
        categories['安全 / 运维 / 系统工具'].append(r)
    elif any(k in o+d+f for k in ['awesome', 'notes', 'leetcode', 'learn', 'hello', 'cs-notes', 'methodology']):
        categories['学习资料 / 方法论'].append(r)
    else:
        categories['其他'].append(r)

md.append('## 🏷️ 按技术领域分类')
md.append('')
for cat, items in categories.items():
    if items:
        md.append(f'### {cat}（{len(items)}）')
        md.append('')
        for r in items:
            md.append(f'- `{r["owner_repo"]}` — {r["file"]}')
        md.append('')

md.append('---')
md.append('')
md.append('## 📝 维护规则')
md.append('')
md.append('1. 新增调研报告后，必须在本表追加索引行。')
md.append('2. 报告文件统一命名：`owner-repo-深度调研.md`。')
md.append('3. 删除/合并报告时，同步更新本表。')
md.append('4. 本表只放摘要，深度详情放 `github项目研究_元目录_20260616_v3.md`（精选详录）。')
md.append('')

content = '\n'.join(md)
out_path = r'E:\Lenovo\Documents\coding\github仓库调研\full-analysis\GitHub 项目研究 — 全量索引表.md'
with open(out_path, 'w', encoding='utf-8') as fp:
    fp.write(content)
print(f"✅ 全量索引表已生成: {out_path}")
print(f"   收录 {len(results)} 个项目, {len(md)} 行")
