# GordenSun/GordenSuperPPTSkills 深度调研

> 调研日期：2026-09-23 ｜ 定位：用 GPT 生图 + 视觉解析，把"图片版豪华 PPT"还原成**完全可编辑** PPTX 的 AI PPT 技能包（三技能串联）｜ Stars：1,997 ｜ 语言：Python ｜ 许可：MIT（商用需注明仓库/作者 @Gorden Sun）｜ 默认分支：main ｜ 最近活跃：2026-06-07

## 一、项目定位（一句话）

Gorden Super PPT Skills 是一套**自包含 Agent 技能包**，核心思路是：先用 GPT 生成"图片格式的豪华 PPT"，再用视觉能力把图片**逐层拆解（背景/框架/图标/文本）**并重新拼装成"背景+骨架+图标+文本"四层、完全可编辑的 `.pptx`——主打"AI PPT 赛道终结者"，目前声明**仅限 Codex 使用**（强依赖 GPT 生图与视觉）。

## 二、项目亮点（差异化）

- **三技能可拆分复用**：`GordenImagePPTGen`（出图片 PPT）、`GordenImage2PPTX`（图片→可编辑 pptx）、`GordenSuperPPTSkill`（编排 A→B 串联），按需单独装。
- **"先出图、再还原可编辑"两步法**：用 GPT 生图拿到"排版/配色/装饰"的高质量视觉，再反向解析成可编辑元素，兼顾"美观"与"可改"。
- **四层拼装还原**：背景图（全幅）→ 整框 PNG → 图标/装饰 PNG（按坐标摆放）→ 文本框（保留字体/颜色/粗体/对齐），文本层真正可编辑。
- **工程化 QA**：`compose_pptx.py` 配套 `layout_guard / placement_qa / visual_compare_qa / probe_palette` 等校验脚本，对还原结果做坐标/配色/视觉一致性检查。
- **自包含分发**：每个技能目录自带 `scripts/ + references/ + 参考图/`，把整个仓库复制到 Agent 的 skills 目录即可用。

## 三、核心架构

```
主题/内容
   │
   ▼
GordenImagePPTGen（GPT 生图）
   ├─ references/image-prompt-guide.md（生图提示词）
   ├─ 参考图/（leader_love / red_grey_project / scholar_green / tech_prize / work_result 五套风格）
   ▼ 每页 .png + 图片型 .pptx
GordenImage2PPTX（视觉解析 → 可编辑 pptx）
   ├─ 依次提取：背景图 / 框架图 / 图标装饰 / 文本（带坐标）
   ├─ compose_pptx.py：按 deck.json 分层拼装（background→frame→icons→texts）
   └─ QA：layout_guard / placement_qa / visual_compare_qa / probe_palette / chroma_key
   ▼ 完全可编辑 .pptx（文本层可改、图框层可移动）
GordenSuperPPTSkill（编排 A→B，references/pipeline.md）
```

- **依赖**：`python-pptx`、`pillow`、`numpy`；图像生成后端按运行时解析（Codex 用内置 `imagegen`）。
- **坐标体系**：`deck.json` 用 fraction（相对幻灯片宽高）或 px 描述每一层 x/y/w/h，`compose_pptx.py` 把分数坐标转 EMU（`EMU_PER_INCH=914400`）写入真实 pptx。

## 四、应用场景与启发

- **"AI 出图 + 还原可编辑"的 PPT 生产范式**：当你要快速拿到"排版豪华、信息密度高"的 PPT 又必须能二次编辑，这套**先视觉生成、再分层还原**的思路比"直接让 LLM 写 pptx"更能保证美观度，可直接借鉴其四层拆解与 QA 链路。
- **Agent 技能包的工程化样本**：三个技能各自 `SKILL.md + scripts + references + 参考图` 自包含，是"可复制给其他 Agent 的技能包"的好范本，对搭 WorkBuddy/Codex 类 skill 体系有参考。
- **局限即启发**：它明确"仅限 Codex + GPT 生图"，提示我们"强依赖特定模型生图/视觉"的技能需要抽象出后端接口才能跨 Agent 移植。

## 五、源码深度解读（关键片段）

