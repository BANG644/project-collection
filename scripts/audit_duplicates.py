import os, re
from collections import defaultdict

os.chdir(r'E:\Lenovo\Documents\coding\github仓库调研\full-analysis')
files = [f for f in os.listdir('.') if f.endswith('.md')]
meta_files = [f for f in files if '元目录' in f or 'README' in f]
files = [f for f in files if f not in meta_files]

def normalize(name):
    n = name.replace('.md','')
    n = re.sub(r'^\d{4}-\d{2}-\d{2}_', '', n)
    n = re.sub(r'^batch\d+_\d+_', '', n)
    n = re.sub(r'^trending_\d{4}-\d{2}-\d{2}_', '', n)
    n = re.sub(r'^报告_', '', n)
    n2 = n.replace('-','_').replace(' ','_')
    for suf in ['_深度调研','深度调研','全方位深度调研','深度调研报告','_深度调研报告','batch03_deep_dive','_deep_dive','deep_dive','_全方位深度调研']:
        if n2.endswith(suf):
            n2 = n2[:-len(suf)]
            break
    n2 = n2.lower()
    return n2

groups = defaultdict(list)
for f in files:
    groups[normalize(f)].append(f)

print(f"总文件: {len(files)}, 规范化分组: {len(groups)}")
print()
print("===疑似重复组（>1个文件）===")
dup_count = 0
for k, v in sorted(groups.items()):
    if len(v) > 1:
        dup_count += 1
        print(f"\n[{k}]")
        for f in v:
            size = os.path.getsize(f)
            print(f"  {f}  ({size} bytes)")

print(f"\n共 {dup_count} 组疑似重复")
