# TencentCloud/CubeSandbox - 全方位深度调研

> 调研时间：2026-07-02 | 仓库：https://github.com/TencentCloud/CubeSandbox
> 报告版本：v1.0

---

## 一句话定位

CubeSandbox 是**腾讯云开源的、基于 RustVMM + KVM 的 AI Agent 代码执行安全沙箱**，能够在亚百毫秒内启动一个硬件级隔离的 MicroVM，单实例内存开销不到 5MB，单机可运行数千个并发沙箱。本质上是 **E2B 的开源自托管替代品**——兼容 E2B SDK，只需改一个 URL 环境变量即可零代码迁移。

---

## 项目亮点

1. **60ms 冷启动 + 5MB 内存开销** —— 创下行业记录：传统 VM 启动数秒，Docker 容器 ~200ms，而 CubeSandbox 在硬件级隔离的前提下做到 <60ms 冷启动、<5MB/实例内存、单节点 2000+ 实例。50 并发下平均 67ms，P95 90ms，P99 137ms。

2. **KVM 硬件级隔离** —— 每个沙箱拥有独立 Guest OS 内核，彻底杜绝 Docker 共享内核的容器逃逸风险。即使 LLM 生成的代码利用内核漏洞，崩溃的也只是沙箱自身的 Guest 内核，宿主机毫发无损。

3. **E2B SDK Drop-in 兼容** —— 原生兼容 E2B SDK 接口规范，只需替换一个环境变量 `E2B_API_URL` 即可完成迁移，业务代码零修改。这消除了平台锁定风险，让开发者可以在 E2B 托管云上开发，在 CubeSandbox 自托管控成本。

4. **eBPF 原生网络隔离 (CubeVS)** —— 自研 eBPF 虚拟交换机，在内核态完成数据包转发和过滤，支持细粒度的出站域名白名单控制，比传统 iptables 方案性能高一个数量级。XDP 层介入，每个沙箱有独立网络策略。

5. **CubeCoW 快照/克隆/回滚** —— 基于内核 FICLONE ioctl 的 Copy-on-Write 快照引擎，百毫秒级 checkpoint，支持从任意保存状态回滚或 fork。增量脏页追踪——只有变化的内存页才写入快照。

---

## 项目架构全景

```
┌─────────────────────────────────────────────────────────────┐
│                     SDK Layer (E2B Compatible)               │
│    Python SDK / Go SDK (E2B SDK drop-in 替换)                │
├─────────────────────────────────────────────────────────────┤
│                    Control Plane (无状态)                     │
│  ┌──────────────────┐  ┌──────────────────┐  ┌────────────┐ │
│  │    CubeAPI       │  │   CubeMaster     │  │   WebUI    │ │
│  │  (Rust/Axum)     │  │   (Go/gRPC)      │  │ (React)    │ │
│  │  REST API 网关   │  │  集群调度器      │  │ 管理控制台  │ │
│  └────────┬─────────┘  └────────┬─────────┘  └────────────┘ │
│           │                     │                             │
│           └──────────┬──────────┘                             │
│                      ▼                                        │
│               ┌──────────────┐                                │
│               │    Redis     │ (状态协调、生命周期事件)         │
│               └──────────────┘                                │
├─────────────────────────────────────────────────────────────┤
│                     Data Plane (节点本地)                      │
│  ┌────────────────────────────────────────────────────────┐  │
│  │                   CubeProxy                            │  │
│  │       (OpenResty 反向代理 + 自动暂停/恢复 sidecar)       │  │
│  └──────────────────────────┬─────────────────────────────┘  │
│                             │                                  │
│  ┌────────────────────────────────────────────────────────┐  │
│  │   Cubelet (Go, 节点生命周期管理器)                       │  │
│  │  ┌──────────────┐ ┌──────────────┐ ┌──────────────┐   │  │
│  │  │  CubeShim    │ │  CubeCoW     │ │  Network Agent│   │  │
│  │  │(containerd   │ │(FICLONE快照) │ │ (Go, 网络配置)│   │  │
│  │  │ Shim v2/Rust)│ │              │ │               │   │  │
│  │  └──────┬───────┘ └──────────────┘ └──────────────┘   │  │
│  │         │                                                │  │
│  │  ┌──────▼───────────────────────────────────────────┐   │  │
│  │  │        CubeHypervisor (RustVMM + KVM)            │   │  │
│  │  │  MicroVM 生命周期: vCPU/内存/virtio 设备/启动/暂停  │   │  │
│  │  │  快照/恢复 · Seccomp 加固 · 最小系统调用面          │   │  │
│  │  └──────────────────────────────────────────────────┘   │  │
│  └────────────────────────────────────────────────────────┘  │
│                                                               │
│  ┌─────────────────────────────────────────────┐              │
│  │          CubeVS (eBPF 虚拟交换机)            │              │
│  │  每个沙箱独立网络策略 · 出站白名单 · 连接追踪  │              │
│  └─────────────────────────────────────────────┘              │
│                                                               │
│  ┌─────────────────────────────────────────────┐              │
│  │       CubeEgress (OpenResty L7 MITM 代理)    │              │
│  │  域名白名单 · 凭据保险箱 · 全审计日志 · 即时阻断 │              │
│  └─────────────────────────────────────────────┘              │
└─────────────────────────────────────────────────────────────┘
```

