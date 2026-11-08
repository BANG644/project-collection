# NVKE (NVIDIA Kubernetes Engine) 深度调研

> 调研日期：2026-11-09 ｜ Stars：776 ｜ 语言：Go（go 1.27.3） ｜ 协议：Apache-2.0 ｜ 主分支：main ｜ 官网/文档：docs.nvidia.com/nvke ｜ 创建：2026-08-04 ｜ 状态：Preview

## 一、项目全景

`dsx-ai-factory/nvke`（NVIDIA Kubernetes Engine）是 NVIDIA 推出的**在自有 NVIDIA GPU 裸金属上运行托管 Kubernetes 服务**的管理平面（management plane）。平台团队安装 NVKE 管理平面来为"客户"创建并运营 K8s 集群；每个工作负载集群都有**独立的控制平面、etcd 与节点池**，客户通过 Kubernetes API / `kubectl` 使用自己的集群。

关键事实（仓库元数据 + README）：
- **多模块 Go 工程**：`go.work` 聚合 **13 个模块**（agent / auth / cli / cluster-api-provider-provisioned / controller / controller/api / controller/deploy/charts / controller/hack/capd-reboot-controller / controller/nico-sim / controller/test/e2e / management-engine / os-image / release）。
- **配套生态**：NVKR（NVIDIA Kubernetes Recipes）负责从固定输入构建并签名节点镜像与组件；CAPNICo（Cluster API Provider for NICo）是底层供给器；AICR 提供加速运行时；`nvkectl` 是官方 CLI。
- **唯一兼容基础设施提供方（Preview）**：NVIDIA Infra Controller（NICo）；节点通过 **SPIFFE/SPIRE + TPM 远程证明**获得加入凭据，etcd 可按集群加密。
- **本地快速试用**：Linux amd64/arm64，≥6 CPU / 12 GiB 内存 / 100 GiB 磁盘 + Docker + 虚拟 TPM，无需 NVIDIA 账号即可在模拟机上跑管理平面与工作负载集群。
- 由 k8s 社区重量级人物参与：`dims`（Derek Carr，k8s SIG-Node 主席）、`TerryHowe`（k8s SIG-Auth）。

**项目亮点**
1. **托管 K8s 范式下沉到裸金属 GPU**：把 GKE/EKS 式"控制平面我来管、你用集群"的体验搬到自有 NVIDIA 硬件。
2. **Cluster API 原生**：基于 CAPI 体系（CAPNICo）做机器供给，复用 k8s 声明式、可观测、可漂移的成熟范式。
3. **零信任节点身份**：TPM + SPIFFE/SPIRE 远程证明，节点拿到 join 凭据前先自证硬件身份。
4. **构建与部署分离、带证据**：NVKR 拥有构建与发布证据，NVKE 只部署已签名制品，供应链可追溯。

## 二、核心架构

NVKE 是典型 **"管理平面 + 多工作负载集群"** 的托管 K8s 架构，且强绑定 NVIDIA 基础设施栈：

- **管理平面（management-engine）**：对外暴露多套 API 表面——`operator-api`（运维操作）、`tenant-api`（租户）、`public-gen`（生成产物）；核心 reconcile 循环在 `controllers/nvkecluster_controller.go`。
- **供给层（cluster-api-provider-provisioned / CAPNICo）**：Cluster API Provider，经 NICo 请求裸金属机器并组建成 K8s 节点；`controller/nico-sim` 提供 NICo 模拟器以支持本地试用。
- **身份与安全（auth / agent）**：`auth` 负责 API 认证；`agent`（即 `nvke-agent`，跑在每个工作负载集群节点上）承接加速运行时与节点侧职责。
- **镜像与发布（os-image / release）**：`os-image` 构建节点 OS 镜像；`release` 管发布；`cli/nvkectl` 是用户/运维入口。
- **可观测与部署（charts / deploy）**：以 Helm chart（`controller/deploy/charts`、`management-engine/chart`）形式分发组件。

数据流：用户/运维经 `nvkectl` 或管理平面 API 请求集群 → management-engine 经 CAPNICo 调 NICo 供给机器 → 节点以 TPM+SPIRE 证明身份后加入 → 各自形成独立控制平面/etcd/节点池 → 客户用 kubectl 操作自己集群。

## 三、源码深度解读

### 1. 多模块工作区（`go.work`）
13 个模块以 `use(...)` 聚合，全部从公共依赖解析，无 vendor 树、无需 NVIDIA 凭据即可构建：

```go
// Go workspace for every module in the repository.
go 1.27.3
use (
    ./agent
    ./auth
    ./cli
    ./cluster-api-provider-provisioned
    ./controller
    ./management-engine
    // ...共 13 个模块，含 controller/api、nico-sim、os-image、release
)
```
这种"单体仓库 + 多 go.mod"的布局，既隔离各组件依赖，又共享统一构建——是大型 K8s 控制面项目的常见工程选择。

### 2. 集群协调循环（`management-engine/controllers/nvkecluster_controller.go`）
文件名与同目录 `nvkecluster_controller_test.go` / `suite_test.go` 表明它沿用 **kubebuilder / controller-runtime** 的 `Reconcile` 范式：监听 `NVKECluster` 自定义资源，对比"期望状态 vs 实际状态"驱动供给/扩缩/升级。测试同目录存在（`suite_test.go` 是 Ginkgo 测试套件入口），说明项目把协调逻辑当一等公民做单测——对比许多"只给 YAML 不管测试"的 CAPI provider，这是成熟度信号。

