# 🔍 alibaba/open-code-review — 阿里出品"确定性工程 × Agent"混合架构的 AI 代码审查 CLI

> **仓库地址**: https://github.com/alibaba/open-code-review  
> **Stars**: 11,333 | **语言**: Go / TypeScript / JavaScript | **许可证**: Apache-2.0  
> **组织**: Alibaba Group  
> **抓取日期**: 2026-07-24（GitHub Trending 当日上榜）

---

## 一、项目定位（一句话）

OpenCodeReview 是阿里集团内部孵化的 **AI 代码审查 CLI**：读 Git diff，把变更文件交给带工具调用能力的 LLM Agent，产出**行级精准**的结构化审查评论；其最大差异点是用"确定性工程 + Agent"混合架构，在保证覆盖率与定位精度的同时把 token 消耗压到通用 Agent 的约 1/9。

---

## 二、项目亮点（差异化）

1. **确定性工程兜底硬约束** — 文件精准筛选、智能文件打包（相关文件成组、子 Agent 隔离上下文）、细粒度规则匹配、独立的位置/反思模块，全部由工程逻辑而非 LLM 保证，从根上消除"通用 Agent 漏审/位置漂移/质量不稳"三大痛点。
2. **同等模型下更高 Precision/F1、仅 1/9 token** — 在 50 个开源库 / 200 个真实 PR / 10 种语言、80+ 资深工程师交叉标注的 1,505 条真值基准上，比 Claude Code 同模型 Precision/F1 显著更高、速度快、token 仅约 1/9（Recall 略低是"重精度轻噪音"的刻意取舍）。
3. **源自阿里生产环境 2 年验证** — 内部已服务数万开发者、识别数百万缺陷，不是玩具项目。
4. **完整 Agent 生态位** — 既是独立 CLI（`ocr review` / `ocr scan`），也能以 Skill / Claude Code·Codex·Cursor 插件 / Delegation 模式 / MCP Server 嵌入你的编码 Agent。
5. **生产级工程配套** — Apache-2.0、OpenSSF Best Practices Silver、多语言文档（中/英/日/韩/俄）、CI/CD（GitHub/GitLab/Gerrit）、OpenTelemetry 遥测、Session Viewer 回放。

---

## 三、核心架构

核心哲学：**确定性工程做"绝不许错"的事，Agent 做"需要动态决策"的事。**

```
Git diff / 全量文件
   │
   ▼
[确定性层] 文件精准筛选 → 智能打包（相关文件成组，每组子Agent隔离上下文）
   │            ↓ 细粒度规则匹配（模板引擎，非自然语言）
   ▼
[Agent 层] 场景调优 Prompt + 蒸馏工具集（来自生产调用轨迹分析）
   │  ├─ 读取完整文件 / 搜索代码库 / 看其他变更文件取上下文
   │  └─ 产出结构化行级评论
   ▼
[确定性层] 外部定位模块（评论落点） + 反思模块（评论内容校验）
   ▼
结构化 Review 结果 → PR 评论 / CI 门禁 / Session Viewer
```

**几个关键工程决策**：
- **模板引擎规则匹配** vs 自然语言规则：前者在大规模上更稳定可预测，从源头消除信息噪声。
- **文件打包 + 子 Agent 隔离上下文**：分治策略，超大变更集上质量不塌。
- **内置精调规则集**（NPE / 线程安全 / XSS / SQL 注入）：把阿里生产经验固化成开箱即用的规则。

---

## 四、应用场景与启发

- **PR 自动审查门禁**：`ocr review --from main --to feature` 接 CI，在合并前拦缺陷。
- **陌生代码库审计**：`ocr scan --path internal/agent` 无 diff 也能整文件扫描，快速摸清陌生仓库风险点。
- **Delegation 模式**：让你的编码 Agent 用自己的 LLM 做审查，OCR 只负责文件筛选与规则解析，零额外 LLM 配置。
- **给 AI 工具构建者的启发**：
  1. **"确定性 × Agent"是比纯 Agent 更稳的范式**——凡是"漏审/漂移/不稳定"能被工程硬约束兜住的环节，就别交给 LLM。
  2. **用生产调用轨迹反推工具集**：OCR 的工具集来自对大规模生产 tool-call 的频率/重复率/链路影响分析，而不是拍脑袋设计。
  3. **刻意接受低 Recall 换高 Precision**：审查场景里"少错报"比"多报"更重要，这个取舍值得所有"AI 评审/审计"类工具抄。

---

## 五、源码深度解读