### 核心技术栈

| 组件 | 语言 | 技术选型 |
|------|------|---------|
| CubeAPI (API 网关) | **Rust** | Axum, Tokio, 完全 E2B 兼容 |
| CubeMaster (调度器) | **Go** | gRPC, Redis 状态协调 |
| CubeShim (容器桥接) | **Rust** | containerd Shim v2 接口 |
| CubeHypervisor (虚拟化) | **Rust** | Cloud Hypervisor 定制, KVM API |
| CubeVS (网络) | **Rust + eBPF** | XDP 程序, BPF map, TPROXY |
| CubeEgress (安全) | **Lua + OpenResty** | L7 MITM 代理, 策略引擎 |
| CubeCoW (存储) | **Rust** | XFS reflink (FICLONE) |
| Cubelet (节点管理) | **Go** | containerd 集成, vsock |
| WebUI | **TypeScript/React** | Tailwind, i18n 中英双语 |
| SDK (Python/Go) | **Python/Go** | E2B 兼容, 文件操作/策略管理 |

---

## 应用场景与启发

### 核心场景：AI Agent 代码执行

CubeSandbox 的设计初衷就是解决 AI Agent 场景下 **"LLM 生成的不可信代码在哪里安全执行"** 的问题。

**工作流闭环：**
```
LLM 生成代码 → Agent 框架 → CubeAPI (E2B SDK) → CubeMaster 调度
→ Cubelet 创建 MicroVM → 沙箱内执行代码 → 结果返回 Agent → 沙箱销毁
```

整个过程在 60ms 内完成沙箱启动，安全隔离不可信代码。

### 典型应用场景

| 场景 | 适用性 | 关键价值 |
|------|--------|---------|
| **AI 代码助手 (C 端)** | ★★★★★ | 硬件级隔离保护用户环境，亚百毫秒响应不影响对话流畅度 |
| **企业内部 Agent 平台** | ★★★★☆ | 自托管满足数据合规，不含任何代码外传到海外闭源服务 |
| **金融/政务 Agent** | ★★★★★ | 硬件级隔离满足等保要求，凭据保险箱保证 API Key 不泄露 |
| **Agent RL 训练** | ★★★★☆ | Harness Loop 模式支持多轮状态保持，快照/克隆加速训练 |
| **在线编程教育** | ★★★★☆ | 隔离学生代码执行，高密度降低服务器成本 |
| **CI/CD 安全构建** | ★★★☆☆ | 构建环境完全隔离，防止供应链攻击横向移动 |
| **多 Agent 协同** | ★★★☆☆ | 每个 Agent 独立沙箱，eBPF 确保沙箱间网络隔离 |

### 关键启发

