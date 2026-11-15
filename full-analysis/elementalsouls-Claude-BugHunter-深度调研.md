# 🔬 elementalsouls/Claude-BugHunter - 全方位深度调研

> 调研日期：2026-11-16 ｜ 数据源：GitHub API（仓库/Issue/Release/源码）+ 全网口碑检索
> ⚠️ 本报告只写 README 之外的判断。安装命令与技能清单请直接看官方 README。

## 📌 一句话定位

把 Claude Code 等编码 Agent 变成「**有纪律的高级漏洞赏金猎人 / 外部红队操作员**」的技能包：83 个按主题自动触发的 SKILL.md + 15 个 slash 命令 + 一个确定性 engagement 引擎，把从 scope（界定范围）→ recon（侦察）→ hunt（漏洞挖掘）→ validate（验证门禁）→ report（报告）的完整流程编码成 Agent 可执行的方法论，知识来源于 681 份公开的 HackerOne 报告（433 份逐条引用可审计）。

一句话点破本质：**它不是扫描器、不是利用框架，而是「方法论 + 知识库 + 流程门禁」——把资深安全研究员的工作纪律注入会编码的 Agent。**

## ⭐ 项目亮点

1. **主题自动触发，无需记技能名**：你描述「端点上看到一个 `?url=` 参数」，Agent 自动只加载 `hunt-ssrf`，而不是把 83 个技能全塞进上下文。这是「按需加载知识」的教科书实现，直接缓解 Agent 的上下文预算问题。
2. **58 个 hunt-* 技能 + 24 类漏洞 + 681 份公开报告蒸馏**：每类漏洞配检测模式、payload 表、绕过表和攻击链模板，且 433 份报告逐条引用可审计（36 个 pattern-library 文件）。知识密度和可追溯性在同类开源包里罕见。
3. **七问门禁（7-Question Gate）作为提交前硬闸**：`triage-validation` 要求「攻击者现在能否用真实 HTTP 请求利用？影响是否在项目接受列表？」等 7 个问题全过才准出报告，并给出 PASS/KILL/CHAIN-REQUIRED/DOWNGRADE 四种分支结论——**把「要不要报」这个主观判断结构化为可判定流程**。
4. **显式的 scope  discipline（范围纪律）**：内置 in-scope 门禁与 PII 脱敏，明确排除内部 AD 攻击、C2、后渗透持久化、恶意软件、大规模定向。这种「主动划红线」在攻击性工具里非常克制，也是它能被安全界正面评价的原因。
5. **多宿主可移植 + 混合许可**：SKILL.md 是开放格式，知识层能进 Claude Code / OpenCode / Codex / Hermes / Antigravity；slash 命令与 engagement 引擎为 Claude Code 专有。Python/shell 辅助用 MIT，方法论内容用 CC BY 4.0——许可分层清晰。

## 🏗️ 项目架构全景

### 六阶段工作流 = 主架构（docs/architecture.md 定义）

```
SCOPE → RECON → HUNT → VALIDATE → REPORT  (+ 贯穿的 redteam-mindset / IR-detection)
 5技能    5技能    83核心层   7问门禁       平台化报告模板
```

83 个技能按「阶段」和「角色能力栈」两种视图组织：主视图是 6 阶段流程（58 个 `hunt-*` 子栈 + 8 个企业平台攻击层 + 集成层 + 决策树）；备选视图是 3 层能力栈（方法论+侦察 → Hunt Arsenal → Ship It）。技能来源标注为 `original`（55）/ `community`（20，v3）/ `vendored`（8，来自 shuvonsec/claude-bug-bounty, MIT）——**来源透明化**是信任建设的关键设计。

### 目录结构 & 设计哲学

```
cbh/cli.py + cbh/data/skill_index.json     # 确定性 CLI + 打包后的技能/报告索引
commands/*.md (15)                        # slash 命令：hunt / recon / triage / report / autopilot ...
docs/disclosed-reports/hunt-*.md (36)      # 逐类漏洞的公开报告蒸馏，可审计
docs/verification/                         # 真实靶场验证（DVWA/Juice Shop/CVE/Jenkins...）
docs/superpowers/                          # 设计规格与计划（ledger memory、native 引擎）
.github/workflows/                         # doc-count-check / eval-harness / leak-guard / skill-lint ...
```

