# 📊 PaperSpine 深度调研报告

> **仓库**: [WUBING2023/PaperSpine](https://github.com/WUBING2023/PaperSpine)  
> **Stars**: 2,700 | **Forks**: 110 | **语言**: Python | **License**: MIT  
> **创建时间**: 2026-05-17 | **最后推送**: 2026-06-04  
> **批次**: batch_03 (#41) | **调研日期**: 2026-06-17

---

## 一、项目定位

PaperSpine 是一个面向 Codex、Claude Code 和 OpenClaw 三大编码 Agent 的论文与报告写作 skill suite。其核心理念是 **"以 motivation 为主线"**：要求 Agent 在写作前先学习目标场景和优秀样例，再记录每一个写作单元为什么这样规划或修改——而不是简单的"帮我润色"。

### 目标用户
- 学术论文写作者（期刊、会议、课程报告、综述、竞赛论文）
- 使用 Claude Code / Codex / OpenClaw 的 Agent 用户
- 重视论文"论证深度"而非"字数达标"的作者

---

## 二、架构设计

### 仓库结构

```
PaperSpine/
├── dist/                     # 真正用于安装的内容
│   ├── codex/skills/         # Codex 扁平 skill suite
│   ├── claude/skills/        # Claude Code 扁平 skill suite（11 个子 skill）
│   └── openclaw/skills/      # OpenClaw 扁平 skill suite
├── src/                      # 共享脚本和参考文档
│   ├── scripts/              # 确定性辅助脚本（安装、更新、引用索引）
│   ├── references/           # 共享工作流参考文档
│   └── agents/               # Agent 元数据源
├── .claude-plugin/           # Claude Code 插件元数据
├── install.ps1               # Windows 安装脚本
└── install.sh                # macOS/Linux 安装脚本
```

### 核心设计理念

1. **逐阶段路由**：主控 skill `paper-spine` 不直接修改句子，而是拆分为 11 个独立分支 skill，各司其职
2. **三宿主兼容**：同一套技能逻辑分别适配 Codex（`$paper-spine` 命名空间）、Claude Code（`/paperspine` slash command）、OpenClaw（`paper-spine` 命令）的差异
3. **本地优先参考文献**：`local_first` 默认模式优先索引本地文件，再按需网络补充

---

## 三、工作流详解

### 两条主线

| 流程 | 用途 | 前置条件 |
|------|------|---------|
| **Rewrite Existing** | 改进已有论文或报告 | 用户已有初稿 |
| **Build From Materials** | 从素材文件夹构筑论文 | 用户有素材（PDF、图片、数据摘要等） |

### 四类目标场景

- `journal` — 期刊论文
- `conference` — 会议论文
- `report/review` — 课程报告、技术报告或综述
- `competition` — 竞赛论文或竞赛报告

### 研究深度两级

- `flash` — 3 篇样例 + 3 篇同领域论文 + 官方要求
- `pro` — 6 篇样例 + 6 篇同领域论文 + 官方要求

### 11 个分支 Skill 流水线

| 序号 | Skill 名称 | 职责 |
|------|-----------|------|
| 1 | `paper-spine-ui` | 打开外部终端配置 UI |
| 2 | `paper-spine-intake` | 校验 `paper_spine_config.json` |
| 3 | `paper-spine-research` | 学习目标场景 + 参考资料 + 优秀样例 |
| 4 | `paper-spine-citation` | 构建逐句 claim 级别的引用支持库 |
| 5 | `paper-spine-rewrite` | 基于上游产物改写已有论文 |
| 6 | `paper-spine-build` | 从素材构筑新论文 |
| 7 | `paper-spine-latex` | 生成 + 检查 LaTeX + 可选 PDF/Word 输出 |
| 8 | `paper-spine-audit` | 审计产物完整性、写作思路深度、引用库质量 |
| 9 | `paper-spine-translate` | 产出完整的中文翻译包 |
| 10 | `paper-spine-humanize` | 让论文更像人类写作 |
| 11 | `paper-spine-update` | 检查并更新本地安装 |

---

## 四、技术亮点

### 1. 跨 Agent 统一架构
同一套 Skill Suite 通过安装脚本自动适配三种宿主，避免为每个 Agent 维护不同版本。

### 2. 本地优先 + 网络补充的参考材料策略
`reference_mode` 支持 `local_first`、`specified_paths`、`web` 三种模式，大幅减少 API 调用次数。

### 3. 基于 Citation 的写作思路矩阵
不是简单的写/改，而是在写作前先建立"claim → citation → evidence"的映射关系，保证每个论点都有据可依。

### 4. 自动版本管理与增量更新
`paperspine_update.py` 通过 GitHub 版本 JSON 比对，只同步变更内容，保留用户配置。

---

## 五、社区生态

- 暂挂维护状态（作者 7 月初前暂停）
- 订阅者星图网站：[https://wubing2023.github.io/PaperSpine/](https://wubing2023.github.io/PaperSpine/)
- B 站使用讲解视频已发布
- 已有社区贡献的 PR（README 在线入口），以及功能请求（Trae 支持、Mineru API 接口等）

---

## 六、关键优势与不足

### 优势
- 🎯 **深度优先**：不是字数补丁工具，而是培养论证思维
- 🔧 **模块化拆解**：每个分支可独立调用，灵活性高
- 📚 **研究驱动**：先研究再写作，符合学术写作规范
- 🌐 **多宿主**：Codex/Claude Code/OpenClaw 全覆盖

### 不足
- 🐌 **上手成本高**：11 个分支 skill + 配置文件的复杂度对新手不友好
- ⏸️ **维护暂停**：关键 Bug 可能得不到及时修复
- 📖 缺乏对非学术场景（博客、文档、产品文案）的支持