1. **E2B 兼容策略是神来之笔**：E2B 已建立事实上的 Agent 沙箱 API 标准，CubeSandbox 不是另起炉灶，而是兼容并超越。开发者在 E2B 上开发，在 CubeSandbox 上部署，锁定期望被打破。

2. **硬件级隔离不是"过度设计"**：Docker 的 Namespace/Cgroup/Seccomp 被广泛认为不够安全（2020s 多次容器逃逸漏洞）。当 LLM 生成的代码完全不可控时，共享内核的任何漏洞都可能导致逃逸。CubeSandbox 选择 KVM 是正确的高安全姿态。

3. **全栈 Rust 验证了"用更好的语言重写"趋势**：从 API 网关到虚拟化再到存储引擎，全栈 Rust 既保证内存安全（VMM 是安全边界最关键组件），又提供 C/C++ 级别的性能。

4. **开源 + 自托管 = 合规的终极答案**：对金融、政务等强合规行业，数据不能出 VPC。CubeSandbox 提供完整自托管栈（含一键部署脚本），让这些行业也能用上 AI Agent 技术。

5. **eBPF 正在重塑基础设施网络**：CubeVS 选择 eBPF/XDP 而非传统 iptables/bridge，代表了云原生网络从"用户态规则匹配"到"内核态高速处理"的范式转变。

---

## 核心源码解读

### 1. CubeAPI 入口：REST API 网关

**位置**: `CubeAPI/src/main.rs`

CubeAPI 使用 Rust + Axum 框架，提供 E2B 兼容的 REST API：

```
模块概览 (CubeAPI/src/main.rs):
- config:  环境变量/CLI 参数配置 (Clap Parser)
- handlers:  路由处理器 (sandboxes/snapshots/templates/agents/auth/health...)
- services:  业务逻辑层 (sandbox 创建/销毁/暂停恢复/模板管理/快照管理)
- middleware:  认证 + 限流
- routes:    路由注册
- db:        数据库 (Redis + MySQL)
- models:    数据模型
- cubemaster: gRPC 客户端连接 CubeMaster
```

**关键设计**：Rust 异步(tokio) + Axum 路由框架，认证回调模式。当设置了 `AUTH_CALLBACK_URL`，每个请求会 POST 到该 URL 验证 token，提供灵活的身份验签集成。

### 2. CubeMaster：Go 调度器

**位置**: `CubeMaster/pkg/`

```
调度流水线:
收到创建请求 → prefilter 预过滤 (资源检查)
→ filter (CPU/内存/磁盘/模板本地性/第三方限制/实时创建限流)
→ score 评分 (镜像亲和性/实时负载/多因子评分)
→ postscore (节点白名单)
→ select → 调度到目标节点 → gRPC 通知 Cubelet
```

**核心模块**:
- `scheduler/`: 调度器主逻辑，含亲和性调度(affinity/)、选择器(selctx/)
- `selector/filter/`: 各路筛选器 — CPUScore、MemFilter、DiskFilter、TemplateLocality、RealtimeCreateLimit
- `selector/score/`: 评分器 — 镜像亲和度、实时负载、多因子加权、亲和性加成
- `pkg/nodemeta/`: 节点元数据管理，模板版本矩阵(versionmatrix)
- `pkg/instancecache/`: 实例缓存，local cache + redis 双层

### 3. CubeHypervisor：Rust VMM 核心

**位置**: `hypervisor/src/main.rs` (~62KB) + `hypervisor/vmm/` 各模块

CubeHypervisor 基于 Cloud Hypervisor 定制，裁剪了非必要设备模拟。VMM 代码主要处理：
- KVM fd → VM fd → vCPU fd 三级句柄链
- virtio 设备链（块/网络/文件系统/控制台/RNG）
- 内存映射（MMIO、PCI BAR）
- 快照/恢复序列化

**裁剪要点**:

| 标准 Cloud Hypervisor | CubeSandbox |
|----------------------|-------------|
| USB 控制器 | 移除 |
| PCI 桥接器 | 精简 |
| TPM 设备 | 移除 |
| Serial Console | 保留(精简) |
| virtio-* | 完整保留 |
| balloon | 保留 |