**设计哲学：知识（SKILL.md）+ 编排（commands/engine）+ 证据（disclosed-reports/verification）+ 门禁（validate）四位一体**。CLI（cbh）是「把技能内容桥接到真实 runner」的粘合层，让方法论不止于文本。

### 技术栈 & 依赖

- Python 3（stdlib + 可选 requests），无构建步骤，可 `pipx` 安装。
- 外部工具链：subfinder / httpx / crt.sh（侦察）、Burp Suite MCP（可选，代理流量）、Playwright（浏览器执行）。
- CI 门禁：doc-count-check、leak-guard（防泄密）、skill-lint、eval-harness、star-history——**把「知识库质量」当代码来 CI**。

## 💡 应用场景与启发（重点章节）

### 典型使用场景

- **授权的漏洞赏金项目**：in-scope 的 H1/Bugcrowd/Intigriti/Immunefi 项目，用 Agent 系统化枚举攻击面、按漏洞类别深挖、生成平台感知的报告。
- **外部红队演练**：针对企业互联网暴露面（M365/Entra、Okta、VPN 设备、vCenter、云 IAM）的攻击链测试。
- **安全教学 / CTF / 靶场**：DVWA、OWASP Juice Shop 等受控环境里学习结构化漏洞挖掘方法。

### 可借鉴的解决方案模式（最具迁移价值）

1. **「按需加载知识」的触发设计**：用描述匹配而非显式调用来决定加载哪个技能。任何大型知识库/技能库（包括你自己的工作区 skills）都可以借鉴——**别把所有知识一次性灌给 Agent，按话题动态加载**。
2. **把「判断」变成「门禁 + 分支结论」**：7-Question Gate + PASS/KILL/CHAIN/DOWNGRADE 四态，是把主观决策结构化的范本。可迁移到代码 review 准入、论文方法评估、需求验收等任何「要不要放行」的场景。
3. **知识来源透明化与可审计**：每个技能标注 original/community/vendored，681 份报告 433 份逐条引用。做知识密集型 Agent 时，「这条知识从哪来」比「这条知识是什么」更影响可信度。
4. **主动声明 out-of-scope**：攻击性/高风险 Agent 必须显式划红线。这个「有所不为」的设计，反而提升了专业可信度——值得任何 dual-use 工具借鉴。
5. **确定性引擎约束 Agent 不跑偏**：`engine/` 把攻击面映射到对应技能，防止 Agent「freelancing」到未经验证的知识之外。**给自由度的 Agent 配一个确定性路由层**是重要架构模式。

### 同类需求的可参考思路 / 可复用片段

- `cbh/cli.py` 的 `configure_http_proxy()` 值得单独抄：它保证「企业 HTTPS_PROXY 环境变量不会悄悄关掉 TLS 校验」，只有显式 `insecure=True`（Burp 场景）才禁用证书验证——**安全默认值设计**的范例。
- `docs/recon-manifest.schema.json` 的 recon→hunt 交接契约：用结构化 manifest 在两个阶段间传递攻击面数据，避免信息丢失。
- `hunt <target>` 的 engagement 目录脚手架（`~/Targets/<name>/`）：把每次测试变成有模板、可复盘的工程化产物。

## 🧠 核心源码解读（克制代码量）

### 入口：cbh/cli.py 的五子命令闭环

```
cbh recon <target>     → recon/<target>/manifest.json（recon→hunt 交接契约）
cbh surface <target>   → 读 manifest，输出 P1/P2/Kill 排序的攻击面
cbh classify <url>     → URL 匹配 hunt-* 技能 + 从 disclosed-reports 排攻击候选
cbh triage <finding>   → 跑 7-Question Gate → PASS/DOWNGRADE/KILL + 理由
cbh report <finding>   → 生成 H1/Bugcrowd/Intigriti/Immunefi 报告草稿
```
五个子命令对应 engagement 的关键跃迁点，**把方法论文本变成可执行的确定性管线**。

### 关键模块：代理与 TLS 的安全默认值（`cbh/cli.py`）

