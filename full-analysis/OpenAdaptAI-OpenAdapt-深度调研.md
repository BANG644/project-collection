# OpenAdaptAI/OpenAdapt 深度调研

> 调研日期：2026-09-23 ｜ 定位：把"人类演示一次 GUI 操作"编译成可确定性重跑、且带独立效果验证的治理型程序，给 computer-use agent 提供"经过验证的手" ｜ Stars：1,737 ｜ 语言：Python ｜ 许可：MIT（Cloud 为商业闭源）｜ 默认分支：main ｜ 最近活跃：2026-09-14

## 一、项目定位（一句话）

OpenAdapt 是一个 **治理型演示编译器（governed demonstration compiler）**：人（或本地 agent）演示一遍任务 → 引擎保留证据、编译出确定性程序 → 按策略任职资格认证 → 在 fail-closed 运行时执行，每一步都让**独立的效应验证器**核对"声明的业务效果是否真的发生"，agent 只负责调用、不负责执行。

## 二、项目亮点（差异化）

- **"绝不把 halt 当成 success"的验证哲学**：运行时在动作前查授权/状态/目标唯一性，动作后等状态落定并评估声明效应，证据不足即 `HALTED_BEFORE_EFFECT` / `RECONCILIATION_REQUIRED`，而不是盲重试。
- **效应契约 + 证据层级（evidence tier）**：编译时从演示的"记录 delta"中**挖掘 effect contract**（例如"写入 1 条系统记录"），运行后由独立 system-of-record 在要求的证据层级确认（如 tier 1 = 独立记录库核对）。
- **结果状态机严谨**：`VERIFIED`（唯一生产成功）/ `HALTED_BEFORE_EFFECT` / `RECONCILIATION_REQUIRED` / `FAILED_PLATFORM` / `CANCELED` / `REJECTED_POLICY` / `COMPLETED_UNVERIFIED`（仅 Demo）/ `ROLLED_BACK`。
- **多表面 + 多后端**：浏览器（Playwright：DOM/无障碍/视觉/OCR/字段几何）、原生桌面（Win/macOS/Linux 的 UIA/Accessibility/AT-SPI）、远程（RDP）、Citrix/VDI，统一归一化到录制契约。
- **数据边界清晰**：原始录制与实时观测默认本地留存，跨边界需本地脱敏 + 完整清单 + 审阅 + 精确哈希审批 + 目标策略检查。

## 三、核心架构

```
人类/本地 agent 演示 ──▶ 表面录制器 (openadapt-capture)
        │
        ▼
openadapt-flow 编译器 ──▶ 可检视 bundle（含 effect contract）
        │
        ▼
任职资格 + 认证（policy，如 clinical-write）
        │
        ▼
治理型运行时（fail-closed）
        │
        ▼
独立效应验证器 ──▶ 契约通过 → VERIFIED ｜ 不确定/失败 → HALT / reconciliation
```

| 组件 | 产品角色 | 源码可用性 |
|------|----------|-----------|
| `OpenAdapt`（本仓库） | 启动器、meta 包、统一 CLI、稳定公开入口 | MIT |
| `openadapt-flow` | 编译器、认证、重放、治理修复、运行报告 | MIT |
| `openadapt-capture` | 原生屏幕/键鼠/时序/窗口/媒体捕获 | MIT |
| `openadapt-desktop` | 跨平台创作与操作员座舱 | MIT |
| `openadapt-privacy` | 本地脱敏与审阅机制 | MIT |
| OpenAdapt Cloud | 托管控制面/身份/计费/舰队协调 | 闭源商业 |

> 本仓库**只实现安装器 + 统一 `openadapt` CLI**，真正的编译器与运行时在 `openadapt-flow`；这种"薄启动器 + 重引擎分仓"是它的重要工程决策。

## 四、应用场景与启发

- **给 agent 一双"经过验证的手"**：当你的 computer-use agent 要操作没有 API 的 GUI（医疗 EMR、保险系统、内部后台），与其让 LLM 边看边点（不可控），不如人演示一遍 → 编译 → 资质认证 → 让 agent 调 `run` 工具，且**每次都返回 VERIFIED 收据**。
- **"确定性回放 + 独立核对"范式**：把"动作是否成功"从"屏幕看起来成功了"升级为"独立记录库确认了那条业务记录"，这套**效应契约 + 证据层级**模型对任何 RPA / agent 执行层都有复制价值。
- **合规敏感场景**：医疗/金融的"零模型调用确定性执行"（OpenEMR 实测 0 次模型 API 调用即完成）是其杀手锏方向。

