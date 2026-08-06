# 🔬 penpot/penpot — 全方位深度调研

> 调研日期：2026-08-07 ｜ 仓库：https://github.com/penpot/penpot
> 本次为**重写升级**（原报告文件名异常 `github.com-penpot-深度调研.md`，缺口碑与源码维度，星标滞后）

---

## 📌 一句话定位

**用 Clojure 写的开源设计平台，把「设计文件」当成代码来对待（SVG/CSS/HTML/JSON 原生），并且是唯一同时具备「官方 MCP Server + 自托管 + 成熟设计系统能力」的 Figma 替代品。**

---

## ⭐ 项目亮点（README 之外的判断）

1. **⚠️ 全网普遍误传的两个事实，本次实测校正**：
   - 许可证是 **MPL-2.0**，不是网上常见的「AGPLv3」（saascompared.com 等站点写错）
   - 星标是 **58,180**，不是「35K+」；旧报告的 57,240 也已过期
   - 默认分支是 **`develop`** 而非 `main`/`master`（clone 与 CI 脚本必踩）
2. **正在用 Rust + WASM 重写渲染引擎**：`render-wasm/` 是独立 Cargo 工程（1,125,042 字节 Rust 代码），Skia 后端。这是对社区最大痛点「大文件卡顿」的正面回应，也是本项目**当前最重要的技术赌注**。
3. **渲染架构有一份罕见的高质量内部文档**：`render-wasm/docs/rendering_architecture.md` 完整讲清 **Live/GPU 路径 vs Vector/PDF 路径的双管线设计**及其一致性守卫（parity guards）——这份文档本身就值得任何做图形编辑器的人读。
4. **MCP 是独立 pnpm monorepo，不是贴片**：`mcp/` 下有 `packages/common` + `packages/plugin`，还有 `docs/multi-user-mode.md`——多用户模式被单独设计过。
5. **贡献高度集中于核心人**：`niwinz` 9,538 次提交，是第二名（`Alotor` 2,645）的 3.6 倍。近 30 天提交 ≥100 次，活跃度很高，但**巴士系数偏低**。
6. **仓库内有 `.opencode/` 与 `.serena/` 目录 + `AGENTS.md`**：Penpot 团队自己在用 AI Agent 开发这个 Clojure 代码库。

---

## 🏗️ 项目全景

| 维度 | 数据（2026-08-07 实时核验） |
|------|------|
| 仓库 | penpot/penpot |
| Stars | **58,180** ⭐（网传 35K+ 已严重过期） |
| Forks | 3,901 |
| 主语言 | **Clojure**（13.1MB，占绝对主导） |
| 许可证 | **MPL-2.0**（非 AGPLv3） |
| 创建 | **2015-12-29**（近 11 年历史项目） |
| 最近推送 | 2026-08-06 |
| Open Issues | **761**（体量大，需辩证看） |
| 默认分支 | **`develop`** ⚠️ |
| 仓库文件数 | 6,064 blob |
| 最新版本 | **2.17.0**（2026-07-22） |
| 近 30 天提交 | ≥100 |
| 认证 | Digital Public Good（DPG）已验证 |

### 语言构成（揭示真实技术形态）

| 语言 | 体量 | 说明 |
|---|---|---|
| Clojure | 13.1 MB | 前后端共用（ClojureScript 跑前端） |
| JavaScript | 1.37 MB | 插件系统、构建 |
| **Rust** | **1.13 MB** | **`render-wasm/` 新渲染引擎** |
| TypeScript | 1.08 MB | `mcp/`、plugins |
| SCSS | 804 KB | 样式 |
| Python / Java / PLpgSQL / Lua… | 少量 | 工具链 |

### 顶层目录

```
backend/      common/      frontend/     exporter/     media-processor/
render-wasm/  ← Rust + WASM 新渲染引擎（战略重点）
mcp/          ← 官方 MCP Server（独立 pnpm monorepo）
plugins/      library/     docker/       experiments/  docs/
AGENTS.md     .opencode/   .serena/      ← 团队自用 AI Agent 配置
manage.sh     deps.edn     CHANGES.md
```