### 5.1 命令入口与编排（`cmd/opencodereview/main.go` + `review_cmd.go` / `scan_cmd.go`）
`main.go` 注册全套子命令；`review_cmd.go` 实现 diff 审查主流程，`scan_cmd.go` 实现整文件扫描。两者共享 `shared.go` 的编排逻辑，是确定性层（文件筛选/打包/规则）与 Agent 层（llm_cmd.go）的接合点。

### 5.2 配置与 Provider（`config_cmd.go` / `provider_cmd.go` + `provider_tui.go`）
交互式 TUI 引导选内置/自定义 Provider、选模型、自动连通性测试；`provider_tui.go` 用 bubbletea 类 TUI 实现，是 CLI 体验的关键。

### 5.3 跨平台进程与 Shell（`procattr_unix.go` / `procattr_windows.go` / `shell_unix.go` / `shell_windows.go`）
用 build-tag 分离的 Unix/Windows 进程属性与 shell 封装，保证 `ocr` 在三大平台行为一致——这是"生产级 CLI"和玩具脚本的分水岭。

### 5.4 编辑器/IDE 扩展（`bin/ocr.js`）
npm 全局安装的 `@alibaba-group/open-code-review` 包，把 `ocr` 能力暴露给 VS Code 等前端，是 CLI→GUI 的桥梁。

---

## 六、全网口碑

- **可信度强**：阿里官方出品、Apache-2.0、OpenSSF Silver、Trendshift 上榜、DeepWiki 自动文档、5 种语言文档——成熟度信号齐全。
- **基准有说服力**：自曝"Recall 低于通用 Agent"的诚实取舍 + 1,505 条人工真值基准，比单纯晒准确率更可信。
- **定位清晰**：不和通用编码 Agent 抢"写代码"，只做"审代码"这一件事并做到极致，社区反馈正面。

---

## 七、竞品对比 + 核心研判

### 竞品对比
| 维度 | OpenCodeReview | CodeRabbit | Greptile | Qodo(Codium) | Amazon CodeGuru | 通用 Agent(Claude Code+Skill) |
|------|:--------------:|:----------:|:--------:|:------------:|:---------------:|:-----------------------------:|
| 架构 | 确定性×Agent | Agent | Agent+RAG | Agent | 规则+ML | 纯 Agent |
| 行级精度 | ✅ 定位模块保证 | ✅ | ✅ | ✅ | ⚠️ | ❌ 易漂移 |
| Token 成本 | ✅ ~1/9 | 中 | 中 | 中 | 低 | ❌ 高 |
| 大变更集稳定 | ✅ 文件打包 | ⚠️ | ⚠️ | ⚠️ | — | ❌ 易漏 |
| 生态嵌入 | ✅ Skill/插件/MCP | ✅ PR Bot | ✅ | ✅ | ⚠️ AWS | ✅ |
| 开源 | ✅ Apache-2.0 | ❌ SaaS | ❌ SaaS | ❌ 部分 | ❌ | ✅ 但无专用审查约束 |
| 来源可信度 | ✅ 阿里生产 2 年 | 创业公司 | 创业公司 | 上市 | AWS | — |

### 核心研判
- **优势**：混合架构在"精度/稳定性/成本"三角上同时占优；阿里生产背书 + 完整开源 + 多形态嵌入，落地门槛低。
- **风险**：Recall 刻意偏低，可能漏掉非常规缺陷；重度依赖 LLM 质量（规则再强也救不了弱模型）；作为新开源项目，社区生态与第三方规则库仍待积累。
- **趋势**："AI 审查"正从 SaaS Bot 走向可自托管的 CLI/插件；"确定性约束 + Agent"会成为这类工具的标配范式。
- **启发**：做 AI 工具时，**先把能工程化硬约束的环节固化掉，再让 LLM 做动态决策**——这是 OCR 给所有 agentic 工具的最值钱一课。

---

## 八、关键文件速查

| 路径 | 作用 |
|------|------|
| `cmd/opencodereview/main.go` | CLI 入口与子命令注册 |
| `cmd/opencodereview/review_cmd.go` | diff 审查主流程 |
| `cmd/opencodereview/scan_cmd.go` | 整文件扫描 |
| `cmd/opencodereview/llm_cmd.go` | Agent/LLM 调用编排 |
| `cmd/opencodereview/config_cmd.go` / `provider_cmd.go` | Provider/模型交互配置 |
| `cmd/opencodereview/procattr_*.go` / `shell_*.go` | 跨平台进程与 shell 封装 |
| `bin/ocr.js` | npm 包 / 编辑器扩展入口 |
| `.claude/commands/open-code-review.md` | Claude Code 插件命令定义 |
