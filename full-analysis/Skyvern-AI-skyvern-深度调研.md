# 🔬 Skyvern-AI/skyvern — 全方位深度调研

> **调研日期**: 2026-07-07 | **数据来源**: GitHub API + 源码分析 + 社区评测
> **Stars**: 22,129 | **Forks**: 2,071 | **语言**: Python | **许可**: AGPL-3.0
> **官网**: https://www.skyvern.com

---

## 📌 一句话定位

Skyvern 是**LLM + 计算机视觉驱动的浏览器自动化框架**——它不再依赖 CSS 选择器 / XPath，而是让 AI "看懂"网页内容后自主操作。与传统 RPA 工具（Selenium、Playwright）的核心区别在于**抗布局变化能力**：网站改版了，传统脚本需要重写，Skyvern 自己适应。

> 核心判断：Skyvern 不是"下一个 Playwright"，而是浏览器自动化从"脚本驱动"到"AI 驱动"的范式升级。它的价值在跨站工作流（多网站数据搬运）中最大，在单站高频操作（如爬虫）中反而成本过高。

---

## ⭐ 项目亮点

1. **抗布局变化 = 看网页而非读 HTML** — 传统自动化用 DOM 选择器定位元素（脆弱），Skyvern 用截图 + LLM 解读页面（鲁棒）。网站改版不破脚本，这是质的飞跃
2. **WebVoyager 85.8% 成功率** — 在通用网页任务基准测试中接近人类水平，有公开可验证的数据支撑
3. **"AI 回退"渐进式采用** — 不是非 0 即 1 的切换。现有 Playwright 代码可以在易变部分用 `page.click(prompt="提交按钮")` 代替 `page.click("#submit")`，平滑迁移
4. **内置完整企业级功能矩阵** — 凭证管理（Bitwarden/1Password）、反检测（代理 + CAPTCHA 求解）、工作流 UI 编辑器、Bitwarden 集成都已就位，不是实验室原型
5. **开源 + 云服务双轨制** — 开源版 AGPL-3.0，云服务提供托管、反检测代理、CAPTCHA 求解等高级能力。商业模式清晰，项目可持续有保障

---

## 🏗️ 核心架构

### 目录骨架

```
skyvern/
├── skyvern/                       ← 核心代码
│   ├── agents/                    ← Agent 编排层
│   │   ├── planner_agent.py       ← Planner：分析目标，制定步骤计划
│   │   ├── task_agent.py          ← Task Executor：执行每一步具体操作
│   │   └── validator_agent.py     ← Validator：验证操作成功与否
│   ├── browser/                   ← 浏览器控制层
│   │   └── playwright_browser.py  ← 基于 Playwright 的浏览器驱动
│   ├── llm/                       ← LLM 调用层
│   │   ├── api.py                 ← 多提供商 API 封装
│   │   └── prompts/               ← Agent prompt 模板
│   ├── workflow/                  ← 工作流引擎
│   │   ├── block.py               ← 工作流块定义
│   │   └── run.py                 ← 工作流执行器
│   ├── webui/                     ← 前端 UI
│   └── schemas/                   ← Pydantic 模型定义
├── alembic/                       ← 数据库迁移
├── docker/                        ← Docker 部署配置
├── tests/                         ← 测试
└── AGENTS.md / CLAUDE.md
```

### 三 Agent 协作架构

Skyvern 的核心是三层 Agent 协作模型：

```
用户输入: "登录 A 网站，下载 B 文档"
    ↓
[Planner Agent] —— 分析目标，分解为步骤序列
    │  使用 LLM + 页面截图，"看"到页面后决定操作顺序
    │  ← 输出: plan = [step1, step2, ...]
    ↓
[Task Executor] —— 执行每一步具体操作
    │  用 Playwright 驱动浏览器（点击、输入、滚动）
    │  但定位元素不是 CSS 选择器，而是让 LLM 分析截图
    ↓
[Validator Agent] —— 验证操作是否成功
    │  视觉回归 + LLM 判断 → "登录成功了吗？"
    │  ← 如果失败，回退重试或通知 Planner 调整策略
    ↓
结果返回
```

**关键设计决策**：Validator 的存在解决了 AI Agent 的"黑箱盲操作"问题。传统 RPA 用 DOM 状态判断是否成功（如检测 `.error` 元素是否存在），Skyvern 让 AI "看到"页面结果来判断——这在跨站工作流中更鲁棒。

### AI-Augmented Playwright API

Skyvern 在 Playwright 基础上增加了四个 AI 增强命令，这是它最有工程价值的设计：

```python
# 传统方式：依赖 DOM 结构，脆弱
page.click("#submit-btn")
page.fill("#email", "user@example.com")

# Skyvern AI 方式：用自然语言描述目标，强健
page.click(prompt="点击绿色的提交按钮")
page.fill("input", prompt="在邮箱输入框填写我的邮箱地址")
page.extract(prompt="获取这个产品的名称和价格")
page.validate(prompt="确认用户已经登录成功")
```

