# CursorTouch/Windows-MCP 深度调研

> 调研日期：2026-09-20 | 星标：7,045⭐ | 语言：Python（3.13+）| 许可：MIT | 默认分支：main | 最近提交：2026-09-16（活跃）
> 定位：把 LLM/AI agent 与 Windows 操作系统桥接起来的 MCP 服务器——让 agent 操控文件、应用、UI、做 QA 测试，无需传统计算机视觉或专用微调模型。

## 一、项目亮点（差异点）

1. **不依赖 CV / 微调模型**：靠 Windows UI Automation（UIA）+ Firefox 的 IAccessible2 回退读取界面，任何 LLM 都能用，部署与调试成本远低于视觉系 CUA。
2. **2M+ 用户规模**：已进入 Claude Desktop Extensions 目录，Trendshift 每日榜在列，社区 adoption 极广。
3. **DOM 模式浏览器自动化**：`use_dom=True` 让 State-Tool 只看网页内容、过滤浏览器 UI，支持 Chrome/Edge/Firefox。
4. **多传输 + 开机自启**：stdio / SSE / streamable-http 三选；`windows-mcp install` 建计划任务，登录即起，日志落到 `~/.windows-mcp/`。
5. **低延迟实时交互**：动作间典型延迟 0.2–0.5s，模块化 service 易扩展（`src/windows_mcp/` 分层清晰）。

## 二、核心架构

```
src/windows_mcp/
  ├─ desktop/   → screenshot / service / views / flash_overlay / utils（截屏+UI状态+高亮）
  ├─ filesystem/→ service / views（文件导航）
  ├─ infrastructure/ → analytics / auth（埋点/鉴权）
  ├─ config.py / __main__.py
  └─ manifest.json / server.json（MCP 服务器元数据，mcp-name: io.github.CursorTouch/Windows-MCP）
serve: uvx windows-mcp serve [--transport {stdio,sse,streamable-http}]
```

设计上把"桌面 UI 操控""文件系统""基础设施"拆成独立 service 模块，MCP 工具按 domain 暴露；底层状态读取走 Windows UIA（无障碍树），因此天然支持"读界面结构→LLM 决策→模拟键鼠"的循环，而无需截图识别。

## 三、应用场景与启发

- **给同类需求的解法**：做"agent 操控桌面"时，**优先吃系统原生无障碍树（UIA/IAccessible2）而非截图 CV**——更快、更稳、且对任意 LLM 友好；这是 Windows-MCP 相比视觉 CUA 的核心取舍。
- **对你（Windows + MCP 方向）**：你身处 Windows 环境，若要让 agent 自动跑本地任务（开软件、点按钮、做回归点击测试），这是当前社区最成熟的开源 MCP 入口；其上还衍生出 `windows-use` 这个专门 agent。
- **可借鉴**：`install` 落地计划任务实现"登录即服务"、三传输适配不同宿主、DOM 模式隔离网页内容——都是桌面 agent 工程的实用范式。

## 四、源码深度解读

**① 模块化 service 结构**（`src/windows_mcp/desktop/`）——桌面交互被拆成截屏、服务、视图、高亮叠加层：

```text
src/windows_mcp/desktop/
  screenshot.py    # 截屏 / 取窗口位图
  service.py       # 暴露 MCP 工具（鼠标/键盘/读 UI 状态）
  views.py         # UI 元素结构化视图（来自 UIA 树）
  flash_overlay.py  # 操作高亮叠加，便于人眼核对 agent 动作
  utils.py
```

**② 运行与传输（README 摘录）**——同一服务三种接法，适配不同宿主：

```shell
uvx windows-mcp serve                                   # stdio（默认，给本地 agent）
uvx windows-mcp serve --transport sse --host localhost --port 8000
uvx windows-mcp serve --transport streamable-http --host localhost --port 8000
windows-mcp install   # 建计划任务 windows-mcp-server，登录自启
```

DOM 模式：State-Tool 设 `use_dom=True` 时只保留 `RootWebArea` 网页内容，Firefox 走 IAccessible2 回退（因不暴露 UIA 的 RootWebArea）。

## 五、社区口碑

- 2M+ 用户、Claude Desktop Extensions 上架、Trendshift 在榜，是 Windows agent 自动化赛道的事实标准开源入口。
- MIT、活跃维护（2026-09 仍有提交）、PyPI 可 `uvx windows-mcp` 直装，门槛低。
- 注意：App-Tool 默认要求 Windows 显示语言为 English（否则建议关闭该工具）；本质依赖 Windows 专属 API，非跨平台。

## 六、竞品对比

| 项目 | 读界面方式 | 跨平台 | 传输 | 规模 |
|------|-----------|--------|------|------|
| **Windows-MCP** | UIA 无障碍树（无 CV） | ❌ 仅 Windows | stdio/sse/http | 2M+ |
| 视觉 CUA（如 UI-TARS） | 截图 + 微调模型 | ✅ | 模型推理 | — |
| Anthropic computer-use | 截图 CV | ✅ | — | — |

## 七、核心研判

Windows-MCP 是"让 agent 操控 Windows"这条赛道里** adoption 最猛、工程最务实**的开源方案——它聪明地避开 CV，用系统原生无障碍树换取低延迟与任意 LLM 兼容。对你在 Windows 上构建本地自动化/QA agent 是直接可用的底座。局限是平台绑定（Windows-only）与英文环境偏好，且"无 CV"意味着纯视觉校验场景（如比对渲染像素）仍需另配截图比对。

## 关键文件路径速查

- `src/windows_mcp/desktop/{service,screenshot,views,flash_overlay}.py` — 桌面 UI 操控核心
- `src/windows_mcp/filesystem/{service,views}.py` — 文件导航工具
- `src/windows_mcp/infrastructure/{analytics,auth}.py` — 埋点/鉴权
- `manifest.json` / `server.json` — MCP 服务器元数据（mcp-name、能力声明）
- `pyproject.toml` — 依赖与入口（`windows-mcp serve/install`）
- `.claude/skills/windows-mcp-tool-tester/SKILL.md` — 自带工具自测技能
