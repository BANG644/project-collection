# Michaelliv-pi-dynamic-workflows - 全方位深度调研

## 项目全景
- **仓库**：`Michaelliv/pi-dynamic-workflows`
- **一句话定位**：Michaelliv/pi-dynamic-workflows：面向特定场景的开源项目
- **解决的问题**：该项目试图把 README 中描述的能力产品化/脚本化，降低特定任务的搭建或执行门槛。
- **基础指标**：Stars=894 / Forks=45 / 默认分支=`main`
- **Topics**：数据不可用
- **Homepage**：数据不可用

## 核心架构
### 目录结构判断
- 顶层目录分布（递归树抽样汇总）：src(6), tests(4), .github(2), .gitignore(1), README.md(1), biome.json(1), extensions(1), package-lock.json(1), package.json(1), tsconfig.json(1)
- 关键文件候选：package.json, tsconfig.json, README.md, src/agent.ts, src/display.ts, src/index.ts, src/structured-output.ts, src/workflow-tool.ts, src/workflow.ts, tests/workflow-display.test.ts, tests/workflow-parser.test.ts, tests/workflow-runtime.test.ts

### 设计亮点研判
- 存在 Node/前端或工具链入口，依赖与脚本编排应主要由 package.json 驱动。
- 项目显式提供测试目录，说明作者至少为关键行为建立了可回归验证。
- 仓库包含 .github 自动化配置，通常代表 CI 或 issue 模板已被纳入工程流程。

## 源码深度解读
### README / 说明文档要点
# pi-dynamic-workflows

