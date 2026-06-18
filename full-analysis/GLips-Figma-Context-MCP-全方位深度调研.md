# 🔬 GLips/Figma-Context-MCP - 全方位深度调研

## 📌 一句话定位

`GLips/Figma-Context-MCP` 是一个面向 Cursor 等 AI 编程工具的 Figma MCP Server：它不是把整份 Figma JSON 原样塞给模型，而是把 Figma 文件、Frame、Group 中和代码生成最相关的布局/样式信息抽取、压缩、翻译成更适合 LLM 使用的上下文。

> 核心判断：它解决的是“截图给 AI 还原 UI 不稳定”的问题；价值在于结构化设计上下文，风险在于强依赖 Figma API token、设计稿质量和 MCP 客户端兼容性。

## 🏗️ 项目全景

| 维度 | 观察 |
|---|---|
| 仓库 | `GLips/Figma-Context-MCP` |
| GitHub | https://github.com/GLips/Figma-Context-MCP |
| Homepage | https://www.framelink.ai/ |
| Stars / Forks | 约 15.1k stars / 1.2k forks（2026-06-19 抽样） |
| 默认分支 | `main` |
| 主要语言 | TypeScript |
| License | MIT |
| 关键词 | AI、Cursor、Figma、MCP、TypeScript |

## 🧠 核心架构

### 设计目标

README 的关键点可以翻译成一句工程目标：**把 Figma API 的复杂响应变成“刚好够 AI 写前端”的精简上下文**。这比截图更可靠，因为模型拿到的是节点层级、布局、尺寸、样式、文本等结构信息。

### 推测运行链路

```text
Cursor / MCP Client
  -> 调用 figma-developer-mcp
  -> 使用 Figma access token 拉取文件/节点
  -> extractor / node walker 清洗 Figma JSON
  -> 返回精简后的布局与样式上下文
  -> AI 生成 React / Vue / HTML / CSS 等实现
```

### 目录与模块信号

现有报告和文件树显示关键文件包括：

- `src/bin.ts`：CLI / MCP server 启动入口。
- `src/commands/fetch.ts`：拉取 Figma 数据的命令层。
- `src/config.ts`：Figma API key、stdio/port 等配置入口。
- `src/extractors/design-extractor.ts`：核心设计信息抽取器。
- `src/extractors/node-walker.ts`：遍历 Figma 节点树。
- `src/extractors/built-in.ts`：内置抽取策略。

**架构判断**：真正的核心不是“接 Figma API”，而是 extractor 层。谁能决定哪些字段保留、哪些字段丢弃，谁就决定了 AI 生成代码的质量。

## 🔍 源码深度解读

### `src/commands/fetch.ts`

该层通常承担“从用户给的 Figma URL 解析 file/frame/group，并调用 API”的职责。它是用户体验最容易出问题的地方：Figma 链接格式、权限、token 失效、节点 ID 解析错误都会让 AI 客户端显示“没有内容”。

### `src/extractors/design-extractor.ts`

该文件是项目的价值核心：它把 Figma 的富 JSON 降维为模型可消费的上下文。这里的权衡是：

- 保留太多字段：模型上下文膨胀，代码生成不稳定。
- 保留太少字段：布局/间距/字体/颜色丢失，生成结果像“看图猜”。

### `src/extractors/node-walker.ts`

节点遍历决定了 Frame、Group、Component、Text、Vector 等对象如何被串起来。Figma 文件越复杂，这层越重要，因为真实团队设计稿常常存在嵌套、Auto Layout、组件实例和命名不规范。

## 🌐 社区口碑画像

外部可靠长评没有检索到，因此不编造“全网好评”。可确认的一手信号来自 GitHub：

- Star 数增长快，说明 MCP + Figma + Cursor 的需求非常强。
- Open issues 约 16，规模不算失控。
- README 引导用户使用 Figma access token，说明安全与权限是采用前必须讲清楚的点。
- 项目把 Framelink 产品站作为主页，开源仓库与商业服务之间存在联动。

## ⚔️ 竞品对比

| 方案 | 优势 | 风险 |
|---|---|---|
| Figma-Context-MCP | 结构化设计数据，适合 Cursor/Agent 直接调用 | 依赖 Figma token 与 MCP 客户端兼容 |
| 直接截图给 AI | 简单，无需 token | 容易丢尺寸、字体、层级和状态 |
| Figma Dev Mode | 官方、适合人工开发 | 不天然接入 AI agent 自动生成链路 |
| Builder.io / Locofy 类工具 | 更产品化的设计转代码 | 平台绑定更强，透明度较低 |

## 🎯 核心研判

### 优势

1. **切中了真实痛点**：AI 写 UI 最怕“只看截图”，Figma 结构数据能显著提升还原度。
2. **MCP 形式正确**：让 Cursor 等工具按需拉上下文，而不是用户手工复制。
3. **抽取层有长期价值**：随着模型上下文变长，真正稀缺的是“把设计稿变成高信噪比上下文”。

### 风险

1. **Figma 文件质量决定上限**：设计稿命名混乱、Auto Layout 不规范，输出也会不稳定。
2. **Token 权限敏感**：企业设计文件通常包含未发布产品信息，部署前必须审查 token 范围。
3. **过度依赖 Cursor 叙事**：README 强调 Cursor，其他 MCP 客户端兼容性需要实际验证。

### 适用场景

- 从 Figma 快速生成前端初稿。
- 设计系统/组件库已有规范，希望 AI 按设计稿实现。
- Cursor / Claude Desktop / OpenClaw 等 MCP 客户端用户。

### 不适用场景

- 高保真复杂交互、动画、状态机密集页面。
- 无法给第三方工具 Figma access token 的企业环境。
- 希望“一次生成即生产可用”的严肃前端项目。

## 📂 关键文件路径速查

- `src/bin.ts`：启动入口。
- `src/commands/fetch.ts`：Figma 数据拉取。
- `src/config.ts`：配置与 token 管理。
- `src/extractors/design-extractor.ts`：设计上下文抽取核心。
- `src/extractors/node-walker.ts`：Figma 节点遍历。
- `README.md`：MCP 配置与 quickstart。

## ⭐ 三条关键发现

1. 项目价值不在“能读 Figma”，而在“把 Figma API 降噪成 AI 可执行上下文”。
2. 采用风险主要来自 Figma token、设计稿质量和 MCP 客户端兼容，不是 TypeScript 代码本身。
3. 这是 AI coding 与设计资产连接的基础设施类项目，适合 PoC 和开发提效，但不应承诺一键生产级还原。

## 🧪 研究方法与数据来源

- GitHub API：仓库元数据、stars、forks、license、topics、open issues。
- README：MCP 配置、Figma token、Cursor 使用方式。
- 现有报告文件树：`src/bin.ts`、`src/commands/fetch.ts`、`src/extractors/*`。
- 外部搜索：未发现可靠第三方长评，故不编造口碑。
