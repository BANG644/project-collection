# 🎒 toon-format/toon — 深度调研报告

> **仓库**: [toon-format/toon](https://github.com/toon-format/toon)
> **调研日期**: 2026-08-05 | **数据来源**: GitHub API + 仓库源码树 + SPEC + 官方 benchmark 结果文件
> **数据**: ⭐ 25,068 | 🍴 1,112 | **语言**: TypeScript | **许可**: MIT | **最后推送**: 2026-08-02
> **作者**: [Johann Schopplich](https://github.com/johannschopplich)（Nuxt/UnJS 生态活跃开发者）
> **当前规范版本**: SPEC v4.1 | 最新 Release: `v4.1.0`（2026-07-26）

---

## 一、项目定位

**Token-Oriented Object Notation（TOON）是一种把 JSON 数据模型重新编码、专为塞进 LLM prompt 而设计的序列化格式**——不是替代 JSON 做程序间通信，而是做**翻译层**：代码里继续用 JSON，喂给模型前编码成 TOON。

一句话概括其设计取舍：**拿 YAML 的缩进结构管嵌套，拿 CSV 的表格形态管均匀数据，再补上 JSON/YAML/CSV 都没有的显式 schema 声明（`[N]` 长度 + `{fields}` 字段列表）**。

本仓库是 **TypeScript/JavaScript 参考实现**；规范本体已独立到 [`toon-format/spec`](https://github.com/toon-format/spec)。

---

## 二、项目亮点（差异化）

1. **"省 token" 是被官方 benchmark 反向限定过的主张**。README 专门写了 `When Not to Use TOON` 一节，明确列出四种"别用 TOON"的场景（深嵌套、半均匀、纯表格、延迟敏感）——这在动辄宣称"节省 60% token"的同类项目里极为罕见的自我设限。
2. **真正的卖点不是压缩率，是「准确率/token 比」**。官方 244 道检索题 × 4 模型的实测：TOON 用 2,474 token 拿到 72.2% 准确率，JSON 用 4,308 token 只拿 71.4%。**TOON 的准确率反而高于原始 JSON**，效率比 29.2 vs 16.6 acc%/1K tok。
3. **四种"形态（form）"自动派生，不需要用户配置**。inline / tabular / keyed-tabular / list 四态由数据形状自动判定，编码器逐列做均匀性分类。
4. **显式长度与字段列表 = 给 LLM 的护栏**。`forecast[3]{day,temp{min,max},condition,rainChance}:` 这一行同时声明了元素数、字段名和嵌套字段组，模型可以自校验行数是否对得上。基准数据集里专门设计了 `Array truncated` / `Extra rows` / `Inconsistent field count` 三类**结构性损坏样本**来验证这个护栏是否真的起作用。
5. **规范与实现分仓、多语言生态**。Python / Rust / Go / Java / Swift / .NET 等社区实现，spec 仓库提供语言无关的 conformance test fixtures。

---

## 三、核心架构

### 3.1 仓库结构（monorepo，pnpm workspace）

```
packages/toon/src/
  ├── encode/
  │    ├── tabular.ts       ← 表格形态判定核心（本报告重点走读）
  │    ├── encoders.ts      ← 主编码调度
  │    ├── normalize.ts     ← JSON 值归一化 / 类型守卫
  │    ├── primitives.ts    ← 原语编码
  │    ├── raw-string.ts    ← 引号最小化策略
  │    └── replacer.ts      ← 类似 JSON.stringify 的 replacer 钩子
  └── decode/
       ├── scanner.ts        ← 词法扫描
       ├── line-reader.ts    ← 缩进感知的行读取
       ├── parser.ts         ← 语法解析
       ├── event-builder.ts  ← 事件流构建（供流式消费）
       ├── validation.ts     ← 声明长度 vs 实际行数校验
       └── errors.ts
packages/cli/               ← npx @toon-format/cli，支持 --stats
benchmarks/                 ← 独立子包：数据集 + 评测脚本 + 结果落盘
docs/                       ← VitePress 文档站（toonformat.dev）
```

**关键设计**：encode 与 decode 完全对称拆分，decode 侧独立出 `event-builder.ts` 意味着解码不是"一次性建整棵树"，而可以走事件流——这对超长 LLM 输出的增量解析是必要的。

### 3.2 四种形态

| 形态 | 触发条件 | 语法样例 |
|------|---------|---------|
| **inline** | 原语数组 | `alerts[2]: frost,wind` |
| **tabular** | 均匀对象数组 | `forecast[3]{day,temp{min,max},condition}:` + 每行一条 |
| **keyed tabular** | 值为均匀对象的对象（≥2 项） | `environments[2:]{region,replicas,debug}:` + `production: eu-central-1,6,false` |
| **list** | 以上都不满足（混合类型/非均匀） | `- ` 逐项，空对象为裸 `-` |

注意 keyed tabular 的标记是**长度后的冒号** `[2:]`——一个字符区分"数组"与"带键映射"，这种极简标记法是 TOON 的典型风格。

---

## 四、应用场景与启发

### 4.1 直接可用的场景

| 场景 | 为什么 TOON 合适 |
|------|-----------------|
| **RAG / 检索结果注入 prompt** | 检索返回的 chunk 元数据（id/score/source/title）天然均匀，tabular 形态压缩率最高（官方 contacts 数据集 −66.5% vs JSON） |
| **给 Agent 喂工具返回的列表数据** | 数据库查询结果、API 分页列表、日志条目都是均匀记录 |
| **Feature flags / 配置映射注入** | keyed tabular 专为此设计，官方 feature-flags 数据集 −54.6% vs JSON |
| **大批量 few-shot 示例** | 示例集通常字段一致，省下的 token 可以多塞几个 shot |
| **成本敏感的高频调用链路** | 每次调用省 30-60% 输入 token，规模化后是真金白银 |

### 4.2 更重要的方法论启发

这个仓库真正值得借鉴的**不是格式本身，而是它论证格式价值的方式**：

1. **"省 token" 必须配 "掉不掉准确率" 一起测**。绝大多数 prompt 压缩方案只报压缩率，TOON 把检索准确率作为一等指标，并且**双轨评测**（Mixed-Structure Track 排除 CSV，Flat-Only Track 才让 CSV 上场），保证 like-for-like 对比。任何做 prompt 工程优化的人都应该抄这套评测框架。
2. **把"结构损坏"当成 benchmark 数据集**。`Array truncated` / `Extra rows` / `Inconsistent field count` / `Missing required fields` 这四个人造损坏数据集，测的是"模型能否发现数据本身有问题"。这是评估**数据格式可靠性**（而非仅仅可读性）的稀缺思路。
3. **显式 schema 前置是给 LLM 的最便宜护栏**。与其在 prompt 里写"下面有 3 条记录，字段是…"，不如把它编码进数据格式的第一行。这个思路可以推广到任何自定义 DSL 设计。
4. **主动写"什么时候别用我"**。README 的 `When Not to Use TOON` 段落把 tabular eligibility 0% / 40-60% / 100% 三档的表现差异摊开讲，甚至承认"纯表格场景 CSV 更小，TOON 那 5-10% 开销买的是可靠性不是体积"。这种诚实反而是最强的可信度背书。

### 4.3 遇到什么问题该回来看这个仓库

- 「prompt 里塞了一大堆 JSON，token 账单太贵」→ 先跑 `cat data.json | npx @toon-format/cli --stats` 看看你的数据形状能省多少
- 「想设计一个给 LLM 读的自定义格式」→ 抄 `[N]{fields}` 的显式 schema 声明思路 + 四态自动派生
- 「要给格式/prompt 优化做 A/B 评测」→ 抄 `benchmarks/` 的双轨 + 结构损坏数据集设计

---

## 五、源码深度解读

### 5.1 `packages/toon/src/encode/tabular.ts` — 表格形态的判定核心

整个 TOON 的压缩收益都取决于"这批数据能不能上 tabular 形态"，判定逻辑集中在这一个文件。核心是三个导出函数 + 一个递归分类器：

```ts
/** Classifies rows into a tabular field list, or undefined when they are not uniformly tabular. */
export function extractTabularFields(rows: readonly JsonObject[]): FieldNode[] | undefined {
  if (rows.length === 0) return
  const firstKeys = Object.keys(rows[0]!)
  if (firstKeys.length === 0) return

  // All objects must have the same set of keys (order per object may vary)
  for (const row of rows) {
    if (Object.keys(row).length !== firstKeys.length) return
    for (const key of firstKeys) {
      if (!Object.hasOwn(row, key)) return
    }
  }

  const fieldNodes: FieldNode[] = []
  for (const key of firstKeys) {
    const fieldNode = classifyColumn(key, rows.map(row => row[key]!))
    if (!fieldNode) return          // 任一列不合格 → 整体降级为 list 形态
    fieldNodes.push(fieldNode)
  }
  return fieldNodes
}
```

三个值得注意的工程决策：

- **键序不敏感、键集敏感**：注释明写 "order per object may vary"，只要键集合相同就算均匀。这让来自不同 ORM/序列化器的数据也能吃到 tabular 收益。
- **全有或全无**：任何一列分类失败就整体 `return undefined` 降级。没有"部分列表格化"的中间态——这是为了让格式保持可预测，代价是半均匀数据（README 承认的 40-60% eligibility 区间）收益骤降。
- **递归嵌套字段组**在 `classifyColumn` 里实现：

```ts
function classifyColumn(name: string, values: readonly JsonValue[]): FieldNode | undefined {
  // Uniform-primitive column: a bare leaf field
  if (values.every(value => isEncodablePrimitive(value))) return { name }

  // Nested-uniform column: non-empty objects sharing one key set, classified recursively
  if (!values.every(value => isJsonObject(value) && !isEmptyObject(value))) return

  const children = extractTabularFields(values as JsonObject[])
  if (!children) return
  return { name, children }
}
```

这段递归就是 `temp{min,max}` 这种**嵌套字段组折进表头、行仍保持扁平**能力的来源——`FieldNode` 是一棵树，行值则由 `collectRowLeaves` 按同一棵树的叶子顺序拍平。表头承担全部结构信息，行只剩纯数据，这是 TOON 相对 YAML 拿到额外压缩的关键。

### 5.2 keyed tabular 的门槛：为什么是 ≥2

```ts
export function extractKeyedTabularFields(value: JsonObject): FieldNode[] | undefined {
  const entryValues = Object.values(value)
  // At least two entries whose values are uniform non-empty objects
  if (entryValues.length < 2) return
  if (!entryValues.every(v => isJsonObject(v) && !isEmptyObject(v))) return
  return extractTabularFields(entryValues as JsonObject[])
}
```

单条记录走 keyed tabular 是负收益（表头开销大于省下的重复键），所以硬编码 `< 2` 直接退出。小而实的边界判断，说明作者是拿真实数据调过的。

---

## 六、官方基准数据（实测摘录）

### 6.1 Token 效率（Mixed-Structure Track，TOON vs 各格式总量）

| 对比对象 | 差值 | 绝对 token |
|---------|------|-----------|
| **TOON** | — | **264,734** |
| vs JSON（pretty） | **−32.7%** | 393,637 |
| vs JSON compact | **+1.6%** ⚠️ | 260,451 |
| vs YAML | −15.7% | 314,140 |
| vs XML | −(约 33%) | — |

⚠️ **关键诚实点**：对 **JSON compact**（无空格压缩 JSON），TOON 在混合结构下总体反而**多 1.6%**。分数据集看，深嵌套配置 +6.7%、半均匀事件日志 +19.9%，只有 100% tabular 的数据集（feature flags −32.8%、contacts −42.9%）才赢。**这是绝大多数二手介绍文章会略掉的数字。**

### 6.2 检索准确率（244 题 × 4 模型：claude-haiku-4-5 / gemini-3.6-flash / gpt-5.4-nano / grok-4.5）

```
TOON           29.2 acc%/1K tok  │  72.2% ±2.8  │  2,474 tokens
JSON compact   23.8 acc%/1K tok  │  69.0% ±2.9  │  2,892 tokens
YAML           20.1 acc%/1K tok  │  70.1% ±2.9  │  3,487 tokens
JSON           16.6 acc%/1K tok  │  71.4% ±2.8  │  4,308 tokens
XML            14.4 acc%/1K tok  │  70.7% ±2.9  │  4,909 tokens
```

TOON 在绝对准确率上也是第一（72.2%），且 token 最少。但注意误差带 ±2.8——TOON 72.2% 与 JSON 71.4% 的差距在统计上并不显著，**真正稳的结论是"同等准确率下省 42.6% token"，而非"TOON 让模型更聪明"**。

---

## 七、社区口碑

- **⭐ 25,068 / 🍴 1,112**，2025 年底开源后快速起量，属于 2026 年 LLM 工程圈的现象级小库。
- **高赞 issue 反映社区关注点**：
  - `#19 Benchmark against Structured Output Endpoints`（👍25，**仍 open**）— 社区最想知道的是：在已有 structured output / JSON mode 的模型上，TOON 还有多少价值？这是目前**未被官方回答的最大质疑**。
  - `#2 Retrieval Accuracy Benchmarks`（👍11，已闭）— 社区一开始就要求补准确率数据，作者照做了，这是 benchmark 体系成型的起点。
  - `#10 Decode`（👍9，已闭）— 早期只有 encode，社区推动补齐解码。
  - `#32 Online playground` / `#80 TOON TOOLS website`（👍9/👍7）— 社区自发做了在线转换对比站。
  - `#187 [Proposal] Mathematical Formalization of TOON's Efficiency vs JSON`（👍7）— 有人尝试给效率优势做字符级数学建模，说明吸引到了偏理论的贡献者。
- **规范治理正规化**：spec 独立仓库 + RFC 流程 + 语言无关 conformance tests，是奔着"多语言标准"去的，不是单库玩具。
- **迭代节奏**：v2.3.1（07-16）→ v4.0.0（07-22）→ v4.1.0（07-26），**十天内跨两个大版本**。速度快是好事，但也意味着 breaking change 频繁，生产接入需要锁版本。

---

## 八、竞品对比

| 方案 | 定位 | 相对 TOON |
|------|------|-----------|
| **JSON compact** | 事实标准 | 混合结构下 token 可能更少（TOON +1.6%）；但无显式长度/字段声明，模型无法自校验；纯 tabular 场景明显落后 |
| **YAML** | 人类友好配置 | 可读性接近，但重复键导致 token 多 15.7%；无长度护栏 |
| **CSV** | 纯表格 | 体积最小，但**无法表达嵌套**，混合结构必须有损扁平化；TOON 用 5-10% 开销换回结构表达力 |
| **XML** | 老牌标记 | 全面落后（token 最多、准确率不占优） |
| **Markdown 表格** | prompt 里最常见的土办法 | 无类型、无长度声明、宽列对齐浪费 token；TOON 是它的严肃版 |
| **LLMLingua 类 prompt 压缩** | 模型侧语义压缩 | 有损、需额外模型推理；TOON 是**无损 + 零推理成本**的结构化压缩，两者可叠加 |
| **模型原生 structured output** | 约束**输出** | 关注点不同：TOON 优化**输入**。二者互补，但 issue #19 提出的对比问题官方尚未回答 |

---

## 九、核心研判

### ✅ 值得采用的情况
- 你的 prompt 里有**均匀对象数组**（RAG 结果、DB 记录、日志、配置映射），且规模大到 token 成本可感知
- 你已经在用 pretty JSON 塞 prompt（那是最差情况，TOON 直接省 32.7%~66.5%）
- 你需要模型能**发现数据被截断/字段缺失**——显式 `[N]{fields}` 是目前最便宜的实现

### ⚠️ 风险与保留
1. **对 JSON compact 的优势并非普遍成立**。若你的数据深嵌套或半均匀，切 TOON 可能**倒亏 token**。上生产前必须用 `--stats` 在自己的真实数据上量一遍，不要信任何二手宣传数字。
2. **准确率优势在误差带内**。72.2% vs 71.4%（±2.8）不构成"TOON 更准"的强结论。真正稳的收益是**同准确率下的 token 节省**。
3. **版本迭代过快**。10 天跨 v2→v4，SPEC 已到 v4.1。生产环境必须锁定 `@toon-format/toon` 版本并跟踪 spec changelog，否则编解码两端版本漂移会静默出错。
4. **延迟未必改善**。README 自己承认"某些部署（尤其本地/量化模型）处理 compact JSON 反而更快"。token 少 ≠ 时间短，TTFT 要自己测。
5. **structured output 场景下的价值未被验证**（issue #19 仍 open）。如果你的链路已经全面依赖模型原生 JSON mode，TOON 的边际收益不明。

### 🎯 一句话研判
**TOON 是 2026 年 prompt 工程领域少见的"数据支撑扎实 + 自我设限诚实"的基础设施项目**。它的最大价值不在于替代 JSON，而在于给出了一套**可复用的评测方法论**——任何声称能省 token 的方案，都应该像它一样同时公布准确率、双轨对比、以及"什么时候别用我"。至于要不要在你的项目里用，答案完全取决于一件事：**跑一次 `npx @toon-format/cli --stats`**。

---

## 十、关键文件路径速查

| 路径 | 说明 |
|------|------|
| `packages/toon/src/encode/tabular.ts` | ⭐ 表格/keyed-tabular 形态判定与嵌套字段组递归分类，全库压缩收益的源头 |
| `packages/toon/src/encode/encoders.ts` | 主编码调度，四态派发 |
| `packages/toon/src/encode/raw-string.ts` | 引号最小化策略（TOON 省 token 的另一来源） |
| `packages/toon/src/decode/validation.ts` | 声明长度 vs 实际行数校验（护栏落地处） |
| `packages/toon/src/decode/event-builder.ts` | 事件流式解码，支持增量消费 |
| `packages/cli/src/cli-entry.ts` | `npx @toon-format/cli --stats` 入口 |
| `benchmarks/results/token-efficiency.md` | ⭐ 官方 token 效率原始结果（含对 JSON compact 的劣势数字） |
| `benchmarks/results/retrieval-accuracy.md` | ⭐ 官方 244 题 × 4 模型准确率结果 |
| `benchmarks/src/structural-corruption.ts` | 结构损坏数据集生成（截断/超行/字段缺失） |
| `benchmarks/src/questions/` | 按数据集分类的检索题库（analytics/event-logs/github/keyed/nested/tabular…） |
| `SPEC.md` | 指向独立规范仓 `toon-format/spec` 的转发说明 |
| `docs/` | VitePress 文档站源码（toonformat.dev） |

---

> **调研方法**：GitHub API 拉取仓库元数据 / 完整文件树（171 项）/ README（35.5KB）/ SPEC.md / benchmark 结果文件 / `encode/tabular.ts` 源码 / 按 reactions 排序的 issue 列表。所有数字均来自仓库内官方文件，未采用二手来源。
