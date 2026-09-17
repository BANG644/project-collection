# srwi/EverythingToolbar 深度调研

> 调研日期：2026-09-18 ｜ 星标：14,758 ⭐ ｜ 语言：C#（GitHub 语言标签误标为 C，实为 .NET 8 / WPF）｜ 协议：未显式声明 SPDX（仓库 LICENSE 文件，API 标 NOASSERTION）｜ 默认分支：develop ｜ 创建：2020-09-13 ｜ 最后推送：2026-09-17 ｜ 依赖：.NET Desktop Runtime 8.0 + Everything ≥ 1.4.1

## 一、一句话定位

EverythingToolbar 是 **Everything 极速文件搜索引擎的 Windows 任务栏前端外壳**：把 Everything 的毫秒级文件名搜索直接嵌进任务栏（搜索框或图标），替代又慢又重的 Windows 自带搜索，**定位「薄前端 + 快引擎」的 shell 集成工具**。

## 二、⭐ 项目亮点

- **任务栏深度集成**：Win11 直接嵌入任务栏搜索框，Win10 / 配合 ExplorerPatcher / StartAllBack 走原生 deskband，呼出即搜，毫秒响应。
- **完整继承 Everything 能力**：复用 Everything 索引，支持正则、匹配路径/大小写、与 Everything 自定义过滤器双向同步；百万文件仍流畅，后台内存仅 10–20MB。
- **接口化平台抽象**：`IClipboard`/`IFileLauncher`/`IFilePreviewer`/`INotifier`/`IShellDialogs` 把系统能力抽象成接口，UI 与平台解耦，便于测试与跨环境。
- **现代化交互**：自动浅/深色主题、可拖拽结果、对接 QuickLook/Seer 预览、`Win+Alt+S` 全局热键、正则驱动自定义「打开方式」动作链。
- **纯净开源**：无广告无捆绑，crowdin 多语化，winget 一键装（`srwi.everythingtoolbar.launcher`）。

## 三、🏗️ 核心架构全景

.NET 多项目解决方案（`EverythingToolbar.sln`）：

- `EverythingToolbar.Core/` — 纯逻辑层（与 UI 无关）：`Search/`（IEverythingClient、SearchQuery、IItemsProvider）、`Data/`（SearchResult、Filter、SortBy、FocusBehavior）、`Services/`、`Platform/`（系统能力接口）、`Helpers/`。
- `EverythingToolbar.Deskband/` — 任务栏 Band 实现：`CSDeskBand.cs`（第三方 CSDeskBand 库，封装 deskband COM）、`Server.cs`、`ToolbarControl.xaml(.cs)`。
- `EverythingToolbar.Launcher/` — Win11 任务栏搜索框嵌入引导；`EverythingToolbar.App/` 主应用；`EverythingToolbar.Platform/` 平台适配。
- `EverythingSDK/` · `EverythingSDK3/` — 内置 Everything 官方 SDK（IPC 查询）。

## 四、💡 应用场景与启发（重点）

- **谁该用**：频繁找文件、嫌 Win+S 慢的人；觉得原生 Everything 窗口「丑」、想要现代融合 UI 的键盘流用户；想用任务栏搜索框替代系统搜索框者（mzlw/IMA 测评共识）。
- **「薄前端 + 快引擎」架构启发**：它不做搜索，只做 Everything 的漂亮入口——把重活交给专业引擎，自己专注交互。任何「包装已有强大后端」的工具都该学这招，避免重造轮子。
- **接口化平台抽象启发**：`Platform/IFileLauncher` 等接口把「打开文件/复制/预览/弹窗」变成可替换实现，使 Core 不依赖具体 Windows API——是桌面工具做可测试、可演进架构的范本。

## 五、🧠 核心源码解读（克制）

### 1. 搜索客户端接口（`EverythingToolbar.Core/Search/IEverythingClient.cs`）

Core 只依赖这个接口，不关心 Everything 具体 IPC 实现；`TryReadCachedFirstPage` 缓存首页、`GetEverythingVersion`/`SetInstanceName` 支持多实例命名：

```csharp
public interface IEverythingClient {
    Task<int>  QueryCountAsync(SearchQuery q, int pageSize, CancellationToken ct);
    Task<IList<SearchResult>> QueryRangeAsync(SearchQuery q, int start, int pageSize, CancellationToken ct);
    bool TryReadCachedFirstPage(SearchQuery q, out IList<SearchResult> results);
    Version GetEverythingVersion();
    void SetInstanceName(string name);
    bool GetIsFastSort(SortBy sortBy, bool descending);
}
```

