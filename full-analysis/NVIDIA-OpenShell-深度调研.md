# NVIDIA/OpenShell 深度调研

> 调研日期：2026-10-24 ｜ Stars：18,624 ｜ 语言：Rust（运行时）+ Python/TypeScript/Go（SDK）｜ 许可：Apache-2.0 ｜ 创建：2026-02-24 ｜ 默认分支：main

## 一、项目定位（一句话）

NVIDIA 出品的 **「自主 AI Agent 安全私有运行时」**——用内核级隔离 + 形式化验证策略，让 agent 能读文件、装包、调 API、用凭据，却拿不到你的数据、密钥与网络。

## 二、项目亮点（差异化，开篇呈现）

1. **内核级强制隔离**：每个 agent 跑在独立 sandbox，内核拦截每一次文件访问 / 系统调用 / 网络连接；凭据只在请求发往「白名单端点」时才由 OpenShell 注入，agent 永远看不到真实密钥。
2. **策略变更形式化验证（Z3 SMT）**：`openshell-prover` 把「策略 + 凭据集 + 二进制能力注册表」编码成 Z3 模型，跑可达性查询，提前标红「带凭据触达新主机 / 调用新 API 方法」这类风险，须人工复核才放行。
3. **多运行时后端 + 多语言 SDK**：Docker / Podman / Kubernetes / VM 四种 driver；Python / TypeScript / Go / Rust 四语言 SDK，且自带 `npx skills add NVIDIA/OpenShell` 的 agent skill（教 agent 写策略、排障网关）。
4. **企业级工程化基座**：Helm 上 K8s（要求 CNI 强制 NetworkPolicy）、OCSF 审计日志、OpenTelemetry 可观测、SBOM、GPU(VFIO) 直通，CI 含 CodeQL / cargo-deny / e2e 矩阵。

## 三、核心架构（克制代码量）

单一 Rust workspace（39 个 crate），职责切分极清晰：

- **Gateway（控制面）**：`openshell-gateway` + `openshell-server`，管理 sandbox / 策略 / 访问。
- **Supervisor（监督）**：`openshell-supervisor` 拆为 `*-network` / `*-process` / `*-middleware` / `*-control`，负责沙箱内进程与网络的实际管控。
- **Sandbox（隔离）**：`openshell-sandbox` + `openshell-sandbox-backend` + `openshell-isolation-interface`，内核级拦截原语。
- **Policy + Verifier**：`openshell-policy` + `openshell-policy-schema`（声明式策略）+ `openshell-prover` / `openshell-prover-cli`（Z3 形式化验证）。
- **Drivers（计算 / 身份 / 凭据）**：`openshell-driver-{docker,podman,kubernetes,vm,vault,mxc,db-credstore,kubernetes-secrets}`。
- **SDK / 扩展 / 可观测**：`openshell-sdk`（Rust）/ `python/openshell` / `sdk/typescript` / `sdk/go`、`openshell-extension-core` + `openshell-gateway-interceptors`、`openshell-otel` + `openshell-ocsf`、`openshell-vfio`（GPU 直通）。

## 四、应用场景与启发（重点）

- **给「敢让 agent 碰真实环境」提供安全底座**：computer-use / coding-agent / 多 agent 编排在本地或集群跑真实命令时，OpenShell 解决「能力 vs 失控」的千古难题——这正是本地 Agent OS、企业 agent 中台的刚需。
- **形式化验证策略变更**是通用范式：任何 permission system（MCP 工具授权、agent skill 沙箱、云 IAM）都能借鉴「把策略 + 凭据 + 能力注册表编码成 SMT，对危险变更做可达性预检 + 人工门」的思路。
- **对 WorkBuddy / 用户自建 agent 工作流的借鉴**：用户在做「论文伴读 / 错题归因」等 agent 系统，若未来要让 agent 操作本地文件或调用付费 API，OpenShell 的「凭据按端点注入 + 策略证明」是可直接复用的安全设计样板。

