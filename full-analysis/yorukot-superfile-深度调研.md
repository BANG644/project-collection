# 🔬 yorukot/superfile — 现代化终端文件管理器（TUI）

> **调研日期**：2026-07-26 | **数据来源**：GitHub API + README + 源码树走读
> **实时数据**：⭐ 19,408（Trending +312/日）| 协议 MIT | 语言 Go 1.26 | 官网 superfile.dev

## 一、项目定位（一句话）

一款 **漂亮、现代、功能完整的终端文件管理器（TUI）**，用 Go + bubbletea 构建，支持多面板、预览、压缩包/图片/PDF 查看、热键与主题定制。

## 二、项目亮点（3-5 条差异化，开篇呈现）

- 🎨 **现代 TUI 体验**：基于 charm 系列（bubbletea v2 / bubbles / lipgloss）打造，UI 细腻，支持主题与热键全自定义。
- 🗜️ **多格式内建预览**：压缩包（7z/rar/zip/xz/iso9660）、图片（imaging）、PDF、exif 元数据均可直接查看，无需出终端。
- 🔍 **模糊查找 + 系统集成**：集成 fzf-lib 模糊搜索、zoxide 一键 `cd`、gopsutil 取系统信息、exiftool 读元数据。
- 🪟 **跨平台**：Linux / macOS / Windows（Windows 仍部分支持），Homebrew / Winget / Scoop 一行装。
- 📦 **MIT + 活跃维护**：核心维护者 @yorukot + @lazysegtree，JetBrains 开源许可支持，社区贡献活跃。

## 三、核心架构

典型 **bubbletea（Elm 架构）** 单 Model 编排多面板：

```
superfile/
├── main.go                 # 入口
├── src/
│   ├── cmd/main.go         # 实际 main
│   ├── config/             # 热键、图标、主题配置（fixed_variable.go / icon/）
│   └── internal/
│       ├── model.go            # 核心 Model（状态 + 面板集合 + 焦点）
│       ├── model_render.go      # View：绘制各面板
│       ├── model_msg.go         # 消息定义
│       ├── model_process*.go    # 业务处理
│       ├── model_navigation*.go # 导航逻辑
│       ├── handle_panel_movement.go  # 面板焦点/布局移动
│       ├── handle_panel_navigation.go
│       └── common/             # 配置加载（load_config / default_config）
└── website/                # 文档站点
```

依赖要点：`charm.land/bubbletea/v2`（事件循环）、`chroma/v2`（语法高亮）、`reinhrst/fzf-lib`（模糊查找）、`lazysegtree/go-zoxide`（cd 集成）、`gopsutil`（系统）、`barasher/go-exiftool`（元数据）、`disintegration/imaging`（图像）。

## 四、应用场景与启发

- **终端党的文件管理器**：替代 ranger/nnn，想要更现代 UI 与多格式预览时首选。
- **TUI 架构样板**：`model.go` + `model_render/model_msg/model_navigation` 的拆分是 bubbletea 大型应用的规范写法，可直接借鉴。
- **面板焦点管理范式**：`handle_panel_movement` / `handle_panel_navigation` 把「多面板焦点 + 布局」与「业务处理」解耦，复杂 TUI 可复用此思路。

## 五、源码解读（核心模块精读）

Elm 架构三件套集中于 `src/internal`：

```go
// src/internal/model.go（结构示意）
type model struct {
    panels   []panel      // 多面板：文件列表 / 预览 / 进程
    focus    int          // 当前焦点面板
    config   Config
    // ...
}
func (m model) Update(msg tea.Msg) (model, tea.Cmd) { /* model_msg / navigation 在此分派 */ }
func (m model) View() string { /* 由 model_render.go 实现 */ }
```

关键设计：`Update` 根据消息类型把事件分派给 navigation / movement / process 子模块，各面板只负责自身渲染与交互——**状态集中在单一 Model，副作用（cd、解压、预览）封装为 `tea.Cmd`**。这种「一个 Model 统领多面板」的结构，是把它从玩具 TUI 做成生产级文件管理器的关键。

## 六、全网口碑

- TUI 圈口碑佳，星标 19K+ 且 Trending 日增 ~312；被多篇「最佳终端文件管理器」盘点收录。
- 用户赞 UI 现代、预览能力强；Windows 支持「尚不完全」是已知短板（README 已标注）。
- 自动更新机制（24h 内检查 GitHub release）被部分用户改为关闭（`auto_check_update: false`）。

## 七、竞品对比 + 核心研判

| 维度 | superfile | ranger | nnn | yazi |
|------|-----------|--------|-----|------|
| 语言 | Go | Python | C | Rust |
| UI | 现代气泡 | 朴素 | 极简 | 现代（async） |
| 预览 | 多格式内建 | 插件 | 少 | 强 |
| 主题/热键 | 全自定义 | 可 | 可 | 可 |

**核心研判**：
- ✅ **优势**：bubbletea 现代观感 + 多格式预览 + MIT 活跃维护，对「想要好看又能看压缩包/PDF」的终端用户黏性强。
- ⚠️ **风险**：Windows 支持未完；Go TUI 在超大目录下的性能依赖后续优化；与 yazi（Rust/异步）在极限性能上有差距。
- 🎯 **启发**：做 TUI 应用时，把 bubbletea 的 Model/Update/View 与「面板焦点管理」拆清楚，是驾驭复杂交互的可扩展范式。

## 八、关键文件速查

- `src/internal/model.go` — 核心 Model（状态中枢）
- `src/internal/model_render.go` — 视图绘制
- `src/internal/handle_panel_movement.go` / `handle_panel_navigation.go` — 面板交互
- `src/config/` — 热键/主题/图标配置
- `go.mod` — 依赖（bubbletea v2 / chroma / fzf-lib / zoxide）
- GitHub：`https://github.com/yorukot/superfile`
