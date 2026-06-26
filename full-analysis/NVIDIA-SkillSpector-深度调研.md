# 🛡️ SkillSpector — AI Agent Skills Security Scanner (NVIDIA)

> **仓库:** [NVIDIA/SkillSpector](https://github.com/NVIDIA/SkillSpector)
> **Stars:** 8,602 ⭐（本周 +5,026）
> **语言:** Python
> **许可:** Apache-2.0
> **关键词:** AI security, agent skills, vulnerability scanner, static analysis, supply chain

---

## 项目定位

NVIDIA 出品的 **AI Agent Skills 安全扫描器**。在安装 Agent 技能前（如 Claude Code、Codex CLI、Gemini CLI 使用的 SKILL.md），检测漏洞、恶意模式和供应链风险。

背景：研究显示 **26.1% 的公开技能存在漏洞，5.2% 存在明显恶意意图**。SkillSpector 回答一个关键问题：**"这个技能安全吗？"**

---

## 核心能力

### 输入支持
- Git 仓库、URL、zip 包、本地目录、单文件
- 多格式输出：终端、JSON、Markdown、**SARIF**（CI/CD 集成）

### 64 个漏洞模式 × 16 大分类

| 分类 | 说明 | 示例模式 |
|------|------|----------|
| **Prompt Injection** | 提示注入 | 指令覆盖、隐藏指令、行为操纵 |
| **Data Exfiltration** | 数据泄露 | 外部传输、环境变量收割、文件系统枚举 |
| **Privilege Escalation** | 权限提升 | 过度权限、sudo/root 执行、凭据访问 |
| **Supply Chain** | 供应链 | 未锁定依赖、远程脚本获取（curl\|bash）、混淆代码 |
| **Excessive Agency** | 过度自主性 | 无限制工具访问、自主决策 |
| **Output Handling** | 输出处理 | 未验证输出注入 |
| **System Prompt Leakage** | 系统提示泄露 | — |
| **Memory Poisoning** | 内存投毒 | — |
| **Tool Misuse / Rogue Agent / Trigger Abuse** | 工具误用等 | — |
| **Dangerous Code (AST)** | 危险代码（AST） | — |
| **Taint Tracking / YARA / MCP 安全** | 污点追踪等 | — |

### 两阶段分析

```
技能文件/SKILL.md
    │
    ▼
┌─────────────────┐
│  Stage 1: 静态分析  │  ← 64 种规则引擎（快速扫描）
│  YARA 签名匹配     │
│  AST 代码分析       │
│  Taint 追踪        │
│  OSV.dev 实时 CVE 查询 │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  Stage 2: LLM 语义评估 │  ← 可选，深度理解意图
│  Provider 可选:        │
│  OpenAI / Anthropic /  │
│  NVIDIA / Ollama      │
└────────────────────────┘
         │
         ▼
    Risk Score: 0-100
    Severity: CRITICAL/HIGH/MEDIUM/LOW
    Actionable Recommendations
```

---

## 部署方式

### 本地安装
```bash
git clone https://github.com/NVIDIA/skillspector.git
cd skillspector
make install
skillspector scan ./my-skill/
```

### Docker
```bash
docker run --rm -v "$PWD:/scan" skillspector scan ./my-skill/ --no-llm
```

### LLM 语义分析配置
支持多 Provider：
- `SKILLSPECTOR_PROVIDER=openai` → gpt-5.4
- `SKILLSPECTOR_PROVIDER=anthropic` → claude-opus-4-6
- `SKILLSPECTOR_PROVIDER=nv_build` → deepseek-v4-flash
- 也支持 Ollama 等本地端

---

## 输出格式

| 格式 | 使用场景 |
|------|----------|
| 终端（默认） | 本地快速扫描，美观格式化 |
| JSON | 机器可读，二次处理 |
| Markdown | 生成文档 / 报告 |
| SARIF | CI/CD 集成，IDE 插件支持 |

---

## 竞品对比

| | SkillSpector | 通用 SAST | 人工审核 |
|---|-------------|-----------|---------|
| **Agent 技能专属** | ✅ 64 个 Agent 特定模式 | ❌ 通用代码漏洞 | ❌ |
| **CI/CD 集成** | ✅ SARIF 输出 | ✅ | ❌ |
| **供应链 CVE** | ✅ OSV.dev 实时查询 | ⚠️ 部分支持 | ❌ |
| **LLM 语义分析** | ✅ 可选深度分析 | ❌ | ✅ |
| **开源** | ✅ Apache-2.0 | ⚠️ 部分 | — |
| **Docker 一键扫描** | ✅ | ✅ | ❌ |

---

## 核心研判

| 维度 | 评价 |
|------|------|
| **创新性** | ⭐⭐⭐⭐ 首个专注于 Agent Skill 安全扫描的开源工具 |
| **实用性** | ⭐⭐⭐⭐⭐ 一键扫描，Docker 化部署，SARIF 输出直接 CI/CD |
| **NVIDIA 背书** | ⭐⭐⭐⭐⭐ 企业级维护，16 类 64 模式覆盖全面 |
| **可扩展性** | ⭐⭐⭐⭐ 支持多 LLM Provider、YARA、Docker |
| **生态前景** | ⭐⭐⭐⭐ Agent 安全是刚需，随 Agent 生态爆发而增长 |

**结论：强烈推荐关注。** 随着 AI Agent（Claude Code、Codex、Cursor）大量安装第三方 Skills，安全扫描将成为基础设施级需求。SkillSpector 作为 NVIDIA 推出的 Agent 安全工具，极有可能成为行业标准。

---

## 关键文件路径

| 文件 | 说明 |
|------|------|
| `docs/DEVELOPMENT.md` | 架构和扩展指南 |
| `Dockerfile` | Docker 构建 |
| `Makefile` | 统一构建/安装入口 |

---

*调研日期: 2026-06-21 02:00 CST*
