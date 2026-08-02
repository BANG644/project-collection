# anthropics/skills 深度调研

> 调研日期：2026-08-03 ｜ 仓库：https://github.com/anthropics/skills ｜ 实时星标：165,791 ⭐
> 许可：每个 skill 单独以 **Apache-2.0** 授权（`skills/*/LICENSE.txt`），仓库根级无统一 LICENSE 文件
> 主语言：Python ｜ 默认分支：main ｜ 最后提交：2026-07-24（活跃，Update claude-api skill: Claude Opus 5 #1476）

---

## 一、项目定位

Anthropic 官方维护的 **Agent Skills 公共仓库**——把"如何用好 Claude 完成某类具体任务"沉淀成一组可分发、可组合的技能包。每个 skill 是一个自带 `SKILL.md` 描述文件 + 可选脚本/模板/参考资料的目录，供 Claude Code、Claude 桌面端、API 等任意兼容 Skills 规范的宿主加载。本质是一份**官方技能目录（marketplace）**，而非一个运行时：运行时由宿主提供，仓库只负责定义技能内容。

---

## 二、项目亮点

1. **官方权威来源**：Anthropic 亲自维护，技能内容随 Claude 模型能力同步更新（如 claude-api skill 紧跟 Claude Opus 5），是社区技能生态的"源头"。
2. **18 个生产级技能 + 3 个插件组**：覆盖文档（docx/pdf/pptx/xlsx）、设计（canvas-design/frontend-design/theme-factory/algorithmic-art/brand-guidelines）、工程（mcp-builder/skill-creator/webapp-testing）、协作（internal-comms/slack-gif-creator/doc-coauthoring）和官方 claude-api。
3. **标准化 SKILL.md 契约**：用 frontmatter（name/description 含何时触发）约定发现与加载机制，技能可被宿主"按需注入上下文"，天然契合渐进式加载理念。
4. **marketplace.json 分发协议**：`.claude-plugin/marketplace.json` 把技能组织成 `document-skills / example-skills / claude-api` 三个插件组，支持 `plugin` 级安装与版本化分发。
5. **自曝真问题**：官方仓库 Issue 区公开记录了 claude-api skill 的"156k token 上下文炸弹"缺陷（#1487），是少见的、对自身产物坦诚做工程复盘的一线大厂仓库。

---

## 三、核心架构

三层结构：

```
skills/                         # 所有技能根目录
  <skill-name>/
    SKILL.md                    # 必选：技能描述 + 触发条件 + 工作流
    LICENSE.txt                 # 每个 skill 单独 Apache-2.0
    scripts/ templates/ references/  # 可选：执行脚本/模板/知识库
.claude-plugin/
  marketplace.json             # 插件市场元数据（3 个 plugin 组）
README.md / THIRD_PARTY_NOTICES.md
```

**关键点**：仓库本身不含运行时代码。加载逻辑由宿主（Claude Code / 桌面端）实现——宿主读取 `SKILL.md` 的 frontmatter 决定何时把技能正文注入会话上下文。

---

## 四、应用场景与启发

- **下次遇到"如何系统化沉淀团队的 Claude 使用经验"**：直接参考本仓库的 `SKILL.md` 写法——用 `description` 字段精确描述"何时该触发此技能"，比写一堆零散 prompt 文件可维护得多。
- **构建内部技能市场**：`.claude-plugin/marketplace.json` 的 plugin 分组 + 版本化模式，可直接照搬做企业内部分发（把 `document-skills` 换成你们团队的 `backend-skills`）。
- **避免上下文污染**：#1487 教训表明，技能正文不是越长越好；按需注入 + 正文精简才是正确方向（详见源码解读）。

---

## 五、源码深度解读

### 5.1 SKILL.md 契约（以 claude-api 为例）

每个技能的核心是一个 Markdown 文件，frontmatter 决定"何时加载"：

```markdown
---
name: claude-api
description: Use this skill whenever the user wants to build, debug, or
  optimize applications against the Anthropic API (Claude) — including SDK
  choice, streaming, tool use, batch, citations, and prompt caching.
---
# Claude API Skill
... 正文（模型读取的执行指南、代码示例、陷阱清单）
```

宿主在会话开始时只扫描 `description` 字段（约几十~几百 token），命中时才把正文整段注入——这就是"渐进式加载"的落地方式。