### 2. 查询取消语义（`IEverythingClient.cs` 注释）

> Canceling means the query was superseded: it returns 0 rather than throwing, and callers are expected to discard the result once they notice the token is canceled.

输入即出结果依赖「上一次查询被新输入取代时立即取消」——用 `CancellationToken` 让被取代的查询静默返回 0，UI 永不卡在旧结果。这是「即时搜索框」流畅感的核心工程细节。

### 3. 任务栏 Band（`EverythingToolbar.Deskband/`）

`CSDeskBand.cs`（第三方库）封装 Windows Deskband COM 注册，`ToolbarControl.xaml` 是 WPF 搜索面板；`Server.cs` 协调 Launcher 与 Deskband 两种集成形态。Launcher 在 Win11 把搜索框「种」进任务栏，是比 deskband 更现代的集成路径。

## 六、🌐 全网口碑画像

- **好评共识**：英文 windowsmastery 长文称其「让 Windows Search  obsolete」，赞 `Win+Alt+S`、可缩放窗口、搜索历史（Ctrl+↑/↓）、缩略图预览；中文 mzlw/今日头条测评列「任务栏深度集成、现代 UI、低内存 10-20MB、正则自定义动作、纯净化」为五大优势。
- **客观短板**：① 依赖后台运行 Everything（且不支持 Lite 版）；② 纯文件名搜索、不索引文件内容（与 Everything 同源限制）；③ 部分高级能力需配合 ExplorerPatcher/StartAllBack（Win11 deskband）。
- **横向共识**：对比原生 Everything（纯粹快但 UI 老）、Wox/Listary（启动器向）、Win+S（慢），EverythingToolbar 以「美观集成 + 极速」定位清晰，是「Everything 的前端皮肤」首选。

## 七、⚔️ 竞品对比

| 维度 | EverythingToolbar | 原生 Everything | Wox/Listary | Windows 搜索 |
|---|---|---|---|---|
| 速度 | 极快（基于 Everything） | 极快 | 快 | 慢（索引内容） |
| 集成 | 嵌入任务栏 | 独立窗口 | 居中弹框 | 系统全屏 |
| UI | 现代/跟随主题 | 传统 | 现代 | 系统 |
| 内容搜索 | ❌ 仅文件名 | ❌ | 部分 | ✅ |
| 定位 | 替代任务栏搜索框 | 专业搜索管理器 | 启动器/工作流 | 系统全局 |

**选择建议**：要「任务栏里极速找文件」选 EverythingToolbar；要深度文件管理/内容搜索用原生 Everything；要「应用+文件」启动器选 Wox/Listary。

## 八、🎯 核心研判

- ✅ **优势**：Everything 生态最优雅的前端外壳，免费纯净、低内存、键盘流友好、跨 Win10/11。
- ⚠️ **风险**：能力上限受 Everything 约束（仅文件名）；依赖后台 Everything 进程；deskband 在 Win11 需第三方补丁才完整。
- 🔮 **趋势**：随 Win11 弱化经典搜索框，其 Launcher 嵌入路线价值上升；若 Everything 自身迭代放缓则天花板可见。
- 💡 **启发**：做 Windows shell 工具，「薄前端封装成熟引擎 + 接口化平台抽象 + 取消即弃的查询语义」是兼顾速度与可维护的范本。

## 九、📂 关键文件路径速查

- `EverythingToolbar.Core/Search/IEverythingClient.cs` — 搜索客户端接口（取消语义/缓存首页）
- `EverythingToolbar.Core/Search/SearchQuery.cs` · `Data/SearchResult.cs` · `Data/Filter.cs` · `Data/SortBy.cs`
- `EverythingToolbar.Core/Platform/` — IClipboard/IFileLauncher/IFilePreviewer/INotifier/IShellDialogs
- `EverythingToolbar.Deskband/CSDeskBand.cs` · `ToolbarControl.xaml(.cs)` · `Server.cs`
- `EverythingToolbar.Launcher/` — Win11 任务栏搜索框嵌入
- `EverythingSDK/` · `EverythingSDK3/` — Everything 官方 SDK
- `README.zh-CN.md` · `FAQ.md` · `CONTRIBUTING.md` — 中文文档/排错/贡献指南
