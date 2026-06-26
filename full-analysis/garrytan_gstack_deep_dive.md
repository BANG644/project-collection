# 🔍 garrytan/gstack — 深度调研报告

> **Garry Tan 的 Claude Code 虚拟工程团队** | 113K ⭐ | MIT | 2026-03 开源

---

## 📌 项目定位

gstack 是 Y Combinator 总裁兼 CEO **Garry Tan** 开源的 Claude Code 技能（Skills）集合。它不是传统意义上的框架或库，而是一套 **角色化、流程化的 AI 编程斜杠命令集**，将 Claude Code 从通用助手转变为可「按需召唤」的专业虚拟工程团队。

核心理念：**一个人 + Claude Code + gstack = 一支完整的创业工程团队。**

Garry Tan 本人用它 「在 60 天内，全职运营 YC 的同时，用空闲时间交付了 3 个生产级服务、40+ 个功能」。

---

## 🏗️ 核心架构

### 23 个斜杠命令 × 6 大角色

| 角色 | 斜杠命令 | 职责 |
|------|----------|------|
| **CEO / 产品合伙人** | `/office-hours` | 对产品 Idea 进行 YC 式灵魂拷问，输出设计文档 |
| **设计师** | `/design-shotgun`, `/design-review`, `/design`, `/cso` | 生成 4-6 个设计变体、安全审计 |
| **工程经理** | `/autoplan`, `/plan-ceo-review`, `/plan-eng-review` | 自动串联 CEO/设计/架构三重评审 |
| **软件工程师** | `/review`, `/qa`, `/desk-check` | 严格代码审查 + 真实浏览器测试 |
| **发布工程师** | `/ship`, `/retro`, `/context` | 同步主干、跑测试、检查覆盖、创建 PR |
| **支持/工具** | `/hackernews-frontpage`, `/explain`, `/design-consultation` | 社区洞察、代码解释、架构咨询 |

### 全流程管线

```
/office-hours → /autoplan → /spec → /build → /review → /qa → /ship → /retro
/design-shotgun → /design-review → /cso (贯穿所有阶段)
```

### 文件结构

```
gstack/
├── agents/           # 虚拟角色配置，定义每个专家角色的 persona 和指导原则
├── bin/              # 脚本入口和工具函数
├── browse/           # headless 浏览器二进制（Playwright 构建）
├── browser-skills/   # 浏览器自动化技能（QA 测试使用）
├── canary/           # 金丝雀发布验证
├── careful/          # 谨慎模式（安全护栏）
├── docs/             # 文档和架构说明
├── contrib/          # 社区贡献技能
└── SKILL.md.tmpl     # 技能文件模板（Slash 命令定义）
```

### 核心技术亮点

1. **browse 二进制**：用 Playwright 构建的自包含无头浏览器，所有系统库静态链接，`file` + `setup` 两步即可工作，无需预装 Chrome。
2. **AskUserQuestion 分治**：v1.51.0 将复杂的用户提问拆分为子问题分别推理，提升准确率。
3. **隔离上下文的 $B 诊断**：v1.48.0 新增 4 项 CDP 资源泄漏修复，保持浏览器会话健康。
4. **Hermetic E2E 隔离**：E2E 测试在完全隔离的环境中运行，防止测试污染生产数据。

---

## 💬 社区口碑

| 维度 | 评价 |
|------|------|
| **Star 增长** | 2026-03 开源，3 个月从 0 → 113K ⭐，最快冲刺达单日 16K+ |
| **用户评价** | 「AI 编程的工程化样板」—「vibe coding 的反义词」|
| **采用情况** | 数千个 Claude Code 用户已将 gstack 作为标准配置 |
| **争议** | 部分用户反映 `/autoplan` 过于激进，有时生成过度工程化的代码 |

### 与竞品对比

| 项目 | 定位 | 核心差异 |
|------|------|----------|
| **gstack** | 角色化全流程 Skill 集 | 23 角色、浏览器隔离、YC 级流程约束 |
| **mattpocock/skills** | 真实工程师 Skill 集 | 工程规范导向、TDD 驱动、轻量无侵入 |
| **addyosmani/agent-skills** | 生产级编码 Skill 集 | 24 个技能 + 7 个斜杠命令，跨平台兼容 |
| **GSD** | 一键生成流程 | 全自动，但缺乏专业角色粒度 |
| **BMAD** | 构建 - 测量 - 调整循环 | 强调构建循环，非角色驱动 |

---

## 🧠 核心研判

1. **流程即产品**：gstack 的本质不是写 AI 能写什么，而是 **AI 应该按什么流程写**。它把 Garry Tan 二十年产品经验的流程智慧数字化了。
2. **YC 级方法论的外溢**：这不仅仅是开发者工具，更是 YC 内部最佳实践的开源化。对早期创业团队的价值可能超过 Claude Code 本身。
3. **浏览器隔离是关键技术壁垒**：browse 二进制独有，竞品尚无等效替代。让 QA 测试从模拟变成真实环境。
4. **Skill 生态的 Apple Watch moment**：gstack 向行业展示了「一个人的 AI 启动套件」的标准模板，可能在 2026 年推动 Skill 生态从「散装指令」走向「工程化套装」。
5. **风险**：过于依赖 Garry Tan 个人的开发风格。如果社区没有实质性增加自己的流程进去，项目可能停留在「搬运模板」阶段。

---

## 🔗 关键链接

- GitHub: https://github.com/garrytan/gstack
- 许可证: MIT
- 安装: `git clone --depth 1 https://github.com/garrytan/gstack.git ~/.claude/skills/gstack && cd ~/.claude/skills/gstack && ./setup`
