# 🔬 wuji-labs/nopua - 全方位深度调研

> 调研日期：2026-09-07 ｜ 重写自模板化旧报告（原"四层组成"通用 boilerplate，无真实源码/架构/外链）
> 数据来源：GitHub 仓库 `wuji-labs/nopua` 真实 README / 目录树抓取（stars 1,388，pushed 2026-07-01，MIT，Python）

## 📌 一句话定位

`wuji-labs/nopua` 是一个**用"尊重、关怀、爱"替代恐惧驱动（PUA）的 AI 行为引导 Skill**：核心理念是——恐惧会让 AI 隐藏不确定性、跳过验证、忽视隐藏 bug；而信任驱动让 AI 多发现 **+104% 的隐藏 bug**。它直接回应了 `tanweai/pua` 那类"用公司恐惧话术驱动 AI"的 Skill。

> 核心判断：它既是**提示词方法论**（"道"=道德经哲学，"术"=系统化调试流程），也是**有实证基准的开源项目**（benchmark/ 开放复现 + arXiv 论文 2603.14373）。真正价值在"把'信任>恐惧'这个主张做成了可验证、可复现的东西"，而非只是鸡汤。

## 🏆 项目亮点（差异化）

1. **有实证基准**：9 真实场景（OCR→NLP→training→RAG，~3000 行 Python），同模型同代码，仅 NoPUA 加载与否；另做 3 条件×5 次×9 场景=135 数据点的三路对比（NoPUA vs PUA vs Baseline）。
2. **统计显著**：NoPUA vs Baseline 步骤 p=0.008\*\*、隐藏 bug p=0.016\*；**PUA vs Baseline 全部 p>0.3（无显著改善）**——"恐惧对 AI 没用，信任才有用"。
3. **7 语言 × 多平台**：Claude Code / Codex / Cursor / Kiro / OpenClaw / Antigravity / OpenCode 全覆盖，语言含中/英/日/韩/西/葡/法。
4. **道术分离**：哲学层（道德经）与方法层（Water Methodology 5 步）解耦，power user 可只取"道"并入自己的 AGENTS.md。
5. **触发灵活**：auto-trigger（失败 2+ 次 / 推锅 / 被动忙活 / 用户挫败语） + 手动 `/nopua`。

## 🏗️ 核心架构

多平台 Skill 包 + 研究资产：

```
nopua/
├── SKILL.md                    # 主 Skill（Three Beliefs / Cognitive Elevation / Water Methodology / 7 Ways）
├── agents/nopua-mentor-{en,ja}.md   # 导师 agent
├── codex/ cursor/ kiro/ commands/  # 各平台安装形态
├── skills/nopua{,-lite,-zh}/SKILL.md
├── benchmark/                  # ← 最有价值：开放复现的实证
│   ├── run_benchmark.py        # 基准测试脚本
│   ├── scenarios.json          # 9 场景定义
│   ├── pua_prompt.txt          # PUA 对照 prompt
│   ├── results_with(out)_nopua.json
│   └── BENCHMARK.md
├── paper/                      # arXiv 2603.14373 论文（LaTeX + 提交包）
├── docs/ examples/ promotion/  # 文档 / lite 模板 / 推广文案
└── validate.mjs / .claude-plugin/  # 校验 + 插件清单
```

## 🧠 源码深度解读

### 1. `benchmark/run_benchmark.py` —— 实证的核心

这是项目最"硬"的部分：脚本在**同一份 ~3000 行生产代码（OCR→NLP→training→RAG 推理）**上跑 9 个真实调试场景，控制变量仅为"是否加载 NoPUA Skill"。产出 `results_with_nopua.json` / `results_without_nopua.json`，供独立复现。方法学透明度远高于一般"提示词玄学"。

### 2. `SKILL.md` 的方法论骨架

