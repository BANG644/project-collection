"""v2: 从文件内容第一行 # 标题 提取真实 owner/repo，生成规范重命名映射。
规范: owner-repo-深度调研.md (斜杠改短横线)
- 元目录文件不参与
- 中文标题式文件(无owner/repo结构)保持清理后原标题
- 截断文件名(....md)从内容恢复真实名
"""
import os, re, json

os.chdir(r'E:\Lenovo\Documents\coding\github仓库调研\full-analysis')
files = sorted([f for f in os.listdir('.') if f.endswith('.md')])

META_KEYWORDS = ['元目录', 'README']
def is_meta(name):
    return any(k in name for k in META_KEYWORDS)

def extract_owner_repo(filepath):
    """从文件第一行 # 标题提取 owner/repo。
    支持格式:
      # owner/repo - xxx
      # 🔬 owner/repo - xxx
      # owner/repo 深度调研
      # owner/repo（xxx）深度调研
    """
    try:
        with open(filepath, 'r', encoding='utf-8') as fp:
            for _ in range(10):  # 读前10行找标题
                line = fp.readline()
                if not line:
                    break
                line = line.strip()
                if line.startswith('#'):
                    # 去掉 # 和 emoji
                    title = re.sub(r'^#+\s*', '', line)
                    title = re.sub(r'^[🔬🔍📌⌚📚🧠🌐⚙️⚔️🎯📂⭐]+\s*', '', title)
                    # 尝试匹配 owner/repo
                    m = re.search(r'([A-Za-z0-9][\w\-\.]*)/([A-Za-z0-9][\w\-\.]*)', title)
                    if m:
                        owner = m.group(1)
                        repo = m.group(2)
                        return f"{owner}-{repo}", title
                    return None, title  # 无 owner/repo,返回标题
    except Exception as e:
        return None, None
    return None, None

def is_chinese_title(title):
    """判断是否是中文标题式(无owner/repo)"""
    if not title:
        return False
    # 含中文字符且无 owner/repo 模式
    has_chinese = bool(re.search(r'[\u4e00-\u9fff]', title))
    has_owner_repo = bool(re.search(r'[A-Za-z0-9][\w\-\.]*/[A-Za-z0-9][\w\-\.]*', title))
    return has_chinese and not has_owner_repo

def clean_chinese_title_filename(title):
    """中文标题清理为合法文件名"""
    n = title
    # 去掉后缀变体
    suffixes = [' - 全方位深度调研', '- 全方位深度调研', '全方位深度调研',
                ' - 深度调研报告', '深度调研报告', ' 深度调研', '深度调研',
                ' - 全方位深度调研报告']
    for suf in sorted(set(suffixes), key=len, reverse=True):
        if n.endswith(suf):
            n = n[:-len(suf)]
            break
    # 空格转短横线
    n = n.replace(' ', '-').replace('—', '-')
    # 清理连续短横线和首尾
    n = re.sub(r'-{2,}', '-', n).strip('-')
    return n + '-深度调研.md'

mapping = []
no_owner_repo = []
conflicts = {}

for f in files:
    if is_meta(f):
        continue
    filepath = os.path.join('.', f)
    owner_repo, title = extract_owner_repo(filepath)

    if owner_repo:
        new_name = f"{owner_repo}-深度调研.md"
    elif title and is_chinese_title(title):
        new_name = clean_chinese_title_filename(title)
        no_owner_repo.append((f, title, new_name))
    else:
        # fallback: 用原文件名清理
        n = f.replace('.md', '')
        n = re.sub(r'^\d{4}-\d{2}-\d{2}_', '', n)
        n = re.sub(r'^batch\d+_\d+_', '', n)
        n = re.sub(r'^trending_\d{4}-\d{2}-\d{2}_', '', n)
        n = re.sub(r'^报告_', '', n)
        n = n.rstrip('.').strip()
        for suf in [' - 全方位深度调研', '全方位深度调研', '深度调研报告', ' 深度调研', '深度调研', '_deep_dive', 'batch03_deep_dive']:
            if n.endswith(suf):
                n = n[:-len(suf)]
                break
        if '_' in n and '/' not in n:
            n = n.replace('_', '-')
        n = n.replace(' ', '-').replace('—', '-')
        n = re.sub(r'-{2,}', '-', n).strip('-')
        new_name = n + '-深度调研.md'
        no_owner_repo.append((f, f"FALLBACK: {title}", new_name))

    if new_name != f:
        mapping.append((f, new_name))
        conflicts.setdefault(new_name, []).append(f)

# 冲突检查
print(f"总报告文件: {len([f for f in files if not is_meta(f)])}")
print(f"需重命名: {len(mapping)}")
print(f"无需重命名: {len([f for f in files if not is_meta(f)]) - len(mapping)}")
print()

real_conflicts = {k: v for k, v in conflicts.items() if len(v) > 1}
if real_conflicts:
    print(f"⚠️ 目标名冲突 {len(real_conflicts)} 个:")
    for k, v in real_conflicts.items():
        print(f"  {k} <- {v}")
else:
    print("✅ 无目标名冲突")

# 检查与未重命名文件冲突
unchanged_files = set(f for f in files if not is_meta(f) and (f, f) not in [(o, n) for o, n in mapping] and f not in [o for o, n in mapping])
target_set = set(n for _, n in mapping)
overlap = unchanged_files & target_set
if overlap:
    print(f"⚠️ 与现有文件冲突: {overlap}")

print(f"\n无owner/repo的中文标题文件({len(no_owner_repo)}个):")
for f, title, new in no_owner_repo:
    print(f"  {f}")
    print(f"    title: {title[:60]}")
    print(f"    -> {new}")

# 保存映射
out_path = r'E:\Lenovo\Documents\coding\github仓库调研\scripts\rename_mapping_v2.json'
with open(out_path, 'w', encoding='utf-8') as fp:
    json.dump({'mapping': mapping, 'no_owner_repo': [(f, t, n) for f, t, n in no_owner_repo]}, fp, ensure_ascii=False, indent=2)
print(f"\n映射已保存: {out_path}")