## 五、源码深度解读（2 个核心模块）

**1. `openshell-prover`（形式化验证，README 实证）**

> Encodes a policy + its attached credential set + a binary capability registry as a Z3 SMT model, then runs reachability queries to detect credentialed-reach and capability changes a reviewer should be aware of.

并暴露独立 containment API：`check_within_boundary(boundary, candidate, CheckOptions)` 仅当返回 `CheckResult::Within` 才接受候选策略——把「新策略是否越界」变成可机器判定的一次调用。

**2. `crates/openshell-cli/src/policy_update.rs`（CLI 策略变更编排）**

```rust
pub struct PolicyUpdatePlan {
    pub merge_operations: Vec<PolicyMergeOperation>,   // 网关侧合并
    pub preview_operations: Vec<PolicyMergeOp>,         // 本地预览（含 prover 预检）
}
pub fn build_policy_update_plan(
    add_endpoints: &[String], remove_endpoints: &[String],
    add_deny: &[String], add_allow: &[String],
    remove_rules: &[String], binaries: &[String],
    rule_name: Option<&str>, any_binary: bool,
    endpoint_path: Option<&str>,
) -> Result<PolicyUpdatePlan> { /* L7 规则必须显式声明 --binary / --rule-name，否则拒绝 */ }
```

`--add-allow/--add-deny` 强制要求完整 `--binary` 列表或显式 `--any-binary`，从类型层面杜绝「一条声明两义」的越权隐患——这正是「策略变更须精确可证」原则在代码层的落地。

## 六、全网口碑

NVIDIA 官方出品、Apache-2.0、文档完善（`docs.nvidia.com/openshell`）、当日 GitHub Trending 上榜；仓库工程水位极高（DCO、CodeQL、SBOM、K8s Helm、e2e 矩阵齐全）。社区讨论与 issue 活跃（565 open issues），属高速演进早期项目。

## 七、竞品对比 + 核心研判

| 维度 | OpenShell | e2b / Modal / Firecracker | 纯 Docker 隔离 | Anthropic/cloudflare 安全 skill |
|---|---|---|---|---|
| 隔离层级 | 内核级 + sandbox | microVM | 进程/命名空间 | 提示层（无内核强制） |
| 凭据保护 | 按端点注入，agent 不可见 | 环境变量注入 | 手动挂载 | 依赖 prompt |
| 策略变更验证 | **Z3 形式化预检 + 人工门** | 无 | 无 | 无 |
| 多 agent  fleet | 原生 gateway 控制面 | 偏单次执行 | 需自搭 | 偏单 agent |

**核心研判**：解决的是「让 agent 操作真实环境」的共性安全刚需，企业 / 多 agent 中台强需求；项目年轻（2026-02 创建）、迭代快、issue 活跃但仍是 0.x 早期，个人小脚本场景偏重。适合「敢让 agent 碰真实文件 / API / 凭据」的团队作为安全底座评估；若仅跑不可信代码，轻量 microVM 仍更省心。许可 Apache-2.0，可商用、可二次开发。

## 八、关键文件路径速查

- 运行时 workspace：`crates/openshell-{gateway,supervisor,sandbox,policy,prover,cli,...}`（39 crate）
- 策略声明与验证：`crates/openshell-policy-schema` · `crates/openshell-prover` · `crates/openshell-prover-cli`
- 多语言 SDK：`python/openshell` · `sdk/typescript` · `sdk/go` · `crates/openshell-sdk`（Rust）
- Agent skill：`skills/`（支持 `npx skills add NVIDIA/OpenShell`）
- 计算后端 driver：`crates/openshell-driver-{docker,podman,kubernetes,vm,vault,mxc}`
- GPU 直通：`crates/openshell-vfio` ｜ 可观测：`crates/openshell-otel` · `crates/openshell-ocsf`