- **Three Beliefs** 替代 "Three Iron Rules"：穷尽选项 / 先行动后提问 / 主动推进——动机从"怕惩罚"改写为"值得做好"。
- **Cognitive Elevation**（失败分级）：2 次→Switch Eyes（换视角）；3 次→Elevate（zoom out）；4 次→Reset to Zero（从最简假设重启）；5+→Surrender（负责任交接）。
- **Water Methodology 5 步**：止（列尝试找共性）→观（逐字读错→搜→读源码→验假设）→转（是否重复/找根因/搜过/读过）→行（新路径+可验证）→悟（为何没想到+顺查相关问题）。

### 3. `paper/nopua-paper.tex` —— 学术包装

把"系统提示词中的动机框架（信任 vs 恐惧）如何影响 AI agent 调试深度"写成 arXiv 论文（2603.14373），引用 Öhman 2001 / Shields 2016 / Deci & Ryan 2000 / Google Aristotle 等支撑"恐惧收窄认知、信任扩展问题求解"的论点。

## 🌐 全网口碑画像

- GitHub：1,388⭐、MIT、活跃（pushed 2026-07-01）、`wuji-labs` 出品，有 arXiv 论文 2603.14373、多语言 README、skills.sh 发布。
- 社区定位：AI agent 提示词方法论（反 PUA 运动），在 vibe-coding / agent 圈有传播度；含微信社群运营。
- 暂无独立第三方大规模复现；以"开放 benchmark + 论文"双重信号看，比纯观点型 skill 更可信。

## ⚔️ 竞品对比

| 方案 | 优势 | 风险 |
|---|---|---|
| `wuji-labs/nopua` | 有实证基准（开放复现）+ 论文 + 7 语言 + 道术分离 | 效果主张依赖自有基准（样本有限）；29KB 对强模型偏冗余 |
| `tanweai/pua` | 方法论同样严谨（穷尽/验证/主动） | 动机层（恐惧）被本项目证明"无显著增益且可能反效果" |
| 通用调试类 skill（systematic-debugging 等） | 聚焦流程、无叙事 | 缺"动机框架"维度的实证探讨 |

## 🎯 核心研判

**优势**：① 把"信任>恐惧"从口号做成**可验证、可复现**的项目（benchmark/ 全开放）；② 道术分离设计让它能融入既有 AGENTS.md 工作流；③ 多语言多平台，分发面广。

**风险**：① 基准为**自有场景 + 单一模型族**（Claude Sonnet 4.6），结论需更多模型/任务独立复现；② "道德经"叙事可能被部分用户视为软性营销；③ 29KB 完整版对强模型冗余（官方已提供 lite 模板）。

**适用场景**：希望 AI agent 更诚实（敢说"我不知道"）、更主动（不止于"修好就停"）、不隐藏 bug 的开发者；已有一套工作流、只想补"动机层"的 power user。

**不适用场景**：把"软"误解为"没标准"——本项目方法论 rigor 与 PUA 完全一致，只换动机；纯追求最短上下文的极简用户应选 lite 版。

## 📂 关键文件路径速查

- `README.md` / 多语言版：问题陈述、PUA vs NoPUA 对比、基准数据、哲学、FAQ、安装。
- `SKILL.md`：Three Beliefs / Cognitive Elevation / Water Methodology / 7 Ways 方法论全量。
- `benchmark/run_benchmark.py` + `scenarios.json` + `results_with(out)_nopua.json`：开放复现的实证核心。
- `paper/nopua-paper.tex`：arXiv 2603.14373 论文。
- `examples/lite-template.md`：power user 提取"道"的 ~3KB 精简模板。
- `codex/ cursor/ kiro/ commands/`：各平台安装形态。

## ⭐ 三条关键发现

1. 它最硬的资产是 **`benchmark/` 的开放复现**——"信任>恐惧"不是观点，而是带 p 值的主张，这在提示词类 skill 里很少见。
2. **道术分离**是聪明设计：方法论（术）可复用、哲学（道）可单取，因此能无缝并入既有 AGENTS.md 而非冲突。
3. 引用需冷静：基准基于**自有 9 场景 + 单一模型族**，建议结合自身项目实测后再下结论，勿直接当成普适真理。