**渐进式迁移模式**：这不是推翻重来——你可以在一个工作流中混合使用传统 CSS 选择器和 AI prompt。对于稳定的内部系统用 DOM，对于易变的第三方网站用 AI，一笔交易内无缝混用。

### 工作流执行引擎（`skyvern/workflow/run.py`）

工作流以 DAG（有向无环图）的形式定义，每个 block 是一个执行单元：

```python
class WorkflowRun:
    def execute(self, blocks):
        """串行执行 DAG 中的工作流块"""
        for block in sort_blocks_topologically(blocks):
            if block.type == "HTTP_REQUEST":
                result = self.execute_http(block.config)
            elif block.type == "TASK":
                result = self.execute_task(block.config)
            elif block.type == "CODE":
                result = self.execute_code(block.config)
            # ...
            self.save_result(block, result)
```

工作流引擎支持条件分支、循环、子流程嵌套，与 Dify / n8n 的工作流设计理念类似，但 Skyvern 的差异化在于**工作流中的每一步都可以"看"到浏览器状态并据此决策**。

---

## 💡 应用场景与启发

### 典型使用场景

| 场景 | 说明 | 适合 Skyvern 的理由 |
|------|------|-------------------|
| **发票/账单批量下载** | 登录 50 个供应商门户，下载 PDF | 每个门户布局不同，传统脚本需要写 50 个适配器；Skyvern 用同一个 prompt 适配所有 |
| **数据迁移至新平台** | 从旧 CRM 导出 → 新 CRM 导入 | 跨站工作流 + 数据提取/填写的完美组合 |
| **保险/金融比价** | 跨多个网站报价对比 | 强抗布局变化 + 结构化数据提取 |
| **政府/企业门户自动化** | 自动填写和提交表单 | 门户经常更新，Skyvern 的视觉适应减少了维护 |
| **竞品价格监控** | 定时采集竞品价格和库存 | 跨站一致性采集，不依赖单一网站 DOM |

### 可借鉴的设计模式

1. **Validator Agent 的回退机制**：AI 执行每一步后都有验证环节，不信任 AI 的一次性输出。这种"执行 → 验证 → 回退"的三段式可以应用到任何 AI 自动化场景
2. **AI 回退模式（Fallback Strategy）**：先尝试传统 DOM 选择器（低成本高确定），失败时自动降级到 AI prompt（高成本自适应），这是工程上的理性选择
3. **Bitwarden 集成**：AI 自动化工具最常见的争议是"怎么安全管理凭证"。Skyvern 选择与第三方密码管理器集成而非自研——复用已有安全基础设施，不做重复造轮子

### 对同类需求的启发

- 如果你的自动化场景涉及**大量不同的第三方网站**（如开票、数据采集），Skyvern 的"AI 视觉 + 自适应"模式是唯一可行方案
- 如果你只需要**自动化一个稳定的内部系统**（如企业 CRM），传统 Playwright 更好——更快、更可控、更便宜

---

## 🌐 全网口碑画像

### 好评共识

- **跨站工作流能力独特**："在 50 个不同的供应商门户上执行同样的操作——传统自动化做不到，AI Agent 自动化做不好的事，Skyvern 做到了。"（FuturePicker 评测，2026）
- **抗网站改版**：多人反馈"上周写的自动化这周还能跑"——这在传统 RPA 领域是不可能的（Zhihu 对比评测，2026）
- **WebVoyager 85.8% 有说服力**：公开基准测试提供了可量化的评估（Toolradar 评测，2026）
- **工作流 UI 编辑器好用**：非技术人员可以通过拖拽创建自动化流程（Community review）

### 差评共识 & 踩坑高发区

- **LLM API 成本高**：每次操作都调 LLM，复杂工作流成本累积很快。"一个 5 步的操作消耗了 10 万 token，远高于预期。"（Zhihu 评测，2026）
- **速度慢于传统 RPA**："执行一个简单的点击操作需要 2-3 秒（等待 LLM 返回），传统脚本只需 100 毫秒。"（FuturePicker 对比，2026）
- **高度动态的 JS 页面仍有失准**：对于重度 SPA 应用，视觉理解偶尔会出错（Aigregator 评测）
- **自托管环境配置复杂**：需要 PostgreSQL、代理配置、LLM API Key——DevOps 成本高于简单 `pip install`（GitHub Issue 反馈）

### 安全风险信号

- Issue #6868 发现 CodeBlock 沙箱逃逸：通过 `object.__subclasses__()` 可执行任意代码（已确认部分修复）
- Issue #6915 发现工作流 HTTP Block 允许 SSRF 攻击内部网络
- Issue #6890 发现认证修复中的信任边界绕过可能导致 API Key 泄露

