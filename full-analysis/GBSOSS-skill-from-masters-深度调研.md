# Skill From Masters — 站在巨人肩膀上生成 AI Skill

> 调研日期：2026-10-06 ｜ Stars：1,587 ｜ 语言：无（Markdown + SKILL.md 技能包）｜ License：MIT ｜ 维护者：GBSOSS
> 仓库：https://github.com/GBSOSS/skill-from-masters

---

## 一、项目亮点（差异化）

1. **解决"做 Skill 最难的部分"**：作者直言——写 Skill 的格式不难，难在"知道这件事最好的做法"。本仓库在生成任何新 Skill 前，先去检索领域大师的成熟方法论并编码进 Skill。
2. **三层检索（3-Layer Search）**：本地方法论库 → 联网搜专家 → 深挖一手来源（primary sources），而不是只抓二手总结。
3. **金色样例 + 反模式（Anti-Patterns）**：不仅找"好输出长什么样"，还主动搜"常见错误"，把"别这么做"也写进 Skill。
4. **跨专家交叉验证**：多专家之间比对共识、标记分歧，避免单一来源偏见。
5. **三件套可独立使用**：`skill-from-masters`（从大师方法论造 Skill）、`search-skill`（从可信源搜现成 Skill）、`skill-from-github`（从优质 GitHub 项目提炼知识造 Skill），且与 `skill-creator` 衔接。

---

## 二、核心架构

```
用户:"帮我做一个用户访谈的 skill"
        │
        ▼
 skill-from-masters
   ├─ 1. 查本地 methodology-database（15+ 领域）
   ├─ 2. 联网搜更多专家
   ├─ 3. 找 golden examples（质量标杆输出）
   ├─ 4. 找 common mistakes（反模式）
   └─ 5. 跨源交叉验证
        │  用户选择要采纳的方法论
        ▼
 提取可行动原则（actionable steps）
        │
        ▼
 skill-creator 生成最终 SKILL.md
```

- **方法论库**：`skill-from-masters/references/methodology-database.md` 收录 15+ 领域大师（写作=Minto/Zinsser/Amazon 6-pager；产品=Cagan/Torres/Biddle；谈判=Voss/Fisher&Ury；决策=Bezos/Munger/Duke 等），另含 `skill-taxonomy.md`（11 类 Skill 分类）与"Oral Tradition"段（Jobs/Musk/Huang 等以演讲访谈传道者）。
- **信任源约束**：`search-skill` 只搜 5 个可信源（官方 → 精选 → 聚合器分层），过滤 stars<10、过期、无 SKILL.md 的结果，并做可疑代码模式安全检查。

---

## 三、源码深度解读（关键模块）

仓库本身是"技能即文档"，没有传统编译代码，核心资产是 **SKILL.md 的提示词工程**。值得看的结构：

### 1. 主技能定义 — `skill-from-masters/SKILL.md`

```
When you want to create a new skill based on expert methodologies:
  - 3-layer search: local database → web experts → primary sources
  - Finds golden examples and anti-patterns
  - Cross-validates across multiple experts
  - Hands off to skill-creator for final generation
```

要点：把"检索→筛选→验证→生成"固化为技能的步骤契约，而非一次性 prompt。

### 2. 方法论库（核心数据资产）— `skill-from-masters/references/methodology-database.md`

| 领域 | 示例大师 |
|------|---------|
| Writing | Barbara Minto, William Zinsser, Amazon 6-pager |
| Product | Marty Cagan, Teresa Torres, Gibson Biddle |
| Sales | Neil Rackham (SPIN), Challenger Sale, MEDDIC |
| Hiring | Laszlo Bock, Geoff Smart, Lou Adler |
| User Research | Rob Fitzpatrick, Steve Portigal, JTBD |
| Engineering | Martin Fowler, Robert Martin, Kent Beck |
| Leadership | Kim Scott, Ray Dalio, Andy Grove |
| Negotiation | Chris Voss, Fisher & Ury |
| Startups | Eric Ries, Paul Graham, YC |
| Decision Making | Jeff Bezos, Charlie Munger, Annie Duke |

