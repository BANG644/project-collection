# DayuanJiang/next-ai-draw-io 深度调研

> 调研日期：2026-09-26 | 数据来源：GitHub API（README / 源码树 / 关键源码文件）| 许可：Apache-2.0 | Stars：36,043 | Forks：3,855 | 语言：TypeScript | 默认分支：main

## 一、项目定位（一句话）

一个把「自然语言」变成「draw.io 标准图表」的 Next.js Web 应用——AI 不只是画草图，而是直接产出**可编辑的 draw.io XML**（`.drawio`/`.svg`/`.png`），并可被 Claude Code / Cursor 等 agent 通过 MCP 调用。

## 二、项目亮点（差异化）

1. **真·draw.io 原生**：产出的是标准 draw.io XML，而非图片，用户可在官方编辑器继续改——这是与多数「AI 画图」工具的根本区别。
2. **全模型多 Provider**：AWS Bedrock（默认）、OpenAI、Anthropic、Google AI/Vertex、Azure、Ollama、OpenRouter、DeepSeek、SiliconFlow、ModelScope、SGLang、Vercel AI Gateway 等，服务端可统一配置 `AI_MODELS_CONFIG`。
3. **MCP Server + Claude 插件**：`packages/mcp-server` + `packages/claude-plugin`，让任意支持 MCP 的 agent 直接画图（`npx @next-ai-drawio/mcp-server`）。
4. **VLM 视觉校验**：用多模态模型对生成图做视觉验证（critical/warning 分级），把问题回灌模型重画。
5. **部署矩阵齐全**：EdgeOne Pages 一键部署、Vercel、Cloudflare Workers、Docker、Electron 桌面端（Win/Mac/Linux）。

## 三、核心架构

Monorepo：`app/`（Next.js 前端）、`lib/`（服务端逻辑）、`packages/`（mcp-server、claude-plugin）、`electron/`（桌面端）、`edge-functions/`。

- 前端框架：Next.js 16 + React 19，图表渲染用 `react-drawio`。
- AI 层：`ai` + `@ai-sdk/*`（Vercel AI SDK），统一多 provider + 流式响应。
- 安全：`lib/ssrf-protection.ts`、`lib/user-id.ts`、`lib/dynamo-quota-manager.ts` 说明其为多租户 SaaS 形态（含管理面板 `/admin`）。

## 四、应用场景与启发

- **Agent 可视化**：把「帮我画个系统架构图」交给 agent，比手写方便得多；MCP 化后可直接嵌入开发工作流。
- **教学/文档**：从 PDF/图片复刻图表，适合课件、技术文档。
- **借鉴点**：「声明式工具 + 严格结构约束 + 视觉自检」三段式，是「LLM 生成结构化产物」的通用范式，可迁移到 PPT/UI/代码生成。

## 五、源码深度解读

**1. `lib/system-prompts.ts`——draw.io XML 生成的核心约束**

系统提示把 AI 框定为「draw.io XML 专家」，并定义了四个工具（`display_diagram` / `edit_diagram` / `append_diagram` / `get_shape_library`）。关键硬约束：

```text
CRITICAL RULES:
1. Generate ONLY mxCell elements - NO wrapper tags (<mxfile>, <mxGraphModel>, <root>)
2. ALL mxCell elements must be siblings - NEVER nest mxCell inside another mxCell
5. Set parent="1" for top-level shapes
Layout constraints: x in 0-800, y in 0-600, container max 700x550
NEVER include XML comments (<!-- -->) — Draw.io strips them, breaking edit_diagram
```

即模型**只生成 mxCell**，根节点由运行时补；坐标被强制收敛到单视口内防分页。这种「把自由生成约束成可解析 DSL」的设计，是其可用性的根基。

**2. `lib/diagram-validator.ts`——VLM 视觉自检闭环**

```ts
export function formatValidationFeedback(result: ValidationResult): string {
  const criticalIssues = result.issues.filter((i) => i.severity === "critical")
  const warnings = result.issues.filter((i) => i.severity === "warning")
  // ...拼装 "DIAGRAM VISUAL VALIDATION FAILED" 反馈，引导模型重画
}
```

实际校验由 `useValidateDiagram` 钩子走 AI SDK 的 `useObject` 完成，校验结果作为工具错误回灌模型——形成「生成→视觉验证→修复」的闭环。

## 六、社区口碑

- 36k⭐ / 3.9k fork，TrendShift 徽章，多语言文档（中/日/英）。
- 商业赞助明确：ByteDance Doubao（demo 用 glm-4.7）、Atlas Cloud（OpenAI 兼容 API），demo 站点可用。
- 口碑信号正向，但属个人维护型项目（sponsor 驱动），长期可持续性待观察。

## 七、竞品对比

| 维度 | next-ai-draw-io | tldraw make-real | Excalidraw AI |
|------|----------------|------------------|---------------|
| 产物 | 标准 draw.io XML（可编辑） | tldraw 画布 | Excalidraw 格式 |
| Agent 接入 | 官方 MCP | 无 | 无 |
| 云架构图标 | AWS/Azure/GCP/K8s 库 | 弱 | 弱 |
| 视觉自检 | VLM 校验 | 无 | 无 |

**差异点**：唯一同时做到「标准可编辑格式 + MCP agent 化 + 云图标库 + 视觉自检」。

## 八、核心研判

- **强模型依赖**：官方明确推荐 Claude Sonnet 4.5 / GPT-5.1 / Gemini 3 Pro / DeepSeek V3.2/R1——弱模型在长 XML 格式约束下易失败，这是质量天花板。
- **护城河 = 提示工程 + 结构约束 + 校验闭环**，而非算法；已被 fork 3.9k 次，壁垒有限。
- **建议**：做「结构化产物生成」类需求（PPT/UI/代码）时，可直接参考其「DSL 约束 + 工具化 + 视觉回灌」三段式；想嵌入 agent 工作流，MCP 接入是首选路径。

## 关键文件路径速查

- `lib/system-prompts.ts` — draw.io XML 生成系统提示与工具定义
- `lib/diagram-validator.ts` — VLM 视觉校验反馈格式化
- `lib/validation-schema.ts` — 校验结果 schema（单一事实源）
- `packages/mcp-server/` — 供 agent 调用的 MCP 服务器
- `packages/claude-plugin/` — Claude Code 插件封装
- `app/`、`components/`、`contexts/` — Next.js 前端与编辑器集成