---

## 🧠 核心架构

### 后端模块划分（`backend/src/app/`）

```
main.clj  system.clj  config.clj
rpc/ rpc.clj          ← RPC 层（Penpot 不走 REST，走自定义 RPC）
db/ db.clj  migrations/ migrations.clj
auth/ auth.clj        storage/ storage.clj
msgbus.clj            ← 实时协作消息总线
redis.clj  metrics.clj  email/  media/  http/  features/  loggers/  setup/  srepl/
nitrate.clj  binfile/  ← 二进制文件格式处理
```

值得注意：`srepl.clj`（生产环境 REPL）是 Clojure 生态特有的运维能力——**可以在线上直接连进运行中的系统改状态、跑诊断**。这是 Clojure 后端相对 JVM/Node 服务的一个实质优势，也是一个安全面。

### 战略核心：`render-wasm/` 的双渲染管线

这是本次调研最有价值的发现。官方文档 `render-wasm/docs/rendering_architecture.md` 开门见山：

> **Penpot's WASM engine has two render paths that must produce the same picture.**

| 路径 | 用途 | 后端 | 代码 |
|------|------|------|------|
| **Live / GPU** | 屏幕工作区、缩略图、PNG 导出 | WebGL surfaces + Skia | `render.rs::render_shape`（+ `render/{fills,strokes,shadows,text,...}.rs`） |
| **Vector** | 真矢量 PDF（未来 SVG）导出 | **单个 CPU Skia canvas，不用 GPU** | `render/vector.rs` → `render/pdf.rs` |

**为什么必须分两条？**（文档原文逻辑）

Live 路径把每个形状画进**多个中间 GPU surface**（fills / strokes / shadows…）再合成。合成必然栅格化——这对屏幕和 PNG 没问题，但**这样产出的 PDF 会是一张位图**。Vector 路径绕过 GPU surface 系统，**直接画到 Skia PDF canvas**，于是路径、文字、填充都是真正的 PDF 矢量指令；只有本质像素化的效果（模糊、模糊阴影）才由 Skia 的 PDF 后端栅格化。

两条管线共享同一棵 shape tree 和同一套底层绘制原语（`draw_stroke_on_rect`、`handle_stroke_caps`、`render_inner_stroke`…），但组合方式不同。文档直言：**"Keeping them in sync is the whole game"**，并专门有一节 *Parity guards*（一致性守卫）。

**架构启发（可迁移）**：任何需要「屏幕渲染」和「矢量导出」双输出的系统，都会遇到这个两难。Penpot 的解法值得抄：**共享形状树 + 共享底层原语 + 分离合成策略 + 显式一致性守卫**，而不是试图用一条管线硬扛。

### MCP Server（`mcp/`）

```
mcp/bin/{client-setup.js, mcp-local.js}
mcp/packages/common/src/{index.ts, types.ts}
mcp/packages/plugin/src/{main.ts, plugin.ts, TaskHandler.ts, PenpotUtils.ts, ErrorUtils.ts}
                        + PenpotUtils.test.ts / ErrorUtils.test.ts
mcp/docs/multi-user-mode.md
mcp/.serena/memories/project_overview.md
```

设计上是 **MCP Server + Penpot 插件**双端配合：`packages/plugin` 是跑在 Penpot 画布里的插件（有 `manifest.json`），`TaskHandler.ts` 负责接收并执行来自 MCP 的任务。这个「MCP 端下发任务 → 画布内插件执行」的桥接模式，是**在无官方 API 的富客户端里接入 Agent 的通用解法**。

---

## 💡 应用场景与启发

### 什么时候该来翻这个仓库

