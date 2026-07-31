# bytebot-ai/bytebot 深度调研

> 调研日期：2026-08-01 ｜ Stars：11,069 ｜ 语言：TypeScript ｜ 协议：Apache-2.0 ｜ 状态：已归档（2025-09-12）
> 由 Tantl Labs 出品

## 一、项目定位

开源的"AI 桌面 Agent"——给 AI 一台**它自己的电脑**：一个完整的虚拟桌面（Ubuntu + XFCE + Firefox + VS Code），让 Agent 像人一样看屏幕、动鼠标、敲键盘，跨浏览器 / 邮件 / Office / IDE 完成多步任务。定位是"虚拟员工"，而非只跑在浏览器里的 RPA。

## 二、项目亮点

1. **拥有真实桌面环境**：区别于浏览器-only Agent，Bytebot 自带完整 Ubuntu 虚拟机（预装应用 + 持久文件系统），能登录网站（含 2FA，借助密码管理器）、下载整理文件、跨程序协作。
2. **四组件一体的自托管架构**：Virtual Desktop + AI Agent（NestJS）+ Task Web UI（Next.js）+ REST API，可 Docker 一键起、可 Helm 上 K8s。
3. **接管模式（Takeover）**：人类可随时切入控制桌面帮 Agent 配置或处理异常，再交还——解决"Agent 卡住"的实操痛点。
4. **多模型 + 密码管理器**：通过 LiteLLM 接 Anthropic/OpenAI/Gemini 及 100+ 提供商（含 Ollama 本地模型）；支持 1Password / Bitwarden 自动认证。
5. **编程可控**：提供 `/tasks` 创建任务、`/computer-use` 直控桌面（截图 / 点击坐标）的 REST 端点，方便把桌面 Agent 编入更大系统。

## 三、核心架构

```
┌─────────────── Virtual Desktop (Ubuntu 22.04 + XFCE) ───────────────┐
│  Firefox / VS Code / 邮件 / 密码管理器(1Password/Bitwarden)         │
└───────────────────────────┬───────────────────────────────────────┘
                              │ 屏幕/键鼠 (computer-use)
        ┌─────────────────────┼─────────────────────┐
   :9990 computer-use    :9991 tasks(REST)      :9992 Task Web UI(Next.js)
        │                     │                        │
        └──────── NestJS Agent 服务(编排 AI + 桌面动作) ┘
                   接 LiteLLM → Anthropic/OpenAI/Gemini/本地
```

三端口职责分离（9990 桌面控制 / 9991 任务 / 9992 UI）是典型的"控制面 / 任务面 / 展示面"解耦。

## 四、应用场景与启发

- **跨应用办公自动化**：批量下载各供应商发票并归类、跨银行导出流水合并、CRM↔ERP 记录同步等"需要真登录+多系统"的流程，是浏览器 Agent 够不到的场景。
- **给同类需求的思路**：
  - "给 Agent 一台虚拟机 + 接管模式"比纯 API 集成鲁棒——遇到非常规 UI 时人类可兜底，这是桌面 Agent 产品化的关键交互设计。
  - 三端口 + NestJS 微服务的拆分，让"桌面控制 / 任务调度 / 前端"可独立扩展，自研 computer-use 产品可照搬。

## 五、源码深度解读

> 路径来自仓库真实 `packages/bytebot-agent-cc/` 与 `packages/bytebot-agent/` 树。

### 1) Agent 核心服务（packages/bytebot-agent-cc/ 或 bytebot-agent/）

```
agent.computer-use.ts   # 屏幕观测 + 键鼠动作执行(对接桌面)
agent.processor.ts      # 把任务拆解成动作序列并驱动循环
agent.scheduler.ts      # 任务调度/排队(对应 :9991 tasks)
agent.tools.ts          # 工具集(截图/点击/打字/文件操作)
input-capture.service.ts# 输入捕获(键鼠事件回传)
tasks/  messages/        # 任务状态机 / 消息协议
```

NestJS 把"感知(computer-use)—决策(processor)—执行(tools)—调度(scheduler)"模块化，是桌面 Agent 后端的标准分层。

### 2) 接管与人工兜底

`input-capture.service.ts` 负责把人类接管时的输入注入桌面会话，使 Agent 循环可在"自动 / 手动"间无缝切换——这是它相比纯自主 Agent 更可用的工程细节。

## 六、社区口碑

- 概念受欢迎：11k Stars、Trendshift 收录、提供 Railway 一键部署与多语言文档，可见"AI 有自己的电脑"叙事有号召力。
- **重大风险信号：仓库已于 2025-09-12 归档（archived）**——不再活跃维护，新部署需自行 fork 承接。这是选型时最该注意的一点。
- 具体 Issue/Discussions 情感「数据不可用」（本轮未逐条抓取）。

## 七、竞品对比 + 核心研判

| 维度 | bytebot | trycua/cua | browser-use | 各类 RPA |
|------|---------|------------|-------------|----------|
| 运行环境 | 完整虚拟桌面(Ubuntu) | 桌面/云 sandbox | 仅浏览器 | 原生/模拟 |
| 跨应用 | 是(任意桌面程序) | 是(桌面+浏览器) | 否(网页) | 视实现 |
| 人工接管 | 是(Takeover) | 部分 | 否 | 是(人写脚本) |
| 维护状态 | 已归档(2025-09) | 活跃 | 活跃 | 各异 |
| 自托管 | 是(Docker/K8s) | 是 | 是 | 各异 |

**核心研判**：
- 优势：完整桌面 + 接管模式 + 三端口解耦，是"桌面 Computer-Use Agent"早期最完整的开源参考实现之一，架构值得学习。
- 风险：已归档是最致命项——安全更新、模型适配、bug 修复都将停滞；生产使用需做好 fork 自维护准备。
- 启发：桌面 Agent 的"虚拟机 + 接管兜底 + 控制/任务/UI 三端口"是可复用的产品范式；若想落地，建议直接基于活跃项目（如 trycua/cua）而非已归档的 bytebot。

## 八、关键文件路径速查

| 模块 | 路径 |
|------|------|
| 桌面控制 | `packages/bytebot-agent-cc/src/agent.computer-use.ts` |
| 任务处理 | `packages/bytebot-agent-cc/src/agent.processor.ts` |
| 任务调度 | `packages/bytebot-agent-cc/src/agent.scheduler.ts` |
| 工具集 | `packages/bytebot-agent-cc/src/agent.tools.ts` |
| 输入捕获/接管 | `packages/bytebot-agent-cc/src/input-capture.service.ts` |
| 状态/消息 | `packages/bytebot-agent-cc/src/tasks/` · `messages/` |
| 部署 | `docker/docker-compose.yml` · `helm/` |
| 文档 | `docs.bytebot.ai`（外部）· README（Quick Start / Architecture） |
