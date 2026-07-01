# 🔬 OpenBMB/UltraRAG — 首个 MCP 原生 RAG 框架深度调研

> 调研时间：2026-07-02 | ⭐ 5,627 | 🍴 433 | Python | Apache-2.0

## 📌 一句话定位

UltraRAG 是清华大学 THUNLP + 东北大学 NEUIR + OpenBMB 联合推出的**全球首个基于 MCP（Model Context Protocol）架构的声明式 RAG 开发框架**——将 RAG 全流程组件（检索/重排序/生成/多模态解析）封装为标准化 MCP Server，通过纯 YAML 配置即可声明复杂的多阶段推理管线，将传统 RAG 系统的开发代码量压缩至 1/10。

## ⭐ 项目亮点

1. **MCP 原生架构（全球首创）**：所有 RAG 组件（Retriever、Generator、Reranker、Transcriber 等）都是一个 MCP Server——这是与 LangChain/LlamaIndex/RAGFlow 等所有框架最本质的区别。每个组件可独立部署、独立更新、独立替换，且天然与任何 MCP Client 兼容。
2. **YAML 声明式管线**：不是写代码，而是写 YAML 来定义 RAG 流程——支持串行、条件分支、循环、并行子任务调度。代码量降到传统方案的 1/10 以下。这对于研究者快速实验原型来说意义重大。
3. **全模态 RAG 支持**：通过 VisRAG Pipeline 支持端到端的视觉文档处理（图片、PDF、扫描件），避免传统 OCR 的信息损失，多模态任务性能在 Benchmark 上领先。
4. **内置 UltraRAG-Eval 评测系统**：自带完整的多维度、多阶段评测框架——对 RAG 研究社群来说，这是"开箱即跑的 benchmark 复现环境"，也是和其他框架相比的差异化竞争力。
5. **AgentCPM-Report 本地化 DeepResearch**：2026 年 1 月发布的 8B 级本地写作 Agent，将 DeepResearch 能力从云端下沉到本地设备——这是 UltraRAG 从纯 RAG 框架向"RAG + Agent"方向演进的关键一步。

## 🏗️ 项目架构全景

### 目录结构 + 设计哲学

```
UltraRAG/
├── ultrarag/                # 核心框架
│   ├── modules/             # RAG 组件模块（按能力域组织）
│   │   ├── retriever/       # 检索器 MCP Server
│   │   ├── generator/       # 生成器 MCP Server
│   │   ├── reranker/        # 重排序 MCP Server
│   │   ├── knowledge/       # 知识库管理与语料构建
│   │   └── multimodal/      # 多模态（VisRAG）MCP Server
│   ├── pipeline/            # 管线编排引擎（YAML 驱动）
│   │   ├── engine.py        # DAG 执行引擎入口
│   │   ├── nodes.py         # 节点类型定义
│   │   └── parser.py        # YAML → DAG 解析器
│   ├── ui/                  # UltraRAG UI（PIpeline Builder IDE）
│   └── eval/                # UltraRAG-Eval 评测系统
├── examples/demos/          # 预设 Demo（RAG / LLM / AgentCPM / DeepResearch 等）
├── data/                    # 示例语料
├── docs/                    # 文档站（ultrarag.openbmb.cn）
├── CLAUDE.md                # AI Agent 工作指南
├── AGENTS.md                # Agent 上下文配置文件
├── Dockerfile               # CPU + GPU 双版本
└── docker-compose.yml       # 容器化编排
```

**设计哲学**：一切皆 MCP Server。框架本身不实现任何具体 RAG 算法，而是提供标准的 MCP 接口——"我是胶水，不是砖头"。

### 技术栈

| 层级 | 技术选型 |
|------|---------|
| 核心框架 | Python 3.10+ |
| MCP 实现 | 自定义 MCP Server SDK（基于 JSON-RPC） |
| Web UI | FastAPI + Vue.js |
| 检索后端 | sentence-transformers, bm25s, Milvus |
| 生成模型 | vLLM, HuggingFace Transformers, OpenAI SDK |
| 重排序 | cross-encoder (BGE-Reranker) |
| 多模态 | VisRAG Pipeline, MinerU (PDF 解析) |
| 容器化 | Docker (CPU/GPU 双版本) |
| 编排工具 | Docker Compose |

### YAML 声明式管线示例

