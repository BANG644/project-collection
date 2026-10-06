# liyue-aigc/female-portrait-director 深度调研

> 调研日期：2026-10-07 | 原始仓库：https://github.com/liyue-aigc/female-portrait-director
> 语言：Markdown / Skill 定义（无编译代码） | 许可：MIT | Stars：≈1,627 | 最近活跃：2026-07 | 多语言 README（en/ja/ko/zh）

## 一、项目定位（一句话）

一个 **Codex/OpenAI Skill**：把一小撮人像参数「导演式」扩展成稳定、可复制、带负向约束的女性人像图像提示词——通过「注册表路由 + 路线 + 叠加层 + 导演闸门」的分层架构，把 prompt 工程变成可维护的模块化系统，而非一次性长 prompt。

## 二、项目亮点（差异化）

- **注册表即路由入口（Registry-as-Routing）**：`style-registry` / `tool-registry` / `overlay-registry` 只做索引；运行时**只加载被选中的 1 条 route + 1 个 tool + 可选 overlay 文件**，极致省 token。
- **参数锁（Parameter Lock）**：用户显式参数（含画幅比例、身形吸引力强度、线条重点）被逐字段锁定、不可被 route/overlay 静默替换，只追加明确标注的默认值——防止「模型自作主张」。
- **导演闸门（Director-Gate）**：在写出最终提示词前，必须完成内部「导演设计阶段」，把年龄/五官/姿态/服装/光线逐段视觉推理，避免机械填表。
- **20 种风格 × 7 种叠加层 × 多工具**：覆盖 lifestyle / curve / fashion / oriental / fantasy / realism / beauty / cinematic，且按「复合指纹」匹配（如 `low-key-cinematic` 需同时满足低光+可读阴影+克制色彩+电影感，单看 `dark`/`cinematic` 不够）。
- **负向约束独立成块**：最终提示词与 negative constraints 分别用两个 `text` 围栏代码块输出，用户可直接复制。

## 三、核心架构

```
female-portrait-director/
├── SKILL.md                      # 入口：9 步加载顺序 + 操作规则（铁律级约束）
├── agents/openai.yaml            # harness 注册：display_name / default_prompt
├── skill/
│   ├── skill.md                  # 规范工作流（canonical）
│   ├── help.md                   # 首次使用教程（20 风格全列 + 演示）
│   ├── style-registry.md         # 20 风格索引（路由入口）
│   ├── tool-registry.md          # 工具索引（诊断/参数推荐/图生提示词…）
│   ├── overlay-registry.md       # 7 叠加层索引
│   ├── parameter_schema.md / public_instructions.md
│   ├── routes/                   # 23 条路线，按类拆分（懒加载）
│   │   ├── beauty/ ancient-lady-dewy-makeup.md
│   │   ├── cinematic/ low-key-cinematic-photography.md
│   │   ├── commercial/ ecommerce-tryon.md
│   │   ├── curve/  black-pearl-dark-gold-ccd.md … pure-desire-curve.md（5 条）
│   │   ├── fantasy/ bright-luxury-gufeng.md … gufeng-xianxia.md（3 条）
│   │   ├── fashion/ sporty-active.md … urban-fashion.md（3 条）
│   │   ├── lifestyle/ clean-lifestyle.md … travel-vacation.md（4 条）
│   │   ├── oriental/ new-chinese.md
│   │   └── realism/ ultra-close-real-face.md
│   ├── overlays/                 # 7 个：bright-heroine / cold-heroine / cool-mature …
│   ├── tools/                    # failure-diagnosis / image-to-prompt / parameter-recommend
│   ├── core/                     # 治理层
│   │   ├── director-gate.md      # 写最终提示词前的内部设计阶段
│   │   ├── parameter-lock.md     # 参数锁定规则
│   │   ├── reference-image-lock.md  # 授权参考图角色锁定
│   │   ├── safety-boundary.md    # 安全边界唯一权威源
│   │   ├── conflict-resolution.md / fallback-rules.md / output-format.md
│   └── references/               # director-expansion / expanded/*（详尽扩展模板）
├── docs/  faq.md · prompt_safety.md · style_guide.md · versioning.md
└── examples/  5 个主题案例包（clean_lifestyle / urban_fashion / gufeng_fantasy …）
```

## 四、应用场景与启发

- **给同类需求的解决思路**：当你要做一个「输入少、输出长且稳定」的生成型 Skill（不只是人像，任何「参数→长篇结构化产物」场景，如报告/方案/脚本生成），「**注册表索引 + 按需加载具体 route/overlay/tool 文件**」是比「把所有规则写进一个 SKILL.md」更可扩展的架构——新增风格只需加一个 route 文件并在 registry 登记，不动主流程。
- **参数锁 + 导演闸门 = 可控生成**：「锁用户参数、内部设计阶段、最后才拼装」的顺序，直接对抗 LLM 在长 prompt 生成中「偷偷改用户意图」的常见失败模式，对任何需要忠实性的生成任务都可借鉴。
- **复合指纹匹配**：避免用单一关键词路由（如 `CCD`/`curve` 多路线需组合判定），是路由逻辑防误判的实用技巧。

