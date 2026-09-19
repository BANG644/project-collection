# icip-cas/PPTAgent（DeepPresenter）深度调研

> 调研日期：2026-09-20 | 星标：5,042⭐ | 语言：Python | 许可：MIT | 默认分支：main | 最近提交：2026-09-14
> 定位：Agentic 框架，把"文档/主题"自动生成可编辑 PowerPoint，论文 PPTAgent（EMNLP 2025）与 DeepPresenter（ACL 2026）的学术落地实现。

## 一、项目亮点（差异点）

1. **"反思式（Reflective）"生成闭环**：设计阶段把渲染出的 HTML 转成图片，再让多模态 LLM"看图找毛病"并自我修正，是 PPTAgent 论文的核心创新，区别于一次性直出 PPTX 的同类工具。
2. **角色即配置（YAML-driven roles）**：Planner / Research / Design / PPTAgent / SubAgent 五类 agent 的 system prompt 全部抽成 `roles/*.yaml`，可改 prompt 不改代码即可调行为。
3. **学术背书 + 自训模型**：配套微调 `DeepPresenter-9B`（HuggingFace / ModelScope，GGUF 量化可用），官方称显著优于现有开源模型；论文双中稿（EMNLP 2025、ACL 2026）。
4. **MCP + 沙箱工具生态**：通过 FastMCP 暴露 `pptagent` / `sandbox` 两套工具服务器，沙箱用 Docker 镜像隔离执行，工具调用安全可回滚。
5. **多形态交付**：Freeform 自由生成 + Template 模板生成，支持 PPTX 导出、离线模式、上下文管理防溢出。

## 二、核心架构

`AgentLoop`（`deeppresenter/main.py`）是总编排器，按请求开关串联各阶段：

```
AgentLoop.run(request)
  ├─ (可选) Planner      → 规划大纲（enable_planner）
  ├─ Research            → 检索/深研补充素材（Tavily/MinerU）
  ├─ Design              → 设计版式（多模态 + Reflective 反思）
  ├─ PPTAgent(renderer)  → 读 Markdown 逐页调用工具"忠实还原"幻灯片
  ├─ SubAgent            → 多 agent 委派（multiagent_mode）
  └─ reflect             → inspect_slide 渲染成图回灌 LLM 自纠
```

渲染链路：Markdown 手稿（`---` 分页）→ `html2pptx/`（Node/Playwright 把 HTML 转 PPTX）→ `finalize` 工具收口。每个 agent 继承 `agents/agent.py` 的 `action()` + `execute()` 基元。

## 三、应用场景与启发

- **给同类需求的解法**：做"文档→PPT"类产品时，把"生成"拆成"规划→检索→设计→渲染→反思"多 agent，比端到端直出更可控；尤其**反思环节**用渲染图回灌多模态模型，能显著收敛版式/内容错误。
- **可直接借鉴**：YAML 角色抽离、MCP 工具服务器 + Docker 沙箱、Checkpoint/上下文管理防溢出——都是 agent 应用工程的通用脚手架。
- **对你（PPT/科研方向）**：与 paper-companion 论文伴读链路可互补——论文伴读产出结构化笔记，PPTAgent 把笔记/论文转成汇报 slides；其 `html2pptx` 渲染层也可单独抽出来复用。

## 四、源码深度解读

**① 反思式设计（`tools/reflect.py`）**——把 HTML 渲染成 PDF 再读成图，回灌多模态 LLM：

```python
@mcp.tool()
async def inspect_slide(html_file, aspect_ratio="16:9"):
    await convert_html_to_pptx(html_path, aspect_ratio=aspect_ratio)
    if REFLECTIVE_DESIGN:                      # 设计 agent 为多模态且开启 heavy_reflect
        pdf_path = Path(tempfile.mkdtemp()) / "slide.pdf"
        async with PlaywrightConverter() as converter:
            image_dir = await converter.convert_to_pdf([html_path], pdf_path, aspect_ratio)
        image_data = (image_dir / "slide_01.jpg").read_bytes()
        return ImageContent(type="image", data=base64.b64encode(image_data).decode(), ...)
```

**② 渲染 agent 的循环（`agents/pptagent.py`）**——逐页 action→execute，直到 `finalize`：

```python
async def loop(self, req, markdown_file):
    while True:
        msg = await self.action(markdown_file=markdown_file, prompt=req.pptagent_prompt)
        yield msg
        outcome = await self.execute(self.chat_history[-1].tool_calls)
        if isinstance(outcome, list):
            for item in outcome: yield item
        else:
            yield outcome; break
```

`roles/PPTAgent.yaml` 的 `instruction` 用 `{{ markdown_file }}` / `{{ prompt }}` 模板注入，并强制"表格必须先用工具生成图片再引用路径"，避免 Markdown 表格直接进 PPTX 失真。

## 五、社区口碑

- 学术双中稿（EMNLP 2025 / ACL 2026），作者来自中科院 icip-cas，可信度高。
- GitHub 5k+ star、配套 9B 模型已上 HF/ModelScope，社区与模型权重同步发布。
- 注意点：README 明确 **Windows 不支持，需用 WSL**；依赖 Docker + Playwright + llama.cpp，部署偏重。

## 六、竞品对比

| 项目 | 路线 | 反思闭环 | 学术背书 | 部署重量 |
|------|------|---------|---------|---------|
| **PPTAgent/DeepPresenter** | 多 agent + 反思 + 自训模型 | ✅ | EMNLP/ACL | 重（Docker/Playwright） |
| HKUDS/Paper2Slides | 4 阶段 pipeline（非 agent 循环） | ❌ | 港大 HKUDS | 中 |
| 传统 LLM→PPTX（如 markitdown） | 单步直出 | ❌ | — | 轻 |

## 七、核心研判

PPTAgent 是"文档→演示"赛道里**工程完成度最高、且有论文+模型双重背书**的开源方案，其反思式设计与角色配置化思路值得任何 agent 应用借鉴。短板是部署重、强依赖 Linux/Docker。对在 Windows 上做 PPT 自动化的用户，需走 WSL；若只想轻量出稿，Paper2Slides 更顺手。

## 关键文件路径速查

- `deeppresenter/main.py` — `AgentLoop` 总编排
- `deeppresenter/agents/{pptagent,planner,research,design,subagent,agent}.py` — 五类 agent + 基类
- `deeppresenter/roles/*.yaml` — 角色 system prompt 配置
- `deeppresenter/tools/reflect.py` — 反思式 `inspect_slide` / `inspect_manuscript`
- `deeppresenter/html2pptx/html2pptx.js` — HTML→PPTX 渲染层
- `deeppresenter/mcp.json.example` — MCP 服务器配置（pptagent + sandbox）
