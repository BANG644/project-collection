# ntdevlabs/tiny11builder — 深度调研

> 调研日期：2026-10-15 ｜ 星标：20,138 ⭐ ｜ 语言：C# / .NET（WinUI 3）+ PowerShell ｜ 协议：**未声明标准 SPDX**（仓库含 `NOTICE.md` 归属/分发说明，GitHub 未检测到许可证）｜ 默认分支：main ｜ 厂商：ntdevlabs（ntdev）｜ 标签：Trending 日榜

## 1. 项目定位（一句话）
**原生 WinUI 3 桌面应用，用来制作"瘦身版 Windows 11 ISO"**：下载官方镜像或用自有镜像，勾选要移除的内容，一键生成更小的可安装 ISO——是知名 `tiny11` 项目的官方图形化 builder。

## 2. 项目亮点（差异化，开篇呈现）
- **原生 WinUI 3 图形界面**：不再是纯 PowerShell 脚本，而是 .NET 解决方案（`Tiny11Builder.sln` + `global.json` 锁 .NET SDK + `Directory.Build.props` 共享构建配置），体验远好于命令行。
- **三种构建模式**：`Tiny11`（移除捆绑应用与多余功能，保留更新/Defender/恢复）、`Tiny11 Core`（进一步移除 servicing/恢复并关闭 Defender，**不可更新/不可维护**）、`Custom`（逐项勾选要移除/保留的 app/组件/功能/服务）。
- **Turbo 模式 + 断点续建**：加速镜像处理；构建中断后，镜像已提交/压缩则可从已保存进度恢复。
- **保留原 PowerShell 构建器**：`tiny11maker.ps1` 与 `tiny11Coremaker.ps1` 仍留在仓库（`scripts/` 与根目录），命令行用户/老工作流可继续用。
- **标准无人参与应答文件**：`autounattend.xml` 提供无人值守安装骨架，是"去胖"的核心机制之一。
- **跨架构分发**：Release 提供 x64（Intel/AMD）与 ARM64（Windows on ARM）版本，解压即以 `Tiny11Builder.exe` 运行（需管理员批准）。

## 3. 核心架构
```
Tiny11Builder.sln
├── src/
│   ├── Tiny11Builder.App       # WinUI 3 前端（UI 交互：模式选择/组件勾选/构建设置）
│   └── Tiny11Builder.Core      # .NET 核心库（镜像处理逻辑，App 调用的业务层）
├── scripts/
│   └── package.ps1             # 打包脚本
├── tiny11maker.ps1             # 原版构建器（标准 Tiny11）
├── tiny11Coremaker.ps1         # 原版 Core 构建器（更激进裁剪）
├── autounattend.xml            # 无人参与安装应答文件
├── global.json                 # .NET SDK 版本锁定
├── Directory.Build.props       # 共享 MSBuild 属性
├── docs/                       # usage.md（用法/兼容性/构建指引）+ 截图
└── NOTICE.md                   # 归属与分发说明
```
- **分层**：`App`（WinUI 3 表现层）与 `Core`（.NET 业务逻辑层）分离，UI 不直接碰镜像操作，便于测试与复用。
- **去胖机制**：由 PowerShell 构建器（`tiny11maker.ps1` 等）实际执行组件移除，App 本质是对其的图形化封装 + 应答文件生成；`Core` 库负责组装与驱动。
- **构建产物**：自定义/组件级移除会自动回退到传统 Windows 安装器（legacy Windows installer）。

## 4. 应用场景与启发
- **低配机 / 虚拟机 / 老旧 PC 的 Win11 精简**：去掉 Cortana/Edge 捆绑、多余 Appx，减小体积、提升响应——对跑开发虚拟机的用户友好。
- **对"图形化封装命令行工具"的范式启发**：ntdev 把原本难用的 PowerShell 镜像脚本，用 WinUI 3 包成可勾选的桌面 app，再保留原脚本兜底——是"**给老 CLI 套原生 GUI 外壳 + 保留底层脚本兼容性**"的清晰样本，与用户工具链兴趣（EverythingToolbar 包 Everything、Clash-Verge 包 Mihomo 同构）。
- **提醒**：README 明确"Core 模式无法更新维护、受保护的 Custom 移除可能破坏 Windows，安装前务必在 VM 中测试"——属于**有风险的操作类工具**，使用者需自负其责。

## 5. 源码深度解读
- `src/Tiny11Builder.Core` 是 .NET class library，承载镜像处理（挂载/卸载、组件清单应用、应答文件注入）；`src/Tiny11Builder.App` 是 `Microsoft.UI.Xaml`（WinUI 3）的 `App`/`MainWindow`，用 `global.json` 固定 SDK、`Directory.Build.props` 统一产物属性。
- 根级 `tiny11maker.ps1` / `tiny11Coremaker.ps1` 是"去胖"的真正执行体（移除 Appx、禁用遥测/Defender、裁剪组件），App 通过 `Core` 调用或直接驱动这些脚本；`autounattend.xml` 提供无人值守安装的组件选择基线。
- 仓库未检测到标准开源许可证（`NOTICE.md` 仅作归属/分发说明），**二次分发/商用需注意合规**。

## 6. 社区口碑
- 20k⭐、GitHub Trending 日榜，承袭 ntdev 的 `tiny11` 既有高人气（ntdev 是 Windows 精简镜像圈知名作者，另有 tiny10 等）；WinUI 3 官方图形化版本发布后口碑集中"终于有 GUI 了"。
- 风险/短板：**未声明明确开源许可**（合规风险）、Core 模式不可维护、Custom 过度移除可导致系统损坏、需管理员权限；属强操作类工具，新手易误伤。

## 7. 竞品对比 + 核心研判
| 维度 | tiny11builder | NTLite | MSMG Toolkit | 手写 PowerShell/DISM |
|---|---|---|---|---|
| 形态 | WinUI 3 GUI + 原 PS | 商业 GUI | 免费 GUI | 脚本 |
| 开源 | 否（无明确许可） | ❌商业 | 免费闭源 | 自写 |
| 易用性 | ✅ 高 | ✅ 高 | 中 | 低 |
| 保留底层脚本 | ✅ | ❌ | ❌ | — |

**研判**：tiny11builder 是"给成熟 PowerShell 去胖脚本套原生 WinUI 3 GUI"的典范，对追求轻量 Win11 的用户价值直接。但**未声明开源许可 + Core 不可维护 + 操作风险**，使其更适合"个人折腾/VM 测试"而非生产分发；作为工具链样本值得收录，使用时务必在 VM 验证。

## 8. 关键文件路径速查
- `src/Tiny11Builder.App/`（WinUI 3 前端）· `src/Tiny11Builder.Core/`（.NET 核心库）
- `tiny11maker.ps1` · `tiny11Coremaker.ps1`（原版 PowerShell 构建器，真正执行移除）
- `autounattend.xml`（无人参与应答文件）
- `global.json` · `Directory.Build.props` · `Tiny11Builder.sln`（.NET 工程配置）
- `docs/usage.md`（用法/兼容性）· `NOTICE.md`（归属/分发说明）
