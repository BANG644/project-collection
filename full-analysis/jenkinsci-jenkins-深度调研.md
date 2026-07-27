# 🔬 Jenkins 深度调研

> **仓库地址**: https://github.com/jenkinsci/jenkins
> **Stars**: 25,855 ⭐ | **语言**: Java | **许可证**: MIT | **创建**: 2010-11-22
> **主页**: https://www.jenkins.io | **定位**: 领先的开源自动化服务器（CI/CD）

---

## 一、项目定位

Jenkins 是 **Java 编写的领先开源自动化服务器**，通过 2,000+ 插件把"构建 / 测试 / 静态分析 / 部署"几乎任何重复任务自动化，让人类专注机器做不了的事。

---

## 二、项目亮点（差异化）

- 🔌 **插件即一切**：2,000+ 官方插件构成生态护城河，从 SCM 到云平台到通知全覆盖
- 🧱 **ExtensionPoint 架构**：核心极薄，能力几乎都通过插件扩展点注入，可热插拔
- 📜 **Pipeline as Code**：`Jenkinsfile`（Groovy DSL）把流水线纳入版本控制，可复现
- 📦 **多形态分发**：WAR / Docker / 原生包 / 安装器，双发布线（Weekly + LTS）
- 🏛️ **治理成熟**：开源社区治理、CII 最佳实践徽章、可复现构建（Reproducible Builds）

---

## 三、核心架构

```
Jenkins WAR (Jetty 内嵌 servlet 容器)
   │
   ├─ Stapler ：URL ↔ Java 对象 自动绑定（Web 层）
   ├─ Plugin Manager ：加载 ./plugins/*.jpi，扫描 @Extension
   ├─ ExtensionList ：核心与插件通过 ExtensionPoint 互相注入
   ├─ Job / Build 模型 ：自由风格 / Maven / 流水线
   └─ Agent (原 Slave) ：分布式构建节点，通过 remoting/JNLP 通信
```

**三大支柱**：① **Stapler** 把 HTTP URL 映射到对象树，写 Web 功能无需手动路由；② **Plugin + ExtensionPoint**：插件打 `META-INF/MANIFEST.MF` 声明，启动时由 `PluginManager` 加载，并用 `@Extension` 注册到各 `ExtensionPoint`；③ **Pipeline**：`Jenkinsfile` 经 Groovy 引擎编译成可持久化的执行图（Workflow）。`bom/`（Bill of Materials）统一管理插件依赖版本，是大型 Jenkins 部署的锁版本关键。

---

## 四、应用场景与启发

| 场景 | 适配度 |
|------|--------|
| 传统 Java/Maven 企业 CI | ⭐⭐⭐⭐⭐ |
| 多技术栈单体 CI 服务器 | ⭐⭐⭐⭐ |
| 云原生/K8s 原生流水线 | ⭐⭐⭐（需 plugin，不如原生方案）|
| 小型项目快速 CI | ⚠️ 偏重，启动/维护成本高 |

> **架构启发**：「核心极薄 + ExtensionPoint 插件化」是超长寿命系统的经典设计——Jenkins 能撑 15 年靠的就是任何能力都能外置为插件而不动核心。做平台型产品时，先定义好扩展点比先堆功能更重要。

---

## 五、源码解读（核心模块）

**1. 插件加载 — `core/src/main/java/hudson/PluginManager.java`**
启动时扫描 `WEB-INF/lib/*.jpi`，用 `pluginFirstClassLoader` 隔离加载，调用插件 `setUp()` 并收集所有 `@Extension` 注解类注册进全局 `ExtensionList`。

**2. Web 层 — Stapler（`stapler` 模块）**
约定优于配置：请求 `/job/foo/` 自动路由到 `Jenkins.getInstance().getJob("foo")` 对象并调用其 `doXxx`/`getXxx`。这是 Jenkins 能用极少代码堆出庞大 Web 功能的原因。

**3. 流水线 — `workflow-*` / `Jenkinsfile`**
`Jenkinsfile` 经 `groovy` 编译成 `CpsFlowDefinition`，由 `workflow-cps` 以 CPS 变换持久化每一步，使流水线可在 Agent 重启后从 checkpoint 续跑。

---

## 六、社区口碑

- **历史地位稳固**：CI/CD 鼻祖级项目，被成千上万企业采用，文档/插件生态无可匹敌
- **口碑分化**：老用户爱其插件万能；新团队吐槽 Java 沉重、Groovy 脚本安全（Script Security 沙箱常被绕过）、插件质量参差、UI 老旧
- **维护健康**：LTS 双线发布、可复现构建、CII 徽章，治理透明度高

---

## 七、竞品对比 + 核心研判

| 项目 | 形态 | 配置 | 适用 |
|------|------|------|------|
| **Jenkins** | 自托管服务 | Groovy/Jenkinsfile | 通用、插件万能 |
| **GitHub Actions** | SaaS/自托管 | YAML | GitHub 生态无缝 |
| **GitLab CI** | 一体化平台 | YAML | GitLab 全家桶 |
| **CircleCI / Travis** | SaaS | YAML | 快速上手 |
| **Argo CD / Tekton** | K8s 原生 | YAML/CRD | 云原生 GitOps |

**核心研判**：
- ✅ **优势**：插件生态无可替代、自托管可控、Pipeline as Code 成熟、企业治理完善
- ⚠️ **风险**：Java 单体 + 插件 sprawl 带来维护与安全风险；云原生/K8s 原生场景被 Argo/Tekton 抢份额；Groovy 沙箱逃逸历史漏洞
- 💡 **启发**：新项目若已深度绑定 GitHub/GitLab，直接用其原生 CI 更轻；只有"多 SCM、多技术栈、需高度定制"的历史基建才值得上 Jenkins。其 ExtensionPoint 架构仍是最值得抄的"长寿平台"范本

---

## 八、关键文件路径速查

| 路径 | 内容 |
|------|------|
| `core/` | Jenkins 核心（Stapler / PluginManager / Job 模型）|
| `war/` | Web 应用打包（Jetty 内嵌）|
| `cli/` | 命令行客户端 |
| `bom/` | Bill of Materials（插件版本锁）|
| `pom.xml` | Maven 多模块构建根 |
| `Jenkinsfile` | 自身 CI 流水线 |
| `docs/` | 维护者指南 / 开发者文档 |
