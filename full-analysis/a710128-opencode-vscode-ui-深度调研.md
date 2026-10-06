# OpenCode UI — 把 OpenCode 会话装进 VS Code 编辑器

> 调研日期：2026-10-06 ｜ Stars：22 ｜ 语言：TypeScript ｜ License：MIT ｜ 维护者：a710128（publisher: zgy）
> 仓库：https://github.com/a710128/opencode-vscode-ui

---

## 一、项目亮点（差异化）

1. **只做"外壳"，不重造 Agent**：OpenCode UI 是 OpenCode（开源 AI 编码 Agent）的编辑器内界面层，把终端里的会话管理搬进 VS Code，复用 OpenCode 自身的推理与工具能力。
2. **工作区感知的会话侧边栏**：从 Activity Bar 按 workspace folder 组织 OpenCode 会话，支持创建 / 重开 / 刷新 / 删除，多项目并行不串。
3. **每会话独立 Tab + 伴侣视图**：每个会话开一个专属 webview panel，并配套 Todo 视图与"改动文件"视图，编码时随时可见 agent 改了哪些文件。
4. **Remote SSH 就绪**：`extensionKind: ["workspace"]`，跑在正确的 extension host 上，Remote SSH 场景下自动对应当前远端 workspace，且要求在远端主机也装 `opencode`。
5. **内置环境自检**：`OpenCode: Check Environment` 命令提前发现 `opencode` 不在 PATH 或不可执行，给出清晰修复提示，而不是等会话起不来才报错。

> ⚠️ 注意：项目处于极早期（22★、v0.0.1、无正式发行版），属于"OpenCode 用户的效率外壳"，受众窄但定位清晰。

---

## 二、核心架构

- **进程模型**：扩展以 `workspace` 模式运行（非 `ui` 模式），因此能跨越本地 / 远端 extension host。每个 workspace folder 维护**一个 OpenCode runtime**。
- **Runtime 状态机**：`WorkspaceRuntime` 的 `state` 取值 `idle | starting | ready | error | stopped | stopping`，扩展负责拉起 `opencode serve` 子进程、探测端口、做健康检查。
- **会话面板**：`SessionPanelManager` 以 `Map<panelKey, SessionPanelController>` 管理每个 `(workspace, session)` 的 webview panel，支持 `retainContextWhenHidden` 保活。
- **通信链路**：扩展通过 `opencode serve` 起的本地 HTTP server + 官方 `@opencode-ai/sdk@1.2.21` 的 `Client` 与 OpenCode 交互；`freeport()` 动态分配 `127.0.0.1` 端口，`health()` 轮询 `/global/health` 直到就绪。

```
传统模式                       OpenCode UI 模式
终端里跑 opencode  ──►   VS Code Activity Bar 里管理会话
多 tab 切终端       ──►   每个会话一个编辑器内 webview Tab
肉眼找改动文件     ──►   "改动文件"伴侣视图直接列出
```

---

## 三、源码深度解读（关键模块）

### 1. 端口分配与健康探针 — `src/core/server.ts`

```ts
export async function freeport() {
  return await new Promise<number>((resolve, reject) => {
    const srv = net.createServer()
    srv.once("error", reject)
    srv.listen(0, "127.0.0.1", () => {           // 让 OS 分配一个空闲端口
      const addr = srv.address()
      if (!addr || typeof addr === "string") { srv.close(() => reject(new Error("failed to allocate port"))); return }
      srv.close((err) => { if (err) reject(err); else resolve(addr.port) })
    })
  })
}

export async function health(url: string, timeout: number, tries: number) {
  for (let i = 0; i < tries; i++) {
    const ctrl = new AbortController()
    const timer = setTimeout(() => ctrl.abort(), timeout)
    try {
      const res = await fetch(`${url}/global/health`, { signal: ctrl.signal })
      if (res.ok) { clearTimeout(timer); return }
    } catch {}
    clearTimeout(timer)
    await wait(400)
  }
  throw new Error("health check timed out")
}
```

要点：端口用 `listen(0)` 交给内核分配，避免硬编码冲突；健康检查轮询 `global/health`，超时前多次重试——这是"拉起子进程后等待就绪"的标准稳健写法。

### 2. 缺失 opencode 的友好报错 — `src/core/runtime-errors.ts`

```ts
const MISSING_OPENCODE_MARKERS = [
  'command "opencode" was not found',
  'command "opencode" is not executable',
  "failed to start opencode:",
  "was not found on PATH",
  "was not found on the current host PATH",
  "is not executable",
]

export function missingOpencodeMessage(rt?: Pick<WorkspaceRuntime, "name">) {
  const host = vscode.env.remoteName || "local"
  const target = rt?.name ? ` for ${rt.name}` : ""
  return `OpenCode UI could not start opencode${target}. Install the opencode CLI on the current ${host} host and ensure it is available on PATH, or set OpenCode UI: Executable Path.`
}
```

要点：用一组错误特征串识别"opencode 没装/不可执行"，并区分 local vs Remote SSH host（`vscode.env.remoteName`），提示用户去对应主机装 CLI——这正是 Remote SSH 场景最常见的踩坑点。

