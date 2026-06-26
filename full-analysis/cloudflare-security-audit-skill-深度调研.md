# cloudflare/security-audit-skill 全方位深度调研

> 调研时间：2026-06-23  
> Stars：346 ⭐ | Forks：29 | Language：JavaScript  
> 创建时间：2026-06-18 | License：MIT  
> 类型：Cloudflare 官方开源 AI Agent 安全审计 Skill  

---

## 一、项目全景

**security-audit-skill** 是 Cloudflare 官方开源的一款**编码 Agent 安全审计 Skill**，能让你的 AI 编码 Agent（如 Claude Code、Codex 等）执行六阶段的安全审计管线——从侦察到报告，再到独立验证。

该项目源自 Cloudflare 内部构建的安全编排工具的早期原型（仅面向单仓库），完整的集群级版本已在博客文章 [Build your own vulnerability harness](https://blog.cloudflare.com/build-your-own-vulnerability-harness) 中介绍。

### 核心差异点

> **不是"用 AI 看代码漏洞"，而是"让多个 AI Agent 并行协作、相互质疑"——相当于在 Agent 层面实现了"同行评审"。**

### 主要特点

1. **六阶段管线**：侦察 → 狩猎 → 验证 → 报告 → 结构化输出 → 独立验证
2. **并行多 Agent 协作**：每个阶段可以 spawn 多个子 Agent，从不同角度攻击
3. **防御性验证**：专门的验证 Agent 试图"证伪"每个发现（消除误报）
4. **运行可累加**：多次审计同一仓库，效果叠加（读取 `findings.json` 跳过已知问题）
5. **标准化输出**：每个发现符合 `report-schema.json` 的 JSON 格式，支持自动化处理

---

## 二、核心架构

### 2.1 六阶段管线

```
Phase 1: Recon（侦察）
 ├── 并行 Agent：映射应用架构、信任边界、输入面
 └── 产出：architecture.md

Phase 2: Hunt（狩猎）
 ├── 并行 7 个 Agent × 不同攻击角度：
 │   ├── 注入攻击（XSS/SQLi/SSRF等）
 │   ├── 访问控制失效
 │   ├── 业务逻辑漏洞
 │   ├── 加密缺陷
 │   ├── 功能滥用
 │   ├── 链式攻击
 │   └── 通配（Wildcard，自由探索）
 │   每个 Agent 可继续 spawn 子 Agent 深入挖掘
 └── 产出：初步发现列表

Phase 3: Validate（验证）
 ├── 独立 Agent 尝试"证伪"每个发现
 └── 产出：通过验证的真实漏洞

Phase 4: Report（报告）
 ├── 产出 REPORT.md（可读版本） + FINDINGS-DETAIL.md（详细追踪）
 └── MEDIUM+ 级别的发现详细记录

Phase 5: Structured Output（结构化输出）
 ├── 产出 findings.json（符合 report-schema.json）
 ├── 自动用 validate-findings.cjs 验证格式
 └── 确保机器可读

Phase 6: Independent Verification（独立验证）
 ├── 全新 Agent 检查 structured output 中每个事实
 └── 对照源代码验证
```

### 2.2 核心设计原则

| 原则 | 说明 |
|------|------|
| **只报告可利用的漏洞** | 每个发现必须有具体的攻击场景，不能是"理论上可能" |
| **对立验证** | 检查发现的 Agent 与发现它的 Agent 不能是同一个 |
| **严重性 = 影响 × 可能性** | 不是 checklist 偏离程度 |
| **纵深防御缺口不是漏洞** | 如果 A 层已经阻止了攻击，B 层缺失只是加固建议 |
| **多次运行提升覆盖率** | 测试发现单次运行只能覆盖约一半的漏洞 |

---

## 三、源码深度解读

### 3.1 文件结构

```
security-audit-skill/
├── SKILL.md                   # 主Skill文件：安装、核心原则、术语、工作流
├── RECONNAISSANCE.md          # Phase 1 侦察阶段的 Prompt 和综合指令
├── HUNTING.md                 # Phase 2 狩猎编排、方法和验证规则
├── ATTACK-CLASSES.md          # 7种攻击角度的 Prompt 定义
├── VALIDATION-AND-REPORTING.md # Phase 3-6 验证、报告和验证指令
├── report-schema.json         # findings.json 的 JSON Schema
├── validate-findings.cjs      # 零依赖 Node.js 验证器
└── LICENSE (MIT)
```

### 3.2 技术栈分析

- **主语言：JavaScript**（validate-findings.cjs 为 Node.js 脚本）
- **Skill 格式**：遵循 Skills CLI（`npx skills`）协议
- **多 Agent 并行**：依赖 Agent 自身 spawn 子 Agent 的能力

### 3.3 攻击角度（ATTACK-CLASSES.md 含7个方向）

1. **Injection**：XSS、SQLi、SSRF、命令注入、LDAP 注入等
2. **Access Control**：水平/垂直越权、IDOR、未授权访问
3. **Business Logic**：竞争条件、逻辑绕过、双花攻击
4. **Cryptography**：弱加密、错误使用、密钥硬编码
5. **Feature Abuse**：文件上传绕过、API 滥用、SSRF 链式攻击
6. **Chained Attacks**：多漏洞组合利用
7. **Wildcard**：自由探索，开发者自己补充攻击思路

---

## 四、社区口碑

- **官方出品**：Cloudflare 官方开源，有博客文章背书，可信度高
- **346 stars / 4 天**：增速合理，来自 Cloudflare 的品牌效应
- **MIT License**：开源友好，可自由使用和修改
- 项目仅 24KB 大小，是"提示词代码"而非传统代码库
- 对于小型代码库的安全审计，这是一个低成本、高覆盖率的方案

---

## 五、竞品对比

| 维度 | Cloudflare security-audit-skill | Semgrep | SonarQube | Snyk |
|------|-------------------------------|---------|-----------|------|
| 核心方法 | 多Agent并行审计 + 交叉验证 | 静态规则匹配 | 静态分析 + 质量门禁 | 依赖扫描 + SCA |
| AI 使用 | 核心驱动力（LLM Agent） | 无 | 有限 | 有限 |
| 误报率 | 低（有专门验证阶段） | 中（取决于规则质量） | 中 | 低 |
| 受众 | AI Agent 用户 | 安全工程师 | 开发团队 | 开发团队 |
| 成本 | 免费 + Agent 订阅 | 免费/商业版 | 社区版/商业版 | 免费/商业版 |
| 深度 | 可深度挖掘业务逻辑漏洞 | 模式匹配为主 | 代码质量为主 | 依赖生态为主 |

**核心差异**：Cloudflare 的方案是**由 LLM Agent 驱动**的，能够理解业务逻辑，发现人类定义的静态规则无法覆盖的漏洞类型。代价是依赖 Agent 的质量和 token 消耗。

---

## 六、核心研判

### 6.1 价值评估

⭐⭐⭐⭐（对代码安全审计领域有重要启示）

**核心洞察**：
1. **多 Agent 交叉验证是降低 LLM 幻觉/误报的关键设计**——这比单一 Agent 直接分析代码可靠得多
2. **对抗式验证**（专门的反驳 Agent）是一个有趣的模式，可延伸至其他 AI 任务
3. 总大小仅 24KB，本质上是一套精心设计的 **Prompt 工程框架**，而非传统安全工具

### 6.2 与本 workspace 的关系

本 workspace 的 OpenClaw 生态与 Skills CLI 兼容。如果需要进行代码审计，此 Skill 可以直接通过 `npx skills add` 安装使用。同时，其**多 Agent 并行**和**对立验证**设计模式，对设计其他领域的深研 Agents 流程也有借鉴意义。

---

## 七、关键文件路径速查

| 文件 | 说明 |
|------|------|
| `SKILL.md` | Skill 主入口，安装和使用说明 |
| `RECONNAISSANCE.md` | Phase 1 侦察阶段 Prompt |
| `HUNTING.md` | Phase 2 狩猎编排 |
| `ATTACK-CLASSES.md` | 7 种攻击角度 Prompt |
| `VALIDATION-AND-REPORTING.md` | Phase 3-6 验证/报告/核实 |
| `report-schema.json` | findings.json 的 JSON Schema |
| `validate-findings.cjs` | 零依赖 Node.js 格式验证器 |

---

*调研 by IMA 知识库管家 | 2026-06-23*
