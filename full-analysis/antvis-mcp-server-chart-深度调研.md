# antvis/mcp-server-chart 全方位深度调研

## 📋 基本信息
- **仓库**: antvis/mcp-server-chart
- **Stars**: ~2,500+（持续增长中）
- **License**: MIT
- **语言**: TypeScript
- **最近更新**: 2026年6月活跃维护
- **npm 包名**: `@antv/mcp-server-chart`
- **最新版本**: v0.7+（迭代迅速）

## 🎯 项目定位

**antvis/mcp-server-chart** 是蚂蚁集团 AntV 团队官方出品的基于 Model Context Protocol (MCP) 的图表生成服务器。项目定位为 **「AI 原生可视化基础设施」**——作为 AI Agent 与可视化的桥梁层，让大语言模型（LLM）能够通过标准化的 MCP 协议直接调用 26+ 种图表的生成能力。

核心定位包含三个层次：

1. **MCP 桥梁层**：遵循 Anthropic 提出的 MCP 协议标准，将 AntV 丰富的可视化能力暴露为标准化工具（Tool），AI 客户端（Claude、Cursor、VSCode、Cherry Studio 等）可一键接入
2. **AI 友好设计**：与传统 ECharts 或 AntV G2 需要用户手写配置语法不同，mcp-server-chart 通过 LLM 自动分析数据特征并选择最佳图表类型，实现自然语言→图表的工作流
3. **私有化部署首选**：支持 npx 一键启动、Docker 容器化部署，以及通过 VIS_REQUEST_SERVER 接入自建渲染服务，满足企业级数据安全需求

## 🏗️ 核心架构

### 整体架构分层

```
┌─────────────────────────────────────────────┐
│          AI 客户端层                          │
│  Claude / Cursor / VSCode / Cherry Studio    │
│  Dify / 阿里云百炼 / ModelScope / Glama      │
└────────────────────┬────────────────────────┘
                     │ MCP Protocol (stdio/SSE/Streamable)
┌────────────────────▼────────────────────────┐
│         MCP 服务器层                          │
│  @antv/mcp-server-chart (TypeScript)         │
│  - 26+ 个 Tool 定义                           │
│  - 调用路由 / Schema 校验                     │
│  - 图表数据参数提取 & 转换                     │
└────────────────────┬────────────────────────┘
                     │ HTTP POST (JSON)
┌────────────────────▼────────────────────────┐
│          AntV 渲染引擎层                      │
│  GPT-Vis-SSR (Node.js SSR 服务)              │
│  或 自建 VIS_REQUEST_SERVER                   │
├─────────────────────────────────────────────┤
│  输出: 图片 URL / Base64 编码                 │
└────────────────────┬────────────────────────┘
                     │ 图片回传
┌────────────────────▼────────────────────────┐
│         记录服务层 (可选)                      │
│  支付宝小程序「我的服务」                       │
│  通过 SERVICE_ID 追踪生成记录                   │
└─────────────────────────────────────────────┘
```

### 传输协议

项目同时支持三种 MCP 传输模式，覆盖不同使用场景：

| 传输模式 | 命令行参数 | 适用场景 | 默认端点 |
|---------|-----------|---------|---------|
| **stdio** | `--transport stdio` | Claude Desktop、本地 CLI | stdin/stdout |
| **SSE** | `--transport sse` | 远程服务、Dify 集成 | `/sse` |
| **Streamable** | `--transport streamable` | Web 应用、HTTP 流式响应 | `/mcp` |

### 核心数据流

1. AI 客户端提供自然语言描述 + 原始数据
2. MCP Server 按预定义的 Tool Schema 解析参数
3. 将数据打包为 `{ type, data }` 格式发送到渲染服务
4. 渲染服务调用 AntV GPT-Vis SSR 引擎生成图表图片
5. 返回图片 URL 给 AI 客户端展示

## 🔍 源码解读

### 关键文件路径