### 3. 面板生命周期管理 — `src/panel/provider/index.ts`

```ts
export class SessionPanelManager implements vscode.Disposable {
  private readonly panels = new Map<string, SessionPanelController>()
  async open(ref: SessionPanelRef) {
    const key = panelKey(ref)
    const existing = this.panels.get(key)
    if (existing) { await existing.reveal(); return existing.panel }   // 已开则聚焦，不重复创建
    const panel = vscode.window.createWebviewPanel(SESSION_PANEL_VIEW_TYPE, panelTitle(ref.sessionId),
      vscode.ViewColumn.Active, { enableScripts: true, retainContextWhenHidden: true,
        localResourceRoots: [vscode.Uri.joinPath(this.extensionUri, "dist")] })
    const controller = this.attach(ref, panel)
    await controller.push()
    return panel
  }
}
```

要点：`panelKey` 去重 + `reveal()` 复用，避免同一会话开多个面板；webview 用 `retainContextWhenHidden` 在切走时保活，`localResourceRoots` 锁定到 `dist` 防越权读文件。

### 4. 依赖与激活 — `package.json`

```jsonc
"engines": { "vscode": "^1.94.0" },
"main": "./dist/extension.js",
"extensionKind": ["workspace"],
"dependencies": { "@opencode-ai/sdk": "1.2.21", "diff": "..." },
"activationEvents": ["onStartupFinished", "onView:opencode-ui.sessions", "onWebviewPanel:opencode-ui.session", ...]
```

要点：强绑定 `@opencode-ai/sdk@1.2.21`，意味着 OpenCode 的 serve 协议一变此扩展就可能要跟进——这是它最大的耦合风险。

---

## 四、应用场景与启发

- **场景**：你已经是 OpenCode 用户、且主要工作在 VS Code 里，想要"不切终端"地管理多个项目的多个会话、随时看改动文件。
- **启发（可借鉴点）**：
  - "Agent 可视化外壳"是一个可复用的产品形态：CLI Agent + 编辑器内 UI 解耦，比把 Agent 塞进 IDE 插件内核更轻、更易跟上游。
  - `extensionKind: workspace` + Remote SSH 对齐，是写 VS Code 扩展时"远端开发"正确姿势的最小范本。
  - 用"错误特征串匹配"做环境诊断，比让异常直接冒泡友好得多，值得任何需要外部 CLI 的扩展借鉴。

---

## 五、社区口碑

数据不可用（22★、无发行版、issues 极少、无公开评测）。结论：属于早期个人/小众效率工具，口碑尚未形成。质量判断应基于源码与定位，而非社区热度。

---

## 六、竞品对比

| 维度 | OpenCode UI | Claude Code / CodeBuddy 内置 UI | Continue / Cody |
|------|-------------|-------------------------------|-----------------|
| 本质 | OpenCode 的编辑器外壳 | 自家 Agent 自带 UI | 独立 AI 编码插件 |
| 是否重造 Agent | 否（纯 UI） | 否 | 否 |
| 多会话管理 | 侧边栏 + 独立 Tab | 各家的会话列表 | 对话式 |
| 改动文件可视化 | 内置伴侣视图 | 部分支持 | 部分支持 |
| 远端 SSH | 原生对齐 | 视实现 | 视实现 |

**差异化**：它不抢 Agent 的活，只解决"OpenCode 在终端里不好管"的痛点；代价是强绑定 OpenCode 版本与 serve 协议。

---

## 七、核心研判

- **价值**：对 OpenCode 用户是"小但准"的效率补丁；架构干净、代码量小（151 文件，核心在 `src/core` + `src/panel`）、值得作为"CLI Agent + 编辑器 UI 解耦"的参考实现。
- **风险**：① Stars 极低、无发行版，维护可持续性存疑；② 强耦合 `@opencode-ai/sdk@1.2.21`，上游协议变更即断裂；③ 功能高度依赖 `opencode serve` 的本地 HTTP 端口，企业代理/防火墙环境可能受阻。
- **建议**：OpenCode 用户可试用；若要做同类"Agent 外壳"，直接 fork 其 `server.ts` 的拉起/健康/报错三段最划算。

---

## 八、关键文件路径速查

| 文件 | 作用 |
|------|------|
| `src/extension.ts` | 扩展入口，注册命令与视图 |
| `src/core/server.ts` | runtime 拉起、`freeport`、`health` 探针、`WorkspaceRuntime` 类型 |
| `src/core/runtime-errors.ts` | 缺失 opencode 的识别与友好报错 |
| `src/core/settings.ts` | 可执行路径 / 代理读取 |
| `src/core/workspace.ts` | `WorkspaceManager` 按 workspace 管 runtime |
| `src/panel/provider/index.ts` | `SessionPanelManager` 面板生命周期 |
| `src/panel/webview/index.tsx` | webview 内 React 入口 |
| `package.json` | 依赖、激活事件、`extensionKind: workspace` |