### 4. CubeVS：eBPF 虚拟交换机

**位置**: 网络相关代码分布在 `CubeEgress/` 和 `network-agent/`

核心 eBPF 程序逻辑：
```
XDP ingress:
  → 解析以太网帧/IP 头
  → BPF map 查找沙箱 ID → 网络策略
  → 若无策略 → XDP_DROP (默认拒绝)
  → 检查目标端口白名单
  → 允许则 XDP_PASS, 拒绝则 XDP_DROP

TC egress:
  → 获取沙箱 ID
  → 查询 egress_rules BPF map
  → 匹配域名/端口白名单
  → 放行/丢包 + 字节计数统计
```

### 5. CubeCoW：Copy-on-Write 快照引擎

利用 Linux 内核 `FICLONE` (文件范围克隆) ioctl 在 XFS 上实现 O(1) 快照：
- **快照 = 元数据操作**，不复制数据块
- **增量脏页追踪**：仅持久化自上次快照以来变化的内存页
- **扁平快照模型**：删除任一快照不影响其他快照
- **回滚**：通过 vsock 向 CubeShim 发送恢复请求

---

## 架构决策与设计哲学

### 1. "Agent-First" 原则

超越经典的 "LLM 调用工具 → 沙箱执行 → 返回结果" 循环。生命周期语义、SDK 形状、自动暂停/恢复、快照/克隆/回滚等设计，都是为了支持 **长时间运行的 Agent 和有状态服务**（持久化开发环境、Web 服务、数据库）直接在沙箱内运行。

### 2. 安全没有妥协：KVM 而非 Docker

Docker 容器隔离 = Namespace + Cgroup + Seccomp。所有容器共享宿主机内核面，一个 Dirty COW 级别的漏洞就足以让所有容器沦陷。CubeSandbox 选择 KVM 硬件虚拟化，每个沙箱独立 Guest OS 内核——即使 Guest 内核被攻破也无法触及 Host。

### 3. "标准兼容"而非"重新定义"

E2B 已经定义了 Agent 沙箱的事实 API 标准（Manus、OpenAI Agents SDK 都在使用）。CubeSandbox 不做第 N+1 个标准，而是 **100% 兼容 E2B SDK**，让开发者一台机器就能完成从 E2B 托管到自托管的迁移。

### 4. 控制面无状态 = 天然水平扩展

CubeAPI 和 CubeMaster 不保存本地状态，所有协调通过 Redis。这意味着任意 CubeAPI 或 CubeMaster 实例可以服务任何请求，水平扩展只需加机器。

### 5. 零信任网络模型（默认拒绝）

- 沙箱默认无网络出站权限
- 域名必须显式加入白名单
- CubeEgress 在 L7 做 MITM 代理，支持凭据替换（API Key 不进入沙箱）
- 所有流量审计日志可查

---

## 全网口碑画像

### 来源 1: WaveSpeed Blog (2026-05-12)
**"CubeSandbox 与 E2B：生产环境智能体对比"**
> "CubeSandbox 是 E2B SDK 的自带基础设施后端……两个项目之间的 SDK 兼容性是整个发布中最有价值的东西——它意味着整个 agent 基础设施领域的锁定税刚刚变小了。"
> 
> "如果月用量低于约 5 万沙箱小时、无合规约束、无基础设施团队 → E2B 托管。超过此数，或有严格的数据驻留要求 → CubeSandbox 自托管。"

### 来源 2: 程序员茄子 (2026-05-02)
**"AI Agent 沙箱三国杀：OpenSandbox vs CubeSandbox vs E2B"**
> "CubeSandbox 的硬件级隔离 + 亚百毫秒启动，适合安全要求极高、需要 E2B 无缝迁移的场景。CubeSandbox 在单沙箱性能和隔离性上完胜。"

**性能数据**: 单并发 60ms 冷启动，50 并发 P95 90ms，单实例 <5MB，100 实例 ~500MB。