`GordenImage2PPTX/scripts/compose_pptx.py` 是还原核心，docstring 即定义了分层 schema：

```python
"""Compose an editable .pptx from background images, cut-out icons, and text.
Final step: background (full-bleed) -> whole-frame PNG -> icon/decoration PNGs
(positioned) -> text boxes. Text stays editable; frame/icons stay movable pictures.
"""
EMU_PER_INCH = 914400
# deck.json 每层用 fraction 或 px 描述坐标；文本用 size_ratio 相对源图高缩放
def _text_size_pt(item, sh_pt, ref_h, default=None):
    if item.get("size_ratio") is not None:
        return float(item["size_ratio"]) * sh_pt   # 随幻灯片高度干净缩放
```

为了让中文正确渲染，它对每个 run 同时设置拉丁/东亚/复杂文字字体：

```python
def _set_run_fonts(run, name):
    run.font.name = name
    rpr = run._r.get_or_add_rPr()
    for tag in ("a:ea", "a:cs"):          # east-asian + complex-script typeface
        el = rpr.makeelement(qn(tag), {}); el.set("typeface", name); rpr.append(el)
```

`GordenImage2PPTX/SKILL.md` 则是该技能的逐步工作流（含背景/框架/图标/文本四阶段提取与约束规则）；`GordenImagePPTGen` 侧用 `references/image-prompt-guide.md` + 5 套参考风格图保证生图一致性。

## 六、全网口碑

- **正面**：星标 2k，国内 AI PPT 赛道人气技能包；效果演示（图片 PPT → 可编辑 pptx）直观，被多个 AI PPT 分享帖引用；技能包自包含、复制即用，对 Codex 用户友好。
- **风险/争议**：**强绑定 Codex + GPT 生图/视觉**（README 明示），Opus+GPT 生图接口理论上可行但未专门适配；还原 1 张图约耗 Plus 订阅 5 小时额度的 10%，成本不低；许可为 MIT 但商用须注明仓库或作者 @Gorden Sun；本质是基于 GPT 能力的"提示词 + 脚本"工程，迁移到其他生图后端需改适配层。

## 七、竞品对比与核心研判

| 维度 | GordenSuperPPTSkills | PPTAgent / Paper2Slides | 直接 LLM 写 pptx |
|------|---------------------|--------------------------|------------------|
| 产出质量 | 生图高美观 + 可编辑 | 结构严谨但偏朴素 | 排版易翻车 |
| 可编辑性 | ✅ 文本/图框分层 | ✅ | ⚠️ 常乱 |
| 模型依赖 | 强绑 GPT 生图/视觉 | 多模型 | 任意 LLM |
| 跨 Agent | 需适配后端 | 较重 | 易 |

**竞品**：`icip-cas/PPTAgent`、`HKUDS/Paper2Slides`（agentic PPT 生成）、各类"LLM 直接输出 pptx"脚本。**GordenSun 的差异**是"先视觉生成保美观、再还原保可编辑"的折中路线。

**核心研判**：⭐⭐⭐ — 想要"又快又好看且能改"的 AI PPT、且已在用 Codex + GPT 的用户，这是性价比很高的技能包，其 **四层还原 + QA 校验 + 自包含技能包** 设计值得抄；但强绑 GPT 生图/视觉与较高 token 成本，使其难以直接跨 Agent/跨模型复用。建议后续抽象出生图后端接口以解除绑定。

## 八、关键文件路径速查

- `GordenImage2PPTX/scripts/compose_pptx.py` — 分层还原为可编辑 pptx 的核心
- `GordenImage2PPTX/scripts/{layout_guard,placement_qa,visual_compare_qa,probe_palette,chroma_key,frame_parts_to_icons}.py` — QA / 拆解辅助
- `GordenImage2PPTX/SKILL.md` · `references/image-to-pptx.md` · `references/runtime-notes.md` — 技能与工作流说明
- `GordenImagePPTGen/SKILL.md` · `references/image-prompt-guide.md` · `参考图/`（5 套风格）— 生图技能
- `GordenSuperPPTSkill/SKILL.md` · `references/pipeline.md` — A→B 编排
- 许可/致谢：README（商用需注明 @Gorden Sun）｜ 社区：LinuxDO