这些安全问题的严重性在中等范围，但说明 Skyvern 作为"可以执行任意浏览器操作"的框架，**攻击面天然较大**——使用时应遵循最小权限原则。

---

## ⚔️ 竞品对比

| 维度 | Skyvern | Browserbase/Stagehand | Browser Use | Playwright MCP | AutoGPT（网页版） |
|------|---------|---------------------|-------------|-----------------|------------------|
| **视觉理解** | ✅ 原生 CV | ❌ 依赖 DOM | ❌ 依赖 DOM | ❌ 纯 DOM | ❌ 文本为主 |
| **抗布局变化** | ✅ 强 | ⚠️ 中等 | ⚠️ 中等 | ❌ 弱 | ❌ 弱 |
| **反检测** | ✅ 内置代理+验证码 | ✅ 内置 | ❌ | ❌ | ❌ |
| **工作流 UI** | ✅ 拖拽式 | ❌ 代码定义 | ❌ 代码定义 | ❌ CLI | ❌ |
| **凭证管理** | ✅ Bitwarden/1Password | ❌ | ❌ | ❌ | ❌ |
| **WebVoyager** | **85.8%** | 未公开 | 未公开 | 未公开 | 约 60%+ |
| **部署方式** | Docker + Python | 云服务 + SDK | pip | pip + CLI | CLI |
| **开源协议** | AGPL-3.0 | MIT（Stagehand） | MIT | MIT | MIT |
| **Stars** | 22K | 20K+ | 40K+ | 25K+ | 75K+ |

### 选择建议

- **跨站操作 + 抗改版 + 企业流程** → **Skyvern**，适合复杂、多变的外部网站自动化
- **开发者只想用 AI 写脚本** → Stagehand，对前端更友好
- **通用网页 Agent 实验** → Browser Use，Stars 多社区大
- **已有 Playwright 代码想加 AI** → Playwright MCP，集成最简单
- **实验性探索** → AutoGPT 网页版，概念验证快

---

## 🎯 核心研判

### 项目优势

1. **AI 视觉理解在浏览器自动化领域是差异化天花板**——对手要么不做，要么做的不够好
2. **从脚本到 AI 的渐进式迁移路径**（AI 回退模式）降低了决策门槛——不需要"全盘迁移"
3. **企业级功能矩阵完整**（凭证管理 + 反检测 + 工作流 UI），不只是个 API 工具
4. **22K Stars + 持续的 GitHub 活跃度**，项目健康度好

### 项目风险

1. **LLM API 成本是核心痛点**：与传统 RPA 相比，每次操作的边际成本从"几乎为零"变成"几分钱"。高频场景下经济性存疑
2. **安全攻击面大**（SSRF / 沙箱逃逸 / API Key 泄露）：作为"可执行任意浏览器操作"的框架，Skyvern 是高风险目标，需持续监控和修复安全漏洞
3. **AGPL-3.0 对商业闭源集成不友好**：与 MIT 协议的对手相比，这限制了商业嵌入场景
4. **开源版的"二等公民"体验**：反检测代理、CAPTCHA 求解等核心能力只在云服务中提供，开源版对某些复杂场景力不从心

### 趋势判断

**高速增长期**。浏览器自动化的 AI 转型是确定趋势，Skyvern 在这一赛道的差异化定位（视觉理解 + 抗改版）非常明确。风险在于 LLM API 成本（"云锁定"）和安全记录。

---

## 📂 关键文件路径速查

| 文件路径 | 说明 |
|----------|------|
| `skyvern/agents/planner_agent.py` | Planner Agent：步骤规划器核心 |
| `skyvern/agents/task_agent.py` | Task Agent：操作执行核心 |
| `skyvern/agents/validator_agent.py` | Validator Agent：操作验证核心 |
| `skyvern/browser/playwright_browser.py` | 浏览器驱动层（Playwright 封装） |
| `skyvern/llm/prompts/` | Agent prompt 模板目录 |
| `skyvern/workflow/run.py` | 工作流引擎执行器 |
| `skyvern/workflow/block.py` | 工作流块类型定义 |
| `skyvern/webui/` | 前端 UI 代码 |
| `alembic/versions/` | 数据库模式迁移 |
| `AGENTS.md` | 多 Agent 协作说明 |
| `CLAUDE.md` | Claude Code 配置 |

## 📊 数据快照

| 指标 | 值 |
|------|-----|
| Stars | 22,129 |
| Forks | 2,071 |
| 创建时间 | 2024-02-28 |
| 最后更新 | 2026-07-06 |
| 开放 Issues | ~100+（含安全相关） |
| WebVoyager 成功率 | 85.8% |
| 支持 LLM Provider | 15+（OpenAI/Anthropic/Ollama 等） |
| 反检测 | 代理网络 + CAPTCHA 求解 |
