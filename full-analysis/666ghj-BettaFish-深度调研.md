# 666ghj/BettaFish 深度调研

> 调研日期：2026-08-03 ｜ 仓库：https://github.com/666ghj/BettaFish ｜ 实时星标：41,920 ⭐
> 许可：**GPL-2.0** ｜ 主语言：Python ｜ 最后提交：2026-07-21（活跃）
> 定位：微舆——人人可用的多 Agent 舆情分析助手，"从 0 实现，不依赖任何框架"

---

## 一、项目定位

**BettaFish（微舆）** 是一个**纯 Python、零框架**实现的多 Agent 舆情分析系统。它把"舆情"建模成一场**多 Agent 论坛讨论**：多个分析 Agent（洞察/媒体/检索）各自产出观点，由一个"主持人"Agent 汇总引导，最终还原舆情原貌、预测走向、辅助决策。最大特色是——Agent 之间的消息传递**不用内存队列，而是用日志文件当总线**。

---

## 二、项目亮点

1. **从 0 实现、零依赖框架**：不依赖 LangChain/LangGraph/AutoGen 等任何 Agent 框架，所有 Agent 调度、节点编排、状态流转全部手写——是"读懂 Agent 本质"的极佳教学样本。
2. **日志文件即消息总线（独家设计）**：`ForumEngine/monitor.py` 的 `LogMonitor` 实时 `tail` 三个日志文件，把"文件变化"当 Agent 间通信信号，每攒够 5 条 Agent 发言就触发主持人——一种罕见却朴素可靠的进程间通信范式。
3. **论坛式多 Agent 协作**：把舆情分析变成"多名专家 + 一名主持人"的圆桌讨论，比单链 prompt 更贴近人类研判，也更易解释。
4. **五引擎职责分离**：ForumEngine（主持）/ InsightEngine（洞察）/ MediaEngine（媒体）/ MindSpider（爬取）/ QueryEngine（检索）各管一段，可独立演进。
5. **中文舆情场景闭环**：MindSpider 含 DeepSentimentCrawling（深度情感爬取，集成 MediaCrawler）+ BroadTopicExtraction（广域话题抽取），覆盖"采→析→议→报"全链路。

---

## 三、核心架构（基于真实仓库树）

```
ForumEngine/      # 论坛主持引擎
  llm_host.py     # ForumHost：用 Qwen3-235B（SiliconFlow）当主持人
  monitor.py      # LogMonitor：日志文件消息总线（核心独家设计）
InsightEngine/    # 洞察引擎（手写 node 流水线）
  agent.py  llms/  nodes/  prompts/  state/  tools/  utils/
MediaEngine/      # 媒体引擎（同构 node 流水线）
  agent.py  llms/  nodes/  prompts/  ...
MindSpider/       # 爬虫引擎
  BroadTopicExtraction/   # 广域话题抽取
  DeepSentimentCrawling/  # 深度情感爬取（含 MediaCrawler 子模块）
QueryEngine/      # 检索引擎
config.py  utils/  requirements.txt  Dockerfile
```

`InsightEngine` 与 `MediaEngine` 结构镜像：

```
nodes/  base_node.py  formatting_node.py  report_structure_node.py
        search_node.py  summary_node.py
state/  state.py        # 流水线状态
tools/  search.py  sentiment_analyzer.py  keyword_optimizer.py
prompts/  prompts.py    # 各节点提示词
llms/   base.py         # LLM 适配层
```

即一个**手写的、类 LangGraph 的 node 状态机**——但没有任何框架，纯 Python 类 + 状态对象串起来。

---

## 四、应用场景与启发

- **下次想"不依赖框架搭多 Agent"**：BettaFish 是零依赖 Agent 的活教材——看它如何用普通 Python 类 + 状态对象实现 node 编排，比直接上 LangGraph 更容易理解底层。
- **进程间/跨进程 Agent 通信**：`LogMonitor` 的"日志即总线"思路，天然支持把不同 Agent 跑在**不同进程甚至不同机器**上，只要共享日志目录——比内存队列更适合分布式/容错场景。
- **可解释的舆情研判**：把分析变成"论坛讨论"，每一步观点都有日志留痕，比黑盒聚合更可信、可审计。
- **教学/二次开发**：因从 0 实现、代码直白，适合作为"Agent 系统原理"课程或公司内训的拆解对象。

---

## 五、源码深度解读

### 5.1 论坛主持人 `ForumEngine/llm_host.py`

```python
class ForumHost:
    """论坛主持人类，使用 Qwen3-235B 模型作为智能主持人"""
    def __init__(self, api_key=None, base_url=None, model_name=None):
        self.api_key = api_key or settings.FORUM_HOST_API_KEY
        self.base_url = base_url or settings.FORUM_HOST_BASE_URL
        self.client = OpenAI(api_key=self.api_key, base_url=self.base_url)
        self.model = model_name or settings.FORUM_HOST_MODEL_NAME  # Qwen3-235B
```

主持人走 SiliconFlow 的 Qwen3-235B，负责把各 Agent 的发言综合成"引导性总结"，推动讨论深入而非简单拼接。

### 5.2 ⚠️ 日志文件消息总线 `ForumEngine/monitor.py`（独家设计）

