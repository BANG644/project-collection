# e2e — 面向 Web / 移动端的 Agent 端到端测试框架

> 调研日期：2026-10-06 ｜ Stars：4,918 ｜ 语言：TypeScript ｜ License：Apache-2.0 ｜ 维护者：TesterArmy
> 仓库：https://github.com/tester-army/e2e ｜ 官网：https://tester.army/e2e

---

## 一、项目亮点（差异化）

1. **自然语言目标驱动**：用 `agent.act("upgrade to Pro plan")` 描述"要达成什么"，由 Agent 自己规划步骤去操作 app，而不是写一堆 `page.click(selector)` 脆弱脚本。
2. **agent 步骤可录制回放、且回放零模型调用**：一次 agent 步骤被后续断言验证后会被记录；下次运行直接**重放录下的动作**，直到 app 行为变化才重新调用模型。纯断言测试（无 agent 步骤）**完全不需要模型**。
3. **Web + 移动端统一**：Web 走 Playwright（Chromium/Firefox/WebKit），移动端走 Expo EAS 模拟器 / 真机（iOS/Android），同一套 `app` / `agent` / `screen` API。
4. **自带决策模型执行器（decision）**：`agent.act` / `agent.assert` 背后是 bounded semantic actions + assertions 的"决策模型"，把"语义动作"和"断言"作为一等公民，而非裸 prompt。
5. **Bring-your-own-model**：自带订阅 / API key / 本地模型都行；CLI 仅发匿名遥测（可 `npx e2e telemetry disable` 关闭），不含测试内容或凭证。

> 状态：活跃开发中、逼近 1.0，API/配置在 minor 间仍可能变（README 明示）。

---

## 二、核心架构

```
tests/checkout.e2e.ts
   │  import { test, expect } from 'e2e'
   ▼
┌─────────────────────────────────────────────┐
│ e2e (SDK + runner + CLI)                      │
│   test('...', async ({ app, agent, screen })│
│     await agent.act('...')                    │  ← 模型驱动，录制动作
│     await agent.assert('...')                 │  ← 验证，写入 ledger
│     await expect(screen.getByRole('status'))  │  ← 普通断言，无需模型
└─────────────────────────────────────────────┘
       │                  │                   │
   @e2e-dev/web     @e2e-dev/mobile      @e2e-dev/decision
   (Playwright)     (Expo EAS 模拟器)     (语义动作/断言执行器)
       │                  │
   @e2e-dev/kernel   @e2e-dev/eas
   (Kernel 托管浏览器) (EAS 托管 iOS/Android 模拟器)
       │
   @e2e-dev/github  (PR 评论报告器)
```

- **引擎分包**：web / mobile / kernel / eas / github / decision 各自独立 npm 包，便于按需安装与替换。
- **Kernel 托管浏览器**：`@e2e-dev/kernel` 通过 `@onkernel/sdk` 在远端托管浏览器，支持录屏回放（`startReplay`/`downloadReplay` 落 MP4）。
- **EAS 模拟器**：`@e2e-dev/eas` 走 Expo 的 GraphQL API（`eas simulator:*`），**不装额外 SDK**，拿到 `daemonUrl`/`daemonToken` 即可驱动真机/模拟器。

---

## 三、源码深度解读（关键模块）

### 1. 自报身份与模型请求头 — `packages/e2e/src/internal/client-identity.ts`

```ts
export const USER_AGENT = `e2e/${packageVersion(import.meta.url, '../../package.json', '0.0.0')} (${process.platform}; ${process.arch})`;

// 每个模型调用都带；Vercel AI Gateway / OpenRouter 读 http-referer 与 x-title 做归属
export const MODEL_REQUEST_HEADERS: Readonly<Record<string, string>> = {
  'user-agent': USER_AGENT,
  'http-referer': 'https://tester.army/e2e',
  'x-title': 'e2e',
};
```

要点：明确"我是 e2e，不是别的客户端"，避免把请求伪装成其他客户端——这是多供应商调用下的归属与计费正确性细节。

### 2. 移动端 EAS 会话生命周期 — `packages/eas/src/client.ts`

```ts
export type EasSessionState =
  | { readonly phase: 'queued' | 'starting' }
  | { readonly phase: 'ready'; readonly daemonUrl: string; readonly daemonToken: string; readonly openPreviewUrl: string | undefined }
  | { readonly phase: 'ended'; readonly status: string };

export interface EasSessions {
  create(params: EasSessionParams, signal: AbortSignal): Promise<EasCreatedSession>;
  state(id: string, signal: AbortSignal): Promise<EasSessionState>;
  stop(id: string, signal: AbortSignal): Promise<void>;
}
```

要点：会话状态机 `queued → starting → ready`，`ready` 才暴露 daemon 地址与 token；带 token 的预览 URL 被刻意排除（`left out so its token stays out of logs`）——安全细节到位。

### 3. Kernel 托管浏览器客户端 — `packages/kernel/src/client.ts`

