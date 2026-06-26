"""v2: 改进元数据提取 - 从标题/前几行提取项目描述, 修正Stars提取。"""
import os, re, json

os.chdir(r'E:\Lenovo\Documents\coding\github仓库调研\full-analysis')
files = sorted([f for f in os.listdir('.') if f.endswith('.md') and '元目录' not in f])

OWNER_REPO_RE = re.compile(r'([A-Za-z0-9][\w\-\.]{1,30})/([A-Za-z0-9][\w\-\.]{1,40})')

def extract_meta(filepath):
    owner_repo = None
    desc = None
    stars = None
    date = None
    try:
        with open(filepath, 'r', encoding='utf-8') as fp:
            lines = fp.read(5000).split('\n')
            full = '\n'.join(lines)

            # owner/repo
            m = OWNER_REPO_RE.search(full)
            if m:
                owner_repo = f"{m.group(1)}/{m.group(2)}"

            # date
            m = re.search(r'(2026-\d{2}-\d{2})', full)
            if m:
                date = m.group(1)

            # stars: 更精确匹配 K/万 结尾或纯数字
            patterns = [
                r'[Ss]tars?[:：\s]*(\d{1,3}(?:,\d{3})*(?:\.\d+)?)\s*[Kk⭐]?',
                r'⭐\s*(\d{1,3}(?:,\d{3})*(?:\.\d+)?)\s*[Kk⭐]?',
                r'(\d{1,3}(?:,\d{3})*)\s*[Kk]⭐',
                r'(\d{1,3}(?:,\d{3})*)\s*⭐',
                r'⭐\s*(\d+(?:\.\d+)?)\s*[Kk]',
            ]
            for p in patterns:
                m = re.search(p, full)
                if m:
                    stars = m.group(1)
                    # 如果是纯数字且较小,检查后面是否有K
                    if re.match(r'^\d+$', stars) and int(stars.replace(',','')) < 1000:
                        # 检查是否附近有K
                        if 'K' in full[m.end():m.end()+3] or 'k' in full[m.end():m.end()+3]:
                            stars = stars + 'K'
                    break

            # 描述: 多策略
            # 策略1: "一句话定位" 后的内容
            m = re.search(r'一句话定位[：:]\s*\*?\*?([^\n]{8,150})', full)
            if m:
                desc = m.group(1).strip().strip('*').strip()
            else:
                # 策略2: "定位" 后的内容
                m = re.search(r'项目定位[：:]\s*([^\n]{8,150})', full)
                if m:
                    desc = m.group(1).strip()
                else:
                    # 策略3: 第一行 # 标题 去掉 owner/repo 后的部分
                    for line in lines[:5]:
                        line = line.strip()
                        if line.startswith('#'):
                            title = re.sub(r'^#+\s*', '', line)
                            title = re.sub(r'^[🔬🔍📌⌚📚🧠🌐⚙️⚔️🎯📂⭐🔥🎤🚢📄🛡️📊]+\s*', '', title)
                            # 去掉 owner/repo
                            title = OWNER_REPO_RE.sub('', title).strip(' -—–')
                            # 去掉常见后缀
                            for suf in ['全方位深度调研报告', '深度调研报告', '全方位深度调研', '深度调研']:
                                if title.endswith(suf):
                                    title = title[:-len(suf)].strip(' -—–')
                                    break
                            if len(title) > 5:
                                desc = title[:100]
                                break
    except Exception:
        pass

    return owner_repo, desc, stars, date

results = []
for f in files:
    owner_repo, desc, stars, date = extract_meta(f)
    # 从文件名生成 owner-repo 作为 fallback
    if not owner_repo:
        base = f.replace('-深度调研.md', '')
        parts = base.split('-', 1)
        owner_repo = f"{parts[0]}/{parts[1]}" if len(parts) > 1 else base
    results.append({
        'file': f,
        'owner_repo': owner_repo,
        'desc': desc or '（详见报告）',
        'stars': stars or '—',
        'date': date or '未知',
    })

results.sort(key=lambda x: x['owner_repo'].lower())

# 统计
has_desc = len([r for r in results if r['desc'] != '（详见报告）'])
has_stars = len([r for r in results if r['stars'] != '—'])
has_date = len([r for r in results if r['date'] != '未知'])
print(f"总: {len(results)} | 有描述: {has_desc} | 有Stars: {has_stars} | 有日期: {has_date}")

out_json = r'E:\Lenovo\Documents\coding\github仓库调研\scripts\index_data_v2.json'
with open(out_json, 'w', encoding='utf-8') as fp:
    json.dump(results, fp, ensure_ascii=False, indent=2)
print(f"保存: {out_json}")
print("\n前15条:")
for r in results[:15]:
    print(f"  {r['owner_repo']:42s} | {r['stars']:10s} | {r['date']} | {r['desc'][:50]}")
