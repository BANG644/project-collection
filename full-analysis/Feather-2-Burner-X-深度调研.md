# Feather-2/Burner-X 深度调研

> 调研日期：2026-09-30 ｜ 数据源：gh API（README / 目录树 / 源码 advanced-search-tools.js）｜ 定位：浏览器即开即用的开源 AI 文献工作站（AGPL-3.0）

## 一、项目定位（一句话）

**Paper Burner X（Burner-X）** 是一款开源的、在浏览器里即开即用的 AI 文献工作站：面向研究生/研究者，对 PDF / DOCX / PPTX / EPUB 等文献做 OCR 识别、高质量翻译、智能分析，纯前端、数据本地化（IndexedDB），BYOK（自接模型端点）。

## 二、项目亮点（差异化）

1. **纯前端 Agentic RAG**：在浏览器里实现「长文本 Agent」——给 AI 全文的「分层意群/地图」结构认知，再配 `grep` / `vector search` / `fetch` 等工具箱，让模型自主多步推理、在长文本里精准检索与提取。
2. **高性能批量处理**：并发 OCR + 并发翻译，配合数万词条的术语库快速匹配；段落级原文/译文对齐对照。
3. **多格式 + 灵活部署**：导入 PDF/DOCX/PPTX/EPUB/MD/代码库，导出 DOCX/MD/HTML；Vercel 静态部署 + 自托管 OCR Server（Docker，向完全离线演进）。
4. **学术增强**：LaTeX 公式/图表渲染、文献矩阵结构化提取、思维导图/Mermaid 流程图生成、多 Key 轮询、提示词池。

## 三、核心架构

- **前端**：Next.js（`app/` 路由 + `css/`）+ `js/chatbot/agents/` 浏览器内 RAG agent。
- **RAG 工具箱** `js/chatbot/agents/`：`advanced-search-tools.js`（正则/布尔搜索）、`semantic-vector-search.js`（向量检索）、`bm25-search.js`、`embedding-client.js`、`rerank-client.js`、`vector-store.js`、`semantic-grouper.js`、`vector-worker.js`。
- **存储**：浏览器 IndexedDB / localStorage（纯前端模式，数据不出本机）。
- **后端（开发中）**：自托管 OCR Server（`Feather-2/PBX-DS-OCR-server`，Docker）+ `admin/`（多用户/配额/统计/系统管理）。
- **衍生**：基于 `baoyudu/paper-burner`（GPL-2.0）重构扩充，现主体 AGPL-3.0。

## 四、应用场景与启发

- **场景**：研究者读英文 PDF 论文（保留公式图表对照翻译）、把多篇文献做成文献矩阵横向对比、对长文档做 Agent 式问答与思维导图；轻量替代沉浸式翻译 + Zotero 插件组合。
- **启发**：
  - 「长文本不给 LLM 全量塞 prompt，而是让 Agent 自己调 vector search / grep / fetch 分块检索」是**前端 RAG** 的经典 Agentic 范式，特别适合浏览器端内存受限场景。
  - 「给模型一套确定性的检索原语（正则/布尔/向量）」比让它直接读全文更可控、更省 token——这类「工具即检索」设计值得在本地知识库/文档问答里复用。

## 五、源码深度解读（核心模块）

**1. `js/chatbot/agents/advanced-search-tools.js`：Agent 的「精准 grep」确定性工具**

```javascript
// js/chatbot/agents/advanced-search-tools.js (节选)
function regexSearch(pattern, text, options = {}) {
  const { limit = 20, context = 2000, caseInsensitive = true, multiline = true } = options;
  const regex = new RegExp(pattern, flags);
  while ((match = regex.exec(text)) !== null && count < limit) {
    const snippet = text.slice(max(0, match.index - context), min(text.length, matchEnd + context));
    results.push({ match: matchText, matchOffset: matchStart, preview: snippet, groups: match.slice(1) });
    if (match.index === regex.lastIndex) regex.lastIndex++;   // 防零宽死循环
  }
  return results;
}
// booleanSearch: 手写分词器 + 递归下降的 AND/OR/NOT/括号求值
//   → 500 字符窗口内邻近匹配 + 相关度打分（must/should/not）
```

这是「给前端 LLM Agent 一套确定性检索原语」的范例：正则搜索带上下文窗口与零宽保护，布尔搜索支持 `"(CNN OR RNN) AND 对比 NOT 图像"` 这类表达式，把「检索正确性」从概率变成了规则。

**2. 整体设计**：长文本 Agent 在纯前端运行——少量文本走全量策略，长文本走 Agent 分块检索；术语库（数万词条）快速注入翻译提示，保证术语一致。

## 六、社区口碑

- 1.7k⭐、769 fork，AGPL-3.0；活跃（2026-09-25 提交），中文研究者向；在线体验 `paperburner.viwoplus.site`；文档含完整部署指南（`deploy/DEPLOYMENT_GUIDE.md`）。
- 由 `baoyudu/paper-burner`（GPL-2.0 极简 PDF 翻译工具）重构扩充而来，作者明确选择 AGPL-3.0 以防「云服务漏洞」（SaaS 化须开源）。

## 七、竞品对比 + 核心研判

| 维度 | Burner-X | 沉浸式翻译（浏览器扩展） | Zotero + 插件 | 通义/DeepL 文档翻译 |
|---|---|---|---|---|
| 纯前端/本地化 | ✅ IndexedDB | ⚠️ 部分 | ✅ | ❌ 云端 |
| Agentic RAG（长文自主检索） | ✅ | ❌ | ⚠️ 需配 | ❌ |
| 术语库 + 多格式 + 离线可演进 | ✅ | 一般 | ✅ | ❌ |
| 文献矩阵/思维导图等学术增强 | ✅ | ❌ | ⚠️ | ❌ |

**研判**：对「研究者长文献的翻译 + 分析 + 结构化」是功能很全的纯前端方案，架构（前端 Agent 工具箱 + 可自托管 OCR）合理、隐私友好。风险：AGPL-3.0 对闭源 SaaS 化有传染性；纯前端模式对复杂/扫描版 PDF 仍依赖外部 OCR 端点（完全离线尚在开发中）；多用户后端仍在开发，当前主打个人单机。与用户的 `paper-companion` 论文伴读方向高度互补，可互为参考。

## 八、关键文件路径速查

- 仓库根：`https://github.com/Feather-2/Burner-X`；在线体验：`https://paperburner.viwoplus.site`
- 起源项目：`https://github.com/baoyudu/paper-burner`（GPL-2.0）
- 自托管 OCR：`https://github.com/Feather-2/PBX-DS-OCR-server`
- RAG 工具箱：`js/chatbot/agents/{advanced-search-tools,semantic-vector-search,bm25-search,embedding-client,rerank-client,vector-store}.js`
- 后端 API：`app/api/glossary/*`；管理面板：`admin/`
- 部署：`deploy/DEPLOYMENT_GUIDE.md`、`Dockerfile`、`NOTICE`
