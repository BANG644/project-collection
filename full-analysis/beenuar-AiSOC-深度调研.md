# beenuar/AiSOC 深度调研

> 一句话定位：开源、可自托管的 AI 安全运营中心（SOC）——接入遥测、关联告警、用「每一步都可审计」的 AI agent 调查事件、人类审批后响应。
> 
> **元数据**：⭐ 6,074 ｜ 语言 Python（monorepo：apps/web + services/* + packages/* + plugins/*）｜ 许可 MIT（由 Cyble 资助并开源）｜ 默认分支 main ｜ 末提交 2026-11-01 ｜ 调研日期 2026-11-02

## 一、项目亮点（差异化）

1. **「可执行是挣来的，不是声明的」**：规则必须被真实事件经真实连接器+引擎重放、并被「看着它触发」才进入编译规则集；1,362 条无法触发的规则被明确拒绝（ratchet 只降不升）。
2. **AI 全程留痕**：agent 的每个 prompt、工具调用、引用、判定、token 成本都写入 Investigation Ledger，并导出自签名证据包（OCSF 1.9.0，字节一致）。
3. **零凭据启动**：`make up` 自带 ~2GB 本地模型（llama3.2:3b-instruct-q4_K_M），无需任何 API key 即可产出真实 triage 判定；另内置 CISA KEV 威胁情报（公开源）。
4. **诚实工程文化**：README 直白列出「未测量即标 not measured，绝不写 0」「演示/样本不是真实事件」「无托管供应商被实测过」，并附 27 页技术指南 PDF。

## 二、核心架构

事件脊（spine）是 Kafka，分层服务化：

```
遥测 → services/ingest（归一化+activity projection）
     → services/fusion（2530 可执行规则 / 7015 在盘，+76 滑动窗口）
     → 关联分组 incidents
     → services/agents（调查 agent：lake 查询/图遍历/富集，写入 Investigation Ledger）
     → services/actions（playbook，三开关同意 + 持久化审批暂停）
     → Postgres（警报/租户）· ClickHouse（事件湖/狩猎）· Neo4j（实体图）
     → services/mcp（MCP server：Claude/Cursor/Continue）
```

87 个点击即连的数据连接器（Splunk/Sentinel/Elastic/CrowdStrike/Okta/AWS/K8s…），`packages/aisoc-migrate` 翻译 Splunk SPL/Sentinel KQL/Elastic EQL（**不能忠实翻译的宁可拒绝**）。

## 三、应用场景与启发

- **可复用范式**：把「AI agent 的每一步决策都作为不可变证据」的设计，对任何需要合规/可问责的 AI 系统（金融、医疗、政企）都值得借鉴——「receipts 优先于结论」。
- **反 hype 模板**：AiSOC 的 `measure_triage_reliability.py`、负向控制（negative control）、「unmeasured≠0」等实践，是把「AI 能力声明」变成「可复现测量」的范本，可直接迁移到自有 agent 评测。
- **对用户的价值**：若构建「AI 辅助决策 + 人类兜底」类产品（如错题归因项目里的归因链路审计），Investigation Ledger + 签名证据包的思路能用上。

## 四、源码深度解读

**① 信任度测量（诚实工程的代表作 `scripts/measure_triage_reliability.py`）**——其 docstring 自揭：此前发布的「44/50、50/50」数字实际来自一个**从未运行过**的脚本（import 了已被移除的常量），本工具通过导入生产 prompt/parser 可复现地给出「为何失败」：

```python
"""Measure how often the local model returns usable auto-triage output.
... the figures published from it ("44 of 50", "50 of 50") describe a run
nobody could have performed. ...
Every record carries its provenance — code revision, model requested and the
model the endpoint says it answered with, prompt name/version/sha256, ..."""
CORPUS = AGENTS_ROOT / "tests" / "eval_data" / "synthetic_incidents.json"
```

**② 架构全景**：`docs/architecture/README.md` 用 11 步 + 5 图把上述脊链路逐步映射到代码（每个框都链接源码），是「文档即导航」的优质实践。

## 五、全网口碑

- 6k⭐、v21.0.0、由安全厂商 Cyble 出资并 MIT 放出（无功能阉割、无遥测），在「开源 AI SOC」细分里稀缺。
- 口碑两极但总体正面：赞赏其审计/可问责深度与诚实度；质疑集中在「太年轻、广度可能超过单组织维护深度」「核心 triage 依赖本地 3B 模型、且无托管供应商实测」——项目自己已把这些标为限制而非掩盖。

## 六、竞品对比 + 核心研判

| 维度 | AiSOC | Splunk/Elastic SIEM | MS Security Copilot | Wazuh+AI |
|---|---|---|---|---|
| 开源 | ✅ MIT | ❌ 商业 | ❌ 商业 | ✅ 但 AI 弱 |
| 本地模型 | ✅ 零凭据 | ❌ | ❌ 云 | 需自接 |
| 证据可审计 | ✅ 签名包 | 中 | 低 | 低 |
| 连接器 | 87+ | 海量 | 微软生态 | 中 |

**核心研判**：AiSOC 在「开源 + 本地推理 + 审计优先」交集上几乎无直接对手，工程诚实度罕见且稀缺。主要风险是项目年轻（单组织主导、广度摊薄）、本地 3B 模型在复杂告警上的可靠性上限。它更适合作为「可审计 AI 决策系统」的参考架构与自托管 SOC 实验台，而非即刻替代企业 SIEM。值得长期跟踪其评测基线与连接器生态。

## 七、关键文件路径速查

-  ingest 归一化：`services/ingest/internal/normalizer/`
-  fusion 检测引擎：`services/fusion/app/core`
-  调查 agent + Ledger：`services/agents/app/investigator`、`services/agents/app/ledger`
-  MCP server：`services/mcp/src/tools`
-  可信测量：`scripts/measure_triage_reliability.py`
-  架构文档：`docs/architecture/README.md` ｜ 现实清单：`docs/audit/REPOSITORY_REALITY.md`
