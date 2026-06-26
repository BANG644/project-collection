"""生成 full-analysis/ 下所有调研报告的规范化重命名映射。
规范: owner-repo-深度调研.md  (owner/repo 的斜杠改短横线)
- 元目录文件不参与重命名
- 输出 mapping 供 review
"""
import os, re, json

os.chdir(r'E:\Lenovo\Documents\coding\github仓库调研\full-analysis')
files = sorted([f for f in os.listdir('.') if f.endswith('.md')])

# 元目录文件不重命名
META_KEYWORDS = ['元目录', 'README', '使用原则', '索引']
def is_meta(name):
    return any(k in name for k in META_KEYWORDS)

def to_owner_repo(name):
    """从任意命名模式提取 owner-repo 并生成规范文件名"""
    n = name.replace('.md', '')
    original = n

    # 1. 去掉前缀
    n = re.sub(r'^\d{4}-\d{2}-\d{2}_', '', n)          # 2026-06-18_xxx
    n = re.sub(r'^batch\d+_\d+_', '', n)                # batch02_18_xxx / batch03_48_xxx
    n = re.sub(r'^batch\d+_', '', n)                     # batchXX_xxx
    n = re.sub(r'^trending_\d{4}-\d{2}-\d{2}_', '', n) # trending_2026-06-19_xxx
    n = re.sub(r'^报告_', '', n)                          # 报告_xxx
    n = re.sub(r'^\d+_', '', n)                           # 纯数字前缀

    # 2. 去掉尾部截断标记 ....
    n = n.rstrip('.').strip()

    # 3. 去掉常见后缀变体,统一为 -深度调研
    suffixes = [
        ' - 全方位深度调研', '- 全方位深度调研', '_全方位深度调研', '全方位深度调研',
        ' - 深度调研报告', '- 深度调研报告', '_深度调研报告', '深度调研报告',
        '_深度调研', '-深度调研', ' 深度调研报告', '深度调研',
        '_deep_dive', '-deep_dive', '_deep_dive_深度调研',
        'batch03_deep_dive', '_batch03_deep_dive',
        ' - 全方位深度调研报告',
    ]
    # 按长度降序匹配,避免短后缀先匹配
    suffixes_sorted = sorted(set(suffixes), key=len, reverse=True)
    matched = True
    while matched:
        matched = False
        for suf in suffixes_sorted:
            if n.endswith(suf):
                n = n[:-len(suf)]
                matched = True
                break
    # 再清理一次尾部可能的 - _ 空格
    n = n.rstrip('-_ ').strip()

    # 4. 统一分隔符: owner/repo 或 owner_repo 或 owner repo -> owner-repo
    # 但保留中文标题里的空格(如 "MaxKB — 开源..." 这种不是 owner-repo 格式)
    # 判断是否是 owner-repo 模式: 含 / 或 含下划线且前半段像owner
    if '/' in n:
        # owner/repo
        parts = n.split('/', 1)
        owner = parts[0].strip()
        repo = parts[1].strip()
        n = f"{owner}-{repo}"
    else:
        # 检查是否 owner_repo 或 owner-repo 模式
        # 如果是中文标题式(含中文且无明确owner/repo结构),保持原样加-深度调研
        has_clear_owner = bool(re.match(r'^[A-Za-z0-9][\w\-]*[ _-][A-Za-z0-9]', n))
        if has_clear_owner and '_' in n:
            # owner_repo -> owner-repo, 但只替换第一个分隔
            # 实际上很多是 owner_repo_name, 需要判断
            # 简化: 把所有 _ 换成 - (因为repo名本身不含_)
            n = n.replace('_', '-')
        elif has_clear_owner and ' ' in n and not re.search(r'[\u4e00-\u9fff]', n):
            n = n.replace(' ', '-', 1)

    # 5. 处理特殊情况: 中文标题式命名(无owner/repo结构)
    # 这些保持原名 + -深度调研
    is_chinese_title = bool(re.search(r'[\u4e00-\u9fff—]', n)) and '/' not in original and not re.match(r'^[A-Za-z0-9][\w\-]*[ _-][A-Za-z0-9][\w\-]*$', n)

    # 6. 最终: 加 -深度调研 后缀
    if not n.endswith('深度调研'):
        new_name = f"{n}-深度调研.md"
    else:
        new_name = f"{n}.md"

    # 7. 清理多余空格
    new_name = re.sub(r'\s+', '-', new_name).strip()
    # 清理连续短横线
    new_name = re.sub(r'-{2,}', '-', new_name)
    # 清理首尾短横线
    new_name = new_name.strip('-')

    return new_name

mapping = []
conflicts = {}
for f in files:
    if is_meta(f):
        continue
    new = to_owner_repo(f)
    if new != f:
        mapping.append((f, new))
        conflicts.setdefault(new, []).append(f)

# 检查目标名冲突
print(f"需重命名文件数: {len(mapping)}")
print(f"目标名冲突检查:")
real_conflicts = {k: v for k, v in conflicts.items() if len(v) > 1}
if real_conflicts:
    print(f"  ⚠️ 发现 {len(real_conflicts)} 个目标名冲突:")
    for k, v in real_conflicts.items():
        print(f"    {k} <- {v}")
else:
    print("  ✅ 无目标名冲突")

# 也检查与未重命名文件的冲突
all_targets = set()
unchanged = [f for f in files if not is_meta(f) and to_owner_repo(f) == f]
for f in unchanged:
    all_targets.add(f)
for _, new in mapping:
    if new in all_targets:
        print(f"  ⚠️ 重命名目标 {new} 与现有未重命名文件冲突!")

# 输出映射到JSON
out_path = r'E:\Lenovo\Documents\coding\github仓库调研\scripts\rename_mapping.json'
with open(out_path, 'w', encoding='utf-8') as fp:
    json.dump({'mapping': mapping, 'total': len(mapping)}, fp, ensure_ascii=False, indent=2)

print(f"\n映射已保存: {out_path}")
print(f"\n前30条预览:")
for old, new in mapping[:30]:
    print(f"  {old}")
    print(f"   -> {new}")
