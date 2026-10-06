# Cloudflare OS — 运行在 Cloudflare Workers 上的「AI 生产力操作系统」

> 调研日期：2026-10-06 ｜ Stars：11,040 ｜ 语言：TypeScript ｜ License：Apache-2.0 ｜ 维护者：Cloudflare
> 仓库：https://github.com/cloudflare/cloudflare-os ｜ 官网：https://os.cloudflare.app

---

## 一、项目亮点（差异化）

1. **不是聊天框，是"Gadgets"范式**：你创建的每张幻灯片/白板/小应用，不是调用某个 SaaS，而是为你**单独起一个私有实例（gadget）**，跑在独立沙箱里——消除"中心化 SaaS 安全漏洞泄漏你的数据"的可能。
2. **Gatekeepers = 超级 MCP + 能力型安全**：每个外部资源接入时生成一个 Gatekeeper（独立 Worker），负责 OAuth、收窄到用户指定的具体资源、记录每次操作、对"有副作用的动作"提供 human-in-loop 审批。
3. **异步 human-in-loop（关键创新）**：传统 HITL 是**同步**的——agent 做到一半卡在审批等你，你走开喝咖啡回来发现它一步没动，于是大家被迫开 `--dangerously-skip-permissions`。Gatekeeper 改为**本地模拟**动作结果让 agent 先继续、把动作排队，你之后**批量**审批/驳回。
4. **真·OS 类比（技术层）**：kernel=`workshop-backend`，drivers=`gatekeeper-*`，shell=`workshop-frontend`，processes=gadgets，executables=blueprints，agents=新增的"一等公民"。
5. **Cloudflare 内部真在用**：README 称 Cloudflare 大量员工（工程到销售）每天用 OS 干活；开源目的是让你 fork 成"*Your Company* OS"，而非直接用它的托管版。

> 状态：v2 完全重写、活跃开发中（2026-08 起可用但仍有 rough edges），定位 early access。

---

## 二、核心架构

```
                用户 / Agent 请求
                       │
   ┌───────────────────┴───────────────────┐
   │  packages/workshop-frontend  (shell)    │  ← 聊天 UI + Gadget 渲染
   └───────────────────┬───────────────────┘
                       │  (Streamable HTTP MCP)
   ┌───────────────────┴───────────────────┐
   │  packages/workshop-backend  (kernel)    │  ← 连接用户↔程序↔设备，沙箱+访问控制
   └──────────┬────────────────────┬─────────┘
              │                    │
   ┌──────────┴──────┐    ┌────────┴──────────┐
   │ Gadgets         │    │ Gatekeepers        │  ← 每个外部服务一个 Worker
   │ (用户私有实例)   │    │ (能力型安全/driver) │
   └─────────────────┘    └───────────────────┘
   蓝图(Blueprint)=模板   外部资源: GitHub / Google / Gmail / ...
```

- **Gadgets**：每个文件/应用是潜在自定义 app，私有默认可安全共享；从 Blueprint（模板，指定"整个应用"而非一段内容）创建。
- **Gatekeepers**：类比 OS 的 device driver，连接用户/agent 到外部服务；封装原生 API 为干净接口，做授权、收窄访问、审计日志、副作用审批。
- **本地一键跑**：`pnpm run-local` 在 wrangler + workerd 上起整套（非生产用）；也可 `deploy` 到自己的 Cloudflare 账户。

---

## 三、源码深度解读（关键模块）

### 1. MCP 客户端（Streamable HTTP + 存储预算钳制）— `packages/mcp-shared/src/client.ts`

```ts
/** MCP revision this client speaks. Sent in `initialize` and the `MCP-Protocol-Version` header. */
export const MCP_PROTOCOL_VERSION = "2025-06-18";

export type ToolCatalog = {
  tools: McpTool[];
  truncated: boolean;   // 目录被截断也要随 tools 带走，否则会被误判为"无此工具"
};
```

要点：
- 客户端**显式实现** `initialize` / `tools/list` / `tools/call`，而非用 SDK 的 `StreamableHTTPClientTransport`——原因写在注释里：它跑在 Durable Object 里、调用间会休眠并把 session id 交还账户，官方 transport 的"长连接重连 + SSE 续传"状态机不适用；且官方 transport 没有 `clampTool` 在解析时钳制工具体积（为守住存储预算）。
- `guardedFetch` +  capped body readers + 401/403/404 分类 = 这个连接器的 **SSRF 与响应体积边界**。
- `truncated` 必须跟着 tools 走，否则 `looksLikePortal` 这类"看工具目录判端点性质"的代码会把截断目录当成完整目录，漏判真实存在的工具。

### 2. 边界请求体解析（防滥用）— `packages/workshop-backend/src/client-errors.ts`

```ts
const MAX_BODY_BYTES = 128 * 1024;

async function readBoundedJson(request: Request): Promise<unknown | "too-large" | "invalid"> {
  const declaredLength = Number(request.headers.get("content-length"));
  if (Number.isFinite(declaredLength) && declaredLength > MAX_BODY_BYTES) return "too-large";
  // ...按块读取，超 128KB 即 cancel 并返回 "too-large"
}
```

