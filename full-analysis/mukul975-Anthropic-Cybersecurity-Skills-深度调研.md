# mukul975/Anthropic-Cybersecurity-Skills — AI Agent 网络安全技能库深度调研

## 项目全景

- **仓库**: [mukul975/Anthropic-Cybersecurity-Skills](https://github.com/mukul975/Anthropic-Cybersecurity-Skills)
- **Stars**: ~4,200⭐ (Trending)
- **许可**: Apache 2.0
- **核心定位**: 754 个结构化网络安全技能，面向 AI Agent，映射至 6 个行业框架（MITRE ATT&CK v19.1、NIST CSF 2.0、MITRE ATLAS v5.4、D3FEND v1.3、NIST AI RMF 1.0、MITRE F3 v1.1）
- **⚠️ 社区项目** — 非 Anthropic 官方项目

## 核心架构

### 技术标准
- 遵循 [agentskills.io](https://agentskills.io) 开放标准
- YAML frontmatter 实现亚秒级发现
- 结构化 Markdown 分步执行
- 引用文件提供深层技术上下文
- 直接在 Claude Code、GitHub Copilot、OpenAI Codex CLI、Cursor、Gemini CLI 等 20+ 平台开箱即用

### 安装方式
```bash
# 推荐：npx
npx skills add mukul975/Anthropic-Cybersecurity-Skills

# 或 Git 克隆
git clone https://github.com/mukul975/Anthropic-Cybersecurity-Skills.git
```

## 技能覆盖范围

| 安全域 | 技能数 | 核心能力 |
|--------|--------|----------|
| 云安全 | 60 | AWS/Azure/GCP 加固 · CSPM · 云取证 |
| 威胁狩猎 | 55 | 假设驱动狩猎 · LOTL 检测 · 行为分析 |
| 威胁情报 | 50 | STIX/TAXII · MISP · 源集成 · 分析者画像 |
| Web 安全 | 42 | OWASP Top 10 · SQLi · XSS · SSRF · 反序列化 |
| 网络安全 | 40 | IDS/IPS · 防火墙规则 · VLAN 分割 · 流量分析 |
| 恶意软件分析 | 39 | 静态/动态分析 · 逆向工程 · YARA 规则 |
| 数字取证 (DFIR) | 38 | 内存/磁盘/网络取证 · Volatility · 时间线分析 |
| 红队/渗透测试 | 36 | 信息收集 · 漏洞利用 · 后渗透 |
| 身份与访问管理 | 32 | IAM 审计 · 零信任 · MFA 实施 |
| 事件响应 | 30 | 分类 · 遏制 · 根因分析 · 复盘 |
| **总计 (26 域)** | **754** | — |

## 跨框架映射 — 核心竞争力

每个技能同时映射至 **6 个行业框架**，这是业界唯一：

| 框架 | 版本 | 覆盖范围 |
|------|------|----------|
| MITRE ATT&CK | v19.1 | 15 战术 · 286 技术 |
| NIST CSF | 2.0 | 6 功能 · 22 类别 |
| MITRE ATLAS | v5.4 | 16 战术 · 84 技术 |
| MITRE D3FEND | v1.3 | 7 类别 · 267 技术 |
| NIST AI RMF | 1.0 | 4 功能 · 72 子类别 |
| MITRE F3 (反欺诈) | v1.1 | 8 战术 · 123 技术 |

### MITRE F3 反欺诈框架亮点
- 2026-04-09 MITRE CTID 发布，联合 JPMorganChase、Citigroup、Lloyds 等共同开发
- 填补了 ATT&CK 在「初始入侵后」欺诈场景的空白
- 新增两个欺诈专属战术：**定位 (FA0001)** 和 **变现 (FA0002)**
- 94 个技能映射至 F3 框架

## 竞品对比

| 维度 | Anthropic-Cybersecurity-Skills | MITRE ATT&CK 知识库 | Atomic Red Team | SecurityRAT |
|------|-------------------------------|-------------------|----------------|-------------|
| AI Agent 原生 | ✅ agentskills.io 标准 | ❌ 需转换 | ❌ 需转换 | ❌ |
| 跨框架映射 | ✅ 6 框架合一 | ❌ 仅 ATT&CK | ⚠️ 部分 | ⚠️ 有限 |
| 技能数量 | 754 | 600+ | 700+ | 有限 |
| 永久免费 | ✅ Apache 2.0 | ✅ | ✅ | ❌ |
| 分步执行指南 | ✅ 结构化 Markdown | ⚠️ 概述 | ✅ Atomic 测试 | ❌ |
| 平台兼容 | 20+ | N/A | 自定义 | 自定义 |

## 核心研判

**优势**：
1. **唯一同时映射 6 个行业框架的开源技能库** — 一个技能六个合规复选框，无可匹敌
2. **AI Agent 原生设计** — agentskills.io 标准保证与所有主流 AI 编程工具兼容
3. **非简单脚本集合** — 每个技能编码真实从业者工作流而非生成摘要
4. Apache 2.0 许可对商业使用友好
5. MITRE F3 反欺诈框架映射极其前沿（2026-04 才发布）

**风险/局限**：
1. 非 Anthropic 官方项目，品牌是蹭名字（已声明）
2. 754 技能的**质量一致性**待验证 — 可能存在部分浅层技能
3. 社区活跃度和贡献接受度未知
4. 跨框架映射的**校验机制**依赖于上游框架更新频率

## 关键文件路径速查

```
/mukul975/Anthropic-Cybersecurity-Skills
├── skills/                  # 754 个结构化技能 (Markdown + YAML)
├── docs/
│   ├── mitre-f3-mapping.md  # F3 映射文档
│   └── framework-mappings.md
├── assets/
│   └── banner.png
├── templates/               # 技能模板
└── LICENSE                  # Apache 2.0
```

## 总结

Anthropic-Cybersecurity-Skills 是 AI Agent 安全领域最全面的结构化知识库。其 6 框架合一映射是独一无二的竞争力，MITRE F3 反欺诈框架支持更是前沿。对于需要在 AI 编程工具中嵌入网络安全能力的团队，这是目前最优的开源选择。但对于质量一致性和社区健康度需要持观察态度。
