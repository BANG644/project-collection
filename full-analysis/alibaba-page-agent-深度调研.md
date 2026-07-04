# 🔬 alibaba/page-agent - 全方位深度调研

> 调研日期：2026-07-05 | 版本：v1.11.0 (2026-07-03) | 许可：MIT
> 仓库：[https://github.com/alibaba/page-agent](https://github.com/alibaba/page-agent)

---

## 📌 一句话定位

**JavaScript 页内 GUI Agent**——一行脚本注入网页，让用户用自然语言操控 Web 界面。不是浏览器自动化工具，而是"住在网页里的 AI Copilot"。

> "GUI Agent Living in Your Webpage. Control web interfaces with natural language."

---

## ⭐ 项目亮点

### 核心创新

1. **纯页内 JS 运行**——不需要浏览器扩展、不需要 Python、不需要无头浏览器，一段 `<script>` 标签给任何网页装上 AI 助理
2. **Text-based DOM 操作**——不截图、不需要多模态 LLM，将 DOM 序列化为结构化文本喂给文本 LLM，大幅降低 Token 成本和延迟
3. **BYO LLM**——不绑定任何模型供应商，支持所有 OpenAI 兼容 API（Qwen、GPT、Claude、DeepSeek、Gemini、Ollama…）
4. **原生利用用户登录态**——运行在用户浏览器内，直接使用已有 Cookie 和 Session，无需额外认证

### 数据概览

| 指标 | 数据 |
|------|------|
| ⭐ Stars | 23,031（2026-07-05） |
| 🍴 Forks | 2,003 |
| 👤 贡献者 | 30 |
| 🔄 Release 数 | 30（含 v1.11.0） |
| 📅 创建时间 | 2025-09-23 |
| 🔄 最近更新 | 2026-07-03（持续活跃） |
| ⚠️ Open Issues | 45 |
| 📦 包名 | `page-agent`（npm） |
| 🔤 语言 | TypeScript |
| 🏷️ 标签 | agent, ai, browser-automation, javascript, mcp, typescript, web |

---

## 🏗️ 项目架构全景

### Monorepo 架构（8 个 npm 包）

```
page-agent/
├── packages/
│   ├── page-controller/   # DOM 操作引擎 + SimulatorMask 遮罩
│   ├── llms/              # LLM 客户端（OpenAI 兼容封装）
│   ├── core/              # Agent 核心调度层（PageAgentCore）
│   ├── page-agent/        # 带 UI 的主入口类（整合 Core+Controller+UI）
│   ├── ui/                # UI 面板 + 国际化（en-US / zh-CN）
│   ├── mcp/               # MCP Server（Beta，外部 Agent 控制浏览器）
│   ├── extension/         # Chrome 扩展（多页跨 Tab 支持）
│   └── website/           # 官网与文档
├── docs/                  # 文档
└── .github/               # CI/CD 工作流
```

### 五层架构金字塔

```
┌──────────────────────────────────────┐
│  Layer 5: UI 面板层                  │
│  Panel / I18n / Card Components      │
├──────────────────────────────────────┤
│  Layer 4: Agent 核心调度层           │
│  PageAgentCore / LLM / Tool Router   │
├──────────────────────────────────────┤
│  Layer 3: DOM 智能感知层             │
│  FlatDomTree / flatTreeToString      │
├──────────────────────────────────────┤
│  Layer 2: 交互操作层                 │
│  clickElement / inputText / scroll   │
├──────────────────────────────────────┤
│  Layer 1: WebGL 视觉效果层           │
│  SimulatorMask / Motion / Shaders    │
└──────────────────────────────────────┘
```

### 核心数据流：Observe → Think → Act 循环

```
用户输入 → [主循环 for(;;)]
  │
  ├─ 1. observe: getBrowserState() → DOM 序列化为文本
  │
  ├─ 2. handleObservations() → 注入系统/历史/步数警告
  │
  ├─ 3. 组装 Prompt → system + 历史 + 页面快照
  │
  ├─ 4. invoke() → LLM 调用
  │
  ├─ 5. normalizeResponse() → 5 级容错解析
  │
  ├─ 6. 执行 Action → click / input / scroll / select / done / ask_user / wait
  │
  ├─ 7. 记录历史 → 存入 history 数组
  │
  └─ 8. 检查终止 → done / maxStep / error → 退出
       │
       └─ 每步 0.4s 冷却 + 完成/失败返回
```

### 关键架构决策

| 决策 | 选择 | 理由 |
|------|------|------|
| Agent 循环 | MacroTool 模式（单工具包装多工具） | 强制 LLM 每个步骤输出反思+记忆+目标+动作 |
| DOM 感知 | 文本序列化（FlatDomTree） | 无需截图、无需多模态、低 Token 成本 |
| 事件模拟 | 完整 W3C 事件序列 | 兼容 React/Vue/各种前端框架 |
| 响应容错 | 5 级渐进修复（normalizeResponse） | LLM 输出不稳定时的"永不崩溃"保障 |
| 状态隔离 | PageController 独立于 LLM | 单元测试友好，可被 Node.js 脚本调用 |
| UI 可剥离 | Core 无 UI 依赖 | 开发者可只用无头核心，自行构建 UI |

---

## 💡 应用场景与启发

### 最佳场景

1. **SaaS AI Copilot**（核心场景）—— 一行代码为 SaaS 产品添加自然语言交互，无需重写后端
2. **智能表单填写** —— ERP/CRM/管理后台中，将 20 次点击工作流压缩为一句话
3. **Web 无障碍增强** —— 让视障用户通过语音/自然语言操作任何网页
4. **产品教学与演示** —— AI 边做边教，演示"如何提交报销申请"等操作流程
5. **复杂后台操作辅助** —— 企业系统员工无需学习复杂 UI，一句话完成操作

### 与 Playwright/Puppeteer 的本质区别

| 维度 | Playwright/Puppeteer | page-agent |
|------|---------------------|------------|
| **运行位置** | 外部进程控制浏览器 | 页面内 JS，同进程 |
| **依赖** | Python + 浏览器二进制 | 仅一个 `<script>` 标签 |
| **用户安装** | 需装扩展或客户端 | 零安装，打开网页即用 |
| **感知方式** | 截图 + 多模态 LLM | Text-based DOM（纯文本） |
| **定位** | 测试、爬虫、RPA | 产品内 AI Copilot、无障碍 |
| **登录态** | 需手动管理 Cookie | 原生复用用户浏览器会话 |
| **适合** | 服务端自动化 | 客户端 Web 增强 |

### LLM 驱动 Web 控制的独特价值

- **语义理解**：LLM 能理解"把上周的销售数据导出成 Excel"这样的高层次意图，分解为多个子步骤
- **自适应性**：页面结构变化时无需重写选择器，LLM 通过 DOM 文本动态定位元素
- **容错性**：5 级渐进修复 + try/catch 体系确保"永不崩溃"
- **低成本**：纯文本 LLM 即可运行，无需昂贵的多模态模型

### 局限与短板

1. **Text-based 固有短板** —— 无法处理 Canvas、验证码、图表等纯视觉元素
2. **单页边界** —— 不加 Chrome 扩展只能操作当前页面
3. **CSP 兼容性** —— 严格 Content Security Policy 可能阻止脚本注入
4. **跨域 iframe** —— 无法获取跨域 iframe 内部 DOM
5. **LLM 延迟** —— 每步 0.5-3s 推理时间，不适合毫秒级高频率自动化
6. **不适用爬虫/测试** —— 官方定位明确：客户端增强，非服务端自动化
7. **贡献门槛** —— 明确不接受纯 AI/Bot 生成的贡献（防止被 PR 淹没）
8. **无完整 Step Replay** —— 不适合金融/医疗等需要审计回放的场景

---

## 🧠 核心源码解读

### 1. `packages/page-agent/src/PageAgent.ts` — 主入口（第 1 层）

```typescript
export class PageAgent extends PageAgentCore {
    panel: Panel
    constructor(config: PageAgentConfig) {
        const pageController = new PageController({...config, enableMask: true})
        super({...config, pageController})
        this.panel = new Panel(this, {language: config.language})
    }
}
```
极简封装：整合 PageController + PageAgentCore + Panel。

### 2. `packages/core/src/PageAgentCore.ts` — 核心循环（第 2 层）

核心 Agent 主循环方法 `execute(task)`：
- **触发流程**：`onBeforeTask` → `while(true)` → `onBeforeStep` → observe → think → act → `onAfterStep`
- **MacroTool 模式**（`#packMacroTool`）：将所有工具合并为 `AgentOutput` 单一 Schema，强制 LLM 输出 `{evaluation_previous_goal, memory, next_goal, action}` 四元组
- **事件系统**：`statuschange`、`historychange`、`activity`、`dispose` 四种事件
- **容错机制**：内层 try/catch 捕获 Agent 错误（继续循环），外层 try/catch 处理外部/配置错误

### 3. `packages/core/src/tools/index.ts` — 工具注册表（第 3 层）

8 个内置工具 + 1 个实验性工具：

| 工具名 | 功能 | 关键代码行 |
|--------|------|-----------|
| `done` | 完成任务 | `return Promise.resolve('Task completed')` |
| `wait` | 等待页面加载 | 智能减去 LLM 调用耗时 |
| `ask_user` | 向用户提问 | 需 `onAskUser` 回调 |
| `click_element_by_index` | 按索引点击 | 委托 `pageController.clickElement` |
| `input_text` | 输入文本 | 委托 `pageController.inputText` |
| `select_dropdown_option` | 选择下拉 | 委托 `pageController.selectOption` |
| `scroll` | 垂直滚动 | 支持 `numPages` / `pixels` / `index` |
| `scroll_horizontally` | 水平滚动 | 同上 |
| `execute_javascript` | 执行 JS（实验性） | 需显式启用 |

### 4. `packages/llms/src/OpenAIClient.ts` — LLM 客户端（第 4 层）

- 兼容所有 OpenAI 格式 API
- 支持自定义 `transformRequestBody`（模型特定参数适配）
- 实现 5 种 HTTP 错误分类：`AUTH_ERROR`, `RATE_LIMIT`, `SERVER_ERROR`, `CONTEXT_LENGTH`, `CONTENT_FILTER`
- Zod 校验工具参数（`safeParse`），解析失败再抛 `INVALID_TOOL_ARGS`

### 5. `packages/page-controller/src/actions.ts` — 交互操作层（第 5 层）

**关键亮点**：
- **完整鼠标事件模拟**：`pointerover → pointerenter → mouseover → mouseenter → pointerdown → mousedown → focus → pointerup → mouseup → click`
- **contentEditable 双方案**：Plan A（合成 InputEvent）失败时自动回退 Plan B（`execCommand`）
- **getNativeValueSetter**：绕过 React Fiber 的 input 劫持
- **智能滚动**：从交互元素向上遍历查找可滚动容器，自动降级到页面滚动

### 6. `packages/page-controller/src/dom/dom_tree/index.js` — DOM 感知层（第 6 层）

**从 browser-use 移植并大幅改造**：
- 三级缓存系统（`boundingRects`、`clientRects`、`computedStyles` WeakMap）
- 多维度交互元素判断：语义标签、ARIA 角色、CSS cursor、事件监听器、data 属性、可滚动容器检测
- 添加 `data-page-agent-ignore` 属性支持（黑名单）
- `isHeuristicallyInteractive()` 启发式判断：基于 className + 位置关系推断
- Shadow DOM 穿透 + iframe 穿透（同源）

### 7. 系统提示词（`packages/core/src/prompts/system_prompt.md`）

精心设计的 prompt 工程模板，包含：
- `<intro>` — 角色定义
- `<browser_state>` — 要素索引格式说明 `[index]<type>text</type>`
- `<browser_rules>` — 严格操作规则（只操作有 index 的元素、单页限制、不处理验证码等）
- `<reasoning_rules>` — 推理模式引导（反思上一步、记忆维护、目标跟踪）
- `<examples>` — 优质输出示范
- `<task_completion_rules>` — 何时调用 `done`、success 判断标准

---

## 🌐 全网口碑画像

### 积极评价

| 来源 | 观点 |
|------|------|
| 博客园(it) | "20.4k stars 说明这个定位击中了很多开发者的痛点" |
| CSDN | "与 Playwright 是互补关系，不是替代关系" |
| 知乎 | "阿里搞的网页打工人——在网站里植入简单的代码，就能用自然语言指挥它" |
| 掘金 | "纯客户端的 GUI Agent 库，把 LLM 的推理能力嵌入到网页里" |
| 51CTO | "与 Selenium、Playwright 的核心区别：纯 JavaScript 方式运行在网页内" |

### 整体社区共识

- **定位精准**：填补了"重后端 Agent 编排"和"重依赖浏览器自动化"之间的空白
- **接入极简**：一行 CDN 代码即可体验，验证成本几乎为零
- **技术选型聪明**：Text-based DOM 避免多模态 LLM 的昂贵成本
- **解决真实痛点**：SaaS 开发者想加 AI Copilot 但又不想重写后端的刚需

### 常见批评与担忧

| 批评点 | 详情 |
|--------|------|
| **视觉盲区** | 纯文本 DOM 无法感知颜色/图标/布局状态 |
| **CSP 限制** | 严格企业 CSP 可能阻止注入 |
| **不适用爬虫** | 最易误用的地方——它是客户端工具，不是爬虫框架 |
| **LLM 不确定性** | 相同任务多次执行可能走不同路径 |
| **延迟成本** | 每步 0.5-3s + LLM API 费用，不适合高频场景 |
| **不够成熟** | 对比 browser-use（91K stars）生态仍有差距 |

---

## ⚔️ 竞品对比

### 核心竞品矩阵

| 维度 | page-agent | browser-use | Stagehand | Skyvern | Playwright |
|------|-----------|-------------|-----------|---------|------------|
| **⭐ Stars** | 23K | ~91K | ~21K | ~25K | ~70K+ |
| **语言** | TypeScript | Python | TypeScript | Python | TypeScript/JS |
| **运行模式** | **页内 JS** | 服务端 + Playwright | 服务端 + Playwright | 云端/自托管 | 服务端 |
| **感知方式** | **纯文本 DOM** | 截图+HTML双轨 | DOM+AI原语 | 截图+视觉 | Selector |
| **LLM 需求** | **文本 LLM 即可** | 偏好多模态 | 支持文本/多模态 | 视觉 LLM | 不依赖 LLM |
| **部署成本** | **一行 `<script>`** | Python+浏览器 | Node+浏览器 | 云 API / 自托管 | Node+浏览器 |
| **登录态利用** | **原生复用** | 需手动管理 | 需手动管理 | 需手动管理 | 需手动管理 |
| **跨页面** | 需 Chrome 扩展 | 内建多 Tab | Playwright 支持 | 内建 | 内建 |
| **MCP 支持** | ✅ Beta | ❌ | ❌ | ✅ | ✅ |
| **自愈性** | 高（LLM 动态定位） | 高 | 中（混合模式） | 高 | 低（选择器固定） |
| **适合场景** | SaaS Copilot、页内 | 复杂自主任务 | 开发者控制层 | 业务流程自动化 | 底层自动化框架 |
| **License** | MIT | MIT | MIT | AGPL-3.0 | Apache-2.0 |

### 定位差异分析

```
                      page-agent                
                    (页内嵌入式 Agent)
                         │
   ┌─────────────────────┼─────────────────────┐
   │                     │                     │
   ▼                     ▼                     ▼
服务端全自主         开发者控制层           业务流程平台
(browser-use)       (Stagehand)           (Skyvern)
   │                     │                     │
   └─────────────────────┼─────────────────────┘
                         │
                         ▼
                    Playwright
              (底层自动化基础设施)
```

### 关键差异

1. **page-agent vs browser-use**：page-agent 是**客户端嵌入式**，browser-use 是**服务端全自主**。前者一行脚本给自家产品加 AI，后者适合跨站点的复杂自主任务。

2. **page-agent vs Stagehand**：page-agent 强调自然语言全流程（一句话完成），Stagehand 强调"AI + 工程控制"混合模式（act/extract/observe 原语）。

3. **page-agent vs Skyvern**：Skyvern 是面向业务流程的**托管平台**（付费），page-agent 是**开源嵌入库**（免费 MIT）。

4. **page-agent vs Playwright**：page-agent 是 **AI 原生**（LLM 驱动），Playwright 是**确定性自动化**（选择器驱动）。二者本质互补，非替代。

---

## 🎯 核心研判

### 项目生命力评估

| 维度 | 评估 |
|------|------|
| **社区增长** | 🟢 极强（10 个月 23K stars，月均 2K+） |
| **更新频率** | 🟢 高（30 个 Release，平均 ~10 天/版本） |
| **代码质量** | 🟢 高（TypeScript 严格类型、Zod 校验、完整测试） |
| **文档质量** | 🟢 好（官方文档 + 中文社区大量教程） |
| **生态成熟度** | 🟡 中（Chrome 扩展 Beta、MCP Beta、社区项目尚少） |
| **团队背景** | 🟢 阿里巴巴开源 + 核心作者 gaomeng1900 持续活跃 |

### 竞争壁垒

1. **页内定位护城河**：service-side 方案无法触及"页内嵌入"这个场景（无需用户安装、原生复用登录态）
2. **极低接入门槛**：一行 `<script>` 标签的集成复杂度在 AI 浏览器工具领域无出其右
3. **成本优势**：纯文本 LLM 即可运行，Token 消耗远低于截图类方案
4. **MIT 许可**：企业可免费商用，无需担心许可限制

### 发展风险

1. **巨头入场**：Google A2UI、OpenAI Operator 等原生浏览器 Agent 可能挤压页内 Agent 空间
2. **browser-use 生态扩张**：browser-use 91K stars 的社区势能可能吸引更多开发者
3. **CSP 普及**：越来越多企业采用严格 CSP，限制页内脚本模式
4. **依赖 browser-use DOM 代码**：虽然合规引用，但核心技术栈存在外部依赖

### 个人判断

**商业价值**：极高。SaaS 产品加 AI Copilot 是 2025-2026 年的刚需，page-agent 以极低成本（一行代码 + MIT 许可）提供了这个能力。

**技术价值**：中高。"页内嵌入式 GUI Agent"这个分支的开创性工作，DOM 序列化为文本 + MacroTool 推理循环的设计模式值得借鉴。

**使用建议**：
- ✅ **推荐**：SaaS 产品加 AI Copilot、后台系统智能填表、产品无障碍增强
- ⚠️ **谨慎**：严格 CSP 环境、需要视觉理解的场景、对延迟有极高要求的场景
- ❌ **不推荐**：大规模爬虫、回归测试、服务端无人值守自动化

**一句话总结**：page-agent 是当前"页内嵌入式 GUI Agent"赛道的标杆项目，找到了一个被 Browser-use 和 Playwright 等 service-side 方案忽视的空白场景并精准击中，23K stars 是其价值的直接证明。

---

## 📂 关键文件路径速查

| 文件 | 说明 |
|------|------|
| `packages/page-agent/src/PageAgent.ts` | 主入口类（整合 Core+Controller+UI） |
| `packages/core/src/PageAgentCore.ts` | Agent 核心调度（Observe-Think-Act 循环） |
| `packages/core/src/tools/index.ts` | 8 个内置工具注册表 |
| `packages/core/src/prompts/system_prompt.md` | LLM 系统提示词（核心 prompt 工程） |
| `packages/core/src/types.ts` | Agent 类型定义 |
| `packages/llms/src/OpenAIClient.ts` | OpenAI 兼容 LLM 客户端 |
| `packages/page-controller/src/PageController.ts` | DOM 操作引擎（`getBrowserState`） |
| `packages/page-controller/src/actions.ts` | 交互操作（点击/输入/滚动） |
| `packages/page-controller/src/dom/dom_tree/index.js` | DOM 序列化引擎（移植自 browser-use） |
| `packages/page-controller/src/dom/dom_tree/type.ts` | FlatDomTree 类型定义 |
| `packages/ui/src/panel/` | UI 面板组件 |
| `packages/extension/src/agent/MultiPageAgent.ts` | Chrome 扩展多页 Agent |
| `packages/mcp/src/index.js` | MCP Server（Beta） |
| `packages/llms/src/utils.ts` | `normalizeResponse` 5 级容错 + `modelPatch` |
| `.github/workflows/ci.yml` | CI 工作流 |
| `docs/developer-guide.md` | 本地开发指南 |
