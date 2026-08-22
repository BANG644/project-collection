# 🔬 microsoft/TypeScript - 全方位深度调研

> 调研日期：2026-08-23 | Stars：⭐ 110,501 | 语言：**Go（原生编译器 `tsc/`）+ TypeScript（JS 工具链 `packages/`）** | 协议：Apache-2.0 | 默认分支：main

## 📌 一句话定位
JavaScript 的超集类型语言 TypeScript——2026 年 7 月 8 日 GA 的 **7.0 把编译器从 TypeScript/JavaScript 整个用 Go 重写（内部代号 Project Corsa / `tsgo`）**，在「完全相同的类型系统」下获得 8–12× 的构建提速，是十年来最重大的 TypeScript 发布。

## ⭐ 项目亮点
- **10× 性能飞跃**：VS Code（150 万行）类型检查从 125.7s（TS 6）→ 10.6s（TS 7），**11.9×**；官方在 VS Code / Sentry / Bluesky / Playwright / tldraw 上测得 7.7×–11.9×。
- **语义零变化**：类型检查规则、诊断、JS 输出与 TS 6.0 **逐字一致**——不是新类型系统，是「同规则换更快引擎」，升级几乎无行为风险。
- **Go 而非 Rust 的刻意选择**：类型检查天然可并行，Go 的 goroutines 共享单地址空间读符号表零拷贝；Rust 所有权模型在这类负载要 `Arc<>` 包裹、复杂度陡增。
- **内存同步下降**：VS Code 构建内存约 18% 减少（原生二进制无 JS 堆）。
- **双轨过渡**：6.x 走经典 JS 编译器（兼容），7.x 走 Go 原生，给生态迁移窗口。

## 🏗️ 项目架构全景
### 目录结构与设计哲学
仓库现在是 **「Go 原生编译器 + JS/TS 工具链」双轨**：

```
microsoft/TypeScript/
├── tsc/                    # ⭐ Go 原生编译器（Project Corsa / tsgo）
│   ├── cmd/tsc/            # main.go, lsp.go, api.go, sys.go —— 入口/编辑器/API/系统
│   ├── internal/ast/       # AST 定义（ast.go）
│   ├── internal/api/       # API 层：encoder(msgpack) / decoder / proto / session / server
│   │   └── encoder/        # encoder.go + 生成的 encoder_generated.go（msgpack 编解码）
│   └── CHANGES.md          # Strada(旧) ↔ Corsa(新) 的刻意差异清单
├── packages/               # JS/TS 工具链（类型、语言服务、转译等）
├── tools/                  # 构建/发布工具
└── README.md
```

设计哲学：**「方法学移植（port）而非重写（rewrite）」**。Hejlsberg 明确把它框定为「把现有编译器逻辑用 Go 重实现」，刻意不趁机改类型系统——所以 breaking change 几乎都只是默认值收紧和砍遗留 target，不是新类型行为。

### 技术栈与依赖
- 原生编译器：`tsc/` 是纯 Go（Go modules，`tsc/go.mod`），`internal/api` 用 **msgpack 编码 + proto** 做进程间/编辑器通信。
- JS 工具链：`packages/` 仍是 TypeScript/JS，供 emit、语言服务与下游工具使用。
- 分发：`@typescript/native-preview`（预览期 `tsgo`）→ 7.0 GA 后命令名统一回 `tsc`。

## 💡 应用场景与启发（重点章节）
### 典型使用场景
- **大型 TS 代码库提速**：CI 类型检查从分钟级掉到秒级，省下的 wall-clock 与 runner 费用可观（例子：每天 200 次 90s 检查 × $0.006/分钟）。
- **编辑器流畅度**：VS Code Native Preview 扩展让大型项目 IntelliSense / 跳转变「即时」。
- **CI 非阻塞并行**：把 `tsgo` 当作快速类型检查旁路跑在 `tsc` 旁，先吃速度、emit 仍信 6.x。

### 可借鉴的解决方案模式
1. **「同语义换引擎」的迁移策略**：TypeScript 不借重写顺手改类型系统，把 scope 锁死在性能——这是大型语言工具「零行为风险升级」的教科书。任何「重写下层但不想动上层语义」的项目都应学。
2. **Go 的「GC + goroutine」对齐函数式编译器**：TS 编译器大量闭包/递归/判别联合，Go 的 GC 内存模型比 Rust 所有权更贴合，移植成本低、并行收益大。**选型理由是 workload 驱动的，不是语言信仰**。
3. **双轨发布**：6.x 保兼容、7.x 上原生，给 `Compiler API` 依赖方留迁移窗口——避免「一升级就红 pipeline」。

### 同类需求的可参考思路
- 你的老牌 JS/TS 工具若遇性能墙，优先考虑「用 Go 移植热点（解析/检查）保留 JS 外壳」而非整体重写。
- `tsc/CHANGES.md` 这种「新旧实现刻意差异清单」值得任何 port 项目借鉴——把「我们故意改了什么」显式写出来，比埋在 commit 里强。

