# 🔬 google/langextract — 深度调研报告

> **仓库**: [google/langextract](https://github.com/google/langextract)  
> **调研日期**: 2026-07-12  
> **数据**: ⭐ 37,130 | 🍴 2,562 | 🐞 107 open issues | 📅 创建 2025-07-08，活跃推送至 2026-07-02  
> **语言**: Python | **协议**: Apache-2.0 | **PyPI**: `langextract`  

---

## 一、项目定位

Google 出品的 **LLM 驱动的非结构化文本结构化提取库**。核心卖点不是"把文本解析成 JSON"，而是 **Source Grounding（源定位）**——每一次提取都锚定回原文的确切字符区间，并生成可交互 HTML 供人工审阅。适用于临床笔记、合同、报告等"提取结果必须可溯源、可审计"的场景。

## 二、项目亮点（差异化）

1. **源定位 Grounding**：每个 extraction 带 `char_interval`，可映射回原文高亮，过滤未锚定（hallucinated）提取。
2. **Few-shot 提示驱动**：用 `examples` 定义行为，零微调，领域自适应只需少量样例。
3. **交互式可视化**：`lx.visualize()` 一键生成独立 HTML，审阅上千实体。
4. **多模型/多部署**：Gemini、Vertex AI、OpenAI、本地 Ollama、自定义 provider 通吃。
5. **长文档优化**：分块 + `max_workers` 并行 + `extraction_passes` 多轮提升召回。

## 三、核心架构

```
lx.extract(text, prompt_description, examples, model_id)
   └─ factory.create_model(ModelConfig)   # provider 路由
        ├─ providers/gemini.py           # 默认 gemini-3.5-flash
        ├─ providers/gemini_batch.py     # Vertex Batch 降本
        ├─ providers/openai.py           # gpt-4o，支持 output_schema
        └─ providers/ollama.py           # 本地，仅 JSON 模式
   └─ chunking.py                        # 长文档分块
   └─ inference.py                       # LLM 调用 + 受控生成
   └─ prompt_validation.py               # prompt alignment 警告
   └─ core/output_schema.py             # 枚举值等强约束（Gemini/OpenAI）
   └─ io.py                             # save .jsonl + visualize HTML
```

- `core/`：`base_model / data / schema / output_schema / format_handler / tokenizer / types`
- `_compat/`：向后兼容层（registry / schema / inference）
- `providers/builtin_registry.py`：内置 provider 注册表；社区可 `router.register()` + `create_model()` 扩展。

## 四、应用场景与启发

- **临床/法律/金融文档抽取**：要求 provenance 的场景，grounding 是关键差异。
- **Human-in-the-loop 标注**：可视化 HTML 让领域专家快速校验，比纯 JSON 友好。
- **给同类需求的解法**：做提取类需求时，优先保证"提取可回溯到原文 span + 可交互审阅"，而非只追求解析成功率。需要私有部署时，Ollama 本地路径零 API key 即可跑。

## 五、源码深度解读

**1) 核心提取 + Grounding 过滤**

```python
import langextract as lx
result = lx.extract(
    text_or_documents=input_text,
    prompt_description=prompt,      # 用自然语言定义抽取规则
    examples=examples,              # few-shot 驱动行为
    model_id="gemini-3.5-flash",
)
# Grounding：仅保留锚定到源文本 span 的提取，过滤幻觉
grounded = [e for e in result.extractions if e.char_interval]
lx.io.save_annotated_documents([result], output_name="out.jsonl")
html = lx.visualize("out.jsonl")    # 独立交互式 HTML 审阅
```

**2) Provider 路由（多模型/自定义）**

```python
# ModelConfig 决定 provider + 参数，factory 解析出对应模型客户端
cfg = lx.core.base_model.ModelConfig(
    provider="openai",
    model_id="gpt-4o",
    provider_kwargs={"api_key": ...},
)
model = lx.factory.create_model(cfg)   # 社区 provider 可 router.register 扩展
```

## 六、全网口碑

- GitHub 37.1k⭐、2.5k fork，Google 官方出品，迭代活跃（2026-07 仍有推送）。
- 社区评价集中于"grounding + 可视化"的组合——被认为是 LLM 提取库里少有的"把审阅当一等公民"的设计。
- 痛点：Ollama 不支持 `output_schema`（仅 JSON 模式）；复杂 schema 约束仍依赖 Gemini/OpenAI 受控生成。

## 七、竞品对比 + 核心研判

| 项目 | 定位 | 与 langextract 差异 |
|------|------|-------------------|
| **google/langextract** | 带 grounding 的 LLM 提取 | 源定位 + 可视化审阅，零微调 |
| instructor (pydantic) | Pydantic 结构化输出 | 强类型好，但无 grounding/可视化 |
| Outlines / LMQL | 受控生成 | 偏底层生成约束，非端到端抽取 |
| LangChain 输出解析器 | 框架内解析 | 绑定 LangChain，无审阅闭环 |
| pydantic-ai / mirascope | Agent 框架含提取 | 重 Agent，轻审计 |

**核心研判**：langextract 的护城河是 **Grounding + Visualization**——它把"提取"重新定义为"带溯源标注的审阅问题"，而非单纯解析。当你的场景要求可审计、可溯源（医疗/法律/合规），它是最优解；若只要高吞吐 JSON 且不在意 provenance，instructor 更轻。多 provider + 本地 Ollama 让它既能上云也能私有部署。

## 八、关键文件路径速查

- `README.md` / `docs/examples/output_schema.md` — 用法与 schema 示例
- `langextract/extraction.py` — 主入口 `extract()`
- `langextract/inference.py` — LLM 调用与受控生成
- `langextract/providers/` — gemini / gemini_batch / openai / ollama / builtin_registry
- `langextract/core/output_schema.py` — 强 schema 约束
- `langextract/chunking.py` / `prompt_validation.py` — 长文档与对齐检查
- `langextract/io.py` — 保存 `.jsonl` 与 `visualize()` HTML
- `COMMUNITY_PROVIDERS.md` — 自定义 provider 接入指南

---

*报告基于仓库 README、源码树与 `lx.extract` API 实地抓取，数据截至 2026-07-12。*
