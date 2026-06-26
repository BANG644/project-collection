"""执行重命名: 从 rename_mapping_v3.json 读取映射, 用 os.rename 执行。
- 跳过 new==old 的情况
- 记录成功/失败
- 输出最终文件列表
"""
import os, json

mapping_path = r'E:\Lenovo\Documents\coding\github仓库调研\scripts\rename_mapping_v3.json'
os.chdir(r'E:\Lenovo\Documents\coding\github仓库调研\full-analysis')

with open(mapping_path, 'r', encoding='utf-8') as fp:
    data = json.load(fp)

mapping = [(o, n) for o, n in data['mapping'] if o != n]
print(f"待重命名: {len(mapping)}")

success = 0
skipped = 0
failed = []
for old, new in mapping:
    if not os.path.exists(old):
        print(f"  ⚠️ 源文件不存在: {old}")
        failed.append((old, new, '源不存在'))
        continue
    if os.path.exists(new) and old != new:
        print(f"  ⚠️ 目标已存在: {new} (源: {old})")
        failed.append((old, new, '目标已存在'))
        continue
    try:
        os.rename(old, new)
        success += 1
    except Exception as e:
        print(f"  ❌ 失败: {old} -> {new}: {e}")
        failed.append((old, new, str(e)))

print(f"\n✅ 成功: {success}")
print(f"⏭️ 跳过: {skipped}")
print(f"❌ 失败: {len(failed)}")
if failed:
    for old, new, reason in failed:
        print(f"  {old} -> {new}: {reason}")

# 最终文件列表
final_files = sorted([f for f in os.listdir('.') if f.endswith('.md')])
print(f"\n最终文件数: {len(final_files)}")
# 验证: 是否还有非规范文件名
non_standard = [f for f in final_files if not f.endswith('-深度调研.md') and '元目录' not in f and 'README' not in f]
if non_standard:
    print(f"\n⚠️ 非 owner-repo-深度调研.md 格式的文件({len(non_standard)}):")
    for f in non_standard:
        print(f"  {f}")
else:
    print("\n✅ 所有报告文件均符合 owner-repo-深度调研.md 格式")