## 🧠 核心源码解读（克制代码量）
### 1. 原生编译器入口（`tsc/cmd/tsc/main.go`）
`cmd/tsc` 下 `main.go`（CLI 入口）、`lsp.go`（语言服务器）、`api.go`（API 层）、`sys.go`（系统调用抽象）分工清晰——**一个二进制同时服务命令行、编辑器 LSP、程序化 API**。

### 2. API 层的 msgpack 编解码（`tsc/internal/api/encoder/`）
原生编译器用 **msgpack 协议 + 生成的编解码器**做进程间通信：
```go
// tsc/internal/api/encoder/encoder.go（示意结构）
// encoder_generated.go 由代码生成，配对 decoder_generated.go
// stringtable.go 做字符串去重，降低协议体积
type Encoder struct { ... }
func (e *Encoder) Encode(v interface{}) ([]byte, error) { /* msgpack */ }
```
`encoder_generated.go` / `decoder_generated.go` 是生成代码，说明通信层高度规范化、可机器生成——这是「编辑器/CI/CLI 多前端共享一个编译器核心」的基建关键。

### 3. 新旧差异清单（`tsc/CHANGES.md`）
明确列出 Corsa(Go) 相比 Strada(JS) **砍掉了什么**（如 Closure header 支持、部分 JS-only 特性），并解释「为什么砍」——是 port 项目的诚实变更日志范本。

## 🌐 全网口碑画像
来源：Microsoft DevBlogs 公告、The Register / Techzine 报道、ecorpit / flowverify / byteiota / runfreetools / imseankim 等 2026 技术博客。

### 好评共识
- **10× 数字真实可复现**：微软自测 + 独立开发者在自己项目上验证一致，非 cherry-pick 微基准。
- **语义零变化最受欢迎**：「类型通过 tsc 就通过 tsgo」让团队敢升级，不被新 false positive 折磨。
- **编辑器体验质变**：大型项目 IntelliSense「即时」是日常最能感知的赢。

### 差评 / 踩坑高发区
- **`Compiler API` 在 7.0 缺失**：typescript-eslint、ts-jest、ts-morph、Vue/Svelte/Astro 模板类型检查**暂不可用**，要等 7.1（数月后）。
- **自定义 transformer 插件阻断**：NestJS decorators、typeorm、部分 emotion 用 Strada API 做编译期 transform，7.0 硬伤。
- **Decorators 仅支持 ES2021+**：ES2015 downlevel 装饰器未做。
- **JSDoc `@enum`/`@constructor` 不再识别**（纯 TS 项目无影响）。

### 升级建议（社区共识）
大多数无 `Compiler API` 依赖的项目：`npm i -D typescript@7` + 构建脚本 `tsc`→`tsgo` + CI 验证即可；有依赖的先留在 6.x 等 7.1。tsconfig 格式不变、JS 输出语义相同。

## ⚔️ 竞品对比
| 维度 | TypeScript 7 (tsgo) | 旧 TS 6 (Strada) | Babel / SWC / esbuild |
|------|--------------------|--------------------|------------------------|
| 类型检查 | ✅ Go 原生 10× | JS 单线程 | ❌ 仅 transpile，无类型 |
| 生态 API | 7.1 才补齐 | ✅ 完整 | 不适用 |
| 输出语义 | 与 6 一致 | 基线 | 仅转译、最快 |
| 定位 | 类型系统 + 检查 + emit | 同左（慢） | 纯转译提速 |

**选择建议**：类型检查 / 语言服务 → tsgo 7（配 6.x 兜底 emit 与工具）；仅需快速转译（Vite 默认 transpile-only）→ SWC/esbuild 本就不依赖 tsc，零影响。

## 🎯 核心研判
### 优势
- 十年来最重大 TS 发布，性能代差级提升且语义零风险。
- Go 选型理由 workload 驱动，是「工程化选语言」的好范本。

### 风险
- **7.0 缺 `Compiler API`**：依赖它的工具链（eslint 类型感知、框架模板检查）暂不可用，是 2026 年实际迁移的最大 blocker。
- 自定义 transformer / 旧 decorator 支持未就绪。

### 适用 / 不适用
- ✅ 纯 TS 项目、大型 mono-repo、CI 类型检查瓶颈、编辑器流畅度诉求。
- ❌ 重度依赖 `Compiler API` / 自定义 transformer 的框架工具链 → 等 7.1。

### 趋势
上升期。7.0 GA（2026-07-08）后进入「双轨过渡」，7.1 补齐 API 后生态会快速跟迁；长尾框架工具是最后一批。

## 📂 关键文件路径速查
- `tsc/cmd/tsc/main.go` — 原生编译器 CLI 入口
- `tsc/cmd/tsc/lsp.go` — 语言服务器入口
- `tsc/cmd/tsc/api.go` — 程序化 API 入口
- `tsc/internal/ast/ast.go` — AST 定义
- `tsc/internal/api/encoder/` — msgpack 编解码（含 generated）
- `tsc/internal/api/session.go` / `server.go` — 会话/服务
- `tsc/CHANGES.md` — Strada↔Corsa 刻意差异清单
- `packages/` — JS/TS 工具链（类型、语言服务、emit）
