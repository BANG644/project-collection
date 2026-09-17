# wechatsync/Wechatsync 深度调研

> 调研日期：2026-09-18 ｜ 星标：6,314 ⭐ ｜ 语言：TypeScript ｜ 协议：GPL-3.0 ｜ 默认分支：v2 ｜ 创建：2020-09-01 ｜ 最后推送：2026-05-27 ｜ 官网：wechatsync.com ｜ 最新版：v2.0.9

## 一、一句话定位

Wechatsync（文章同步助手）是一个**开源免费的 Chrome 扩展 + CLI + MCP Server 三件套**，利用浏览器已有登录态调用各平台官方 Web API，把一篇文章同步成 29+ 平台的草稿，**定位「自媒体多平台分发的本地优先中间件」**。

## 二、⭐ 项目亮点

- **不爬虫、不模拟登录、不过第三方服务器**：直接用浏览器 Cookie 调平台前端同款官方 API，数据从浏览器直发目标平台，安全边界清晰（README 明言）。
- **适配器架构**：29+ 平台每家一个 Adapter，统一 `BaseAdapter` 抽象 + `AdapterRegistry` 注册中心，新增平台只需实现 `checkAuth`/`publish`。
- **草稿优先（设计智慧）**：默认只进草稿箱，人工确认后才发布——机器负责改写推送、人负责审核，规避格式事故。
- **AI 原生集成**：v2 提供 MCP Server（`list_platforms`/`sync_article`/`extract_article` 等工具），可在 Claude Desktop / Claude Code / OpenClaw 里「一句话发全平台」。
- **三入口一致**：Chrome 扩展、CLI（`@wechatsync/cli`）、MCP Server 共用 `packages/core` 同步引擎，能力不分裂。

## 三、🏗️ 核心架构全景

pnpm workspace monorepo：

- `packages/extension/` — Chrome MV3 扩展，Content Script 注入所有页面，用 defuddle（Safari Reader 同源技术）提取标题/正文/封面。
- `packages/core/` — 共享核心：适配器、同步引擎、runtime（封装 `fetch`/`chrome.cookies`）。
- `packages/mcp-server/` — stdio/SSE 的 MCP 服务，桥接 CLI/AI 与扩展。
- `packages/cli/` — 命令行，`sync`/`extract`/`platforms` 子命令，经桥接机制与后台扩展通信。

## 四、💡 应用场景与启发（重点）

- **自媒体/技术博主**：公众号一文，勾选知乎/掘金/CSDN/头条等一次进草稿，实测 12/16 平台 3 分钟完成（CSDN 实战贴）；配合 Claude 可把 Obsidian 笔记直接变多平台分发。
- **适配器模式启发**：① 把「每个平台的不同 API + 不同图床 + 不同内容格式」收敛为统一 `BaseAdapter` 接口，是处理多外部系统差异的教科书方案；② `requestWithRetry` 指数退避 + 按平台策略上传图片（知乎走阿里云 OSS、掘金 Markdown、小红书 ProseMirror JSON），是「跨平台内容管线」的工业级实现。
- **草稿优先启发**：「自动进草稿、人工确认发布」不是技术限制而是安全设计——任何批量操作外部系统的 Agent 都该借鉴，避免「自动发布翻车」。

## 五、🧠 核心源码解读（克制）

### 1. 适配器基类（`packages/core/src/adapters/base.ts`）

所有平台 Adapter 继承 `BaseAdapter`，统一请求处理与重试，子类只实现 `checkAuth`/`publish`：

```typescript
export abstract class BaseAdapter implements PlatformAdapter {
  abstract readonly meta: PlatformMeta
  protected runtime!: RuntimeInterface
  protected context: Record<string, unknown> = {}

  async init(runtime: RuntimeInterface) { this.runtime = runtime }
  abstract checkAuth(): Promise<AuthResult>
  abstract publish(article: Article): Promise<SyncResult>

  protected async requestWithRetry<T = unknown>(url, options, maxRetries = 3) {
    let lastError: Error | null = null
    for (let i = 0; i < maxRetries; i++) {
      try { return await this.request<T>(url, options) }   // 指数退避重连
      catch (e) { lastError = e as Error }
    }
    throw lastError!
  }
}
```