## 五、源码深度解读（关键片段）

`docs/architecture.md` 明确给出治理型编译器闭环：人类演示 → Surface recorder → `openadapt-flow` 编译器 → Inspectable bundle → 任职资格 → 治理运行时 → 独立效应验证器 → `VERIFIED` / `HALTED`。关键约束写在 README：

```
A click landing is not evidence that a transaction committed.
Every terminal run says what the runtime actually knows about the business effect.
```

`tutorial` 流程会真实跑出收据：`[4/5] Admit and execute under the standard profile → VERIFIED in 4.1s; 0 model calls; the system of record holds 1 record(s)`。而 `openadapt quickstart --break-it` 故意让 backend 在成功横幅之后拒绝写入，运行时因"独立读记录库与展示不一致"而 halt——这正是产品的核心价值：横幅会撒谎，独立核对不会。

`openadapt/cli.py`（本仓库）是统一入口，提供 `openadapt doctor / flow / quickstart / agent serve` 等命令，把 `openadapt-flow` 的引擎能力暴露给本地。

## 六、全网口碑

- **正面**：定位独特（"verified last-mile execution for agents"），工程严谨度高于多数 RPA/agent 开源项目；有真实证据（OpenEMR 19/20 通过、RVU 审计年回收 ~$75k 应收账款）；文档与成熟度治理（production-lifecycle、platform-manifest）成熟。
- **风险/争议**：架构拆分为多仓（本仓只装 CLI，核心在 `openadapt-flow`），上手心智成本较高；商业 Cloud 闭源，本地安全关键验证不收费但治理/舰队能力收费；pre-1.0 monolith 已冻结于 `legacy/`，迁移需注意；研究方向（openadapt-ml 等）与产品线是两回事，勿混淆。

## 七、竞品对比与核心研判

| 维度 | OpenAdapt | 通用 computer-use agent | 传统 RPA |
|------|-----------|------------------------|----------|
| 执行方式 | 演示编译成确定性程序，0 模型调用 | 模型实时决策点击 | 固定脚本/选择器 |
| 成功判定 | 独立效应验证（VERIFIED） | 屏幕/坐标猜测 | 步骤通过 |
| 安全模型 | fail-closed + 证据层级 | 弱 | 中 |
| 适用 | 无 API 的 GUI、合规敏感 | 开放网页 | 稳定内部系统 |

**竞品**：Anthropic/OpenAI 的 computer-use、各类 GUI agent、UiPath 等。**OpenAdapt 的独特价值**是把"执行正确性"从概率问题变成"可验证的契约问题"。

**核心研判**：⭐⭐⭐⭐ — 它是 agent 执行层里少见的"先治理、后跑批"范式样本，其 **effect contract + 独立证据验证 + fail-closed** 三件套值得任何做 RPA/agent 落地的团队抄作业；但多仓拆分 + 商业边界 + 资质门槛使其偏"严肃场景"，个人尝鲜成本不低。关注其 Production 准入机制与 Seal 合约是否会成为行业可验证执行的参照标准。

## 八、关键文件路径速查

- `openadapt/cli.py` — 统一 `openadapt` CLI（doctor/flow/quickstart/agent）
- `docs/architecture.md` — 治理型编译器架构与仓库角色表
- `docs/LEGACY_FREEZE.md` — pre-1.0 monolith 冻结与迁移
- `scripts/` — 发布健康、平台清单、准入候选等发布治理脚本
- 核心引擎（分仓）：[openadapt-flow](https://github.com/OpenAdaptAI/openadapt-flow) ｜ 捕获层：[openadapt-capture](https://github.com/OpenAdaptAI/openadapt-capture) ｜ 桌面：[openadapt-desktop](https://github.com/OpenAdaptAI/openadapt-desktop)
- 研究线：[openadapt-ml](https://github.com/OpenAdaptAI/openadapt-ml) ｜ 文档：[docs.openadapt.ai](https://docs.openadapt.ai)