要点：所有前端错误上报请求都先按声明长度 + 实际读取双判，超 128KB 直接拒——这是 Worker 环境下"不可信输入"的标准防御。

### 3. 本地编排脚本 — `scripts/run-local.ts` / `scripts/run-dev-server.ts`

```ts
// run-local.ts：装依赖 → 只构建运行所需（typed-storage + frontend 资源）→ 起本地 server
runPnpm(["install"]);
runPnpm(["exec", "vp", "run", "--cache", "@gadgets/typed-storage#build"]);
runPnpm(["exec", "vp", "run", "--cache", "@gadgets/workshop-frontend#build:assets"]);

// run-dev-server.ts：为每个发现的 worker 生成 wrangler.dev.jsonc，再 wrangler dev 全部拉起
interface Gatekeeper { name: string; dir: string; }  // 包目录名即 worker 名
```

要点：`findGatekeepers` 把 `packages/gatekeeper-*` 目录自动发现为 Worker；`vp run`（Cloudflare 内部构建编排）+ 机器感知并发，是大型 Worker 单体仓的成熟工程实践。

---

## 四、应用场景与启发

- **场景**：企业内部"安全地让全员用 AI 干活"——销售做客户幻灯片、工程起 issue 看板、任何人自制小工具并安全分享；安全团队能睡安稳觉。
- **启发（可借鉴点）**：
  - **异步 HITL 是 Agent 安全落地的关键突破**：同步审批逼人开 `--dangerously-skip-permissions`，而"模拟结果 + 批量审批"既安全又不打断 agent——任何要给人审批的 Agent 系统都应抄这个思路。
  - **能力型安全（capability-based）优于 ACL**：Agent 不该被当普通用户，而应持有受限 capability；Gatekeeper 即"每资源一个最小权限 driver"。
  - **"每用户一个私有实例"的 Gadget 范式**挑战了 25 年 SaaS 中央集权，前提是"任何人能 prompt agent 加功能"——AI 真的改变了软件分发等式。

---

## 五、社区口碑

- 11,040★、1,310 forks，Cloudflare 官方出品 + 内部真实使用，话题度高；被视为"Agent 协作/企业 AI 操作系统"方向的重要开源参考。
- ⚠️ 局限：early access、v2 重写中、rough edges 多；深度绑定 Cloudflare Workers/wrangler/workerd 生态，离开 CF 难自托管；Gatekeeper 独立部署模型未定型。
- 结论：架构理念（尤其异步 HITL、能力型安全）口碑极佳，但"拿来即用"的生产成熟度尚早。

---

## 六、竞品对比

| 维度 | Cloudflare OS | ChatGPT/Claude 企业版 | Dify / Coze | 自研 Agent 平台 |
|------|---------------|----------------------|-------------|----------------|
| 每用户私有 app 实例 | ✅ Gadgets | 否（中心化） | 部分 | 视实现 |
| 能力型安全 / 异步 HITL | ✅ Gatekeepers | 部分 | 弱 | 少 |
| 自托管 | ✅（CF 账户） | 否 | ✅ | ✅ |
| 外部系统集成模型 | 每服务一个 Gatekeeper | connector | plugin | 自写 |
| 定位 | 企业内部 AI OS | 通用助手 | 低代码 Agent | 定制 |

**差异化**：把"操作系统隐喻 + 能力型安全 + 异步审批"落到 Worker 实现，是理念最完整的企业 AI 生产力底座之一。

---

## 七、核心研判

- **价值**：不是又一个 chatbox，而是"Agent 时代软件该如何组织"的一份高质量参考实现；其 Gatekeeper 异步 HITL 与能力型安全模型，值得任何做企业 Agent 平台的团队直接借鉴。
- **风险**：① 强绑 Cloudflare 生态，非 CF 用户迁移成本高；② v2 早期、API/部署形态未稳；③ Gadget 范式要求"用户能自由改代码"，对企业治理是双刃剑。
- **建议**：作为**架构学习样本**价值最高（重点读 `packages/mcp-shared` 与 Gatekeeper 设计）；若要落地，先取其"异步 HITL + 能力型安全"两原则，不必整体搬 CF 栈。

---

## 八、关键文件路径速查

| 文件 | 作用 |
|------|------|
| `README.md` | OS 概念、Gadgets/Gatekeepers、OS 类比表 |
| `packages/workshop-backend` | kernel：用户↔程序↔设备连接 + 沙箱 + 访问控制 |
| `packages/workshop-frontend` | shell：聊天 UI + Gadget 渲染 |
| `packages/gatekeeper-*` | drivers：每个外部服务的 Gatekeeper Worker |
| `packages/mcp-shared/src/client.ts` | 最小 MCP 客户端（Streamable HTTP，存储预算钳制） |
| `packages/workshop-backend/src/client-errors.ts` | 边界请求体防御（128KB 上限） |
| `scripts/run-local.ts` | 本地一键起整套 |
| `scripts/run-dev-server.ts` | 自动发现 Gatekeeper 并 wrangler dev |
| `docs/blueprints.md` `docs/sharing.md` `docs/observers.md` | 蓝图 / 分享 / 观察者文档 |
