"""从153个调研报告批量提取元数据, 生成全量索引表。
提取: owner/repo, 一句话定位, Stars, 调研日期
输出: 全量索引表 markdown
"""
import os, re, json

os.chdir(r'E:\Lenovo\Documents\coding\github仓库调研\full-analysis')
files = sorted([f for f in os.listdir('.') if f.endswith('.md') and '元目录' not in f])

OWNER_REPO_RE = re.compile(r'([A-Za-z0-9][\w\-\.]{1,30})/([A-Za-z0-9][\w\-\.]{1,40})')
STARS_RE = re.compile(r'(?:Stars?|⭐|星)[^\d]*(\d[\d,\.]*)\s*[Kk⭐]?', re.I)
DATE_RE = re.compile(r'(2026-\d{2}-\d{2})')

def extract_meta(filepath):
    """提取 owner/repo, 一句话定位, Stars, 日期"""
    owner_repo = None
    oneliner = None
    stars = None
    date = None
    try:
        with open(filepath, 'r', encoding='utf-8') as fp:
            content = fp.read(3000)  # 读前3000字符足够
            # owner/repo
            m = OWNER_REPO_RE.search(content)
            if m:
                owner_repo = f"{m.group(1)}/{m.group(2)}"
            # stars
            m = STARS_RE.search(content)
            if m:
                stars = m.group(1)
            # date
            m = DATE_RE.search(content)
            if m:
                date = m.group(1)
            # 一句话定位: 找"一句话定位"后的内容
            m = re.search(r'一句话定位[：:]\s*([^\n。]{10,120})', content)
            if m:
                oneliner = m.group(1).strip()
            else:
                # fallback: 找"定位"后的内容
                m = re.search(r'定位[：:]\s*([^\n。]{10,120})', content)
                if m:
                    oneliner = m.group(1).strip()
    except Exception as e:
        pass
    return owner_repo, oneliner, stars, date

results = []
no_owner = []
for f in files:
    owner_repo, oneliner, stars, date = extract_meta(f)
    if not owner_repo:
        no_owner.append(f)
    results.append({
        'file': f,
        'owner_repo': owner_repo or f.replace('-深度调研.md', '/').replace('-', '/', 1).rstrip('/'),
        'oneliner': oneliner or '（未提取到定位）',
        'stars': stars or '数据不可用',
        'date': date or '未知',
    })

# 按字母排序
results.sort(key=lambda x: x['owner_repo'].lower())

print(f"总报告: {len(results)}")
print(f"成功提取owner/repo: {len([r for r in results if r['owner_repo'] != '未提取'] )}")
print(f"未提取owner/repo: {len(no_owner)}")
if no_owner:
    print("未提取的文件:")
    for f in no_owner:
        print(f"  {f}")

# 保存JSON
out_json = r'E:\Lenovo\Documents\coding\github仓库调研\scripts\index_data.json'
with open(out_json, 'w', encoding='utf-8') as fp:
    json.dump(results, fp, ensure_ascii=False, indent=2)
print(f"\n数据已保存: {out_json}")
print(f"\n前10条预览:")
for r in results[:10]:
    print(f"  {r['owner_repo']:40s} | {r['stars']:12s} | {r['date']} | {r['oneliner'][:50]}")
