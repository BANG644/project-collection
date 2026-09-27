# LorenzCK/OnTopReplica — 深度调研

> 调研日期：2026-09-28 ｜ 星标：3,396 ｜ 许可：**MS-RL（Microsoft Reciprocal License）** ｜ 语言：C# / .NET Framework 4.7（Windows Forms）｜ 平台：Windows Vista+（需 DWM/Aero）

## 1. 项目定位（一句话）
Windows 平台的**实时"窗口克隆"小工具**：把任意窗口实时镜像成一个始终置顶的副本，方便监控后台进程、多窗口工具/游戏、边工作边看视频。

## 2. 项目亮点
- **原生 DWM 缩略图**：通过 Windows 桌面窗口管理器（DWM）Thumbnail API 直接取目标窗口的实时画面，无需逐帧截图，性能高、画质好。
- **子区域选择**：可只克隆窗口的某块区域，支持相对坐标存储（换位置也不乱）。
- **丰富的置顶交互**：自动缩放（原尺寸/半屏/四分/全屏）、四角锁位、可调透明度、**点击转发**（能直接操作克隆体）、**点击穿透**（变纯浮层叠加）。
- **分组切换模式**：在一组窗口间自动轮流克隆。
- **长期稳定**：从 Vista 时代活到现在，MSI 安装包、接受 PR。

## 3. 核心架构
- **WinForms 应用**：主窗体 `src/OnTopReplica/MainForm.cs` 用部分类拆成 `MainForm_ChildForms` / `MainForm_Features` / `MainForm_Gui` / `MainForm_MenuEvents`，共 135 个 `.cs` 文件，结构清晰。
- **消息泵处理器** `MessagePumpProcessors/`：负责把鼠标/键盘等消息拦截并转发给目标窗口——`ShellInterceptProcessor.cs`（外壳拦截）、`FlashCloner.cs`、`GroupSwitchManager.cs`、`HotKeyManager.cs`、`WindowKeeper.cs`。
- **原生互操作** `Native/CommonControls.cs`：封装 DWM / Shell 相关 Windows API；`CloneClickEventArgs.cs` 承载点击转发事件；`FullscreenFormManager.cs` 管全屏模式。

## 4. 应用场景与启发
- **Windows 多窗口工作者的实用小工具**：用户是 Windows 重度用户，可用它把监控面板/日志/视频钉在角落，边写代码边看。
- **借鉴"原生 Windows API + 轻量 WinForms"范式**：做其他 Windows 增强小工具（窗口管理、截图浮层）时，DWM Thumbnail + 消息泵拦截是可直接复用的技术路线。
- **注意许可**：MS-RL 是互惠许可——你修改并分发就必须开源你的改动，不适合闭源打包。

## 5. 源码深度解读
点击转发是 OnTopReplica 区别于"单纯置顶"的核心。其 `CloneClickEventArgs.cs` 定义克隆体上的鼠标事件，由 `MessagePumpProcessors/ShellInterceptProcessor.cs` 在消息泵中拦截并**转发给目标窗口**，实现"在浮层上点，实际操作原窗口"：
> Click forwarding: allows to interact with the cloned window

原生画面取自 DWM：`Native/CommonControls.cs` 封装 `DwmRegisterThumbnail` / `DwmUpdateThumbnailProperties`（README 明言 "native DWM Thumbnails to create replicas"），由 `WindowKeeper.cs` 维持目标窗口句柄与区域映射。整体是"**Win32 原生能力 + .NET 薄封装**"的典型 Windows 工具架构。

## 6. 社区口碑
- 3.4k⭐、长期维护、被多次推荐为"窗口置顶/克隆"首选；MSI 安装、上手简单。
- 局限：仍基于 **.NET Framework 4.7**（非 .NET Core/跨平台），高 DPI 支持在 Roadmap 中尚未完善；新功能迭代慢。

## 7. 竞品对比 + 核心研判
| 项目 | 能力 | 差异 |
|---|---|---|
| OnTopReplica | **实时克隆窗口 + 点击转发** | 唯一"活缩略图克隆" |
| DeskPins | 仅置顶 pin | 无克隆/无实时画面 |
| PowerToys | 布局/唤醒，无克隆 | 不提供窗口镜像 |
| Actual Multiple Monitors | 商业，多显增强 | 功能更全但闭源收费 |

**研判**：小而精的利基工具，技术核心是 DWM 缩略图 API，实用性强；许可与旧框架是其主要约束。适合作为"Windows 原生小工具"的参考实现。

## 8. 关键文件路径速查
- `src/OnTopReplica/MainForm.cs`(+ `_ChildForms`/`_Features`/`_Gui`/`_MenuEvents`) — 主窗体
- `src/OnTopReplica/MessagePumpProcessors/ShellInterceptProcessor.cs` — 消息/点击拦截转发
- `src/OnTopReplica/MessagePumpProcessors/WindowKeeper.cs` — 目标窗口句柄维护
- `src/OnTopReplica/Native/CommonControls.cs` — DWM/Shell 原生封装
- `src/OnTopReplica/CloneClickEventArgs.cs` — 点击转发事件
- `Installer/script.nsi` — NSIS 安装脚本
- `Docs/Settings List.txt` — 设置项清单