### 来源 3: 掘金技术社区 (2026-05-13)
**"60ms 启动一个安全沙箱：深入解析腾讯云 CubeSandbox"**
> "AWS Firecracker 需要 ~125ms，Cloud Hypervisor ~150ms。CubeSandbox 的优化在于：内存文件系统（memfd）省掉磁盘 I/O、直接内核启动（direct kernel boot）跳过 BIOS/UEFI、VMM 预初始化。"

### 来源 4: 腾讯云官方 (2026-04-21)
**"腾讯云开源OpenAI、Manus同款Agent底座"**
> "业内首个兼顾硬件级隔离与亚百毫秒启动的 AI Agent 执行环境底座。原生兼容 E2B 标准，冷启动 <60ms，单实例内存 <5MB，单机可运行 2000+ 沙箱。"

### 来源 5: SegmentFault (2026-05-29)
**"Cube Sandbox 替代 E2B：零代码迁移+性能碾压"**
> "所有基于 E2B 的 Agent 应用，优先迁移到 Cube Sandbox，兼顾体验、安全、成本。"

### 来源 6: HPCwire
**"Tencent Cloud Cube Sandbox Goes Fully Open Source"**
> 引用了腾讯云官方数据：CubeSandbox 的启动时间是"行业平均水平(150ms)的三分之一"。

### 来源 7: CNCF Landscape
CubeSandbox 已被收录到 **CNCF Landscape** 的 "AI-Native Infrastructure — Workload Runtime" 分类，标志着其作为 AI 基础设施的行业认可。

---

## 竞品对比

### 对比矩阵

| 维度 | CubeSandbox (腾讯云) | E2B (美国) | OpenSandbox (阿里) |
|------|-------------------|------------|-------------------|
| **开源协议** | Apache 2.0 | 闭源(仅 SDK 开源) | Apache 2.0 |
| **开源日期** | 2026-04 | N/A | 2026-04 |
| **底层技术** | KVM + RustVMM | Firecracker (KVM) | Docker / K8s |
| **隔离级别** | 硬件级 (独立内核) | 硬件级 (microVM) | 逻辑级 (共享内核) |
| **冷启动** | **<60ms** | ~150-200ms | 秒级 (池化~180ms) |
| **单实例内存** | **<5MB** | ~5MB | ~80MB (Docker) |
| **单节点密度** | **2000+** | N/A (云托管) | 受限于 Docker |
| **E2B 兼容** | ✅ Drop-in 级别 | ✅ 原生 | ⚠️ 部分兼容 |
| **多语言 SDK** | Python/Go | Python/JS-TS | Python/Java/JS/C# |
| **集群部署** | ✅ 一键集群 | 仅 SaaS | ✅ Helm Chart |
| **GPU 支持** | ❌ 上游不支持 | ❌ 不支持 | ❌ 不支持 |
| **网络隔离** | eBPF XDP 内核级 | microVM 隔离 | K8s NetworkPolicy |
| **快照/克隆** | ✅ CubeCoW (O(1)) | ✅ 模板快照 | ✅ 池化预热 |
| **Web 控制台** | ✅ React + i18n | ✅ E2B Cloud | ❌ |
| **CNCF 收录** | ✅ | ❌ | ❌ |
| **GitHub Stars** | ~6.8K | N/A | ~10K |

### 选择建议

```
你需要私有化部署吗？
├── 否 → E2B (最省心，云托管)
└── 是
    ├── 安全要求是否到「硬件级隔离」？
    │   ├── 是 → CubeSandbox ⬅️
    │   └── 否
    │       ├── 需要大规模批量交付(1000+沙箱)？→ OpenSandbox
    │       └── 需要多语言 SDK？→ OpenSandbox
```

**典型场景推荐：**

| 场景 | 推荐 | 理由 |
|------|------|------|
| AI 代码助手 (C 端) | **CubeSandbox** | 安全第一，60ms 不打断用户体验 |
| 企业内部 Agent 平台 | **CubeSandbox** | 自托管不落地开放给海外闭源 |
| 金融/政务 Agent | **CubeSandbox** | 硬件隔离满足等保 |
| 已有 E2B 项目迁移 | **CubeSandbox** | 零代码改动 |
| 多语言 SDK 需求 | OpenSandbox | Python/Java/JS/C# |
| 大规模 CI/CD | OpenSandbox | 池化 5000 沙箱 10 秒 |
| 海外无合规限制团队 | E2B | 省心 SaaS |