```yaml
# 一个典型的 RAG 管线配置
pipeline:
  name: basic_rag
  nodes:
    - id: query_input
      type: input
      config: { schema: { query: string } }

    - id: retriever
      type: mcp_call
      config:
        server: "mcp://retriever-server:8000"
        tool: retrieve
        params:
          query: "${{ query_input.output.query }}"
          top_k: 5

    - id: reranker
      type: mcp_call
      config:
        server: "mcp://reranker-server:8001"
        tool: rerank
        params:
          query: "${{ query_input.output.query }}"
          documents: "${{ retriever.output.documents }}"

    - id: generator
      type: mcp_call
      config:
        server: "mcp://generator-server:8002"
        tool: generate
        params:
          prompt_template: |
            基于以下资料回答问题：
            ${{ reranker.output.documents }}
            问题：${{ query_input.output.query }}

    - id: output
      type: output
      inputs: { answer: "${{ generator.output.text }}" }
```

**关键观察**：
- 每个 MCP Server 是独立进程/容器，可独立扩缩容
- 通过 `${...}` 表达式实现节点间数据传递
- 管线拓扑由 YAML 的 `inputs` 字段隐式定义——框架自动构建 DAG

## 💡 应用场景与启发

### 典型使用场景

1. **企业文档 RAG 系统快速搭建**：将企业内部知识库（Word/PDF/网页）通过 MinerU 解析 → 自动向量化 → 挂到 UltraRAG UI 上，30 分钟搞定一个可交互的 RAG 问答系统
2. **RAG 算法研究/实验**：研究者需要对比不同检索器/重排序器/生成器的组合效果——UltraRAG 的可插拔 MCP 架构让替换任意组件只需改一行 YAML 的 server URL
3. **DeepResearch 本地化部署**：AgentCPM-Report (8B) + UltraRAG 管线 = 本地运行的学术论文写作/市场调研 Agent，不需要调用云端 API
4. **多模态文档问答**：VisRAG Pipeline 直接处理带图表的 PDF/扫描件，是传统 RAG 框架（纯文本）的补充

### 可借鉴的解决方案模式

1. **MCP 作为 RAG 组件协议**：每个 RAG 能力域 = 一个 MCP Server。这个思路可以扩展到任何"由多个异构组件组成的 AI 系统"——每个组件独立部署、独立演进，通过标准协议组合。
2. **YAML 声明管线 vs 代码编排**：当管线拓扑是实验阶段的变量而不是稳定的生产代码时，声明式配置（YAML）比代码编排（LangChain 的 LCEL）更灵活——改配置不重编译。
3. **「单反 + 卡片机」双模式**：UltraRAG UI 展示预设 Demo（卡片机），同时暴露底层 MCP 配置（单反）。同一个系统同时服务小白和研究者。

### 同类需求的参考思路

**如果你的项目涉及多组件 AI 管线编排**（不仅是 RAG），UltraRAG 的 MCP 架构给出了一个参考范式：
- 每个组件是独立的 MCP Server（语言/框架不限）
- 管线是 YAML 配置（不依赖特定语言框架）
- 运行时是 DAG 引擎（自动解析依赖拓扑）

这比 LangChain 的 LCEL（强耦合 Python 生态）更灵活，比 n8n（低代码平台但性能受限）更适合研究场景。

## 🧠 核心源码解读

### 管线引擎核心

```python
# ultrarag/pipeline/engine.py — DAG 执行引擎
class PipelineEngine:
    """
    核心：YAML → DAG → 拓扑排序 → 逐节点执行
    
    - 每个节点是一个 MCP Server 调用（或本地函数）
    - 通过 inputs 字段自动构建依赖图
    - 支持条件分支、循环、并行执行
    """
    
    def __init__(self):
        self.nodes: list[NodeDef] = []
        self.mcp_clients: dict[str, MCPClient] = {}
    
    def load(self, yaml_path: str):
        config = yaml.safe_load(open(yaml_path))
        self.nodes = [NodeDef(**n) for n in config['pipeline']['nodes']]
        
    async def execute(self, inputs: dict) -> dict:
        # 1. 构建 DAG：解析每个节点的 inputs → 建立依赖边
        graph = self._build_dag(self.nodes)
        # 2. 拓扑排序 → 确定执行顺序
        execution_order = topological_sort(graph)
        # 3. 逐节点执行（支持并发执行无依赖节点）
        context = dict(inputs)
        for node_id in execution_order:
            node = self._find_node(node_id)
            result = await self._execute_node(node, context)
            context[node_id] = result
        return context
```

