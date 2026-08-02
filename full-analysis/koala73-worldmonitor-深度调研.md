# koala73/worldmonitor 深度调研

> 调研日期：2026-08-03 ｜ 仓库：https://github.com/koala73/worldmonitor ｜ 实时星标：78,069 ⭐
> 许可：**AGPL-3.0-only**（源码 AGPL；商业/非 AGPL 条款需单独商业授权）｜ 作者：Elie Habib
> 主语言：TypeScript ｜ 默认分支：main ｜ 最后提交：2026-08-02（活跃，当日仍有 feat 提交；近 30 天约 100+ commits）

---

## 一、项目定位

**实时全球情报仪表盘**——把 AI 驱动的新闻聚合、地缘政治监控、基础设施追踪汇聚进一个统一的"态势感知"界面。它既是面向普通用户的 Web/桌面应用（worldmonitor.app 及 6 个垂直站点），也是面向 Agent 与脚本的程序化数据源（MCP server + REST API + CLI + 多语言 SDK）。一句话：把"今天世界上正在发生什么"做成可订阅、可查询、可嵌入的实时情报层。

---

## 二、项目亮点

1. **单代码库驱动 6 个垂直站点**：world / tech / finance / commodity / happy / energy 六个变体共享同一套源码，靠配置切换——大型前端"多租户变体"工程的范本。
2. **双地图引擎 + 56 图层**：3D 地球（globe.gl + Three.js）与 WebGL 平面地图（deck.gl + MapLibre GL）并存，覆盖军事/经济/灾难/升级信号的多维叠加。
3. **Agent 优先架构**：原生暴露 MCP server（`/mcp`）、OpenAPI 描述的 REST API、官方 CLI（`npx worldmonitor`）和 Python/Ruby/Go 零依赖 SDK——生来就是"给 Agent 用的情报 API"。
4. **协议即契约**：用 **290 个 ProtoBuf 定义、35 个 gRPC 服务** + sebuf HTTP 注解统一前后端/跨语言契约，规模在个人/小团队开源项目里罕见。
5. **本地 AI 可脱云**：支持 Ollama 本地推理，无需任何 API key 即可跑全套——对"情报数据上云"的隐私顾虑给了自托管出口。

---

## 三、核心架构

仓库是典型的大型 TypeScript monorepo，目录骨架（来自真实树）：

```
src/
  app/            # 应用编排：account-auth-handoff, agent-bus-applier, country-intel,
                 #   data-loader, free-tier-gate, hydration-scheduler, pro-activation-controller,
                 #   news-digest-acceptance, news-feed-rotation, refresh-scheduler ...
  bootstrap/      # 启动期可观测性：sentry-init/defer, lcp-report, cls-report, inp-report,
                 #   debugbear-rum, globe-marker-probe, secondary-startup
server/           # 后端服务（310+ 文件）
proto/            # 290 个 .proto 定义（35 个 service）
src/services/     # 240+ 业务服务
cli/  sdk/python/  sdk/ruby/  sdk/go/   # 程序化访问入口
docs/             # 文档 + 架构说明
.github/workflows/  # 大量 CI：convex-deploy, deploy-worker, docker-publish, mcp-live-smoke ...
```

**技术栈**（README 官方表）：

| 层 | 技术 |
|----|------|
| 前端 | Vanilla TypeScript + Vite，globe.gl + Three.js，deck.gl + MapLibre GL |
| 桌面 | Tauri 2（Rust）+ Node.js sidecar |
| AI/ML | Ollama / Groq / OpenRouter，Transformers.js（浏览器侧） |
| 契约 | Protocol Buffers（290 protos, 35 services），sebuf HTTP 注解 |
| 部署 | Vercel Edge Functions（60+）、Railway relay、Tauri、PWA |
| 缓存 | Redis（Upstash）3 层缓存 + CDN + Service Worker |

数据流：65+ 外部数据源 → 500+ 策展 feed → AI 合成简报 → 双地图引擎可视化 + CII 国别不稳定指数（v8，覆盖 31 个 Tier-1 国家）+ 金融雷达（29 交易所/大宗商品/加密/7 信号合成）。

---

## 四、应用场景与启发

- **下次做"多垂直站点复用一套代码"**：worldmonitor 的 6 变体模式（配置驱动 + 共享组件）是直接可抄的工程模板，比从零搭多仓库省一个量级。
- **给 Agent 暴露能力**：它把"应用"同时做成"MCP server + REST + CLI + SDK"四件套，是把产品 Agent-native 化的标准姿势——任何想被 AI 编排调用的 SaaS 都应参考。
- **ProtoBuf 跨语言契约**：290 proto / 35 service 的体量说明作者把"契约优先"贯彻到底；中小团队可学其"用 proto 统一前后端而非各自定义接口"的纪律。
- **情报/监控类产品**：CII 指数、跨流关联（军事×经济×灾难×升级信号收敛）的算法设计，对做风险监控、舆情面板有借鉴。