---

## 核心研判

### 优势

1. **极致的性能 + 极致的安全**：60ms 冷启动 + 硬件级隔离的组合在业内独一无二。Firecracker 方案 ~125ms，Docker 方案则无法提供硬件级隔离。CubeSandbox 同时占据了两端。

2. **E2B 兼容策略高明**：直接站在 E2B 的生态基础上，避免从头培养开发者习惯。这意味着 TensorOpera AI、Manus、OpenAI Agents SDK 等所有基于 E2B 的框架都可以无缝切换到 CubeSandbox。

3. **腾讯云大规模验证**：源自腾讯云内部生产环境，非实验室项目。已有腾讯云 SaaS 级验证背书。

4. **架构设计水平高**：六层组件职责清晰（API 网关 / 调度器 / 节点管理 / VMM / 网络 / 存储），控制面数据分离，全栈 Rust(关键路径) + Go(编排) 的语言分工合理。

5. **开源战略坚定**：Apache 2.0 协议，CNCF Landscape 收录，PR welcome，社区活跃。

### 风险

1. **KVM 依赖限制部署场景**：需要裸金属或启用了 KVM 嵌套虚拟化的云服务器。普通虚拟机（VPS）无法直接运行。虽然腾讯云提供了 PVM 方案作为退路，但这增加了部署复杂度。

2. **GPU 直通尚不支持**：Agent 推理需要在沙箱内进行 GPU 计算时，当前版本无法满足。gVisor/Daytona 等替代方案可能更适合。

3. **项目较新（2026-04 开源），外部生产案例有限**：目前只有腾讯云内部的大规模案例，外部社区的"生产级"部署案例较少。文档覆盖面不如 E2B 成熟。

4. **运维成本不可忽视**：自托管 microVM 集群需要内核管理、快照池调优、eBPF 策略维护、值班等持续投入。团队至少需要 1-2 人/周的初始配置时间。

5. **竞品追赶速度**：阿里的 OpenSandbox (10K stars) 发展迅速，如果其未来支持 KVM 运行时，竞争会更激烈。

### 适用场景

- **最适合**：构建 AI Agent (Code Agent) 产品的团队，需要在安全隔离环境中执行 LLM 生成的不可信代码
- **最适合**：强合规行业（金融/政务/医疗），数据不能出 VPC，需要自托管 + 硬件级隔离
- **适合**：已有 E2B 项目，希望降成本、控数据的企业
- **适合**：RL 训练、SWE-Bench 等需要大规模隔离执行环境的场景

### 趋势研判

1. **AI Agent 沙箱正在基础设施化**：就像 Docker 把容器化变成云原生标配，沙箱将是 Agent 时代的标配运行时。CubeSandbox 在这个赛道占据了有利位置。

2. **标准化竞赛已经开场**：到 2027 年，CNCF 或 Linux Foundation 大概率会推动 Agent 沙箱 API 标准化。谁先建立生态（类似 OCI 之于容器），谁就有话语权。CubeSandbox 的 E2B 兼容策略正是为此布局。

3. **GPU 直通是下一个战场**：当 Agent 需要在沙箱内做推理时，GPU 支持将成为差异化竞争力。预计 CubeSandbox 会在 v0.5+ 支持。

---

## 关键文件路径速查

### 核心组件