## 五、源码深度解读

### 1) SKILL.md 的「强制加载顺序」（渐进披露到极致）

```text
## Required loading order
1. 帮助类请求 → 只读 help.md
2. 读 skill/skill.md（规范工作流）
3. 优化/诊断/参数推荐/安全改写/图生提示词 → 读 tool-registry.md + 选中 tool 文件
4. 读 style-registry.md，仅选 1 条已实现的 primary route
5. 仅读选中的 routes/ 文件
6. 兼容性情方向 → 读 overlay-registry.md + 选中的 overlays/ 文件
7. 需保留参考图身份 → 读 core/reference-image-lock.md 建角色锁表
8. 读 core/director-gate.md，完成内部导演设计阶段
9. 仅读 skill.md 指向的 core/ references/ 相关小节
```

9 步顺序本质是「**先索引、后按需取叶节点**」的依赖图加载，把一次生成可能需要的上下文从「全量」压到「所选 route + overlay + tool」三小块。

### 2) 操作规则中的「参数锁 + 双代码块输出」

```text
- Lock explicit user parameters … Expand them without silently replacing them.
- …the parameter lock result is a complete field-by-field record of the user's explicit input.
  Do not merge, paraphrase away, omit, or replace explicit fields …
- Always render the final fused prompt and negative constraints as two separate
  Markdown fenced code blocks with the `text` language tag so the user can copy them directly.
- Standard detailed output … five substantial paragraphs:
  (1) person/age/face/makeup/temperament; (2) time slice/pose/action chain/gaze;
  (3) body/clothing/palette/materials; (4) scene/camera/depth of field;
  (5) lighting/filter/texture.
```

`agents/openai.yaml` 进一步固化入口：

```yaml
interface:
  display_name: "女性人像提示词导演"
  short_description: "20种风格的女性人像导演式提示词与授权参考图生成能力"
  default_prompt: "使用 $female-portrait-director 显示 V1.6 首次使用教程，列出全部 20 种风格，并演示…"
```

## 六、全网口碑

- GitHub ≈1.6k stars，定位垂直（成人女性人像导演式提示词），README 提供 en/ja/ko/zh 四语，表明面向国际 AIGC 创作者。
- 工程化程度高：版本化（V1.5/V1.6）、FAQ、安全摘要、风格指南、版本说明一应俱全；`docs/prompt_safety.md` 明确「默认虚构成年、禁止未成年化/裸露/非自愿情境/欺骗性身份」，治理意识成熟。
- 相对 `ian-xiaohei-illustrations`（12k stars）更垂直、更「硬核工程化」，受众是严肃做 AIGC 人像的创作者而非泛内容写作者。

## 七、竞品对比 + 核心研判

| 维度 | female-portrait-director | 通用人像 prompt 合集 | 单文件长 prompt |
|---|---|---|---|
| 风格扩展 | 20 route 文件可插拔 | 列表，无结构 | 写死 |
| 参数忠实度 | 参数锁 + 导演闸门 | 易漂移 | 易漂移 |
| token 成本 | 按需加载 | 全量 | 全量 |
| 安全治理 | 独立 safety-boundary 权威源 | 无/散落 | 无 |

**核心研判**：它是「**把 prompt 工程做成可维护软件**」的范本——注册表路由、参数锁、导演闸门、独立安全边界四件套，几乎是生成型 Skill 的架构教科书。对任何想做「复杂多分支生成 Skill」的开发者（含用户自建 skill 体系）都有直接借鉴价值。局限：垂直到成人女性人像，泛化需重构 registry；且强依赖底层图像生成能力，本身不含模型。

## 八、关键文件路径速查

- 入口与铁律：`SKILL.md`、`skill/skill.md`
- 路由索引：`skill/style-registry.md`、`skill/routes/`（23 文件，按类拆分）
- 叠加层：`skill/overlay-registry.md`、`skill/overlays/`（7 文件）
- 工具：`skill/tool-registry.md`、`skill/tools/`（failure-diagnosis / image-to-prompt / parameter-recommend）
- 治理核心：`skill/core/director-gate.md`、`skill/core/parameter-lock.md`、`skill/core/reference-image-lock.md`、`skill/core/safety-boundary.md`
- harness 注册：`agents/openai.yaml`
- 安全摘要（公开）：`docs/prompt_safety.md`
- 案例：`examples/`（5 主题包）