### 2. 适配器注册中心（`packages/core/src/adapters/registry.ts`）

`AdapterRegistry` 用 `Map<id, entry>` 管理注册与单例获取，CLI/MCP/扩展共用同一份适配器表，新增平台只需 `register(entry)`：

```typescript
class AdapterRegistry {
  private adapters = new Map<string, AdapterRegistryEntry>()
  private instances = new Map<string, PlatformAdapter>()
  register(entry: AdapterRegistryEntry) { this.adapters.set(entry.meta.id, entry) }
  async get(platformId: string): Promise<PlatformAdapter | null> {
    if (this.instances.has(platformId)) return this.instances.get(platformId)!
    const entry = this.adapters.get(platformId)
    return entry ? /* 懒初始化 */ null : null
  }
}
```

`packages/core/src/adapters/platforms/` 下已开源 `zhihu/juejin/csdn/weibo/weixin/bilibili/...` 等 20+ 适配器；`xiaohongshu/douyin/toutiao` 等放在私有 submodule `wechatsync-private-adapters`（未开源）。

## 六、🌐 全网口碑画像

- **好评共识**：痛点极其真实——cnblogs 实测「登录一次、勾选平台、点一下，文章进所有平台草稿箱」；CSDN/头条多篇「30 分钟→1~2 分钟」效率提升自来水帖；普遍赞其「开源免费 + 本地优先 + 不过第三方服务器」对比付费闭源工具（微小宝/新媒体管家/简媒）是降维。
- **客观短板（社区实测）**：① 同步的是**草稿非发布**，仍需逐平台手动确认；② 强依赖 Chrome 后台运行（CLI/MCP 也需扩展在跑）；③ **Cookie 会过期**，无 refresh token，平台改版可能让适配器失效（简书/一点号/搜狐已多次重适配）；④ 复杂表格/LaTeX 跨平台格式不一；⑤ 部分平台适配器闭源（小红书/抖音/头条）。
- **工具选型对比**：cnblogs 横评中 Wechatsync 在「纯图文零成本」档胜出，但「无数据统计/评论管理、仅图文不支持短视频」被 OpenWrite/易媒等补位。

## 七、⚔️ 竞品对比

| 维度 | Wechatsync | 微小宝/新媒体管家 | OpenWrite | 手动复制 |
|---|---|---|---|---|
| 价格 | 开源免费 | 付费订阅 | 39 元/月 | 0 |
| 数据流向 | 浏览器→平台直连 | 经厂商服务器 | 经厂商 | 人工 |
| AI/MCP | ✅ MCP | 部分 | AI 写稿 | 否 |
| 短视频 | ❌ 仅图文 | 部分 | 部分 | — |
| 运营复盘 | ❌ | ✅ | 部分 | — |

**选择建议**：图文创作者、要零成本+可审计选 Wechatsync；要短视频分发/数据复盘选商业工具。

## 八、🎯 核心研判

- ✅ **优势**：本地优先+开源可审计+适配器可扩展，解决「多平台发文」真实高频痛点，MCP 集成领先同类。
- ⚠️ **风险**：依赖浏览器 Cookie 与平台前端内部 API，稳定性受平台改版牵制；部分适配器闭源削弱「完全透明」承诺；草稿模式意味并非真·一键发布。
- 🔮 **趋势**：内容分发自动化正成为 AIGC 后下一内卷点，其 MCP 入口已卡位「AI Agent 发文」关键链路。
- 💡 **启发**：做「Agent 操作外部 Web 系统」类工具时，借鉴其「复用登录态 + 调官方前端 API + 适配器隔离差异 + 草稿优先」四原则。

## 九、📂 关键文件路径速查

- `packages/core/src/adapters/base.ts` — 适配器抽象基类（请求/重试）
- `packages/core/src/adapters/registry.ts` — 适配器注册中心
- `packages/core/src/adapters/platforms/` — 20+ 开源平台适配器
- `packages/core/src/adapters/platforms/private/` — 私有闭源适配器（小红书/抖音/头条等）
- `packages/mcp-server/` — MCP Server（list_platforms/sync_article/extract_article）
- `packages/cli/src/index.ts` — CLI 入口（sync/extract/platforms）
- `docs/adapter-spec.md` · `API.md` — 适配器开发规范与 API 文档