```python
def configure_http_proxy(proxy_url=None, insecure=False):
    """TLS 校验仅在 insecure=True（显式 Burp opt-in）时关闭；
    企业 HTTPS_PROXY/HTTP_PROXY 仍生效但保持证书校验 ON——
    这样企业代理环境变量永远不会在探测生产目标时悄悄关闭 TLS 验证。"""
```
**设计解读**：这是一个被很多人忽略的安全细节——「环境里有代理」不等于「可以关闭证书校验」。作者把「便利性开关」和「安全性开关」严格分离，是专业安全工具该有的默认值。

### 关键模块：技能来源标注与计数（docs/architecture.md）

```
83 skills: 55 original, 20 community (v3), 8 vendored (shuvonsec/claude-bug-bounty, MIT)
681 disclosed reports curated, 433 individually cited & auditable across 36 pattern files
```
**设计解读**：可审计性被当成一等公民——技能数量、来源、报告引用数都精确到个位并标注出处。这直接回应了「AI 生成的安全知识可信吗」的质疑。

### 隐藏特性 & 未文档化细节

- **engagement 状态账本**：`docs/superpowers/` 下有 `engine-native-ledger-memory-design.md` 和 `autopilot-ledger` 计划——说明项目在构建「跨会话记忆状态账本」，避免长周期测试丢失上下文。
- **验证靶场是真实搭的**：`docs/verification/` 下有 phase2h 的 docker-compose + nginx 配置、多个 CVE 复现（Apache CVE-2021-41773、Jenkins CVE-2024-23897），不是纸上谈兵。
- **IR 检测技能**：`mid-engagement-ir-detection` 能识别测试中途 SOC 打补丁、外部攻击者活动、基线漂移，并把观察转成可交付发现——这是很实战的细节。

## 📐 架构决策与设计哲学

- **非线性工作流**：方法论层编码的是「非线性」的 recon→hunt→validate→report，允许在任意阶段跳入（"you can jump in at any phase mid-engagement"），契合真实测试的迭代性。
- **Claude-Code-only 的编排，跨宿主的知识**：明确接受「slash 命令和引擎依赖 Claude Code 执行模型」这一事实，不强行全平台一致——**务实的边界取舍**。
- **版本演进**：v2.0（2026-05-25，报告蒸馏 + 5 个缺失面 + 链 + engagements）→ v2.1（2026-06-05，社区技能 + CI gate + 安全修复）。但 Issue #82 显示 3 个 SKILL.md description 超过 1024 字符限制——**技能暴增带来的规范债**开始显现。

## 🌐 全网口碑画像

### 好评共识

- OffSec Blog（2026-10）评价其「scope discipline 异常明确，值得细读」，并认可「确定性 engine 让 Agent 不越出知识边界」。
- vibecodes.net / valuealignmentconsulting 给出「Wide coverage」「Built-in scope and accepted-impact gates」等正面标签，editor score 6.5、综合 3.85/5。
- 热度真实：约 6,188⭐ / 900+ fork，2026-11 中旬上 trending，单周 +355 星（vibecodes），是 Agent Skills 安全赛道头部。

### 差评共识 & 踩坑高发区

- **法律与授权边界**：多家媒体（agentbeam / vibecodes）反复强调「只用于你拥有或书面授权的目标」；Anthropic 运行时网络安全护栏可能拦截 dual-use 工作，需加入 Cyber Verification Program。
- **安装信任问题**：agentbeam 专门发文「install and scope checks」——第三方 Agent 指令以你的权限运行，应 pin 已审阅版本、隔离测试主机；`--burp-mcp` 会把 Burp 桥接到所有宿主， powered 但危险。
- **Claude Code 依赖**：完整体验（slash 命令 + 引擎）只在 Claude Code；其他宿主只有知识层。
- **上下文与规范债**：Issue #82（open）——3 个技能描述超过 Anthropic 规定的 1024 字符上限；#87（open）安装文案问题。

### 争议焦点

- **「知识包 vs 武器化」的定位**：安全界认可它是「methodology, not munitions」（方法论非军火），但因为触及企业 CVE 链、云提权，讨论始终伴随「谁可以用、用在什么授权下」的争议。
- **行业大背景**：与 Cloudflare security-audit skill 等一起，被归入「Agent Skills 供应链」议题——第三方技能以 Agent 权限执行，代码审查与来源可信度成为核心关切。