| 文件/目录 | 描述 |
|-----------|------|
| `CubeAPI/src/main.rs` | CubeAPI 入口 (Rust, Axum REST 网关) |
| `CubeAPI/src/handlers/sandboxes.rs` | 沙箱生命周期 API 处理器 |
| `CubeAPI/src/services/sandboxes.rs` (~49KB) | 沙箱服务核心逻辑 |
| `CubeAPI/src/handlers/agenthub.rs` (~145KB) | AgentHub 处理器 |
| `CubeMaster/cmd/cubemaster/app/main.go` | CubeMaster 主入口 |
| `CubeMaster/pkg/scheduler/` | 调度器核心逻辑 |
| `CubeMaster/pkg/service/sandbox/sandbox_run.go` | 沙箱运行创建 |
| `CubeMaster/pkg/service/httpservice/cube/snapshot.go` | 快照服务 HTTP 层 |
| `hypervisor/src/main.rs` (~62KB) | CubeHypervisor 主入口 |
| `hypervisor/vmm/src/lib.rs` (~97KB) | VMM 核心逻辑 |
| `hypervisor/vmm/src/vm.rs` (~117KB) | VM 生命周期管理 |
| `hypervisor/virtio-devices/src/` | virtio 设备实现 |
| `hypervisor/pci/src/vfio.rs` | VFIO 直通实现 |
| `hypervisor/vmm/src/memory_manager.rs` (~118KB) | 内存管理 |
| `hypervisor/vmm/src/cpu.rs` (~101KB) | vCPU 管理 |

### 网络与安全

| 文件/目录 | 描述 |
|-----------|------|
| `CubeEgress/lua/access_phase.lua` (~20KB) | eBPF 网络隔离接入策略 |
| `CubeEgress/lua/policy.lua` (~13KB) | 网络策略引擎 |
| `CubeEgress/lua/audit.lua` (~15KB) | 审计日志 |
| `CubeEgress/lua/cert_signer.lua` | 证书管理 |
| `network-agent/internal/service/local_service.go` (~38KB) | 网络服务核心 |

### SDK 与示例

| 文件/目录 | 描述 |
|-----------|------|
| `sdk/python/cubesandbox/sandbox.py` (~30KB) | Python SDK 沙箱类 |
| `sdk/python/cubesandbox/_template.py` (~16KB) | Python SDK 模板类 |
| `sdk/python/cubesandbox/_policy.py` (~13KB) | Python SDK 策略类 |
| `sdk/go/client.go` | Go SDK 核心 |
| `CubeAPI/examples/benchmark.py` (~31KB) | 性能基准测试脚本 |
| `openapi.yml` (~28KB) | OpenAPI 规范文档 |

### 部署与配置

| 文件/目录 | 描述 |
|-----------|------|
| `web/src/pages/AgentHub.tsx` (~96KB) | WebUI AgentHub 页面 |
| `web/src/pages/TemplateStore.tsx` (~25KB) | 模板商店页面 |
| `deploy/` | 部署脚本 |
| `.github/workflows/` | CI/CD 流水线 (build/release/test) |

### 文档

| 文件/目录 | 描述 |
|-----------|------|
| `docs/architecture/overview.md` | 架构总览 |
| `docs/guide/quickstart.md` | 快速开始 |
| `docs/changelog/` | 版本变更日志 |
| `docs/guide/security-proxy.md` | 安全代理指南 |
| `docs/guide/webui.md` | WebUI 使用指南 |
| `docs/blog/posts/2026-06-01-cubesandbox-perf-benchmark.md` | 性能基准报告 |

---

## 总结

CubeSandbox 是一个**技术深厚、定位精准、战略清晰**的 AI 基础设施项目。它不是 Docker 的替代品，而是专门为 AI Agent 代码执行场景设计的硬件级隔离沙箱。其 **60ms 冷启动 + 5MB 内存开销 + 硬件级隔离** 三合一的技术指标冠绝行业。

最大的战略亮点是 E2B SDK 兼容——这使 CubeSandbox 站在了现有生态的肩膀上，而不是另起炉灶。对于已经使用 E2B 的团队，迁移成本只是一个环境变量。对于正在选择沙箱方案的团队，CubeSandbox 提供了一个开源、自托管、高性能、高安全的选项。

**综合评分：★★★★☆ (4/5)**
- 技术实力：★★★★★
- 生态兼容：★★★★★
- 社区成熟度：★★★☆☆ (开源仅 2 个月)
- 运维友好度：★★★☆☆ (自托管仍需一定投入)
- 文档完整度：★★★★☆