| 你的处境 | 来这里找什么 |
|---|---|
| 「要自建设计工具/白板/图形编辑器」 | `render-wasm/docs/rendering_architecture.md` —— 双管线设计是绕不开的坑，这份文档能省你几个月 |
| 「要做真矢量 PDF 导出，但现有渲染是 GPU 合成的」 | `render/vector.rs` → `render/pdf.rs` 的分离思路 |
| 「要给一个富客户端 Web 应用接 AI Agent」 | `mcp/` 的「MCP Server + 画布内插件 + TaskHandler」桥接范式 |
| 「企业要求设计资产必须自托管、数据不出境」 | Penpot 是当前唯一成熟选项（Docker 自托管 + MPL-2.0 + EU 云） |
| 「设计与代码要有单一真源」 | 原生 Design Tokens（社区公认**强于 Figma**）+ SVG/CSS/HTML/JSON 开放格式 |
| 「想看 Clojure 全栈大型项目长什么样」 | 11 年历史、13MB Clojure、前后端同语言，教科书级样本 |
| 「想学怎么用 AI Agent 维护冷门语言代码库」 | `AGENTS.md` + `.opencode/` + `.serena/` |

### 三条可迁移的设计思想

1. **「双管线 + 一致性守卫」**：不要试图用一条渲染路径同时满足屏幕性能和矢量导出质量。分开，然后显式地守住二者一致。
2. **「开放格式即护城河」**：Penpot 唯一无法被 Figma 复制的优势不是功能，而是 SVG/CSS/HTML/JSON 原生存储带来的零锁定。第三方实测：**Penpot 的 SVG 导出比 Figma 小 31%**（4.2KB vs 6.1KB），因为 Figma 注入大量 clip-path 噪声。做工具类产品时，「输出物的干净程度」是被低估的差异化维度。
3. **「用插件做 Agent 的手」**：当主程序没有可编程 API 时，`MCP Server ←→ 应用内插件` 的双端配合比硬啃逆向更可持续。

---

## 🌐 全网口碑（正反并陈）

### 负面（且高度一致）——**性能是核心短板**

| 来源 | 具体反馈 |
|------|------|
| Penpot 官方社区 *Evaluation: Figma vs Penpot*（企业级评估帖，2026-04） | 「文件渲染非常慢。画布缩放时只显示占位图，即使页面上只有少量组件。多人同时编辑时更新不实时——有人编辑便签，改动要等他『离开』便签才可见。」结论：**「未来几年内我们不会切换，但会作为备份保留」**。同时明确肯定：**「Penpot 的 design tokens 处理比 Figma 好得多」**，并表示「特别期待新渲染引擎——如果性能问题解决，整体体验会显著改善」 |
| toolvs.co 实测（2026-04，48 屏移动 onboarding 流，$7 Hetzner CX11 自托管） | Figma 全程稳定 60fps；**Penpot 在约 80 帧以内维持 54–58fps，超过后跌到 28fps**（同一台 2021 MacBook Air）。另记录一个真实 bug：**v2.3 组件覆盖（override）在页面重载后静默重置**，浪费 40 分钟。边界情况：**布尔运算在锚点 > ~600 的路径上失败，返回空白且无错误提示**，需先在 Inkscape 里简化到 500 点以下 |
| saascompared 评测 | 插件生态远小于 Figma；变量、嵌套覆盖等高级组件能力晚到且不够打磨；自托管比云方案需要更多 DevOps 投入；Dev Mode/inspect 成熟度不及 Figma |

### 正面

| 来源 | 观点 |
|------|------|
| 同上企业评估帖 | Design tokens 处理**优于 Figma** |
| toolvs 实测 | **SVG 导出体积小 31%**，「图标工作和 CSS 导出，Penpot 确实更好」 |
| saascompared | 「对有 GDPR 数据驻留要求的欧盟团队，或不愿承担 Figma 按席位定价的公司，Penpot 是目前最可行的开源替代」；无数据售卖、无 AI 训练、EU 或自托管数据位置 |
| Penpot 官方对比文（利益相关，谨慎采信） | 定位为「唯一同时具备官方 MCP Server + 成熟设计平台 + 开放格式 + 自托管」的组合 |
| 第三方对比评分 | Figma 8.0/10 vs Penpot 7.3/10；12 项对比中 Figma 胜 7 项、Penpot 胜 5 项（价格、开源、自托管、SVG、无用户数限制） |