```ts
export interface KernelBrowsers {
  create(params: KernelBrowserParams, signal: AbortSignal): Promise<KernelBrowser>;
  delete(sessionId: string, signal: AbortSignal): Promise<boolean>;
  listActive(tags: Readonly<Record<string, string>>, signal: AbortSignal): Promise<string[]>;
  startReplay(sessionId: string, params: KernelReplayParams, signal: AbortSignal): Promise<string>;
  stopReplay(sessionId: string, replayId: string, signal: AbortSignal): Promise<void>;
  downloadReplay(sessionId: string, replayId: string, file: string, signal: AbortSignal): Promise<void>;
}
```

要点：把"浏览器"抽象成带 tag 的可检索会话，录屏回放直接落盘 MP4——天然适配"测试失败留证"的需求（`failure-evidence-budget` changeset 也印证了这点）。

### 4. 构建矩阵 — `package.json`

```jsonc
"build": "pnpm --filter e2e run build && pnpm --filter @e2e-dev/web run build && ... @e2e-dev/decision run build",
"test": "pnpm run build && pnpm --filter e2e run test && pnpm --filter @e2e-dev/web run test && ...",
```

要点：pnpm workspace 单体仓（1442 文件），每个引擎独立 `build`/`test`，CI 可并行；`changeset` 管版本，工程化成熟度高于多数同类早期项目。

---

## 四、应用场景与启发

- **场景**：Web / React Native / SwiftUI 应用的端到端测试，尤其适合"流程长、选择器易碎、想用自然语言描述验收"的团队；可在每次 PR 跑（@e2e-dev/github 直接发 PR 评论）。
- **启发（可借鉴点）**：
  - "录制 agent 动作 → 回放零模型"是降本关键：首跑付模型费，之后回归几乎免费，且 app 一变就自动重新规划——比纯 prompt 测试稳。
  - 把"语义动作"和"断言"做成显式决策模型（而非隐式 prompt），便于约束、审计与重放。
  - 把浏览器/模拟器外包给 Kernel / EAS 托管，本地只跑协调逻辑——是"重资源外移"的干净架构。

---

## 五、社区口碑

- 4,918★、204 forks，作为 2026-07 新建仓增长极快，已上 GitHub Trending；TesterArmy 有商业平台背书，文档完备（docs 站点 + `examples/` 含 Vite/Next/Expo/SwiftUI 可跑样例）。
- ⚠️ 局限：仍 early access，API 可能变；遥测默认开（虽可关、不含敏感内容）；模型调用成本由用户 own。
- 结论：口碑正面、势能强，但生产采用前建议锁定版本并评估 1.0 稳定性。

---

## 六、竞品对比

| 维度 | e2e (tester-army) | Playwright | Cypress | QA.tech / Octomind |
|------|-------------------|-----------|---------|--------------------|
| 编写方式 | 自然语言目标 + agent | 选择器脚本 | 选择器脚本 | AI 生成 |
| 模型依赖 | 仅 agent 步骤需模型，回放免费 | 无 | 无 | 有 |
| Web+移动 | ✅ 统一 API | Web | Web | Web 为主 |
| 录制回放 | ✅ 动作 ledger | 有（trace） | 有 | 有 |
| 自托管 | ✅（BYO model） | ✅ | ✅ | 多 SaaS |

**差异化**：以"语义动作 + 免费回放"把 Agent 测试的成本压下来，同时保持 Web/移动统一与自托管。

---

## 七、核心研判

- **价值**：把"Agent 驱动 E2E"从 demo 推向可工程化（动作录制/回放、决策模型、托管浏览器、PR 报告器齐全），是当前最像"正经测试框架"的 Agent 测试方案之一。
- **风险**：① 逼近 1.0、API 仍可能变；② agent 步骤首次运行依赖模型质量与稳定性；③ 多包单体仓，踩坑时需读多个 `@e2e-dev/*` 源码。
- **建议**：Web 端先小范围试点（回放免费、ROI 高）；移动端需 EAS/Kernel 账户；生产前 pin 版本并关遥测或显式合规评估。

---

## 八、关键文件路径速查

| 文件 | 作用 |
|------|------|
| `packages/e2e/src/internal/client-identity.ts` | 自报 USER_AGENT 与模型请求归属头 |
| `packages/eas/src/client.ts` | EAS 模拟器会话（Expo GraphQL，无 SDK） |
| `packages/kernel/src/client.ts` | Kernel 托管浏览器 + 录屏回放 |
| `packages/web` | Playwright 三内核 Web 引擎 |
| `packages/mobile` | iOS/Android 引擎（agent-device） |
| `packages/decision` | 语义动作 / 断言决策模型执行器 |
| `packages/github` | PR 评论报告器 |
| `docs/*.mdx` | 全量文档（agent-steps / decision-models / mobile 等） |
| `examples/` | Vite/Next/Expo/SwiftUI 可跑样例 |
