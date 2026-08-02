# -*- coding: utf-8 -*-
import io

BASE = r"E:\Lenovo\Documents\coding\github仓库调研"
META = f"{BASE}/full-analysis/GitHub 项目研究 — 元目录.md"
README = f"{BASE}/README.md"

def read(p):
    with io.open(p, encoding="utf-8") as f:
        return f.read()
def write(p, s):
    with io.open(p, "w", encoding="utf-8") as f:
        f.write(s)

# ---- 元目录.md ----
m = read(META)
assert m.count("owner-repo-深度调研.md × 314") == 1, "meta count1"
m = m.replace("owner-repo-深度调研.md × 314", "owner-repo-深度调研.md × 316")
assert m.count("| 314 |") == 3, f"meta |314| expected 3, got {m.count('| 314 |')}"
m = m.replace("| 314 |", "| 316 |")
assert "314" not in m, "meta still has 314"
write(META, m)

# ---- README.md ----
r = read(README)
assert r.count("| 调研报告总数 | **314** |") == 1, "readme count"
r = r.replace("| 调研报告总数 | **314** |", "| 调研报告总数 | **316** |")
assert "**314**" not in r, "readme still has 314"
write(README, r)

print("META + README UPDATED OK (314 -> 316)")