### 口碑综合判断

**共识非常清晰**：功能与性能不如 Figma，但在**自主可控、开放格式、Design Tokens、成本**四项上明确胜出。761 个 open issue 更多反映的是项目体量与用户基数，而非质量崩坏——近 30 天 100+ 提交说明维护强度依然很高。

**关键变量是 `render-wasm/`**：整个社区都在等这个 Rust/WASM 引擎解决性能问题。如果成了，Penpot 的评估结论会被大面积改写；如果拖着不成，「作为备份保留」将长期是企业的默认态度。

---

## ⚔️ 竞品对比

| 维度 | **Penpot** | Figma | Sketch | Excalidraw | Pencil.dev / Paper |
|---|---|---|---|---|---|
| 开源 | ✅ **MPL-2.0** | ✗ | ✗ | ✅ MIT | 部分 |
| 自托管 | ✅ Docker，无用户数限制 | ✗ | ✗ | ✅ | 部分 |
| 存储格式 | **SVG/CSS/HTML/JSON 原生** | 私有格式 | 私有 | JSON | — |
| 官方 MCP Server | ✅ | Dev Mode MCP | ✗ | ✗ | ✅ MCP-first |
| Design Tokens | ✅ **社区评价优于 Figma** | 有（变量） | 弱 | ✗ | — |
| 大文件性能 | ⚠️ **明显短板**（>80 帧掉到 28fps） | ✅ 稳 60fps | ✅ 原生 | ✅ 轻量 | — |
| 插件生态 | 成长中 | **1000+** | 中 | 少 | 早期 |
| 原型/交互 | 基础 | **强** | 中 | ✗ | 弱 |
| 定价 | 免费/自托管无限；云 $7/编辑者 | $15–75/编辑者 | 一次性/订阅 | 免费 | — |
| 合规/数据主权 | ✅ **EU + 自托管 + DPG 认证** | ✗ | ✗ | ✅ | — |
| 成熟度 | 11 年，2.17.0 | 行业标准 | 老牌 | 轻量成熟 | 新 |

**决策速查**：
- 要**数据主权 / GDPR / 自托管** → Penpot（几乎无替代）
- 要**设计系统 tokens 与代码单一真源** → Penpot 优于 Figma
- 要**复杂原型、50+ 交互、大文件流畅** → Figma，不用犹豫
- 要**Agent 驱动的设计工作流且不在意成熟度** → Pencil.dev / Paper（MCP-first）值得同时评估
- 只做**白板/草图** → Excalidraw 更轻

---

## 🎯 核心研判

### 优势
- **数据主权是不可替代的护城河**：自托管 + MPL-2.0 + EU 云 + DPG 认证，这套组合 Figma 给不了。
- **开放格式带来真实工程收益**：SVG 导出比 Figma 小 31%，CSS/HTML 直出，Dev handoff 无需翻译层。
- **Design Tokens 强于 Figma**（企业评估帖的原话，非官方宣传）。
- **官方 MCP Server 已落地**，且是独立 monorepo 工程而非 demo。
- **维护强度高**：11 年项目、近 30 天 100+ 提交、月度 minor 版本节奏（2.15→2.16→2.17）。
- **架构文档质量罕见**：`rendering_architecture.md` 是可以拿去教学的级别。

### 风险
1. **性能是硬伤，且已被多方独立复现**：>80 帧掉到 28fps、缩放只显示占位图、协作更新不实时。这不是个别人的机器问题。
2. **`render-wasm` 是没有兑现日期的赌注**：Rust 重写渲染引擎工程量巨大，社区在等，但 CHANGES 里没有明确 GA 时间表。
3. **巴士系数低**：`niwinz` 一人 9,538 提交，是第二名的 3.6 倍。核心人离开会显著影响项目。
4. **已知功能缺陷有真实杀伤**：组件覆盖重载后静默重置（v2.3）、布尔运算在 >600 锚点路径上无声失败——这类「无错误提示的静默失败」对设计师最致命。
5. **761 个 open issue**：需要辩证看，但确实意味着大量已知问题排队。
6. **Clojure 门槛**：想自己改代码、贡献 PR 的团队，需要有人会 Clojure/ClojureScript——这是个很小的人才池。
7. **⚠️ 默认分支 `develop`**：所有 CI/自动化脚本注意。

