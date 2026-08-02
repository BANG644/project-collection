# -*- coding: utf-8 -*-
import io
README = r"E:\Lenovo\Documents\coding\github仓库调研\README.md"
r = io.open(README, encoding="utf-8").read()
r = r.replace("调研报告-314-blue", "调研报告-316-blue")
n = r.count("| 314 |")
assert n == 2, f"expected 2 '| 314 |', found {n}"
r = r.replace("| 314 |", "| 316 |")
assert r.count("× 314") == 1, f"expected 1 '× 314', found {r.count('× 314')}"
r = r.replace("× 314", "× 316")
assert "314" not in r, "README still has 314"
io.open(README, "w", encoding="utf-8").write(r)
print("README residual 314 fixed (->316)")
