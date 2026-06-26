"""v3: 更稳健地从文件第一行(不管是否#开头)提取 owner/repo。
关键修正: 很多QClaw时期文件第一行是压缩正文(无#标题)，但含 owner/repo。
"""
import os, re, json

os.chdir(r'E:\Lenovo\Documents\coding\github仓库调研\full-analysis')
files = sorted([f for f in os.listdir('.') if f.endswith('.md')])

META_KEYWORDS = ['元目录', 'README']
def is_meta(name):
    return any(k in name for k in META_KEYWORDS)

OWNER_REPO_RE = re.compile(r'([A-Za-z0-9][\w\-\.]{1,30})/([A-Za-z0-9][\w\-\.]{1,40})')

def extract_owner_repo(filepath):
    """从文件前5行提取 owner/repo。"""
    try:
        with open(filepath, 'r', encoding='utf-8') as fp:
            for i in range(5):
                line = fp.readline()
                if not line:
                    break
                m = OWNER_REPO_RE.search(line)
                if m:
                    owner = m.group(1)
                    repo = m.group(2)
                    # 过滤掉明显不是github owner/repo的(如包含数字串、太短)
                    if len(owner) >= 2 and len(repo) >= 2:
                        return f"{owner}-{repo}"
    except Exception:
        pass
    return None

def clean_filename_fallback(name):
    """文件名 fallback 清理。"""
    n = name.replace('.md', '')
    # 去前缀
    n = re.sub(r'^\d{4}-\d{2}-\d{2}_', '', n)
    n = re.sub(r'^batch\d+_\d+_', '', n)
    n = re.sub(r'^batch\d+_', '', n)
    n = re.sub(r'^trending_\d{4}-\d{2}-\d{2}_', '', n)
    n = re.sub(r'^报告_', '', n)
    n = re.sub(r'^\d+_', '', n)
    n = n.rstrip('.').strip()
    # 去后缀
    suffixes = [' - 全方位深度调研', '- 全方位深度调研', '_全方位深度调研', '全方位深度调研',
                ' - 深度调研报告', '- 深度调研报告', '_深度调研报告', ' 深度调研报告', '深度调研报告',
                '_深度调研', '-深度调研', ' 深度调研', '深度调研',
                '_deep_dive', '-deep_dive', '_batch03_deep_dive', 'batch03_deep_dive',
                '_20260621', '-20260621',
                '_20260612_1755']
    for suf in sorted(set(suffixes), key=len, reverse=True):
        if n.endswith(suf):
            n = n[:-len(suf)]
            break
    # 分隔符统一
    n = n.replace('_', '-').replace(' ', '-').replace('—', '-')
    n = re.sub(r'-{2,}', '-', n).strip('-')
    return n

mapping = []
no_owner_repo = []
conflicts = {}

for f in files:
    if is_meta(f):
        continue
    filepath = os.path.join('.', f)
    owner_repo = extract_owner_repo(filepath)

    if owner_repo:
        new_name = f"{owner_repo}-深度调研.md"
    else:
        # fallback: 文件名清理
        cleaned = clean_filename_fallback(f)
        new_name = f"{cleaned}-深度调研.md" if not cleaned.endswith('深度调研') else f"{cleaned}.md"
        no_owner_repo.append((f, new_name))

    # 清理 new_name 中的连续短横线和首尾
    new_name = re.sub(r'-{2,}', '-', new_name).strip('-')

    if new_name != f:
        mapping.append((f, new_name))
        conflicts.setdefault(new_name, []).append(f)

print(f"总报告文件: {len([f for f in files if not is_meta(f)])}")
print(f"需重命名: {len(mapping)}")
print(f"无需重命名: {len([f for f in files if not is_meta(f)]) - len(mapping)}")
print(f"无owner/repo(fallback): {len(no_owner_repo)}")
print()

# 冲突检查
real_conflicts = {k: v for k, v in conflicts.items() if len(v) > 1}
if real_conflicts:
    print(f"⚠️ 目标名冲突 {len(real_conflicts)} 个:")
    for k, v in real_conflicts.items():
        print(f"  {k}")
        for src in v:
            print(f"    <- {src}")
else:
    print("✅ 无目标名冲突")

# 与未重命名文件冲突检查
all_new_names = set(n for _, n in mapping)
unchanged = set(f for f in files if not is_meta(f) and f not in [o for o, _ in mapping])
overlap = all_new_names & unchanged
if overlap:
    print(f"⚠️ 与未重命名文件冲突: {overlap}")

print(f"\n=== 无owner/repo的fallback文件({len(no_owner_repo)}) ===")
for f, n in no_owner_repo:
    print(f"  {f} -> {n}")

out_path = r'E:\Lenovo\Documents\coding\github仓库调研\scripts\rename_mapping_v3.json'
with open(out_path, 'w', encoding='utf-8') as fp:
    json.dump({'mapping': mapping, 'no_owner_repo': no_owner_repo}, fp, ensure_ascii=False, indent=2)
print(f"\n映射已保存: {out_path}")
