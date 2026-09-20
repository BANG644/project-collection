# excalidraw/excalidraw-mcp 深度调研

> 调研日期：2026-09-21 | 星标：5,337⭐ | 语言：TypeScript | 许可：MIT（仓库未放标准 LICENSE 文件）| 默认分支：main | 最近提交：活跃

## 一句话定位
Excalidraw 官方出品的 MCP App 服务器：把「手绘风图表」以流式逐元素绘制 + 可交互全屏编辑的方式吐回聊天，兼容任何支持 MCP Apps 的客户端（Claude / ChatGPT / VS Code / Goose）。

## 项目亮点
- **基于 MCP Apps 扩展**：用 `@modelcontextprotocol/ext-apps/server` 的 `registerAppResource / registerAppTool`，返回可交互 HTML 界面而非纯文本——服务器直接把图表渲染进对话。
- **流式逐元素 + 视口动画**：通过 Excalidraw 元素 JSON 协议，先发 `cameraUpdate` 定视口，再按 z-order 渐进 emit（背景→形状→标签→箭头），相机平滑移动引导注意力。
- **内置 RECALL cheat-sheet**：`server.ts` 顶部把 Excalidraw 元素 schema（颜色表 / 形状字段 / 箭头绑定 / 相机 4:3 尺寸）作为共享知识喂给模型，省去反复 read_me，显著降低 token。
- **远程即用 + 自部署**：官方托管 `https://mcp.excalidraw.com`；也可 `npx` 本地或一键 Vercel 部署，`.mcpb` 双击装 Claude Desktop。

## 核心架构
- `src/server.ts`：MCP App 服务器，注册 `create_view` 等工具，注入 RECALL cheat-sheet 与绘制协议。
- `src/mcp-app.tsx` / `src/mcp-entry.tsx`：流式 UI，监听工具返回的元素数组，实时画到 Excalidraw canvas。
- 协议：元素 JSON（rectangle / ellipse / diamond / arrow / text + 伪元素 cameraUpdate / delete），经 deflate 压缩传输。

## 应用场景与启发
- 「让 LLM 画图解释架构 / 流程」场景的官方方案：比让模型吐 Mermaid 更直观、可交互编辑。
- cheat-sheet 注入模式值得借鉴：把领域 DSL schema 作为常驻系统知识，避免每轮重复解释工具用法。
- 远程 MCP App 模式（服务端渲染 + 客户端内嵌）是「富交互工具」的轻量替代。

## 源码解读
**绘制协议与 cheat-sheet（`src/server.ts`）**

```ts
const RECALL_CHEAT_SHEET = `# Excalidraw Element Format
## Color Palette ... Blue #4a9ed ...
## Elements: type/x/y/width/height; label 自动居中
## cameraUpdate: 视口伪元素，4:3 比例(400×300…1600×1200)，平滑动画
## Drawing Order: 先 cameraUpdate，再 bg→shape→label→arrow 渐进 emit`;
// 工具返回元素数组，UI 端按 z-order 流式渲染
registerAppTool(server, "create_view", { /* 接收 elements[] */ });
```

## 全网口碑
GitHub 5.3k⭐、官方仓库（excalidraw 组织）、demo gif 直观；社区作为「LLM 画手绘架构图」首选。许可标注为 MIT 但仓库未放标准 LICENSE 文件（小瑕疵）。

## 竞品对比 + 核心研判
- 竞品：`mcp-server-diagram`（Mermaid）、`markmap`（思维导图）、drawio MCP 等。
- 研判：官方背书 + 流式交互 + cheat-sheet 省 token 是差异化；适合「讲解架构 / 画流程」需求。注意它走 MCP Apps 协议，需客户端支持（Claude / VS Code 已支持，部分客户端仅纯文本）。

## 关键文件路径速查
- `src/server.ts` — MCP App 服务器 + RECALL cheat-sheet
- `src/mcp-app.tsx` — 流式绘制 UI
- `manifest.json` — MCP App 清单
- 官方远程：`https://mcp.excalidraw.com`