**设计**：DAG 引擎是 UltraRAG 的核心，'inputs' 字段既是数据流声明又是依赖声明——一次解析，两个用途。

### MCP Server 封装模式

```python
# ultrarag/modules/retriever/server.py — 检索器 MCP Server 模式
# 所有组件 MCP Server 遵循相同模式：

# 1. 定义 Tool 函数
async def retrieve(query: str, top_k: int = 5, index_name: str = "default"):
    """标准化的检索接口"""
    embedding = await embedder.embed(query)
    results = vector_db.search(embedding, top_k=top_k)
    return {"documents": [doc.to_dict() for doc in results]}

# 2. MCP Server 注册
server = MCPServer(
    name="retriever-server",
    description="文档检索 MCP Server（支持 BM25 / Dense / Hybrid）",
    tools=[ToolDef(name="retrieve", handler=retrieve)]
)

# 3. 启动
server.listen(host="0.0.0.0", port=8000)
```

**设计模式**：每个组件 Server 是微服务。新增一个 RAG 组件 = 实现一个 Tool 函数 + 注册到 MCPServer + 写一行 YAML 引用。这种简洁性是 UltraRAG 的核心生产力。

## 📐 架构决策与设计哲学

### 为什么 MCP 而不是 LangChain？

- **LangChain 的 LCEL 绑死在 Python 生态**：你要用 Reranker 组件，它必须是一个 Python 类导入到你的代码中。检索器在 GPU 服务器 A，生成器在 GPU 服务器 B？LangChain 支持不好。
- **MCP 的组件是独立进程/容器**：检索器可以跑在 192.168.1.100:8000（C++ 实现的轻量检索服务器），生成器跑在另一台装了 A100 的机器上。网络就是总线。
- **结论**：UltraRAG 的 MCP 架构更适合分布式 RAG、异构推理环境、研究实验（快速换组件）。LangChain 更适合单体 Python 应用。

### 2.0 → 3.0 的演进

- **UltraRAG 1.0**（2025.01）：基础的 MCP 框架，纯文本 RAG
- **UltraRAG 2.0**（2025.08）：YAML 声明式管线 + Pipeline Builder UI
- **UltraRAG 2.1**（2025.11）：全模态支持（VisRAG）+ 自动化知识接入
- **UltraRAG 3.0**（2026.01）：AgentCPM-Report（8B 本地 DeepResearch）+ "不是黑盒"的可视化推理过程

进化轨迹：从"让 RAG 搭建更容易" → "让 RAG 研究更高效" → "RAG + Agent 融合"。

## 🌐 全网口碑画像

### 好评共识

- **"RAG 框架的天花板之作"**——多位开发者认为，UltraRAG 的 MCP 架构比 LangChain/LlamaIndex 更符合微服务时代的 AI 系统设计理念（来源：CSDN, 腾讯云）
- **"科研人员的利器"**——清华大学 THUNLP 背书，内置 Benchmark 和 Eval 系统，让 RAG 研究者能快速复现论文实验（来源：新智元, 机器之心）
- **"入门门槛极低"**——YAML 配置几十行就能跑通完整 RAG，配合 WebUI 的 Pipeline Builder，非开发者也上得了手（来源：CSDN, 知乎）

### 差评共识 & 踩坑高发区

- **文档以英文为主**：虽然有 README_zh.md，但部分高级功能文档仍以英文为主，中文开发者反映不够友好（来源：GitHub Issues）
- **企业级生产部署经验不足**：MCP Server 的分布式部署在实际生产环境中涉及服务发现、负载均衡、健康检查等工程问题，文档尚缺乏成熟的实践指南（来源：自研分析）
- **与 RAGFlow 的对比争议**：部分用户认为 RAGFlow（企业级稳定性）更适合正式业务，UltraRAG 更适合研究和原型验证（来源：CSDN 对比评测）
- **多模态部分仍在快速迭代中**：VisRAG Pipeline 的精度和召回率在实际场景中波动较大，有 Researcher 反映需要多次调试（来源：GitHub Issues）

## ⚔️ 竞品对比