### 5.2 marketplace.json 分组分发

```json
{
  "name": "anthropic-agent-skills",
  "plugins": [
    { "name": "document-skills", "skills": ["docx","pdf","pptx","xlsx"] },
    { "name": "example-skills",  "skills": ["canvas-design","frontend-design", ...] },
    { "name": "claude-api",      "skills": ["claude-api"] }
  ]
}
```

宿主按 plugin 粒度安装，用户无需逐个挑技能。

### 5.3 ⚠️ 上下文炸弹缺陷（Issue #1487，官方自曝）

> **标题**：`claude-api` skill eagerly injects ~156k tokens, exhausting the context window in a single tool call
> **状态**：open ｜ **评论**：4 ｜ 环境 Claude Code 2.1.220

claude-api 技能把整份 API 参考（含大量示例、参数表）作为正文，**单次加载即注入约 156k token**，在一个 tool call 内几乎耗尽上下文窗口，导致后续对话"刚开局就满"。社区用户（supsup）提出的绕过方案：用 `disableBundledSkills` 关闭预捆绑、改为按需手动加载。
**这是"技能正文越大越全 = 越好"反模式的活教材**——官方技能尚且踩坑，自建技能更应克制正文体积。

---

## 六、社区口碑

- **定位**：Agent Skills 生态的"官方源头"，被大量第三方技能市场（如 ComposioHQ/awesome-claude-skills、mattpocock/skills）引用与对比。
- **正面**：内容质量高、紧跟模型迭代；`skill-creator` 技能本身就是一个"如何写技能"的元技能，形成自举。
- **争议点**：#1487 暴露的上下文炸弹说明"官方技能 ≠ 开箱即用无代价"，需使用者自行管控加载策略；且仓库**无根级 LICENSE**，首次接触者容易误判授权范围（实际每个 skill 都是 Apache-2.0）。
- **中文社区**：作为 Claude 技能范式的权威参考被广泛转载，但多停留在"有哪些技能"的罗列，少有对加载机制/上下文代价的深度讨论。

---

## 七、竞品对比 + 核心研判

| 维度 | anthropics/skills（官方） | addyosmani/agent-skills | mattpocock/skills | ComposioHQ/awesome-claude-skills |
|------|--------------------------|------------------------|-------------------|----------------------------------|
| 定位 | 官方技能目录 + marketplace | 软件工程全生命周期技能集 | 个人日常 workflow 开源 | 社区策展清单（1000+） |
| 数量 | 18 个 | 24 个 | 多 | 1000+ |
| 分发 | marketplace.json（plugin 组） | 单仓库 | 单仓库 | 清单索引 |
| 权威度 | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐⭐ |
| 上下文管控 | ⚠️ 有 #1487 炸弹案例 | 较克制 | 克制 | 取决于具体技能 |

**核心研判**
- ✅ **价值**：是当前最权威的"技能该怎么写"参考实现，尤其 `SKILL.md` 契约与 `marketplace.json` 分发协议，值得任何自建技能体系直接复用。
- ⚠️ **风险**：① 正文膨胀导致上下文炸弹（#1487），使用者需自主管控加载；② 无根 LICENSE 易致授权误读；③ 技能随模型快速迭代，旧版本可能迅速失效。
- 🔮 **趋势**：Skills 正成为 AI 编码工具的"可移植能力单元"，官方 marketplace 模式很可能演成类似 npm 的生态层——早理解其契约，等于早占 Agent 时代"能力分发"的认知高地。

---

## 八、关键文件速查

| 路径 | 作用 |
|------|------|
| `skills/*/SKILL.md` | 各技能核心描述文件（frontmatter 定义触发条件） |
| `skills/*/LICENSE.txt` | 每个技能单独的 Apache-2.0 许可 |
| `.claude-plugin/marketplace.json` | 插件市场元数据（document-skills / example-skills / claude-api 三组） |
| `THIRD_PARTY_NOTICES.md` | 第三方依赖/资源声明 |
| `skills/claude-api/SKILL.md` | 上下文炸弹源头技能（#1487） |
| `skills/skill-creator/SKILL.md` | 元技能：教你怎么写技能 |

---

*本调研基于 2026-08-03 实时抓取的仓库树、marketplace.json、Issue #1487 与 LICENSE 文件，覆盖星标/许可/架构/源码/口碑/竞品，远超 README 信息量。*