### 适用 / 不适用
- ✅ **适用**：有数据主权/GDPR 硬要求的欧盟或受监管企业；重视 Design Tokens 与设计-代码单一真源的团队；预算敏感且团队人数多（无席位费）；图标/CSS 导出为主的工作流；想接 Agent 做设计自动化的团队。
- ❌ **不适用**：需要 50+ 交互复杂原型的产品团队；日常处理超大设计文件（性能会直接劝退）；重度依赖特定 Figma 插件；需要平滑客户交付流程的代理商；没人会 Clojure 且需要深度定制的团队。

### 一句话结论
**Penpot 不是「更便宜的 Figma」，而是「唯一能让你完全拥有设计基础设施的选项」——买它是在买自主权和开放格式，不是买流畅度。在 `render-wasm` 兑现之前，最理性的姿势是「设计系统与 tokens 落在 Penpot，复杂原型仍留 Figma」的双轨制，而不是一次性迁移。**

---

## 📂 关键文件路径速查

| 想看什么 | 路径 |
|---------|------|
| **渲染双管线架构文档（最值得读）** | `render-wasm/docs/rendering_architecture.md` |
| Rust/WASM 渲染引擎 | `render-wasm/`（`Cargo.toml`、`build.rs`、`render/{vector,pdf,fills,strokes,shadows,text}.rs`） |
| 官方 MCP Server | `mcp/bin/{client-setup.js, mcp-local.js}`、`mcp/packages/common/src/` |
| MCP 画布内插件 | `mcp/packages/plugin/src/{main.ts, plugin.ts, TaskHandler.ts, PenpotUtils.ts}` |
| MCP 多用户模式设计 | `mcp/docs/multi-user-mode.md` |
| 后端入口/系统装配 | `backend/src/app/{main.clj, system.clj, config.clj}` |
| RPC 层（非 REST） | `backend/src/app/rpc.clj` + `backend/src/app/rpc/` |
| 实时协作消息总线 | `backend/src/app/msgbus.clj` |
| 生产 REPL（Clojure 特有运维能力） | `backend/src/app/srepl.clj` |
| 二进制文件格式 | `backend/src/app/binfile/` |
| 数据库迁移 | `backend/src/app/migrations/` + `migrations.clj` |
| 前后端共用代码 | `common/` |
| 前端 | `frontend/` |
| 导出服务 | `exporter/` |
| 媒体处理 | `media-processor/` |
| 插件系统 | `plugins/` |
| 自托管部署 | `docker/`、`.env.example`、`manage.sh` |
| 变更日志 | `CHANGES.md` |
| 团队 AI Agent 约定 | `AGENTS.md`、`.opencode/`、`.serena/` |
| 依赖声明 | `deps.edn`、`pnpm-workspace.yaml` |
| **许可证（MPL-2.0，非 AGPL）** | `LICENSE` |

---

## 🔗 参考

- 仓库：https://github.com/penpot/penpot （**默认分支 `develop`**）
- 官网：https://penpot.app/
- MCP Server：https://penpot.app/penpot-mcp-server ｜ 快速开始 https://help.penpot.app/mcp/#quick-start
- Design Tokens：https://penpot.dev/collaboration/design-tokens
- 自托管指南：https://help.penpot.app/technical-guide/getting-started/
- 企业级评估帖（含性能吐槽原文）：https://community.penpot.app/t/evaluation-figma-vs-penpot/10508
- 第三方实测（fps/SVG 体积/已知 bug）：https://toolvs.co/compare/figma-vs-penpot
- 第三方评测：https://saascompared.com/product/penpot
