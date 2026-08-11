# 📊 深度调研报告：op7418/guizang-social-card-skill

> **仓库**: [op7418/guizang-social-card-skill](https://github.com/op7418/guizang-social-card-skill)
> **Stars**: 6,201 ⭐ | **Forks**: 501 | **Open Issues**: 9
> **语言**: HTML / JavaScript | **License**: AGPL-3.0（另附商业授权文件） | **默认分支**: `main`
> **创建**: 2026-05-27 | **最后推送**: 2026-07-01 | **文件数**: 46 blob
> **调研日期**: 2026-08-11（本次为 2026-06-17 版本的**重写升级**：原报告缺源码/口碑/竞品/研判，且仓库已从"静态图文卡片"演化为"实况照片生产线"，能力面貌大变）

---

## 一、项目定位（一句话）

**一个把"社交平台图文排版"整体外包给 Agent 的 Skill——输入文章/截图/视频，输出符合小红书 3:4、公众号 21:9+1:1 规格的成品卡片，且现在支持渲染成 iPhone 实况照片（Live Photo）。**

---

## 二、项目亮点（差异化）

1. **⚡ 已经不是"生成图片"了，是"生成实况照片"** — 这是相比 2026-06 版本最大的能力跃迁。仓库现在能把用户提供的视频/录屏，封装成 iPhone 原生 `.pvt` Live Photo 包（JPG + H.264 MOV 配对），直接 AirDrop 到手机发小红书。**"图文帖里塞动效"这个小红书流量玩法被工程化了。**
2. **单文件 HTML → PNG 的极简管道** — 唯一运行时依赖是 `playwright ^1.60.0`。不需要设计工具、不需要图片 API、不需要模型出图。排版逻辑全在 HTML/CSS 里，Agent 写 HTML，Playwright 截图，完事。
3. **`check-skill-docs.mjs`：给 Skill 文档写单元测试** — 极罕见的做法。用 `mustInclude` / `mustNotMatch` 对 SKILL.md 做断言校验，把"文档里必须有这句护栏"变成 CI 可执行的测试。
4. **反污染护栏被硬编码进测试** — 有一条断言专门检查 SKILL.md 必须包含 `"Generated work must live in a task folder, not in the skill root."`。作者踩过 Agent 把生成物拉到仓库根目录的坑，然后把这个教训写成了测试。
5. **"能力圈"式的自我设限** — SKILL.md 里明确列 `Do not use this skill for:` 三条（完整 PPT / 长视频生成 / 纯图片编辑无排版需求），并指向兄弟 skill。同时把小红书 11 个高频品类归成三个桶，做 recipe 级路由。
6. **AGPL-3.0 + 独立商业授权文件** — 中文 Agent Skill 生态里少见的双轨授权。个人用户自由用，商用需另谈。作者对"技能资产化"是有商业意识的。

---

## 三、核心架构

### 3.1 真实文件树（46 blob，`main` 分支）

```
guizang-social-card-skill/
├── SKILL.md                    ← 主入口（含能力圈 + 反污染护栏）
├── AGENT.md  PRODUCT.md  HANDOFF.md
├── COMMERCIAL_LICENSING.md     ← 商业授权（AGPL 之外的双轨）
├── package.json                ← 唯一依赖：playwright ^1.60.0
├── agents/openai.yaml          ← 跨运行时适配
│
├── assets/
│   ├── template-editorial-card.html    ← 电子杂志风模板
│   ├── template-swiss-card.html        ← 瑞士国际主义风模板
│   ├── magazine-bg-webgl.js            ← WebGL 背景生成
│   └── screenshot-backgrounds/
│       ├── style-a/  (dune / forest-ink / indigo-porcelain / kraft-paper / monocle-classic)
│       └── style-b/  (ikb-dot-gradient / lemon-green-dot-shadow / lemon-grid / safety-orange-halftone)
│
├── references/                 ← 17 个知识分片（惰性加载）
│   ├── live-photo-production.md    ← ⭐ 新增能力核心
│   ├── category-cookbook.md        ← 11 品类 recipe 路由
│   ├── style-system.md  theme-presets.md  layout-recipes.md
│   ├── components.md  background-systems.md  screenshot-treatment.md
│   ├── image-overlay.md  portrait-fill.md  map-component.md
│   ├── content-planning.md  title-shortener.md  platform-specs.md
│   ├── production-workflow.md  qa-checklist.md
│
└── scripts/
    ├── package-live-photo.py           ← JPG+MOV → .pvt 打包
    ├── add-livephoto-mov-metadata.swift    ← MOV 侧元数据注入
    ├── add-livephoto-maker-note.swift      ← 关键帧 MakerNote
    ├── make-video-contact-sheet.py     ← 视频接触印相（选帧用）
    └── check-skill-docs.mjs            ← ⭐ Skill 文档单元测试
```

### 3.2 三层架构

```
┌─ L1 路由层 ── SKILL.md description（含 11 类中文触发词：小红书图文/实况照片/
│                二宫格实况拼图/微信公众号封面/Swiss Style ...）
│
├─ L2 决策层 ── SKILL.md 正文：能力圈（What To Produce / Do not use）
│                + 品类三桶分流 + 反污染护栏（输出必须落 local-tests/<slug>/）
│
└─ L3 执行层 ── references/*.md（17 片按需加载）
                 + assets/*.html（模板）
                 + scripts/*（Playwright 截图 / Live Photo 打包 / Swift 元数据）
```

### 3.3 Live Photo 管道（本次调研最值得记录的新增架构）

这是一条**跨语言、跨平台的真实工程管道**，不是提示词游戏：

```
用户视频 / 录屏
   ↓ make-video-contact-sheet.py       # 生成接触印相，Agent 视觉选帧
   ↓ [首帧提取 → 静态图预览]            # Preview-First：先确认排版再烧渲染预算
   ↓ HTML 模板（image well → video well）
   ↓ Playwright 渲染                    # 1080x1440 JPG（key photo）
   ↓ H.264 MOV 编码
   ↓ add-livephoto-mov-metadata.swift  # MOV 侧 Live Photo 元数据
   ↓ add-livephoto-maker-note.swift    # 关键帧 MakerNote
   ↓ package-live-photo.py (makelive)  # → .pvt bundle
   ↓ AirDrop → iPhone 相册 → 发小红书
```

**关键设计：Preview-First。** `live-photo-production.md` 明确写了——先抽视频首帧当静态图，确认排版无误，**再**去生成 MOV/.pvt。这是对"渲染成本"的显式管理，也是 Agent 工作流里少见的成本意识设计。

---

## 四、应用场景与启发 ⭐

### 4.1 什么时候该想起这个仓库

| 你的问题 | 这个仓库给的答案 |
|---|---|
| "怎么让 Agent 产出能直接发的社交图文，而不是丑排版？" | HTML 模板 + Playwright 截图，排版确定性由 CSS 保证，不靠模型审美 |
| "怎么用代码生成 iPhone Live Photo？" | `scripts/` 四件套：Python(makelive) + 两个 Swift 元数据注入器，**这是全网可复制性最高的开源实现之一** |
| "我的 Skill 文档老被 Agent 改坏/关键护栏被删怎么办？" | `check-skill-docs.mjs`：给文档写断言测试，进 CI |
| "Agent 老把生成物拉到项目根目录污染仓库" | 抄它的 `local-tests/<slug>/` 强制任务文件夹约定 + 测试断言兜底 |
| "怎么防止 Skill 什么都想干、边界模糊？" | 抄它的 `Do not use this skill for:` 三条 + 指向兄弟 skill |
| "视频太长塞不进卡片怎么办？" | Intake Decision Tree：裁剪 / 加速 / 拆三连拼图 / 反问用户要时间段 |
| "怎么避免生成的内容一看就是 AI 做的？" | 它有条很妙的规则见 4.2 ③ |

### 4.2 可迁移的四个设计模式

**① 确定性排版 vs 生成式排版。** 用 HTML/CSS 模板 + 无头浏览器截图，而不是让模型直接画图。**排版质量的下限由 CSS 锁死，模型只负责填内容**。任何需要"稳定出图"的场景（报表、证书、海报、发票）都该走这条路，而不是 diffusion。

**② 给文档写单元测试。** `mustInclude(file, needle, label)` / `mustNotMatch(file, pattern, label)` 两个原语就够了。当你的 SKILL.md 里有"绝不能丢"的护栏句，就给它加一条断言。**Agent 会改文档，测试才是护栏的护栏。**

**③ 区分"生产标签"与"读者可见文案"。** `live-photo-production.md` 里有一条极精妙的规则：`3s`、`5s`、`Live Photo`、`triple collage`、`information budget`、`speed-up`、`highlight detection` 这些内部生产术语**只能出现在规划笔记、文件名、QA 摘要里，绝不能进 H1 或正文**——"可见卡片应该读起来像用户发的，而不是像 Agent 在解释自己怎么做的"。
> **这条规则的普适性远超社交卡片。** 任何 AI 生成的对外产物（邮件、周报、文案、PPT），都存在"内部脚手架词汇泄漏"问题。把"术语黑名单"写进 Skill，是低成本高收益的做法。

**④ Preview-First 成本闸门。** 昂贵操作（渲染、模型调用、编码）之前先出一个廉价预览，确认再执行。Agent 工作流里应该到处都有这种闸门。

### 4.3 局限提醒

- **Live Photo 链路强依赖 macOS**：两个元数据注入器是 `.swift`，Windows/Linux 用户拿不到完整能力。
- **AGPL-3.0 有传染性**：商用前务必看 `COMMERCIAL_LICENSING.md`。
- **强中文场景绑定**：触发词、品类 cookbook、平台规格全部围绕小红书/公众号，海外场景要大改。

---

## 五、源码深度解读（克制版）

### 5.1 `check-skill-docs.mjs` — 全仓最值得抄的 30 行

```javascript
#!/usr/bin/env node
import fs from "node:fs";
const checks = [];
const fileText = (file) => fs.readFileSync(file, "utf8");

function mustInclude(file, needle, label) {
  checks.push(() => {
    const ok = fileText(file).includes(needle);
    return { ok, label,
      detail: ok ? `${file} includes "${needle}"` : `${file} must include "${needle}"` };
  });
}
function mustNotMatch(file, pattern, label) {
  checks.push(() => {
    const ok = !pattern.test(fileText(file));
    return { ok, label, detail: ok ? `...` : `${file} must not match ${pattern}` };
  });
}

mustInclude("SKILL.md",
  "Generated work must live in a task folder, not in the skill root.",
  "root output guardrail in SKILL.md");
mustInclude("SKILL.md", "local-tests/<slug>/", "default task folder in SKILL.md");
```

**解读**：整个测试框架就是两个高阶函数 + 一个 checks 数组，没有引入 jest/vitest。极致克制。真正的价值在**被断言的内容**——第一条断言保护的是"防止 Agent 把生成物拉到仓库根目录"这条护栏。这说明作者被这个问题咬过，而且解决方式不是"再强调一遍"，是"让 CI 保证这句话永远在"。

`package.json` 里挂成 `"test:docs": "node scripts/check-skill-docs.mjs"`，零依赖可跑。

### 5.2 `package-live-photo.py` — Live Photo 打包的最小实现

```python
#!/usr/bin/env python3
"""Package a JPG/MOV pair as an AirDrop-friendly Live Photo .pvt bundle.
Run with:
  UV_CACHE_DIR=/private/tmp/uv-cache UV_TOOL_DIR=/private/tmp/uv-tools \
  uvx --from 'makelive==0.7.0' python scripts/package-live-photo.py IMG.JPG IMG.MOV
"""
from makelive import save_live_photo_pair_as_pvt

def main() -> None:
    # jpg: 通常 1080x1440 key photo；mov: 配对的 H.264
    asset_id, pvt_path = save_live_photo_pair_as_pvt(str(jpg), str(mov))
    print(asset_id); print(pvt_path)
```

**解读**：核心逻辑其实是第三方库 `makelive==0.7.0` 干的，本脚本只做参数校验 + 调用。但**版本被死锁**（`makelive==0.7.0` 而非 `>=`），且通过 `uvx --from` 临时安装、`UV_CACHE_DIR` 重定向到 `/private/tmp`——**不污染用户全局 Python 环境**。这是 Agent Skill 调用外部 Python 工具的正确姿势：临时、隔离、锁版本。

### 5.3 `SKILL.md` 的能力圈声明

```markdown
Do not use this skill for:
- Full slide decks or horizontal PPT websites. Use the PPT skill for that.
- Long-form video generation. Use a video skill for that. This skill only supports
  short, layout-bound Live Photo cards that replace a still image slot with video.
- Pure image editing with no layout or article extraction requirement.
```

三条否定 + 每条都指向替代方案。**否定清单比肯定清单更能定义一个 Skill**——它是防止过度触发的唯一手段，也是 Skill 之间协作而非打架的前提。

---

## 六、社区口碑

- **增长曲线**：2026-06-17 调研时 3,229 ⭐ → 2026-08-11 达 **6,201 ⭐**，不到两个月**接近翻倍**。在中文 Agent Skill 里属于头部梯队。
- **Fork/Star 比 8.1%（501/6,201）**：中高。符合"模板类仓库"特征——大量用户 fork 后改成自己的品牌配色/字体/尺寸。
- **Issue 9 个开放**：对一个有 Playwright + Swift + Python 多语言链路的仓库来说非常少，说明核心路径稳定；也可能反映**Windows 用户直接放弃**（Live Photo 链路要 macOS）而非提 issue。
- **作者背书**：op7418（歸藏）是中文 AI 圈知名 KOL，本仓库是其「歸藏 PPT 风格体系」的社交卡片衍生品。**流量来源主要是作者影响力，而非自然搜索**——这意味着星标数含一定"人气溢价"，实际深度使用者比例需打折。
- **维护节奏**：2026-05-27 创建 → 2026-07-01 最后推送。近 6 周未更新，但期间完成了从"静态卡片"到"Live Photo 生产线"的重大能力扩张，属于**集中式迭代后的平台期**。
- **商业化信号**：`COMMERCIAL_LICENSING.md` 的存在 + AGPL-3.0 选择，说明作者认真考虑过技能资产的商业边界。这在开源 Skill 里是少数派。

---

## 七、竞品对比

| 项目 | 定位 | 对比结论 |
|---|---|---|
| **Canva / 稿定设计 / 创客贴** | SaaS 图文设计 | 模板更多、上手更易；但**无法嵌入 Agent 工作流**，需人工操作，且不能生成 Live Photo |
| **HTML→图 类通用 Skill**（如 nexu-io/html-anything，本库已收录） | 通用 HTML 渲染 | 更通用但无视觉体系。guizang 的价值恰恰在于**预置了两套完整视觉语言 + 11 品类 recipe**，不需要用户懂设计 |
| **op7418/guizang PPT skill**（同作者） | PPT 生成 | 同源视觉体系的姊妹项目。本仓库 SKILL.md 明确声明"借用其视觉原则但不得修改原 PPT skill" |
| **纯 Diffusion 出图（Midjourney / SD / Nano Banana）** | 生成式图像 | 审美上限更高，但**排版不可控、文字渲染不可靠、尺寸不精确**。做规格化社交卡片是 CSS 完胜 diffusion 的典型场景 |
| **op7418/Humanizer-zh**（同作者，本库已收录） | 中文文本人味化 | 互补——一个管文字，一个管排版，可串联 |
| **手动 Keynote/Figma 导出** | 人工排版 | 质量上限最高，速度最慢。本仓库把"够用的质量"的边际成本压到接近零 |

**竞争位置判断**：它不与 Canva 竞争"最好用的设计工具"，而是占据了**"Agent 工作流里的最后一公里排版"**这个位置。护城河是两套成熟视觉体系 + 中文平台规格的深度适配 + 作者的审美信誉。Live Photo 能力目前在开源侧近乎独一份，是最强差异点。

---

## 八、核心研判

**值得抄的（★★★★★）**
1. `scripts/check-skill-docs.mjs` 的**"给 Skill 文档写单元测试"** — 30 行、零依赖、立刻能用在任何 Skill 仓库上。
2. **"生产术语不得进入读者可见文案"** 这条规则 — 普适于一切 AI 对外产物。
3. `scripts/package-live-photo.py` 的 **`uvx --from` + 锁版本 + 缓存重定向** 调用姿势 — Agent 调外部 Python 工具的标准答案。

**值得装的（★★★★☆ / macOS 用户；★★★☆☆ / 其他）**
如果你在 macOS 上做中文社交内容，这是目前开源侧最完整的方案，装了就能用。Windows/Linux 用户能用静态卡片部分（Playwright 链路跨平台），但拿不到 Live Photo——**能力打对折**。

**要清醒的（⚠️）**
1. **AGPL-3.0 传染性**：商用前必读 `COMMERCIAL_LICENSING.md`，不要想当然。
2. **6,201 ⭐ 含 KOL 人气溢价**：作者影响力驱动的星标，与"实际日活使用者"不是一回事。评估时按实际能力而非星数判断。
3. **近 6 周未更新**：平台期正常，但 Playwright、makelive 版本锁死，长期需自行跟进依赖安全更新。
4. **强绑定中文平台规格**：小红书 3:4、公众号 21:9+1:1 是硬编码假设，海外平台（Instagram 4:5、Threads）需要自己改 `platform-specs.md`。
5. **17 个 references 的上下文成本**：全量加载会很重，依赖惰性加载机制正常工作。

**一句话结论**
> **一个从"AI 排版工具"进化成"iPhone 实况照片生产线"的 Skill。** 它最大的技术贡献不是那些漂亮模板，而是证明了：**确定性排版（HTML+CSS+Playwright）在规格化出图上完胜生成式模型**；而它最大的方法论贡献，是把"给 Skill 文档写单元测试"和"生产术语不得泄漏到读者文案"这两条经验固化成了可执行代码。

---

## 九、关键文件路径速查

| 路径 | 为什么重要 |
|---|---|
| `scripts/check-skill-docs.mjs` | **给 Skill 文档写单元测试**，30 行零依赖，最值得直接抄走 |
| `references/live-photo-production.md` | Live Photo 完整工作流：信息预算 / 三连拼图 / 长视频决策树 / 术语黑名单 |
| `scripts/package-live-photo.py` | JPG+MOV → `.pvt` 打包，`uvx --from` 隔离调用范例 |
| `scripts/add-livephoto-mov-metadata.swift` | MOV 侧 Live Photo 元数据注入（macOS 专用） |
| `scripts/add-livephoto-maker-note.swift` | 关键帧 MakerNote 注入 |
| `scripts/make-video-contact-sheet.py` | 视频接触印相，供 Agent 视觉选帧 |
| `SKILL.md` | 能力圈声明 + 反污染护栏 + 11 品类三桶分流 |
| `assets/template-editorial-card.html` / `template-swiss-card.html` | 两套视觉体系的模板本体 |
| `references/category-cookbook.md` | 小红书 11 品类的 recipe 级路由表 |
| `references/platform-specs.md` | 各平台尺寸/安全区规格 |
| `COMMERCIAL_LICENSING.md` | 商用前必读，AGPL 之外的双轨授权 |

---

*调研方法：GitHub API 实时元数据 + `git/trees` 全量 46 文件树 + raw.githubusercontent 源文件直读（SKILL.md / package.json / check-skill-docs.mjs / live-photo-production.md / package-live-photo.py）；星标/Fork/Issue 为 2026-08-11 实时值。*