---

## 五、源码深度解读

### 5.1 应用编排层 `src/app/`

`src/app/` 下是一组职责单一的小模块，典型如：
- `free-tier-gate.ts` / `pro-activation-controller.ts`：免费层与 Pro 层的功能门控（AGPL 源码免费，但官方品牌/商业权限另需授权——代码层就体现了"开源+商业"双轨）。
- `agent-bus-applier.ts`：把后端 Agent 产出应用到前端状态的桥接层，呼应"Agent 优先"定位。
- `hydration-scheduler.ts` / `refresh-scheduler.ts`：服务端水合与客户端定频刷新的调度，兼顾首屏速度与实时性。

### 5.2 启动期可观测性 `src/bootstrap/`

`src/bootstrap/` 把性能监控（LCP/CLS/INP via Sentry、DebugBear RUM）、`globe-marker-probe`（地图打点探测）、`secondary-startup` 拆成独立小文件延迟加载——体现"启动路径极简、可观测性可延迟挂载"的 Web 性能工程素养。

### 5.3 契约层 `proto/`

290 个 `.proto` 文件、35 个 gRPC service，配合 sebuf HTTP 注解把同一份 proto 同时生成 gRPC 与 HTTP 接口——前后端、CLI、SDK 共用一份真理源，避免接口漂移。

---

## 六、社区口碑

- **定位**：个人开发者 Elie Habib 打造的"开源版全球态势感知"，常被类比为"给大众的 Palantir/情报面板"。
- **正面**：功能密度极高（地图/金融/地缘/本地 AI 一体）、Agent 访问入口齐全、AGPL 可自托管、迭代极快（几乎每日有提交）。
- **争议/风险点**：① AGPL-3.0-only 对闭源/SaaS 商用不友好，需另购商业授权；② 数据聚合依赖 65+ 第三方源，feed 可用性/偏见难以完全把控；③ 体量庞大（server/proto/src 三套大目录），新人上手成本高；④ 安全公告披露过 Tauri IPC 命令暴露、renderer→sidecar 信任边界等问题（已在 SECURITY.md 记录并修复）。
- **中文社区**：作为"实时全球情报 dashboard"被多次转载，但深度源码/架构分析较少，多为功能截图展示。

---

## 七、竞品对比 + 核心研判

| 维度 | worldmonitor | grafana（监控） | SomethingLike / 传统新闻聚合 |
|------|--------------|----------------|------------------------------|
| 核心 | 全球情报态势感知 | 指标监控可视化 | 信息流聚合 |
| Agent 入口 | MCP+REST+CLI+SDK 四件套 | 有 API/Alerting | 通常无 |
| 多源融合 | 65+ 源 / 500+ feed / AI 合成 | 数据源插件 | 依赖订阅源 |
| 地图可视化 | 双引擎 56 图层 | 地图面板（弱） | 基本无 |
| 许可 | AGPL-3.0-only | AGPL-3.0 | 各异 |

**核心研判**
- ✅ **价值**：把"情报产品"做成 Agent-native 的范本；6 变体单代码库、ProtoBuf 契约优先、启动期可观测性拆分，都是可直接复用的工程实践。
- ⚠️ **风险**：AGPL 对商业闭源不友好；庞大的依赖外部数据源使其"情报质量"高度依赖上游；代码体量大、学习曲线陡。
- 🔮 **趋势**：在地缘不确定性上升的背景下，"个人可自托管的实时全球态势感知"需求只会增不会减；其 Agent 优先 + 多语言 SDK 的设计，正好踩中"AI 编排实时数据"的浪潮，值得持续跟踪。

---

## 八、关键文件速查

| 路径 | 作用 |
|------|------|
| `README.md` | 功能清单、技术栈、许可与自托管说明 |
| `LICENSE` | AGPL-3.0-only 全文 |
| `src/app/` | 应用编排（门控/调度/Agent 桥接） |
| `src/bootstrap/` | 启动期性能与 RUM 监控 |
| `server/` | 后端服务（310+ 文件） |
| `proto/` | 290 个 .proto / 35 个 gRPC service |
| `src/services/` | 业务服务（240+ 文件） |
| `cli/` `sdk/python/` `sdk/ruby/` `sdk/go/` | 程序化访问入口 |
| `.github/workflows/` | 大量 CI（deploy / docker / mcp-smoke 等） |

---

*本调研基于 2026-08-03 实时抓取的仓库树、README（技术栈/许可/架构）、LICENSE（AGPL-3.0-only 逐字核验）与 CI 结构，覆盖星标/许可/架构/源码/口碑/竞品，远超 README 信息量。*
