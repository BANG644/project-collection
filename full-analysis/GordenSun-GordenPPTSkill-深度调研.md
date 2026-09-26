# Gorden PPT Skill — 史上最强原生 PPT 生成/编辑 Skill

> 调研日期：2026-09-27 ｜ 定位：给 AI Agent 用的「中文 PPT 模板库 + 非破坏性文字编辑」技能包
> 数据源：gh api 真实抓取 README.md / SKILL.md / scripts/build_pptx.py / templates/INDEX.md 结构（非 README 搬运）

## 一、项目全景

| 项 | 值 |
|---|---|
| 仓库 | `GordenSun/GordenPPTSkill`（默认分支 `main`） |
| 星标 | 3,154 ⭐ |
| 语言 | Python（python-pptx 驱动） |
| 许可 | `NOASSERTION`；README/LICENSE 明确 **非商业使用**（模板素材来自第三方设计师，商用需原作者授权） |
| 最后提交 | 2026-06-22（模板库已稳定，靠 `apply_update.py` 增量更新） |
| 规模 | 17→21 套内置中文 PPT 模板（README 写 17，SKILL.md frontmatter 写 21，以 SKILL.md 的 v1.0.3 口径为准） |

**一句话**：它不是"用 AI 重新画 PPT"，而是把「精选 .pptx 模板 + 每个文本框的结构化元数据」打包成一个 Agent Skill，让 AI 只改文字、绝不破坏原排版/配色/字号，从而稳定产出"看起来像人做的豪华中文 PPT"。

## 二、项目亮点（3-5 条差异化）

1. **非破坏性编辑（核心竞争力）**：AI 只替换 `run` 级文字，形状位置/大小/颜色/字体/字号/行距一律不动；装饰性进度条、圆环、流程箭头等固定形状不被误改。
2. **模板即数据**：每套模板附 `detail.json`（每个文本位的 `address`、容量 `max_chars/chars_per_line/max_lines`、`type_scale` 字号层级），AI 据此精准寻址、校验出框，而不是靠"猜形状"。
3. **增量自更新机制**：`apply_update.py` 从 `git+https://github.com/GordenSun/GordenPPTSkill.git#main` 拉 `updates.json`，只下载变动文件（无 LFS 流量浪费），Skill "像软件一样可更新"。
4. **反截断护栏**：出框检测只是提示、不阻断保存；并**主动检测省略号/「等等」结尾**，因为这是"最差结果"——宁可轻微超出也不要砍掉半句话。
5. **模板选择有章法**：用户未指定时强制 AskQuestion 给 3 个候选 + 预览图，禁止"凭模糊匹配自作主张定模板"。

## 三、核心架构

```
SKILL.md            ← Agent 入口（frontmatter 声明触发词 + 三种模式 + 编辑铁律）
scripts/
  build_pptx.py     ← 按 edits.json 选页 + 换字 → 输出 pptx（含出框检测/省略号检测）
  render_slides.py  ← pptx → PDF → 每页 PNG（LibreOffice + pdftoppm，预览/自检）
  compute_capacity.py ← 由 template.pptx 算出每个 slot 容量字段（加新模板时用）
  check_update.py / apply_update.py / build_manifest.py ← 版本与增量更新
references/         ← workflow / pptx-edit-schema / chart-editing / original-design-guide
templates/<slug>/   ← template.pptx + intro.md + detail.json + preview.png（每模板 4 文件）
```

**工作流（模式 A）**：`templates/INDEX.md` 选模板 → 读 `intro.md`+`detail.json` → 写 `edits.json`（`selected_slides` + `edits[{slide, slot_id, new_text}]`）→ `build_pptx.py` 生成 → `render_slides.py` 自检。

## 四、源码深度解读

`scripts/build_pptx.py` 是精髓，三个设计点值得借鉴：