> Claude-Code-style dynamic workflows for [Pi](https://github.com/earendil-works/pi).

A Pi extension that adds a `workflow` tool. Instead of one assistant doing everything sequentially, the model writes a small JavaScript script that fans out the work across many isolated subagents, then synthesizes the results.

Great for codebase audits, multi-perspective review, large refactors, and fan-out research.

Inspired by Anthropic's [dynamic workflows in Claude Code](https://claude.com/blog/introducing-dynamic-workflows-in-claude-code).

## Install

```bash
pi install npm:pi-dynamic-workflows
# or from a local checkout
pi install /path/to/pi-dynamic-workflows
```

Then in Pi:

```text
/reload
```

That's it. The extension registers a `workflow` tool and activates it on session start.

## Usage

Just ask Pi for a workflow in plain language:

```text
Run a workflow to inspect this repository and summarize the main modules.
```

The model will write a workflow script and call the `workflow` tool. Live progress shows up inline:

```text
◆ Workflow: inspect_project (3/3 done)
  ✓ Scan 1/1
    #1 ✓ repo inventory
  ✓ Analyze 2/2
    #2 ✓ source modules
    #3 ✓ final summary
```

Press `Esc` to cancel a running workflow. Active subagents are aborted and surfaced as skipped.

## Workflow script shape

A workflow is plain JavaScript. The first statement must export literal metadata. `name` and `description` are required; `phases` is optional documentation for an expected outline. The live progress view is driven by `phase(...)` calls at runtime:

```js
export const meta = {
  name: 'inspect_project',
  description: 'Inspect a repository and summarize the main modules',
  phases: [
    { title: 'Scan' },
    { title: 'Analyze' },
  ],
}

phase('Scan')
const inventory = await agent('Inspect the repository structure.', {
  label: 'repo inventory',
})

phase('Analyze')
const summary = await agent(
  'Summarize the main modules from this inventory:\n' + inventory,
  { label: 'module summary' },
)

return { inventory, summary }
```

Phases are discovered as the script runs, so conditional and loop-created phases work naturally. If a branch is skipped, its 
...[truncated]

### 关键文件精读
### `package.json`
```
{
  "name": "pi-dynamic-workflows",
  "version": "1.0.1",
  "description": "Claude-Code-style dynamic workflow orchestration for Pi.",
  "type": "module",
  "main": "./dist/index.js",
  "types": "./dist/index.d.ts",
  "exports": {
    ".": {
      "types": "./dist/index.d.ts",
      "import": "./dist/index.js"
    },
    "./workflow": {
      "types": "./types/workflow.d.ts"
    }
  },
  "files": [
    "dist/",
    "extensions/",
    "src/",
    "types/",
    "README.md"
  ],
  "scripts": {
    "test": "npm run check && npm run build && npm run test:unit",
    "test:unit": "tsx --test tests/**/*.test.ts",
    "check": "biome check .",
    "format": "biome format --write .",
    "lint": "biome lint .",
    "build": "tsc",
    "dev": "tsx src/index.ts"
  },
  "keywords": [
    "pi-package",
    "pi",
    "workflow",
    "agents"
  ],
  "pi": {
    "extensions": [
      "extensions/workflow
...[truncated]
```

### `tsconfig.json`
```
{
  "compilerOptions": {
    "target": "ES2022",
    "module": "NodeNext",
    "moduleResolution": "NodeNext",
    "strict": true,
    "esModuleInterop": true,
    "skipLibCheck": true,
    "forceConsistentCasingInFileNames": true,
    "rootDir": "src",
    "outDir": "dist",
    "declaration": true
  },
  "include": ["src/**/*.ts"]
}
```

### `README.md`
```
# pi-dynamic-workflows

> Claude-Code-style dynamic workflows for [Pi](https://github.com/earendil-works/pi).

A Pi extension that adds a `workflow` tool. Instead of one assistant doing everything sequentially, the model writes a small JavaScript script that fans out the work across many isolated subagents, then synthesizes the results.

Great for codebase audits, multi-perspective review, large refactors, and fan-out research.

Inspired by Anthropic's [dynamic workflows in Claude Code](https://claude.com/blog/introducing-dynamic-workflows-in-claude-code).

## Install

```bash
pi install npm:pi-dynamic-workflows
# or from a local checkout
pi install /path/to/pi-dynamic-workflows
```

Then in Pi:

```text
/reload
```

That's it. The extension registers a `workflow` tool and activates it on session start.

## Usage

Just ask Pi for a workflow in plain language:

```text
Run a workflow to i
...[truncated]
```

### `src/agent.ts`
```
import type { AssistantMessage, TextContent } from "@earendil-works/pi-ai";
import {
  type CreateAgentSessionOptions,
  createAgentSession,
  createCodingTools,
  getAgentDir,
  SessionManager,
  SettingsManager,
  type ToolDefinition,
} from "@earendil-works/pi-coding-agent";
import type { Static, TSchema } from "typebox";
import { createStructuredOutputTool, type StructuredOutputCapture } from "./structured-output.js";

export interface WorkflowAgentOptions {
  cwd?: string;
  /** Extra tools available to the subagent in addition to the structured output tool. */
  tools?: ToolDefinition[];
  /** Override any createAgentSession option (model, authStorage, resourceLoader, etc.). */
  session?: Partial<CreateAgentSessionOptions>;
  /** Extra system guidance prepended to every subagent task. */
  instructions?: string;
}

export interface AgentRunOptions<TSchemaDef extends TSchema | unde
...[truncated]
```

### `src/display.ts`
```
import type { ExtensionContext } from "@earendil-works/pi-coding-agent";
import type { WorkflowMeta } from "./workflow.js";

export type WorkflowAgentStatus = "queued" | "running" | "done" | "error" | "skipped";

export interface WorkflowAgentSnapshot {
  id: number;
  label: string;
  phase?: string;
  prompt: string;
  status: WorkflowAgentStatus;
  resultPreview?: string;
  error?: string;
}

export interface WorkflowSnapshot {
  name: string;
  description?: string;
  phases: string[];
  currentPhase?: string;
  logs: string[];
  agents: WorkflowAgentSnapshot[];
  agentCount: number;
  runningCount: number;
  doneCount: number;
  errorCount: number;
  durationMs?: number;
  result?: unknown;
}

export interface WorkflowDisplay {
  update(snapshot: WorkflowSnapshot): void;
  complete(snapshot: WorkflowSnapshot): void;
  clear(): void;
}

export interface WorkflowDisplayOptions {
  key
...[truncated]
```

### `src/index.ts`
```
export type { AgentRunOptions, AgentRunResult, WorkflowAgentOptions } from "./agent.js";
export { WorkflowAgent } from "./agent.js";
export type {
  WorkflowAgentSnapshot,
  WorkflowAgentStatus,
  WorkflowDisplay,
  WorkflowDisplayOptions,
  WorkflowSnapshot,
} from "./display.js";
export {
  createToolUpdateWorkflowDisplay,
  createWidgetWorkflowDisplay,
  createWorkflowSnapshot,
  preview,
  recomputeWorkflowSnapshot,
  renderWorkflowLines,
  renderWorkflowText,
} from "./display.js";
export type { StructuredOutputCapture, StructuredOutputToolOptions } from "./structured-output.js";
export { createStructuredOutputTool } from "./structured-output.js";
export type {
  AgentOptions,
  WorkflowMeta,
  WorkflowMetaPhase,
  WorkflowRunOptions,
  WorkflowRunResult,
} from "./workflow.js";
export { parseWorkflowScript, runWorkflow } from "./workflow.js";
export type { WorkflowToolInput, Workfl
...[truncated]
```

### 关键逻辑总结
- 从关键文件组合看，项目更像是**围绕单一目标组织的任务流水线/工具链**，而不是超重平台。
- 入口文件决定外部交互界面（CLI / API / UI），配置文件决定运行时依赖，测试文件则暴露作者真正关心的行为边界。
- 如果用户只读 README，通常只能知道“能做什么”；而从目录与入口文件能看出“怎么做、扩展点在哪、维护成本高不高”。

## 社区口碑
### GitHub Issues 抽样
- #17 [CLOSED] Mentioning sources of randomness in agent prompts triggers the non-determinism checker（comments=[] labels=无）
- #14 [CLOSED] Need a types intelligence or work flow field schema to help when writting workflw ts file.（comments=[] labels=无）
- #13 [OPEN] Support strong/medium/weak model configuration for workflow agents（comments=[{'id': 'IC_kwDOSqt5l88AAAABEXMryw', 'author': {'login': 'joshuacc'}, 'authorAssociation': 'NONE', 'body': 'I like the idea of having this as an option that I can set defaults on, but I also need to be able to set arbitrary models on specific agents. I have a branch [over here](https://github.com/joshuacc/pi-dynamic-workflows/tree/codex/per-agent-model-selection) that allows this and it\'s been working great for me.\n\nBecause of that need, I\'d suggest that "small", "big", and "medium" be set via a `modelTier` or `modelClass` config property instead of the `model` property.', 'createdAt': '2026-05-31T19:00:17Z', 'includesCreatedEdit': False, 'isMinimized': False, 'minimizedReason': '', 'reactionGroups': [{'content': 'THUMBS_UP', 'users': {'totalCount': 1}}], 'url': 'https://github.com/Michaelliv/pi-dynamic-workflows/issues/13#issuecomment-4587727819', 'viewerDidAuthor': False}] labels=无）
- #12 [CLOSED] [bug] Error: #<Promise> could not be cloned.（comments=[] labels=无）
- #11 [OPEN] Audit: faithfulness gaps vs Claude Code's integrated Workflow tool (6 untracked)（comments=[] labels=无）
- #10 [OPEN] Support forked agents (fan-out from a shared parent context)（comments=[] labels=无）

### Pull Requests 抽样
- PR #25 [CLOSED] Add deterministic JSON file helpers to workflow runtime
- PR #24 [CLOSED] Add per-agent model selection, scriptPath loading, and persisted transcripts
- PR #23 [MERGED] Fix determinism checks for prompt mentions
- PR #22 [MERGED] Add workflow authoring types
- PR #21 [MERGED] Guard workflow results against Promise clone failures

### Releases 抽样
- v1.0.1（published=2026-05-31T07:19:39Z latest=True）
- v1.0.0（published=2026-05-28T21:22:48Z latest=False）

### 真实反馈与维护信号研判
- 抽样 issue 中 open/closed 约为 5/3，可作为维护者响应速度的弱信号。
- 近期 PR 抽样里可见已合并项 4 个，说明项目并非完全冻结。
- 存在 release 记录，说明作者有版本化交付意识。
- 由于本批处理以 GitHub 官方数据为主，若外部搜索结果缺失，应把 GitHub issue/PR 视为最可信的一手社区反馈源。
- 高频问题通常比 README 更能暴露真实落地难点：安装、兼容性、性能边界、文档歧义、平台限制。

## 竞品对比
| 维度 | pi-dynamic-workflows | 竞品/替代 |
|---|---|---|
| 定位 | 面向仓库作者设定的具体场景，通常更垂直 | LangGraph / AutoGen / CrewAI 往往更通用或生态更大 |
| 学习曲线 | 依赖其内部脚本/配置约定 | 通用方案学习成本更高，但生态更成熟 |
| 差异化 | 仓库通常以“快上手、场景专用、意见化实现”为卖点 | 通用方案强调可扩展、稳定性、跨场景能力 |
| 风险 | 作者驱动、文档深度可能不足、接口稳定性不确定 | 大项目更稳定，但改造成本更高 |

## 核心研判
### 优势
- 对目标问题有强意见化实现，落地路径通常比“从零搭建通用栈”更短。
- 如果核心文件少而清晰，二次阅读和定制成本较低。
- GitHub 原生 issue / release / PR 能直接帮助判断项目是否仍在演进。

### 风险
- 若 stars、forks、release 或 PR 活跃度偏低，意味着长期维护能力要谨慎评估。
- 如果关键逻辑过于集中在单文件脚本中，后续扩展会受到可维护性约束。
- 若缺少测试/CI/配置 schema，生产环境采用前应先做自测和边界验证。

### 适用场景
- 需要快速验证该仓库所解决的问题是否值得投入。
- 团队愿意接受一定的作者意见化设计，以换取更快交付。
- 适合作为参考实现、内部 PoC、垂直任务工具，而非默认直接替代成熟平台。

### 不适用场景
- 对 SLA、兼容矩阵、长期 LTS 有强要求的核心生产系统。
- 需要极高社区冗余、插件生态或企业级支持的场景。

## 关键文件路径速查
- `package.json`
- `tsconfig.json`
- `README.md`
- `src/agent.ts`
- `src/display.ts`
- `src/index.ts`
- `src/structured-output.ts`
- `src/workflow-tool.ts`
- `src/workflow.ts`
- `tests/workflow-display.test.ts`
- `tests/workflow-parser.test.ts`
- `tests/workflow-runtime.test.ts`

## 3 条关键发现
- 代码入口/骨架集中在：package.json, tsconfig.json, README.md, src/agent.ts, src/display.ts
- 近期开源反馈以 issue 为主，典型议题包括：Mentioning sources of randomness in agent prompts triggers the non-determinism checker；Need a types intelligence or work flow field schema to help when writting workflw ts file.
- 发布节奏可从最新 release 观察：v1.0.1

## 研究方法与数据来源
- GitHub Repo API / README / 默认分支递归文件树
- 关键源码文件抽样精读
- Issues / PRs / Releases 社区活动抽样
- 说明：若外部搜索数据不可用，则明确标注并不伪造口碑结论
