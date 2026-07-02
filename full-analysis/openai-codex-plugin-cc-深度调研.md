# 🔬 openai/codex-plugin-cc — 全方位深度调研

> 在 Claude Code 中使用 OpenAI Codex 审查代码或委派任务——AI 编程助手间的跨平台协作桥

**调研日期**: 2026-07-03
**仓库**: [openai/codex-plugin-cc](https://github.com/openai/codex-plugin-cc)
**Stars**: 22,561⭐ | **Forks**: 1,375 | **License**: Apache-2.0
**语言**: JavaScript | **最新发布**: v1.0.5 (2026-06-23)

---

## 📌 一句话定位

OpenAI 官方出品，让 Claude Code 用户能在不离开当前会话的情况下直接调用 Codex 进行代码审查、对抗性审查、Bug 修复委派和会话转移——是两个顶级 AI 编程助手之间的"桥梁"插件。

## ⭐ 项目亮点

1. **"AI 编程助手的联邦"——跨平台委派** — 这是目前唯一一个官方支持的"Claude Code ↔ Codex"协作插件。你不是只能选一个，而是可以让 Claude Code 做规划、Codex 做审查、Claude 再处理修复——形成流水线。
2. **审查门控（Review Gate）——自动安全检查** — 独特的 `Stop` 钩子机制：在 Claude 提交代码前自动触发 Codex 审查，如果发现问题就阻止提交。这是一个"AI 帮 AI 做代码审查"的闭环。
3. **8 个斜杠命令覆盖完整工作流** — 从 `/codex:review`（审查）到 `/codex:rescue`（委派修复）到 `/codex:transfer`（转移会话），覆盖了"审查→委派→追踪→转移→取消"的完整生命周期。
4. **Codex 子代理（codex-rescue）** — 委派任务时不是简单的"让 Codex 跑命令"，而是通过一个 AI 子代理做任务分解、进度跟踪和结果汇报。子代理的设计模式值得所有 AI 插件借鉴。
5. **后台任务+状态轮询** — 所有耗时操作（审查、委派）支持 `--background` 参数，主线程不阻塞，通过 `/codex:status` 和 `/codex:result` 查询进度。这是"异步 AI 协作"的正确工程模式。

## 🏗️ 项目架构全景

### 目录结构

```
openai/codex-plugin-cc/
├── .claude-plugin/
│   ├── marketplace.json
│   └── plugin.json
├── plugins/codex/
│   ├── .claude-plugin/
│   │   └── plugin.json
│   ├── agents/
│   │   └── codex-rescue.md        # 子代理定义
│   ├── commands/
│   │   ├── review.md               # /codex:review
│   │   ├── adversarial-review.md   # /codex:adversarial-review
│   │   ├── rescue.md               # /codex:rescue
│   │   ├── transfer.md             # /codex:transfer
│   │   ├── status.md               # /codex:status
│   │   ├── result.md               # /codex:result
│   │   ├── cancel.md               # /codex:cancel
│   │   └── setup.md                # /codex:setup
│   ├── hooks/
│   │   └── hooks.json              # Stop 钩子（审查门控）
│   ├── prompts/
│   │   ├── adversarial-review.md   # 对抗性审查提示
│   │   └── stop-review-gate.md     # 审查门控提示
│   ├── schemas/
│   │   └── review-output.schema.json
│   └── scripts/
│       ├── codex-companion.mjs     # 主脚本
│       ├── app-server-broker.mjs   # App Server 代理
│       └── lib/
│           ├── codex.mjs           # Codex CLI 封装
│           ├── git.mjs             # Git 操作
│           ├── job-control.mjs     # 作业控制
│           ├── broker-endpoint.mjs # Broker 通信
│           ├── broker-lifecycle.mjs
│           ├── app-server.mjs
│           ├── app-server-protocol.d.ts
│           └── ...
├── package.json
└── README.md
```

### 设计哲学

1. **"Claude 负责创意，Codex 负责严谨"** — 这是项目默认的设计假定。Claude Code 更擅长自由探索和创意方案，Codex 更擅长结构化审查和精确修复。插件让两者各取所长。
2. **审查门控是可选而非默认** — 项目在 FAQ 中明确警告"审查门控可能快速消耗 API 限制"，设计上保持谨慎，需要用户主动启用。
3. **会话即上下文** — 委派和转移操作的核心是将 Claude 的对话上下文序列化后传给 Codex，利用 `SessionTransfer` API 实现跨助手的上下文连续性。

### 技术架构

这是一个相对轻量的插件——代码主要是胶水层（glue code），复杂逻辑依赖 Codex CLI 和 App Server：

```
Claude Code 会话
    ↓ 插件拦截斜杠命令
[codex-companion.mjs]  ← 主协调器
    ↓ ↓ ↓ ↓
[codex.mjs]  → 调用本地 Codex CLI
[git.mjs]    → 获取代码差异
[job-control] → 管理后台任务队列
[broker]     → Codex App Server 通信
    ↓
Codex CLI / Codex App Server
```

## 💡 应用场景与启发

### 典型使用场景

| 场景 | 工作流 | 方法 |
|------|--------|------|
| **提交前代码审查** | Claude 写代码→自动触发 Codex 审查→有 Bug 则阻止 | 审查门控 + `/codex:review` |
| **架构决策的压力测试** | 设计评审时用 Codex 的逻辑推理能力挑战假设 | `/codex:adversarial-review` |
| **Bug 修复委派** | Claude 发现 Bug 但不想中断当前思路→委派给 Codex 后台处理 | `/codex:rescue --background` |
| **会话上下文转移** | 在 Claude Code 中开始的调试，转移到 Codex 专项处理 | `/codex:transfer` |
| **多模型并行探索** | 同一个问题用 Claude 和 Codex 各自跑两遍，对比方案 | `/codex:rescue`（独立后台线程） |

### 可借鉴的解决方案模式

1. **"审查门控"的 Stop 钩子模式**：这是最值得借鉴的设计——用另一个 AI 的输出来卡主 AI 的提交。门控不是阻断，而是"发现问题→反馈→修正→放行"的循环。这种元审查（meta-review）机制可以扩展到其他场景（安全门禁、合规检查、风格统一等）。

2. **后台任务队列的 Token 安全**：Codex 后台任务使用与 Claude Code 独立的 Token/API 资源，不会影响主会话。对于需要"两边同时跑"的 AI 协作场景，这是架构刚需。

3. **命令的 `--background` 参数**：对所有耗时操作提供 `--background` 和 `--wait` 两种模式。用户可以不等待后台任务，但也可以通过状态命令主动查询。这种"异步非阻塞"的设计应该在所有 AI 工具中推广。

### 同类需求的参考思路

如果你要实现"AI 帮 AI"的插件，codex-plugin-cc 的架构模板：

- **命令定义**：`commands/*.md` 每个命令一个文件，纯文本提示词
- **子代理**：`agents/codex-rescue.md` 定义代理角色和行为
- **钩子系统**：`hooks/hooks.json` 定义前置/后置钩子
- **执行脚本**：`scripts/*.mjs` 实际的 Node.js 执行逻辑

## 🧠 核心源码解读

### 后台任务管理的设计模式

这是项目工程上最复杂也最巧妙的部分——后台任务生命周期管理：

```javascript
// scripts/lib/job-control.mjs（简化）
const jobs = new Map();

export function startJob(type, identifier, runFn) {
  const id = crypto.randomUUID();
  const job = {
    id, type, identifier,
    status: 'running',
    startedAt: Date.now(),
    runFn,  // 实际执行函数
  };
  jobs.set(id, job);
  
  // 异步执行，不阻塞主线程
  runFn().then(result => {
    job.status = 'completed';
    job.result = result;
  }).catch(err => {
    job.status = 'failed';
    job.error = err.message;
  });
  
  return id;
}

export function getJob(id) {
  return jobs.get(id);
}

export function cancelJob(id) {
  const job = jobs.get(id);
  if (job && job.status === 'running') {
    job.status = 'cancelled';
    // 向 Codex 进程发送信号
  }
}
```

**设计启示**：这是一个典型的"作业提交→异步执行→轮询状态"模式。AI 编程助手中的耗时操作（审查、部署、测试）都应该采用这种模式，否则用户体验极差。

### Codex 调用的透明代理

```javascript
// scripts/lib/codex.mjs（简化）
import { execSync, exec } from 'child_process';

export function isCodexInstalled() {
  try {
    execSync('codex --version', { stdio: 'pipe' });
    return true;
  } catch {
    return false;
  }
}

export function runReview(codeDir, options = {}) {
  const args = ['review', codeDir];
  if (options.base) args.push('--base', options.base);
  
  if (options.background) {
    // 后台模式——用子进程，不阻塞
    const child = exec(`codex ${args.join(' ')}`);
    return { pid: child.pid };
  } else {
    // 前台模式——等待完成
    return execSync(`codex ${args.join(' ')}`, { encoding: 'utf-8' });
  }
}
```

**核心洞察**：插件本身不实现代码审查能力——它只是 Claude Code 和 Codex CLI 之间的透明代理。这种"胶水模式"的优点是维护成本极低（审查看似复杂的功能，其实只是一层 `exec`），缺陷是两个工具的版本兼容性需要持续跟进。

## 🌐 全网口碑画像

### 好评共识

- **"跨平台协作太香了"** — Claude Code 用户普遍认为能将"不想中断的工作"委派给 Codex 是刚需，尤其是长时间后台审查
- **"审查门控确实发现了很多漏掉的 bug"** — 多位用户在 Issue/Reddit 上分享了被审查门控"救了一命"的经历
- **"设置简单，一行 `/plugin install` 搞定"** — Claude Code 的插件生态 + Codex 的本地安装形成了顺畅的体验

### 差评共识 & 踩坑高发区

- **"审查门控太费 Token 了"** — 项目 FAQ 已警告此事，但用户的抱怨依然集中在启用审查门控后 Token 消耗暴增（可能一个提交需要 3-4 次审查循环）
- **"`/codex:rescue` 的模型选择玄学"** — 不同模型（gpt-5.4-mini vs spark）的审查质量差异很大，用户需要反复试验才能找到最适合自己项目的组合（Issue #42、#67）
- **"跨平台协作还不是真正的联邦"** — 批评观点认为 Codex Plugin 只是"单向桥接"（Claude → Codex），不是真正的双向会话

### 争议焦点

**"OpenAI 为何要做 Claude Code 的插件？"** 部分用户认为这是 OpenAI 的"渗透策略"——让 Claude Code 用户习惯 Codex 的能力，最终可能迁移到纯 Codex 工作流。但也有人认为这是良性的开放生态建设——毕竟 Codex 同样也支持 GitHub Copilot 集成。

### 维护者风格

OpenAI 官方团队的维护风格——Issue 有模板、Release 有 Changelog、CI/CD 流水线完善。响应速度不如 Caveman 那样的个人项目快（平均 48h），但回复质量高且规范。

## ⚔️ 竞品对比

| 维度 | **codex-plugin-cc** | **Anthropic Claude Code 原生** | **Codex CLI 独立使用** | **headroom** |
|------|-------------------|------------------------------|----------------------|-------------|
| Star | 22,561⭐ | — | — | 38,636⭐ |
| 定位 | Claude ↔ Codex 桥接 | 完整 IDE | CLI 编码代理 | 上下文压缩 |
| 审查能力 | ✅ Codex 审查（可引导） | ❌ 无原生审查 | ✅ 内置 `/review` | ❌ |
| 委派+后台 | ✅ `/codex:rescue` | ❌ | ✅ 原生 | ❌ |
| 会话转移 | ✅ `/codex:transfer` | ❌ | ✅ 原生 | ❌ |
| 代码编写 | 委派给 Codex | ✅ 原生 | ✅ 原生 | ❌ |
| Token 费用 | Claud + Codex 双计费 | 单计费 | 单计费 | 输入压缩节省 |

**选择建议**：
- 重度使用 Claude Code + 需要自动审查 → **codex-plugin-cc**
- 纯 Codex 用户 → 直接使用 Codex CLI（不需要插件）
- 只用 Claude Code + 想要代码审查 → 考虑其他审查方案（如 `caveman-review`）

## 🎯 核心研判

### 项目优势

1. **定位唯一**：当前市场上没有第二个"Claude ↔ Codex 桥接"产品。对于同时使用两个工具的开发者来说，这是不可替代的体验提升
2. **审查门控是独特卖点**：在 CI 流水线之外，增加了一道 AI 驱动的"预提交"安全检查。对于大型项目，这是代码质量的重大加分项
3. **OpenAI 官方维护**：不会突然停更，API 兼容性有保障

### 项目风险

1. **双倍 Token 消耗（最大风险）**：Claude Code + Codex 双重调用意味着费用翻倍。虽然审查价值客观存在，但成本问题会成为中小团队采用的阻力
2. **Claude Code 和 Codex 的竞争关系**：两个产品本质上存在竞争。如果未来 Anthropic 或 OpenAI 推出自己的"全栈"编码代理（涵盖审查/委派能力），插件价值会被稀释
3. **审查门控的误报率**：AI 审查可能存在误报，导致"审查→修正→审查"死循环。项目提供的 `--disable-review-gate` 本质上是承认门控还不够完美

### 适用场景 & 不适用场景

| ✅ 适用 | ❌ 不适用 |
|---------|----------|
| 大型项目的发布前安全检查 | 个人小项目（不值得双倍 Token 开销） |
| 团队协作中需要代码质量门禁 | Token 预算紧张的独立开发者 |
| Claude Code + Codex 双平台用户 | 只用单一编码代理的用户 |
| 需要后台异步处理的耗时任务 | 追求零配置一键上手的场景 |

### 趋势判断

**上升期（📈）**。22K Star + OpenAI 官方支持 + 每周稳定更新，项目处于上升通道。关键观察点是是否会出现"双向协作"（Codex → Claude 的委派路径），以及审查门控的空转率是否能降低。

## 📂 关键文件路径速查

| 文件 | 路径 | 用途 |
|------|------|------|
| 主脚本 | `plugins/codex/scripts/codex-companion.mjs` | 插件核心协调器 |
| Codex 封装 | `plugins/codex/scripts/lib/codex.mjs` | Codex CLI 的 Node.js 封装 |
| 任务控制 | `plugins/codex/scripts/lib/job-control.mjs` | 后台任务生命周期管理 |
| Broker 通信 | `plugins/codex/scripts/lib/broker-endpoint.mjs` | Codex App Server 通信协议 |
| 子代理定义 | `plugins/codex/agents/codex-rescue.md` | rescue 子代理的角色和指令 |
| 审查门控 | `plugins/codex/prompts/stop-review-gate.md` | Stop 钩子的审查提示词 |
| 对抗性审查 | `plugins/codex/commands/adversarial-review.md` | `/codex:adversarial-review` 命令模板 |
| 审查 Schema | `plugins/codex/schemas/review-output.schema.json` | 审查输出的 JSON Schema |
| 钩子配置 | `plugins/codex/hooks/hooks.json` | 插件钩子定义 |
