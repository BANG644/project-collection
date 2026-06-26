# santifer/career-ops — AI 求职系统深度调研报告

> **一句话定位**：用 AI 编码 CLI 打造的个人求职作战指挥中心，从职位搜索→简历生成→投递追踪全流程自动化。

## 📊 项目全景

| 属性 | 值 |
|------|-----|
| **仓库** | [santifer/career-ops](https://github.com/santifer/career-ops) |
| **Stars** | 54,765 ⭐（2026-06-20） |
| **语言** | JavaScript (53.1%) / Go (24.9%) / Python (10.2%) |
| **许可** | 开源（MIT） |
| **创建** | 2026-04-04 |
| **最新** | 2026-06-18 |
| **大小** | 30.7 MB |
| **官方** | [career-ops.org](https://career-ops.org) |

## 🏗 核心架构

### 系统架构图

```
用户输入（简历/偏好） → Claude Code CLI → career-ops Agent 系统
                          ├── 14 Skill Modes（职位筛选/简历生成/追踪/面试...）
                          ├── Go Dashboard（Web 面板）
                          ├── PDF 引擎（ATS 优化简历）
                          └── 批处理引擎（并行处理 10+ 职位）
```

### 关键目录结构

```
/
├── .agents/           # Agent 定义
├── .claude/           # Claude Code 配置
├── .claude-plugin/    # 插件系统
├── batch/             # 批处理脚本
├── config/            # 配置中心
├── dashboard/         # Go Web 面板
├── data/              # 数据层
├── docs/              # 多语言文档
├── examples/          # 使用示例
├── fonts/             # PDF 字体
├── interview-prep/    # 面试准备
├── jds/               # 职位描述数据库
├── modes/             # 14 种 Skill 模式
├── output/            # 输出目录
├── providers/         # 门户集成（Greenhouse/Ashby/Lever）
├── reports/           # 报告生成
├── scaffolder/        # 项目脚手架
└── writing-samples/   # 写作样本
```

## 🔍 核心功能详解

### 1. 自动化职位评估系统（A-F Scoring）
- 10 个加权维度的结构化评分
- 自动打分 + 手动调整
- 推荐分数 ≥ 4.0/5 才投递（过滤噪音）

### 2. PDF 简历引擎
- 基于 LaTeX 的 ATS 优化 CV
- 每职位定制化生成
- 支持多语言输出

### 3. 门户自动化扫描
- 支持 Greenhouse / Ashby / Lever / 公司自有页面
- 自动提取职位描述并评估

### 4. 批处理引擎
- 通过子代理并行评估 10+ 职位
- 单数据源追踪（完整性校验）

### 5. Go Dashboard
- 独立的 Web 可视化面板
- 实时追踪求职进度

### 6. 活体验证系统（Liveness Check）
- `liveness-core.mjs` — 检测职位是否已过期/不再招聘
- 多模式匹配 → 自动标记失效职位

### 7. 14 种 Skill Modes
包括但不限于：职位搜索、简历定制、求职信生成、网络挖掘、面试准备、薪酬分析、公司研究等

## 📈 社区口碑

| 维度 | 评价 |
|------|------|
| **现象级热度** | 54K+ Stars，GitHub Trending 多日霸榜 |
| **社区反馈** | "终于有靠谱的 AI 求职工具了" — 大量正面评价 |
| **多语言支持** | 中文/英文/日文/韩文/葡语/西语/乌克兰语等多语言 README |
| **完整性** | 含 AGENTS.md / CLAUDE.md / CONTRIBUTING.md / LICENSE 等全套社区文档 |

## ⚔ 竞品对比

| 特性 | career-ops | 传统求职工具 | AI 简历生成器 |
|------|-----------|-------------|-------------|
| 职位自动搜索 | ✅ | ⚠️ 有限 | ❌ |
| ATS 优化简历 | ✅ | ❌ | ✅ |
| 门户集成 | ✅ | ❌ | ❌ |
| 面试准备 | ✅ | ❌ | ❌ |
| Go Dashboard | ✅ | ❌ | ❌ |
| 批量处理 | ✅ | ❌ | ❌ |
| 开源 | ✅ MIT | ❌ | 部分 |
| AI Agent 驱动 | ✅ | ❌ | ❌ |

## 💡 核心研判

1. **真实需求驱动**：作者本人的求职经历促使开发，非凭空造轮子
2. **Agent 原生架构**：深度绑定 Claude Code 生态，14 skill modes 是其核心差异化
3. **生产力价值极高**：从"投没人看"→"AI帮你筛选→自动生简历→一键投递"
4. **技术栈合理**：JS（主体）+ Go（Dashboard）+ Python（脚本），各司其职

## 🔑 关键文件路径

| 用途 | 路径 |
|------|------|
| AGENTS.md | `AGENTS.md` |
| CLAUDE.md | `CLAUDE.md` |
| 活体验证核心 | `liveness-core.mjs` |
| 扫描引擎 | `scan.mjs` |
| PDF 生成 | `generate-pdf.mjs` |
| Dashboard 主程序 | `dashboard/` |
| 批处理模式 | `modes/` |
| 职位数据库 | `jds/` |
| 配置模板 | `.env.example` |