```python
class LogMonitor:
    """基于文件变化的智能日志监控器"""
    def __init__(self, log_dir="logs"):
        self.forum_log_file = self.log_dir / "forum.log"
        self.monitored_logs = {
            'insight': self.log_dir / 'insight.log',
            'media':   self.log_dir / 'media.log',
            'query':   self.log_dir / 'query.log',
        }
        self.agent_speeches_buffer = []      # Agent 发言缓冲
        self.host_speech_threshold = 5       # 每 5 条触发一次主持人

    # 目标节点识别：通过日志行模式匹配 SummaryNode 输出
    self.target_node_patterns = [
        'InsightEngine.nodes.summary_node',
        'MediaEngine.nodes.summary_node',
        'QueryEngine.nodes.summary_node',
        '正在生成首次段落总结', '正在生成反思总结',
    ]
```

**机制**：各分析引擎把"产出"写到自己的 `*.log`；`LogMonitor` 用 `file_positions` 记住读取偏移，持续 `tail`，一旦命中 `summary_node` 模式就把该行当作"一条 Agent 发言"塞进缓冲区；**攒满 5 条**即调用 `ForumHost` 生成主持人发言写入 `forum.log`。整套跨 Agent 协作不依赖任何消息队列或共享内存，纯靠文件 I/O + 轮询——朴素、可跨进程、易于排错。

### 5.3 手写 node 流水线 `InsightEngine/`

`InsightEngine` 与 `MediaEngine` 用同构设计：`base_node.py` 定义节点接口，`search_node`（检索）→ `summary_node`（总结）→ `formatting_node`（格式化）→ `report_structure_node`（报告结构）串成状态机，`state/state.py` 在节点间传递上下文，`tools/` 提供 `sentiment_analyzer`（情感分析）、`keyword_optimizer`（关键词优化）、`search`（检索）。这正是 LangGraph 的"手写平替版"。

---

## 六、社区口碑

- **定位**：中文圈知名的"从零实现多 Agent 舆情分析"开源项目，常被当作"不依赖框架也能做 Agent"的范例。
- **正面**：零依赖、代码直白、架构有巧思（日志总线），适合学习与二次开发；deepwiki 文档齐全（deepwiki.com/666ghj/BettaFish）。
- **争议/风险**：① GPL-2.0 对闭源商用不友好；② 日志轮询式总线在高吞吐下延迟/重复消费需自行处理，生产化前要加固；③ 依赖外部 LLM API（SiliconFlow/Qwen3）与爬虫源（MediaCrawler），上游变动会影响可用性；④ 个人项目，维护节奏随作者时间波动。
- **中文社区**：B 站/知乎有拆解视频与文章，多聚焦"零框架多 Agent"的教学价值。

---

## 七、竞品对比 + 核心研判

| 维度 | BettaFish（微舆） | AutoGen | LangGraph | MetaGPT |
|------|------------------|---------|-----------|---------|
| 依赖框架 | ❌ 零依赖手写 | ✅ | ✅ | ✅ |
| Agent 通信 | 日志文件总线 | 内存消息 | 图状态 | 角色消息 |
| 特色场景 | 舆情论坛式研判 | 通用对话 | 通用编排 | 软件公司模拟 |
| 可解释性 | 高（日志留痕） | 中 | 中 | 中 |
| 许可 | GPL-2.0 | MIT/Apache | MIT | MIT |

**核心研判**
- ✅ **价值**：零框架多 Agent 的最佳"原理级"参考实现之一；日志总线思路为分布式/容错 Agent 通信提供了极简替代方案；论坛式协作模型可解释性强。
- ⚠️ **风险**：GPL-2.0 限制闭源；日志轮询总线需自行加固才能上生产；依赖外部 API/爬虫，稳定性受上游牵制。
- 🔮 **趋势**：当 Agent 框架愈发臃肿，"回归朴素实现"的教学与可控需求在上升；BettaFish 证明"不依赖框架也能做出像样的多 Agent 系统"，其"文件即总线"的低技术解法，在边缘/嵌入式/跨进程场景会持续有生命力。

---

## 八、关键文件速查

| 路径 | 作用 |
|------|------|
| `ForumEngine/llm_host.py` | 论坛主持人（Qwen3-235B via SiliconFlow） |
| `ForumEngine/monitor.py` | **日志文件消息总线 LogMonitor（核心独家设计）** |
| `InsightEngine/nodes/summary_node.py` | 洞察引擎总结节点（总线监听目标） |
| `InsightEngine/state/state.py` | 流水线状态传递 |
| `MediaEngine/` | 媒体引擎（同构 node 流水线） |
| `MindSpider/DeepSentimentCrawling/` | 深度情感爬取（含 MediaCrawler 子模块） |
| `MindSpider/BroadTopicExtraction/` | 广域话题抽取 |
| `QueryEngine/` | 检索引擎 |
| `config.py` `requirements.txt` | 配置与依赖 |

---

*本调研基于 2026-08-03 实时抓取的仓库元数据（GPL-2.0/41,920⭐）、真实仓库树（5 引擎结构）与 `ForumEngine/llm_host.py`、`monitor.py` 源码核验（日志总线机制逐行确认），覆盖星标/许可/架构/源码/口碑/竞品，远超 README。*