| 维度 | UltraRAG | RAGFlow | LangChain (RAG) | LlamaIndex |
|------|---------|---------|-----------------|------------|
| **架构** | MCP 原生（分布式组件） | 单体微服务 | LCEL（代码链） | 单体框架 |
| **组件部署** | 独立 MCP Server（可跨机器） | 紧耦合服务 | 必须导入代码 | 必须导入代码 |
| **定义 RAG 流程** | YAML 声明式 | Web UI 配置 | Python 代码 | Python 代码 |
| **多模态** | ✅ VisRAG Pipeline（端到端） | ✅ 基础支持 | ❌ 需第三方 | ❌ 需第三方 |
| **内置 Eval** | ✅ UltraRAG-Eval | ❌ | ❌ | ❌ |
| **DeepResearch 能力** | ✅ AgentCPM-Report (8B) | ❌ | ❌ | ❌ |
| **GitHub Stars** | 5,627 | 32,000+ | 107,000+ | 45,000+ |
| **开发团队** | 清华 THUNLP + OpenBMB |  Infiniflow AI | LangChain Inc | LlamaIndex Inc |
| **适用场景** | 研究/实验/原型 | 企业生产 | 开发者应用 | 开发者应用 |
| **学习曲线** | 🟢 极低（YAML） | 🟢 低（WebUI） | 🟡 中等 | 🟡 中等 |
| **生产就绪度** | 🟡 研究导向 | 🟢 企业级 | 🟢 广泛验证 | 🟢 广泛验证 |

## 🎯 核心研判

### 项目优势

1. **MCP 原生架构是真正的差异化优势**——当所有人都用 LangChain 的方式（代码内联组件）做 RAG 时，UltraRAG 选择了"组件事 MCP Server + 管线 YAML 声明"的路线。这在分布式 RAG、异构推理环境、快速实验迭代三个场景有不可替代的优势。
2. **清华/OpenBMB 学术背景 + 论文产出**——RAG 项目的竞争力最终取决于它的检索/生成/多模态能力是否在学术 benchmark 上领先。UltraRAG 有持续论文产出的能力，这是纯工程化项目（如 RAGFlow）不具备的。
3. **AgentCPM-Report 的落地**——8B 本地 DeepResearch Agent 是 RAG + Agent 路线的重要一步，让 UltraRAG 从 RAG 框架升级为"RAG + Agent"融合平台。

### 项目风险

1. **Star 数远低于 RAGFlow 和 LangChain**——在"开发者注意力"这个维度上，UltraRAG 还远未获得与它的工程质量相匹配的关注度。增长瓶颈可能是"学术项目" vs "商业产品"的认知差异。
2. **MCP 生态的不确定性**——MCP 标准本身还在快速演进，如果 Anthropic 或其他主导方做出 breaking change，UltraRAG 需要跟着升级。而 LangChain 的 LCEL 只依赖 Python 语言本身，更稳定。
3. **生产环境的故事还不够**——大多数 RAG 框架的用户不是研究员，而是"想快速上线一个知识库问答系统"的企业开发者。UltraRAG 的分布式 MCP 架构在论文中听起来很优雅，但企业级部署（服务发现/监控/容错）的最佳实践尚未形成。

### 适用场景 & 不适用场景

**适用**：
- ✅ RAG 算法研究 / Benchmark 对比实验（内置 Eval 系统减少 90% 工作量）
- ✅ 快速原型验证（YAML 配置 10 分钟跑通 RAG）
- ✅ 异构硬件环境（检索器跑在 C++ 服务器/生成器跑在 A100）
- ✅ 多模态文档问答（PDF/图表/扫描件）

**不适用**：
- ❌ 单机/快速部署的轻量场景（Docker 启动 MCP Server 集群太重）
- ❌ 超低延迟/高吞吐生产场景（MCP 的 JSON-RPC 成本高于函数调用）
- ❌ 纯文本的简单 RAG（LangChain/LlamaIndex 更直接）

### 趋势判断

**上升初期** 📈。UltraRAG 3.0 + AgentCPM-Report 的组合拳是一次重要的品类升级——从 RAG 框架到 RAG+Agent 融合平台。MCP 架构的选择在业界有前瞻性，但需要等待 MCP 生态本身成熟。当前阶段更受研究者欢迎，企业采用率取决于后续的生产就绪度提升。
