# boykopovar/AnyPS5 — 深度调研

> 调研日期：2026-10-08 ｜ 来源：GitHub Trending（当日新增，未入库）

## 1. 项目定位（一句话）
AnyPS5 是一个**把 PS5 原生可执行文件自动移植到 Linux / Windows 的 C++ 工具链**——通过 relinker 把可执行文件转成目标平台原生格式，并提供一套 PRX 系统库做动态链接，**无模拟器、无独立运行时进程**。

## 2. 项目亮点（差异化，开篇呈现）
- **零模拟、原生运行**：与 RPCS3 等模拟器路线根本不同——relinker 直接转换可执行格式，PRX 库实现 PS5 系统调用动态链接，进程内原生执行。
- **模块化 core 分层**：`relinker`（格式转换）/ `libs/prx`（系统库）/ `shader/recompiler`（SPIR-V 重编译）/ `Decoder`，各司其职。
- **真实可玩验证**：Dreaming Sarah（2D 平台）在 GTX 1050 Ti / i5-7500 稳定 60fps；项目用 badge 公示"已知系统库函数占比"进度，公开透明。
- **严格错误处理**：不支持/未预期状态一律 `throw std::runtime_error`，`what()` 打印 stderr 并终止——失败可观测、不静默。
- **合规声明明确**：仅用于互操作/研究/保存/兼容，不含/不分发/不依赖版权固件、密钥或专有库。

## 3. 核心架构
```
AnyPS5/
 ├─ core/relinker/        可执行格式转换 → 目标平台原生格式
 ├─ core/libs/prx/         PS5 系统 PRX 库（动态链接实现，按函数声明进度增长）
 ├─ core/shader/recompiler/Recompiler.cpp  着色器重编译器 → SPIR-V
 ├─ core/Decoder/          解码相关
 ├─ 3rdparty/SPIRV-Tools   SPIR-V 校验（编译开 ANYPS5_ENABLE_SPIRV_TOOLS）
 ├─ tools/  docs/  CMakeLists.txt  (.gitmodules 拉子模块)
```
构建走标准 CMake（`cmux` 风格不同，这里是跨平台 C++ 工程）；`docs/dev/ARCHITECTURE.md` 与 `TechnicalDebt.md` 公开架构与技术债，工程透明度高。

## 4. 应用场景与启发
- **给同类需求的解法**：把"平台二进制移植"拆成"格式 relink + 系统库桩 + 着色器重编译"三件独立可验证的事，比"写个大模拟器"务实得多——可复用到任何"二进制兼容性/旧平台保存"问题。
- 与研究/保存（preservation）强相关：为不再可得的硬件生态提供软件层延续。
- 与今日同批调研的 `morluto/rea` 形成对照：rea 是"理解后重建行为"，AnyPS5 是"就地原生重定位"——两者都是"跨平台可互操作"谱系。

## 5. 源码深度解读
**① relinker（core/relinker）**
负责把 PS5 可执行文件转换为目标系统的原生可执行格式。关键是**不模拟、只重定位**——把原平台的加载/链接假设映射到本机加载器，使进程能在宿主直接跑，省去运行时开销。README 强调"no emulation or separate runtime process"。

**② PRX 系统库（core/libs/prx）**
实现 PS5 系统库（prx）的动态链接版本。函数以声明形式逐步补齐，`badge-libraries.svg` 公示"项目已知的函数占比"（非全部 PS5 系统函数）。这种**众包式按函数填坑**的进度模型，让外部贡献者能精准认领缺口。

**③ 着色器重编译器（core/shader/recompiler/Recompiler.cpp）**
把 PS5 着色器成功产出 SPIR-V，并可用 `3rdparty/SPIRV-Tools` 校验（编译开 `ANYPS5_ENABLE_SPIRV_TOOLS`）。这是"图形可玩"的关键——没有它只能跑逻辑、跑不了画面。

## 6. 社区口碑
- 9.6k⭐、723 forks、288 open issues（活跃但问题多，符合早期硬核逆向工程项目的特征），2026-08 创建、10-07 仍在高频推送。
- 进度 badge 与 COMPATIBILITY.md（已验证游戏清单）让社区能直观判断成熟度；免责声明降低了法律/伦理顾虑。
- 属小众硬核（console RE）圈层，star 增速稳健非 viral，含金量高于同日多数 Trending 项。

## 7. 竞品对比 + 核心研判
| 维度 | AnyPS5 | RPCS3(PS3 模拟) | 其他模拟器 |
|------|--------|------------------|------------|
| 执行方式 | 原生 relink | 模拟执行 | 模拟执行 |
| 运行时开销 | 低 | 高 | 高 |
| 覆盖范围 | PS5 早期 | PS3 成熟 | 各异 |
| 合规姿态 | 明确仅互操作 | 类似 | 类似 |

**研判**：AnyPS5 走的是"原生移植"而非"模拟"的少有人走通的路，工程取向务实且模块边界清晰。价值在于为 PS5 生态的软件保存提供轻量路径。风险与边界：① 进度早期，系统库覆盖有限，多数游戏暂不可玩；② console RE 长期游走在厂商 DMCA 边缘，合规声明虽明确但未来仍有政策风险；③ 强依赖社区按函数填坑，可持续性看贡献者基数。对"二进制兼容性/格式重定位"工程，relinker+prx 桩的拆分思路值得借鉴。

## 8. 关键文件路径速查
- 核心：`core/relinker/`、`core/libs/prx/`、`core/shader/recompiler/Recompiler.cpp`、`core/Decoder/`
- 第三方校验：`3rdparty/SPIRV-Tools`
- 文档：`docs/dev/ARCHITECTURE.md`、`docs/dev/TechnicalDebt.md`、`docs/dev/BUILD.md`、`docs/dev/CONVENTIONS.md`、`docs/user/USAGE.md`、`docs/user/COMPATIBILITY.md`、`docs/user/INPUT_MAPPING.md`
- 工程根：`CMakeLists.txt`、`.gitmodules`、`CONTRIBUTING.md`、`LICENSE`(GPL-2.0 only)