```
mcp-server-chart/
├── src/
│   ├── charts/                    # 核心：所有图表类型定义
│   │   ├── index.ts               # 图表导出入口
│   │   ├── base.ts                # BaseChart 基类 & Schema 定义
│   │   ├── area.ts                # 面积图 Tool 定义
│   │   ├── bar.ts                 # 柱状图（横向比较）
│   │   ├── column.ts              # 柱状图（纵向比较）
│   │   ├── line.ts                # 折线图（趋势展示）
│   │   ├── pie.ts                 # 饼图（占比展示）
│   │   ├── scatter.ts             # 散点图（变量关系）
│   │   ├── boxplot.ts             # 箱线图（数据分布）
│   │   ├── histogram.ts           # 直方图（区间分布）
│   │   ├── radar.ts               # 雷达图（多维对比）
│   │   ├── funnel.ts              # 漏斗图（阶段流失）
│   │   ├── sankey.ts              # 桑基图（数据流向）
│   │   ├── treemap.ts             # 矩形树图（层级数据）
│   │   ├── network_graph.ts       # 网络关系图
│   │   ├── mind_map.ts            # 思维导图
│   │   ├── fishbone_diagram.ts    # 鱼骨图（因果分析）
│   │   ├── flow_diagram.ts        # 流程图
│   │   ├── word_cloud.ts          # 词云
│   │   ├── venn.ts                # 维恩图
│   │   ├── violin.ts              # 小提琴图
│   │   ├── liquid.ts              # 水波图（百分比）
│   │   ├── organization_chart.ts  # 组织架构图
│   │   ├── dual_axes_chart.ts     # 双轴图
│   │   ├── district_map.ts        # 行政区划地图（高德）
│   │   ├── path_map.ts            # 路径地图
│   │   ├── pin_map.ts             # POI 标注地图
│   │   └── spreadsheet.ts         # 透视表/电子表格
│   ├── services/                  # MCP 传输协议实现
│   │   ├── sse.ts                 # SSE 传输服务
│   │   ├── stdio.ts               # Stdio 传输服务
│   │   └── streamable.ts          # Streamable HTTP 服务
│   ├── utils/
│   │   ├── callTool.ts            # 工具调用核心逻辑
│   │   ├── generate.ts            # 图表生成核心函数
│   │   ├── schema.ts              # Schema 转换工具
│   │   └── env.ts                 # 环境变量配置
│   └── index.ts                   # 服务器入口 & CLI 解析
├── docker/
│   ├── Dockerfile                 # Docker 构建
│   ├── docker-compose.yaml        # Docker Compose 编排
│   ├── sse/                       # SSE 服务 Dockerfile
│   └── streamable/                # Streamable 服务 Dockerfile
├── tests/                         # 测试套件
│   ├── charts/                    # 各图表类型测试
│   └── utils/                     # 工具函数测试
└── package.json                   # 项目配置 & 依赖
```

### 关键设计模式

1. **Tool 注册模式**：每个图表类型是一个独立的 Tool，统一继承 `BaseChart` 接口，通过 `index.ts` 集中注册，AI 客户端按需调用
2. **Schema 驱动**：基于 MCP 的 `tool.schema` 机制定义每个工具的输入参数，LLM 自动根据 Schema 决定传入什么数据
3. **渲染解耦**：MCP Server 本身只做数据转发和参数校验，实际的图表渲染由 `GPT-Vis-SSR` 完成，这个设计让 MCP Server 非常轻量

## 📊 社区口碑

### 用户反馈摘要

- **积极评价**：
  - "一行 npx 搞定安装使用，体验非常丝滑"（SegmentFault 用户）
  - "AntV 的图表质量确实比竞品高，特别是地图和桑基图"（博客园开发者）
  - "和 Claude/Cursor 无缝集成，数据可视化效率翻倍"（CSDN 教程作者）
  - "版本迭代极快，从 5 月的 0.3 到现在的 0.7+，新增了 10+ 种图表"（GitHub Issue 用户）

- **改进建议**：
  - 部分国内开发者反馈高德地图组件仅限中国大陆使用
  - 私有化部署需要自建 GPT-Vis-SSR 服务，配置门槛略高
  - 图表生成的图片 URL 有有效期限制，需自行保存或使用 MinIO 等对象存储

### 生态覆盖