### 维护者响应风格

- Issue #89 被关闭并转为 #88 继续（subagent pipeline 提案），说明维护者在做提案收敛；#.github 全套 issue template（bug/dx/false_positive/new_skill）显示流程化管理。
- 最近提交 2026-11-15（刷新 star history），活跃度高。

## ⚔️ 竞品对比

| 维度 | Claude-BugHunter | shuvonsec/claude-bug-bounty | Cloudflare security-audit skill | 传统扫描器（Burp/ZAP） |
|------|------------------|-----------------------------|----------------------------------|------------------------|
| 定位 | 外部攻击+红队方法论 | 赏金方法论（被本项目 vendored 8 技能） | 防御性代码审计 | 自动化漏洞扫描 |
| 知识规模 | 83 技能/681 报告 | 较小 | 单审计技能 | 规则库驱动 |
| 流程门禁 | 7 问 Gate + scope | 有方法论 | 弱 | 无（靠人判断） |
| 宿主 | 5 种（知识层） | Claude Code | Claude Code | 独立工具 |
| 输出 | 平台化赏金报告 | 赏金报告 | 代码审计意见 | 扫描报告 |

**选择建议**：授权的外部赏金/红队 → 本项目；防御性审计自己的代码库 → Cloudflare security-audit；自动化面扫描 → Burp/ZAP 配合本项目做「扫描后验证」。注意本项目 vendored 了 shuvonsec 的 8 个技能，两者非竞争而是承继关系。

## 🎯 核心研判

### 项目优势（不可替代的价值点）

- **知识密度 + 可审计性**：681 份公开报告蒸馏、433 份逐条引用、技能来源标注——这种「可追溯的 AI 安全知识」目前少见。
- **纪律性设计**：7 问门禁 + scope 红线 + PII 脱敏 + 确定性引擎路由，把「纪律」而非「攻击能力」作为核心卖点。
- **活跃维护 + MIT 许可（代码层）**：更新频繁（最近 11-15），可商用。

### 项目风险（潜在隐患和局限性）

- **高风险 dual-use 属性**：安装即用你的权限，Burp MCP 桥接触达实时流量；授权边界靠「使用者自觉 + prompt 门禁」，不是技术强制。合规失误后果严重。
- **上下文与规范债**：83 技能带来描述超限（#82）、技能间依赖与选择性安装的问题。
- **宿主割裂**：核心编排 Claude-Code-only，跨平台用户拿到的是「阉割版」。
- **许可分层需留意**：方法论内容 CC BY 4.0（非纯 MIT），商用分发要遵守署名要求。

### 适用场景 & 不适用场景

- ✅ 适用：授权赏金项目、外部红队、安全教学/CTF、受控靶场。
- ❌ 不适用：未授权测试、内部 AD/后渗透（作者明确排除）、日常代码仓库的防御性审计、无安全合规意识的团队。

### 趋势判断

**上升期**：2026-11 上 trending、周增 355 星、持续迭代，踩中「Agent Skills 安全化」风口。长期看，价值取决于两点：① Anthropic 网络安全护栏政策是否收紧（可能阻断 dual-use）；② 技能库膨胀带来的上下文/规范债能否治理（ledger memory 设计是积极信号）。**建议：安全从业者可作为「方法论结构」认真学习；采用时务必守住授权红线并 pin 版本、隔离环境。**

## 📂 关键文件路径速查

| 文件 | 作用 |
|------|------|
| `docs/architecture.md` | 6 阶段工作流 + 3 层能力栈双视图，83 技能全景 |
| `cbh/cli.py` | 五子命令 engagement 闭环 + 代理/TLS 安全默认值 |
| `docs/disclosed-reports/*.md` | 36 个漏洞类的公开报告蒸馏（可审计知识库） |
| `docs/recon-manifest.schema.json` | recon→hunt 阶段交接契约 |
| `docs/skills.md` / `docs/multi-harness.md` | 技能清单 / 多宿主安装差异 |
| `.github/workflows/leak-guard.yml` | 防泄密 CI 门禁 |
| `docs/superpowers/specs/*ledger*` | 跨会话状态账本设计（进行中特性） |
| `SECURITY.md` | 明确的 in/out-of-scope 授权边界声明 |