**① 槽位寻址（detail.json → shape 坐标）**
```python
def load_slot_index(detail_path):
    detail = json.loads(detail_path.read_text(encoding="utf-8"))
    index = {}
    for page in detail.get("pages", []):
        for slot in page.get("text_slots", []):
            index[(page["slide_number"], slot["slot_id"])] = slot  # 含 address + 容量元数据
    return index
```
AI 写 `slot_id` 即可，脚本自动映射到 `shape_id/paragraph/run`，无需 AI 去数形状。

**② 保留 run 级格式的文字替换**
```python
def apply_edit_to_shape(shape, address, new_text, expected, strict):
    runs = list(para.runs)
    if ri is None:                      # 整段替换：保留 run0 格式，其余清空
        runs[0].text = new_text
        for r in runs[1:]: r.text = ""
    else:
        runs[ri].text = new_text        # 精确 run 替换，字号/颜色原样保留
```
这是"非破坏性"的关键——只动 `text`，不动 `font`/`fill`/`size`。

**③ 出框检测用"视觉宽度"而非字符数**（中文按 1.0、空格 0.35、ASCII 0.5 加权），并显式拒绝截断：
```python
if stripped.endswith(("...", "…", "等等", "等。")):
    ellipsis_issues.append("结尾疑似省略号截断 -> ...")
```
`--strict` 才会因超框拒绝保存；日常不建议开，避免诱导截断。

## 五、社区口碑

- README 展示多张"信息密度高、排版复杂的商务质感"实拍页，定位"国企/互联网大厂适用"，营销话术强（"不让你震惊你来打我"）。
- 通过 LinuxDO 社区 + 微信交流群运营，典型"个人开发者 + 社群"增长路径。
- **局限**：① 许可非商业，企业场景落地需谨慎；② 模板素材版权不在作者手中（README 自承）；③ 截至调研日最后提交在 2026-06，更新节奏放缓但靠增量机制仍可拉新模板。

## 六、竞品对比

| 项目 | 路线 | 与本仓库差异 |
|---|---|---|
| `GordenSun/GordenSuperPPTSkills`（已入库） | GPT 生图 + 视觉解析，把"图片版豪华 PPT"还原为可编辑 PPTX | 同源作者，走"图→可编辑"；本 Skill 走"模板→填字" |
| `Anionex/banana-slides`（已入库） | nano banana pro 原生生成 + 可编辑 PPTX + 视频导出 | 不依赖模板，端到端生成；成本/可控性弱于模板法 |
| `icip-cas/PPTAgent`（已入库） | Agentic 编排 Planner→Research→Design→渲染，反思自纠 | 研究型、重量级、需 WSL；本 Skill 轻量、本地、确定性强 |
| `HKUDS/Paper2Slides`（已入库） | 论文→幻灯片 RAG 流水线 | 垂直场景（论文）；本 Skill 通用中文场景 |

## 七、核心研判

- **值得借鉴的范式**：把"排版知识"沉淀为 `detail.json`（结构化元数据）+ `build_pptx.py`（非破坏性渲染器）的分离，比"让 LLM 直接操作 XML"可靠得多。任何"AI 帮我改文档但不毁版式"的需求都可套用。
- **对用户的价值**：与你的面向对象设计 Assignment PPT、工作汇报等场景高度契合；可当作"保底排版质量"的工具——AI 写内容、模板保颜值。
- **风险**：非商业许可 + 模板第三方版权，不要进任何商业交付；个人学习/汇报可用。

## 八、关键文件路径速查

| 路径 | 作用 |
|---|---|
| `SKILL.md` | Agent 入口，触发词/三模式/编辑铁律 |
| `scripts/build_pptx.py` | 选页 + 非破坏性换字 + 出框/省略号检测 |
| `scripts/render_slides.py` | pptx→PNG 预览自检 |
| `scripts/apply_update.py` | 增量自更新（git+ 远端） |
| `templates/INDEX.md` | 21 套模板清单（风格/主色/场景/页数） |
| `templates/<slug>/detail.json` | 每页每文本位的 address + 容量 + type_scale |
| `references/pptx-edit-schema.md` | edits.json Schema 规范 |