### 3. CLI 入口（`cli/cmd/nvkectl` + `management-engine/cmd`）
`cli/cmd` 下唯一子目录即 `nvkectl`，是面向用户的命令行入口；`management-engine/cmd` 则分为 `main.go` + `operator-api` / `public-gen` / `tenant-api` 四个子命令/服务，对应管理平面的多租户 API 切分。模块化的 `cmd` 布局便于独立部署与水平扩展各 API 面。

## 四、应用场景与启发

- **自有 GPU 集群的"托管化"**：科研机构/企业已有大量 NVIDIA 裸金属，NVKE 让平台团队用 GKE 式体验把它们变成多租户 K8s 服务，省去自研控制平面的成本。
- **CAPI 供给范式的再印证**：把"机器供给"完全交给 Cluster API Provider（CAPNICo），印证了 CAPI 作为异构基础设施统一抽象层的价值——任何要做"声明式供给"的系统都可复用此思路。
- **零信任节点身份落地样板**：TPM + SPIFFE/SPIRE 的远程证明流程，是"不可信硬件如何安全入网"的现成参考实现，可迁移到边缘/多云场景。
- **构建-部署证据分离**：NVKR 管构建与签名证据、NVKE 只部署已签名制品，是供应链安全（SLSA 思路）在 K8s 发行里的具体落地。

## 五、社区口碑

NVKE 于 2026-08 才创建、当前为 **Preview**，独立第三方测评极少，**外部口碑数据不可用**；以下为可核实信号：
- **官方背书强**：NVIDIA 出品 + k8s SIG-Node 主席 `dims`、SIG-Auth `TerryHowe` 直接参与，工程可信度起点高。
- **README 透明度**：明确标注 Preview 限制——安装后 API 认证默认关闭、用明文 HTTP；管理集群**不自我升级/扩缩/替换**，无管理平面升级或备份/恢复流程；FDE 节点镜像仅评估用、不提供静态数据机密性。这种"把已知缺陷写在前"的做法利于早期评估者建立信任。
- **赛道关注**：作为 NVIDIA 在"托管 GPU K8s"的官方落子，正值 RunAI（被 NVIDIA 收购）整合期，社区普遍将其视为 NVIDIA 自有 K8s 战略的一环。

> 口碑研判：工程出处与透明度俱佳，但 Preview 阶段、文档/生态尚在早期，生产采用需谨慎；建议持续跟踪其 GA 路线图。

## 六、竞品对比

| 维度 | NVKE | GKE/EKS/AKS | RunAI(NVIDIA) | Rancher/OpenShift | kubeadm/k3s 裸金属 |
|------|------|-------------|---------------|-------------------|-------------------|
| 厂商 | NVIDIA（自有硬件） | 云厂商 | NVIDIA（调度层） | SUSE/Red Hat | 自运维 |
| 定位 | 裸金属 GPU 托管 K8s | 公有云托管 | GPU 调度/编排 | 通用平台 | 自建 |
| 供给抽象 | Cluster API(CAPNICo) | 云原生 | — | Rancher/Operator | 手动 |
| 节点身份 | TPM+SPIFFE/SPIRE | 云 IAM | — | 平台内 | 自管 |
| 供应链证据 | NVKR 签名制品 | 云管 | — | 镜像签名 | 自管 |

结论：NVKE 的对手是"在自有 NVIDIA 硬件上自建/自管 K8s"的繁琐路径，以及与云托管 K8s 的体验落差；它与 RunAI（同属 NVIDIA）更可能是**互补**（RunAI 管 GPU 调度，NVKE 管集群生命周期）。相对 Rancher/OpenShift，NVKE 更聚焦 NVIDIA GPU 裸金属这一窄而深的场景。

## 七、核心研判

1. **战略卡位清晰**：NVIDIA 把"卖硬件"延伸到"卖硬件上的托管 K8s 体验"，NVKE + NVKR + CAPNICo + AICR 构成闭环，是 GPU 云化的关键拼图。
2. **工程范式成熟**：CAPI 原生 + controller-runtime reconcile + 多模块 go.work + 同目录测试，说明不是玩具项目，而是沿 k8s 主流工程实践搭建。
3. **Early-stage 风险明确**：Preview、无管理平面 HA/备份、API 默认不安全——只适合评估，不宜生产；跟踪 GA 与 NICo 多供应商支持是后续重点。
4. **数据不可用**：无独立第三方基准/性能报告；"DeepMind 式背书"不适用本项目，外部实测缺失。

## 八、关键文件路径速查

- `go.work` — 13 模块 Go 工作区聚合（agent/auth/cli/controller/management-engine/os-image/release …）
- `cli/cmd/nvkectl/` — 官方命令行入口
- `management-engine/cmd/` — 管理平面服务（main.go + operator-api / public-gen / tenant-api）
- `management-engine/controllers/nvkecluster_controller.go` — NVKECluster 协调循环（含 _test.go / suite_test.go）
- `cluster-api-provider-provisioned/` — CAPNICo 供给器（api/cmd/config/controllers/go.mod）
- `controller/` — 主控制器模块（api/cmd/deploy/charts/nico-sim/profiles）
- `controller/nico-sim/` — NICo 模拟器（支撑本地无硬件试用）
- `auth/` `agent/` — API 认证 / 节点侧 nvke-agent（加速运行时）
- `os-image/` `release/` — 节点 OS 镜像构建 / 发布管理
- `docs/` — 安装/运维/API 认证/已知限制等官方文档
