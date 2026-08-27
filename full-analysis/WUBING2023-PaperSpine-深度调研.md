# 📊 PaperSpine 深度调研报告（修复增强版）

> **仓库**: [WUBING2023/PaperSpine](https://github.com/WUBING2023/PaperSpine)
> **Stars**: 5,002 ⭐（2026-08-28 复核，原调研时 2,700） | **Forks**: 196 | **语言**: Python | **License**: MIT
> **创建时间**: 2026-05-17 | **最后推送**: 2026-08-26（活跃） | **订阅者**: 11
> **修复说明**: 本版补齐「项目亮点 / 应用场景与启发 / 源码深度解读 / 竞品对比」四个缺失维度，并刷新社区数据（星标翻倍至 5k+、维护恢复活跃）。

---

## 一、项目定位

PaperSpine 是一个面向 Codex、Claude Code 和 OpenClaw 三大编码 Agent 的**论文与报告写作 skill suite**。其核心理念是 **"以 motivation 为主线、以 contribution 为最高组织单元"**：要求 Agent 在写作前先学习目标场景和优秀样例，再记录每一个写作单元为什么这样规划或修改，而不是简单的"帮我润色"。

---

## 二、项目亮点（差异化）

1. **反"补丁式润色"**：明确自我定位为 *research-writing workflow, not a prose patcher*——先研究场景、强制定稿 motivation，再逐行设计论文，最后才动笔。
2. **Contribution-First / Reviewer-Aware 关卡体系（V4）**：引入 `confirmed_contribution.md`、`results_validation.md`、`reviewer_audit.md` 三道硬关卡，配 `contribution_check.py` 等脚本做自动 gate，未通过不得宣告完成。这是它与普通"写作助手"最本质的区别。
3. **三宿主统一分发**：同一套 Skill 通过安装脚本自动适配 Codex（`$paper-spine`）、Claude Code（`/paperspine`）、OpenClaw（`paper-spine`），避免多版本维护。
4. **claim → citation → evidence 引用矩阵**：写作前先建立论点—引用映射，保证每个 claim 有据可依，而非事后补参考文献。
5. **中文母语级体验**：`ui_language=zh` 时全程中文沟通（含中间进度、错误提示），不夹杂英文状态句。

---

## 三、核心架构

### 仓库结构

```
PaperSpine/
├── dist/                     # 真正用于安装的内容
│   ├── codex/skills/         # Codex 扁平 skill suite
│   ├── claude/skills/        # Claude Code 扁平 skill suite（主入口 paper-spine）
│   └── openclaw/skills/      # OpenClaw 扁平 skill suite
├── src/                      # 共享脚本和参考文档
│   ├── scripts/              # 确定性辅助脚本（安装、更新、引用索引）
│   ├── references/           # 共享工作流参考文档（playbook 集合）
│   └── agents/              # Agent 元数据源
├── atlas/                    # 星标可视化（fetch_stargazers.py 等）
├── .claude-plugin/           # Claude Code 插件元数据
└── install.sh / install.ps1  # 跨平台安装
```

### 设计决策

1. **逐阶段路由**：主控 skill `paper-spine` 本身不直接改句子，而是按阶段读取 `references/` 下的 playbook（intake→research→citation→rewrite→build→latex→audit…）。
2. **三宿主兼容**：通过安装脚本抹平三个 Agent 的命名空间/调用差异。
3. **本地优先参考文献**：`reference_mode` 支持 `local_first` / `specified_paths` / `web` 三种模式，默认先索引本地文件再网络补充，降低 API 调用。

### 两类主线 × 四种场景 × 两级深度

| 维度 | 取值 |
|------|------|
| 工作流 | `rewrite_existing`（改已有稿）/ `build_from_materials`（从素材构筑） |
| 场景 | `journal` / `conference` / `report_review` / `competition` |
| 研究深度 | `flash`（3 样例+3 同域论文）/ `pro`（6+6） |

---

## 四、应用场景与启发

**可用场景**
- 学术写作（期刊 / 会议 / 课程报告 / 综述 / 竞赛论文）——尤其适合"论证深度"优先于"字数达标"的作者。
- 已有初稿的系统性重写（rewrite 主线），或从一堆 PDF/数据/图片素材构筑成稿（build 主线）。
- 需要**审稿人视角自检**的投稿前打磨（`reviewer_audit.md` 生成 objection register）。

**给同类需求的启发**
- **"把关卡（gate）前置进写作流"** 是工程化写作 Agent 的关键范式：PaperSpine 用 `contribution_check.py` 等把"贡献是否明确""结果是否验证贡献""审稿人能否买账"变成可机器校验的硬门槛，比单纯 prompt 约束可靠得多。
- **playbook 目录即知识库**：把每个阶段的方法论沉淀为独立 markdown，Agent 按需读取，比塞进一个超大 prompt 更易维护、可版本化。
- **"先 Motivation 后动笔"** 对一切长文生成类 Agent（技术报告、方案书、白皮书）都有借鉴意义——先对齐"为什么写"，再决定"写什么"。

---

## 五、源码深度解读

### 1. 编排器 SKILL.md（dist/claude/skills/paper-spine/SKILL.md）

主控 skill 极薄，**只做路由，不做生成**。它用一张表把触发词映射到对应 playbook：

```markdown
## Command Routing
| Trigger | Read |
| `resume`/`continue` | references/resume.md |
| `update`/`check for updates` | references/update.md |
| `audit` | references/audit.md |
| `translate` | references/translate.md |
...
```

```markdown
## Operating Principle
PaperSpine is a research-writing workflow, not a prose patcher. Its job is to
learn the target scene and strong examples first, force a user-confirmed
motivation, design the paper row by row, and only then write or rebuild.
Never fabricate data, metrics, p-values, datasets, citations, figures...
```

> 解读：核心代码哲学是"**编排器薄、playbook 厚**"。所有领域知识在外挂 `references/*.md`，Skill 本体仅维护一张路由表，降低耦合、便于按场景扩展。

### 2. Contribution-First 三道硬关卡（V4）

SKILL.md 明确三规则"坐在 motivation 之上"：

```markdown
1. Contribution-First. Do not begin substantive writing until
   `confirmed_contribution.md` exists ... Gate: contribution_check.py
2. Results-as-Validation. Each major Results subsection must validate
   at least one contribution promise ... Gate: results_validation_check.py
3. Reviewer-Aware. create `reviewer_audit.md` (reviewer value map +
   objection register + editorial fit) ... Gate: reviewer_audit_check.py
# The Stage 12 Final Audit hard gate runs all three checks.
```

> 解读：把学术写作的隐性质量标准（贡献明确、结果验证贡献、审稿人视角）显式化为**文件产物 + 校验脚本**，形成"写不出文件就过不了关"的强制约束，是该项目的灵魂设计。

### 3. 本地优先引用策略

`reference_mode` 三档（`local_first` / `specified_paths` / `web`）与 `citation-support-bank.md` 配合，先建本地 claim→citation 库再按需联网——既减少 API 开销，也保证引用可追溯。

---

## 六、社区口碑

| 维度 | 信号 |
|------|------|
| **增长** | 星标由初次调研时的 2,700 翻倍至 **5,002**（约 3 个月 +85%），验证需求真实 |
| **活跃度** | 最后推送 2026-08-26，含 `.github/workflows`（atlas/validate/verify-release 三条 CI），维护已恢复活跃 |
| **社区规模** | 196 forks、11 subscribers，B 站有使用讲解视频，已有社区 PR（在线入口、Trae 支持请求） |
| **已知痛点** | Issue #15「图形界面和配置 UI 不可用」仍 open；历史 #13 反映旧版更新器强求已移除文件导致 `--yes` 失败（已修） |
| **定位争议** | 11 个分支 skill + 配置文件上手成本高，对非学术场景（博客/文档/产品文案）支持弱 |

> 口碑小结：需求侧强劲、增长健康；主要吐槽集中在"配置 UI 不稳"和"学习曲线陡"，属于成长型项目的典型阵痛，非信任危机。

---

## 七、竞品对比

> 说明：以下按**品类**而非具体仓库对比，避免虚构竞品。

| 维度 | PaperSpine | 通用大模型对话（ChatGPT/Claude 直聊） | 传统 LaTeX 工具链（Pandoc/Manubot/Overleaf） | 其他"论文 Agent"套件 |
|------|-----------|--------------------------------------|--------------------------------------------|---------------------|
| 写作哲学 | motivation + contribution 主线，先研究后写 | 你来我往的补丁式生成 | 格式/引用自动化，不管论证 | 参差不齐，多为单 prompt |
| 质量把关 | 三道脚本化硬关卡 | 无（靠人工） | 无（只管排版） | 多数无 |
| 引用可靠性 | claim→citation 矩阵 + 本地优先 | 易编造文献 | 强（BibTeX 体系） | 视实现 |
| 多宿主 | Codex/Claude/OpenClaw 统一 | 各模型独立 | 与编辑器绑定 | 通常单平台 |
| 适用边界 | 学术/竞赛/报告为主 | 万能但浅 | 偏排版 | 不定 |

**核心研判**：PaperSpine 的护城河不是"能写"，而是**把学术写作的评审标准工程化为可校验关卡**。它填补了"通用大模型（写得快但不严）"与"传统 LaTeX 工具（管格式不管论证）"之间的空白——一个**论证质量优先**的写作 Agent。若能在"配置 UI 稳定性"和"非学术场景扩展"上补强，天花板很高。

---

## 八、关键文件路径速查

| 用途 | 路径 |
|------|------|
| 主入口 Skill | `dist/claude/skills/paper-spine/SKILL.md` |
| 阶段 playbook 集合 | `dist/claude/skills/paper-spine/references/*.md` |
| 贡献/结果关卡模板 | `references/contribution.md`、`references/results-validation.md`、`references/reviewer-audit.md` |
| 安装脚本 | `install.sh` / `install.ps1` |
| 插件元数据 | `.claude-plugin/plugin.json` |
| 星标可视化 | `atlas/fetch_stargazers.py` |

---

*报告由 AI 基于 GitHub 源码（SKILL.md、references、CI）、仓库元数据与 Issue 复核生成（2026-08-28 修复增强）。*