### 3. 三个子技能职责划分

- `skill-from-masters`：从专家方法论造 Skill（质量靠"选"，不是"写"——口号 *Quality isn't written. It's selected.*）
- `search-skill`：从可信市场搜现成 Skill，带安全过滤（stars<10 / 无 SKILL.md / 可疑代码模式 一律排除）
- `skill-from-github`：搜 stars>100 且活跃维护的 GitHub 项目 → 深挖 README/源码/示例 → **提炼知识**（不是包一层工具），使 Skill 即使原工具没装也能工作

---

## 四、应用场景与启发

- **场景**：你想给团队/自己造一批高质量 Skill（写 PRD、做用户访谈、代码评审…），但不想从零拍脑袋定方法论。
- **启发（可借鉴点）**：
  - "知识型 Skill"优于"工具包装型 Skill"：`skill-from-github` 明确编码项目*知识*而非调用项目，Skill 更鲁棒——这条原则可直接用于你自己的 skill 写作规约。
  - 把"反模式"和"金色样例"当作一等公民，是提升生成质量的高杠杆动作。
  - 跨专家交叉验证对抗单一来源偏见，适合任何"AI 替你总结最佳实践"的场景。

---

## 五、社区口碑

- Stars 1,587、Forks 158，作为"技能方法论"类仓库增长健康；README 在 Claude Code / Codex 用户圈有传播。
- ⚠️ 局限：方法论库偏英文商业/产品领域，中文语境与工程细分领域覆盖不足；"联网搜专家"依赖运行环境有搜索能力，离线场景退化为仅本地库。
- 结论：口碑偏正面（"立意好、即插即用"），但 Empirical 评测数据不可用。

---

## 六、竞品对比

| 维度 | skill-from-masters | anthropics/skills 官方集 | 各路 "skill 生成器" |
|------|-------------------|------------------------|--------------------|
| 是否带方法论库 | ✅ 15+ 领域大师 | 部分 | 多无 |
| 反模式 / 金色样例 | ✅ | 视具体 skill | 少 |
| 交叉验证 | ✅ | 否 | 否 |
| 从 GitHub 提炼知识 | ✅（skill-from-github） | 否 | 个别有 |
| 定位 | 造 Skill 的"前置质量门" | 成品 skill 合集 | 格式生成器 |

**差异化**：它卡在"造 Skill 之前"这步，补的是市面生成器普遍缺失的方法论来源，而非又一个格式脚手架。

---

## 七、核心研判

- **价值**：对"要写很多 Skill"的用户（尤其 AI 工作流 builder）是高杠杆工具；其方法论库与"知识型 vs 工具型"原则值得直接抄进你自己的 skill 规约。
- **风险**：① 方法论库覆盖广度有限，长尾领域会退化成纯联网搜索；② 强依赖 `skill-creator` 存在；③ 仓库无自动化测试，质量靠人工维护的数据库。
- **建议**：把它当"Skill 质量门禁"用，而不是"一键生成器"；重点复用其 `methodology-database.md` 的结构与"金色样例 + 反模式 + 交叉验证"三步法。

---

## 八、关键文件路径速查

| 文件 | 作用 |
|------|------|
| `skill-from-masters/SKILL.md` | 主技能：从大师方法论造 Skill |
| `skill-from-masters/references/methodology-database.md` | 核心数据资产：15+ 领域大师方法论库 |
| `skill-from-masters/references/skill-taxonomy.md` | 11 类 Skill 分类法 |
| `skills/search-skill/SKILL.md` | 从可信源搜现成 Skill（带安全过滤） |
| `skills/skill-from-github/SKILL.md` | 从 GitHub 项目提炼知识造 Skill |
| `README.md` | 安装 / 用法 / 三件套说明 |
| `LICENSE` | MIT |
