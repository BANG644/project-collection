# w4po/ExplorerTabUtility 深度调研

> 调研日期：2026-09-23 ｜ 定位：让 Windows 11 新开的资源管理器窗口自动变成标签页的工具（含复用/复制/重开/搜索/热键）｜ Stars：2,942 ｜ 语言：C#（.NET 9 + .NET Framework 4.8.1）｜ 许可：MIT ｜ 默认分支：master ｜ 最近活跃：2025-05-04

## 一、项目定位（一句话）

Explorer Tab Utility 是一个常驻系统托盘的 Windows 11 小工具：拦截新开的资源管理器窗口，**自动把它们合并进已开窗口的标签页**，并提供标签复用、复制、重开已关、标签搜索、自定义路径热键等能力，把"一堆散落窗口"收敛成"一个带标签的资源管理器"。

## 二、项目亮点（差异化）

- **原生标签体验补完**：Windows 11 资源管理器虽有标签页，但新开窗口≠新标签；本工具用 COM 钩子补齐"窗口自动转标签 + 同路径复用"这一官方缺失体验。
- **功能密度高**：自动转标签、标签复用（已开路径直接切换）、复制当前标签、重开已关标签（跨重启保留历史）、崩溃/重启后恢复窗口、拖出吸附分屏、空区域鼠标/键盘前后导航、CLSID/环境变量/URL 自定义路径、标签搜索切换、`Ctrl+Shift` 强制新窗口。
- **可编排热键**：多 Profile（全局/仅资源管理器作用域）+ 多种 Action 类型（Open/Duplicate/ReopenClosed/TabSearch/NavigateBack/DetachTab/Snap…）+ 单热键链式多动作（如 Ctrl+Q：拖出→左半屏→右半屏）。
- **工程质量到位**：WPF 现代化 UI、系统托盘、主题样式 XAML、STA 任务调度、`SemaphoreSlim` 同步；通过 SignPath 免费代码签名；winget/choco 分发包齐备。

## 三、核心架构

```
系统托盘常驻 (App.xaml)
   │
   ▼
ExplorerWatcher (Hooks/ExplorerWatcher.cs) ──▶ ShellWindows + WinEventHook
   ├─ 监听 Explorer 窗口创建/销毁（SHDocVw.ShellWindows）
   ├─ PIDL 路径比较（Interop/ShellPathComparer）判断"是否同路径"
   ├─ DualKeyDictionary<InternetExplorer, nint?, WindowInfo> 线程安全追踪
   └─ StaTaskScheduler + SemaphoreSlim 串行化 COM 调用
   │
   ▼
Managers/（SettingsManager / ProfileManager / HookManager / RegistryManager / UpdateManager）
   │
   ▼
WinAPI/（WinApi.cs · INPUT/RECT/VirtualKey P/Invoke）+ Hooks/Keyboard · Hooks/Mouse（全局钩子）
```

- **COM 集成**：通过 `Shell32` + `SHDocVw` 原生接口操作 Explorer；PIDL（ID 列表指针）处理文件系统对象，避免路径字符串歧义。
- **进程/事件系统**：`ProcessWatcher` 监控 explorer.exe 崩溃并自动恢复；事件驱动 UI；非阻塞 COM（STA 调度）。
- **性能优化**：窗口句柄缓存、路径比较优化、标签状态追踪、COM 对象妥善释放。

## 四、应用场景与启发

- **Windows 效率工具范式**：当你想给"没有干净 API 的桌面程序"做行为增强（强制标签化/热键化），本工具是 **COM + WinEventHook + STA 调度** 的现成范本，可直接借其 `ShellWindows` 监听与 PIDL 比较思路。
- **"渐进式增强原生 UI"的设计姿态**：它不强改 Explorer，而是用钩子在原生行为之上叠加标签层（且提供"替代隐藏法保主题"开关），这种"最小侵入"思路对做其他桌面增强工具很有参考。
- **个人效率**：对重度依赖资源管理器、又嫌窗口乱的用户，是即装即用的"标签页化"方案。

## 五、源码深度解读（关键片段）