- 已上架 **Dify Marketplace**（插件名 `antv/visualization`）
- 已集成 **阿里云百炼** MCP 市场、**ModelScope**、**Glama.ai**、**Smithery.ai**
- 支持 **Claude Desktop**、**Cline**、**Cursor**、**Cherry Studio** 等主流 AI 客户端
- HiGitHub 社区 Issue 推荐，获得广泛曝光

## ⚔️ 竞品对比

| 对比维度 | antvis/mcp-server-chart | echarts-mcp-server | 自建 MCP + Vega-Lite |
|---------|----------------------|-------------------|---------------------|
| **开发方** | 蚂蚁集团 AntV 官方团队 | 社区开发者 | 个人开发者 |
| **图表数量** | 26+ | 10+ | 取决于集成 |
| **图表质量** | ⭐⭐⭐⭐⭐（AntV 背书） | ⭐⭐⭐（基本可用） | ⭐⭐⭐⭐ |
| **部署方式** | npx/Docker/SSE 三模 | 单一模式 | 需自建 |
| **文档质量** | ⭐⭐⭐⭐⭐（中英文完整） | ⭐⭐ | 依赖 Vega-Lite |
| **商业支持** | 阿里云百炼背书 | 无 | 无 |
| **更新频率** | 活跃（周更） | 低 | 自维护 |
| **特色图表** | 鱼骨图/思维导图/组织架构图 | 无 | 无 |
| **地图能力** | ✅ 高德地图（限国内） | ❌ | ❌ |

**结论**：mcp-server-chart 在图表覆盖度、官方支持力度、生态集成广度三个维度均明显领先于同类 MCP 可视化方案。其核心竞争力在于背靠蚂蚁 AntV 的成熟可视化体系，作为 AntV 在 MCP 领域的官方入口。

## 💡 核心研判

### 优势

1. **背靠 AntV 生态**：AntV 是国内最专业的数据可视化开源组织（G2/G6/F2/L7），图表质量和渲染能力有保障
2. **MCP 赛道先发优势**：在 AI Agent 和 MCP 协议爆发的浪潮中，AntV 是最早推出官方 MCP Server 的可视化团队之一，已抢占大量 AI 客户端集成场景
3. **AI 原生体验**：LLM 自动选择图表类型+提取数据，用户无需学习任何配置语法，真正实现"一句话生成图表"
4. **部署灵活**：从 npx 到 Docker 到私有化，覆盖个人开发到企业级部署的全场景

### 风险

1. **MCP 协议竞争**：MCP 协议目前是 Anthropic 主导，如果出现新的 AI Agent 协议标准（如 Google 的 A2A），存在协议切换成本
2. **渲染服务依赖**：默认依赖官方 GPT-Vis-SSR 服务，企业私有化部署需要额外配置渲染后端
3. **地图组件局限**：高德地图仅限中国大陆使用，海外用户无法使用地理可视化功能
4. **非开源渲染核心**：GPT-Vis-SSR 渲染逻辑非完全开源（部分依赖 AntV 内建服务），社区难以深度二次开发

### 建议

- **个人开发者**：直接在 Claude/Cursor/Cherry Studio 中配置 npx 命令即可，零成本接入
- **企业团队**：使用 Docker 部署 + 自建 GPT-Vis-SSR + MinIO 对象存储，构建私有化图表服务
- **集成场景**：项目即将推出的 `chart-visualization` skill（适配 Claude Code），能自动选择最佳图表类型，值得关注

## 🔗 参考链接

- GitHub: https://github.com/antvis/mcp-server-chart
- npm: https://www.npmjs.com/package/@antv/mcp-server-chart
- Dify Marketplace: https://marketplace.dify.ai/plugins/antv/visualization
- AntV 官网: https://antv.vision
- GPT-Vis-SSR: https://github.com/antvis/GPT-Vis/tree/main/bindings/gpt-vis-ssr
- MCP 协议规范: https://modelcontextprotocol.io
- Aliyun Bailian MCP Market: https://bailian.console.aliyun.com/?tab=mcp#/mcp-market
- Smithery Registry: https://smithery.ai/servers/@antvis/mcp-server-chart