`ExplorerTabUtility/Hooks/ExplorerWatcher.cs` 是核心钩子，用 `ShellWindows`（`SHDocVw`）监听资源管理器实例，并用 `DualKeyDictionary` + `ConcurrentDictionary` 做线程安全追踪：

```csharp
private ShellWindows _shellWindows = null!;
private readonly DualKeyDictionary<InternetExplorer, nint?, WindowInfo> _windowEntryDict = [];
private readonly ConcurrentDictionary<nint, byte> _processedHWnds = new();
private readonly SemaphoreSlim _toOpenWindowsLock = new(1);
// 用 PIDL 比较判断目标路径是否已有标签，命中则切换而非新建
public nint SearchForTab(string targetPath) {
    targetPidl = _shellPathComparer.GetPidlFromPath(targetPath);
    foreach (var (window, windowInfo, tabHandle) in _windowEntryDict) {
        if (_shellPathComparer.IsEquivalent(targetPath, comparePath, targetPidl))
            return tabHandle.Value;   // 复用已有标签
    }
    return 0;
}
```

`WinAPI/WinApi.cs` 封装 `INPUT/RECT/VirtualKey` 的 P/Invoke 用于模拟输入；`Hooks/Keyboard.cs` / `Hooks/Mouse.cs` 提供全局热键；`Managers/SettingsManager.cs` 把配置存到 `%APPDATA%\ExplorerTabUtility\settings.json`。整体呈现典型的"COM 读状态 + 注入输入 + STA 串行化"桌面增强实现。

## 六、全网口碑

- **正面**：星标 2.9k+，Windows 效率工具圈口碑好；功能完整、更新稳定、有代码签名与包分发（winget/choco）；README 文档详尽、截图/动图充分；明确说明杀软误报原因（COM + 低级钩子属正常）。
- **风险/争议**：Windows 11 专属且依赖 File Explorer Tabs 特性（22H2+），Win10 不可用；README 标注"部分操作受 Explorer 本身 API 限制而偏慢"（标签接口无官方编程控制）；最近一次提交在 2025-05，主仓库迭代节奏放缓（但 release 仍可用）。

## 七、竞品对比与核心研判

| 维度 | ExplorerTabUtility | EverythingToolbar | QTTabBar |
|------|-------------------|------------------|----------|
| 核心 | 窗口→标签自动合并 | 任务栏搜索外壳 | Explorer 多标签增强 |
| 技术 | COM + WinEventHook | Everything 引擎 | Explorer Band 扩展 |
| 维护 | 中（2025-05 后缓） | 活跃 | 老牌但慢 |

**竞品**：`w4po/EverythingToolbar`（搜索外壳）、`indiff/qttabbar`（经典多标签扩展）、Stardock 类商业工具。**ExplorerTabUtility 的差异**是"新窗口自动转标签 + 同路径复用 + 强热键编排"这一具体痛点做得最顺手。

**核心研判**：⭐⭐⭐⭐ — 想要"资源管理器真正标签页化"的 Windows 用户，这是当下最省心、最完整的开源方案，其 **COM 监听 + PIDL 比较 + STA 调度** 也是做桌面增强的优质参考；但绑定 Win11、主仓迭代放缓，长期维护活跃度是主要隐忧。可关注社区是否有人接手活跃维护。

## 八、关键文件路径速查

- `ExplorerTabUtility/Hooks/ExplorerWatcher.cs` — 核心窗口钩子（ShellWindows + WinEventHook）
- `ExplorerTabUtility/Interop/ShellPathComparer.cs` — PIDL 路径比较
- `ExplorerTabUtility/WinAPI/WinApi.cs` — INPUT/RECT/VirtualKey P/Invoke
- `ExplorerTabUtility/Hooks/Keyboard.cs` / `Mouse.cs` — 全局热键/鼠标钩子
- `ExplorerTabUtility/Managers/` — Settings/Profile/Hook/Registry/Update 管理
- `ExplorerTabUtility/UI/` — WPF 视图与主题（XAML）
- 安装：[winget](https://github.com/w4po/ExplorerTabUtility) ｜ 分发：winget/choco/SignPath
