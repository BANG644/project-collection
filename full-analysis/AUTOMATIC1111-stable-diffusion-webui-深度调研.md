# 🔬 AUTOMATIC1111/stable-diffusion-webui — 全方位深度调研

> 调研日期：2026-09-02 ｜ 星标：164,759 ⭐ ｜ Fork：30,558 ｜ 开放 Issue：2,503 ｜ 语言：Python ｜ 协议：AGPL-3.0 ｜ 默认分支：**master** ｜ 创建：2022-08-22 ｜ 仓库体积：36.5 MB

## 📌 项目定位

`AUTOMATIC1111/stable-diffusion-webui`（社区简称 **A1111**）是 Stable Diffusion 生态**事实上的第一代标准 Web 前端**：基于 Gradio 的本地文生图 / 图生图工作台，靠"插件即扩展目录"的机制长出了整个 SD 插件生态（ControlNet、Regional Prompter、Tagger 等均以它为宿主）。

> **核心判断（本次调研最重要的修正）**：A1111 已从"活跃项目"转为**事实冻结的生态基座**。`master` 分支最后一次提交是 **2024-07-27**（即 v1.10.0 的 changelog 提交），距今约 2 年零功能推进；`dev` 分支仅剩"装不上就修一下"的依赖急救。它今天的价值不是"活跃的好工具"，而是**插件生态的兼容性锚点 + API 契约的历史标准**。任何新项目选型都不应把它当成会持续演进的上游。

## 🏆 项目亮点（差异化）

1. **"扩展 = 一个目录"的极低插件门槛**：`extensions/` 下放一个含 `scripts/` 的 git 仓库即生效，无需注册中心、无需打包发布。这是 SD 插件生态爆发的直接原因，也是它至今无法被替代的护城河。
2. **`sd_hijack_*` 猴补丁架构**：不 fork 上游 CompVis / k-diffusion / open_clip，而是运行时替换其内部函数（见下文源码解读）。用极小代价换来"跟得上上游模型演进"的能力。
3. **采样器矩阵作为独立抽象层**：`sd_samplers_kdiffusion` / `sd_samplers_timesteps` / `sd_samplers_lcm` / `sd_schedulers` 把"采样算法"与"UI/流程"彻底解耦，新采样器可独立接入。
4. **显存分级降级策略**：`lowvram.py` + `devices.py` 让 4GB 显存也能跑（模块级动态搬运 CPU/GPU），这是它在消费级硬件普及的关键。
5. **`xyz_grid.py` 参数网格实验**：内置的多维参数扫描脚本，把"调参"变成可批量复现的对照实验——很多商业工具至今没做这么好。
6. **完整 HTTP API 复用同一套处理管线**：`modules/api/api.py` 暴露的 `/sdapi/v1/txt2img` 等端点成了行业默认契约，大量第三方（含商业产品）按它的请求体格式对接。

## 🏗️ 核心架构（克制版）

```
webui.sh / webui.bat  ──►  launch.py ──► 依赖自举 (prepare_environment)
                                          │  git clone 上游 repo 到 repositories/
                                          ▼
                                       webui.py  (initialize)
        ┌─────────────────────────────────────────────────────────┐
        │ modules/initialize.py · shared*.py（全局状态 & options） │
        └───────────────┬─────────────────────────────────────────┘
                        ▼
        ┌───────────────────────────────────────────────────────────┐
        │ sd_hijack*.py  ← 猴补丁层（替换 CompVis/CLIP/注意力实现）  │
        │   sd_hijack_clip / open_clip / unet / optimizations ...   │
        └───────────────┬───────────────────────────────────────────┘
                        ▼
        ┌───────────────────────────────────────────────────────────┐
        │ processing.py  ← 真正的生成主流程（StableDiffusionProcessing）│
        │   prompt_parser → sd_samplers_* → sd_vae → postprocessing  │
        └───────┬───────────────────────────────┬───────────────────┘
                │                               │
   scripts.py（脚本/扩展调度）           extra_networks.py（Lora/Hypernet/TI）
                │                               │
   ┌────────────▼──────────────┐    ┌───────────▼──────────────┐
   │ scripts/ · extensions/    │    │ extensions-builtin/Lora  │
   │ extensions-builtin/       │    │ LDSR · SwinIR · ScuNET   │
   └───────────────────────────┘    └──────────────────────────┘
                │
   ┌────────────▼──────────────────────────────┐
   │ 出口双通道： ui*.py (Gradio) │ api/api.py │
   └───────────────────────────────────────────┘
```

要点：**`launch.py` 会在首次运行时 git clone 上游仓库到 `repositories/`**——这是它"依赖地狱"的根源，也是 dev 分支近两年所有修复的战场（上游 URL 失效、CLIP 装不上、setuptools 版本冲突）。

## 💡 应用场景与启发（重点）

**什么时候该去翻这个仓库？**

- **要设计"零注册插件系统"时**：`modules/scripts.py` + `script_callbacks.py` 是教科书级范本——目录扫描 + 生命周期回调 + `AlwaysVisible` 哨兵 + 拓扑排序解决插件顺序。任何需要"用户丢个文件夹就能扩展"的产品（编辑器、CLI、Agent 工具箱）都值得抄这套。
- **要在不 fork 上游的前提下改上游行为时**：`sd_hijack_*` 展示了猴补丁的工程化做法（集中管理、可撤销、按上游版本分叉如 `sd_hijack_clip_old.py`）。这是"依赖快速演进但你必须改它"场景的现实解法。
- **要做显存/资源分级降级时**：`lowvram.py` 的"按模块动态搬运权重"思路可迁移到任何大模型本地推理产品。
- **要定义领域 HTTP API 时**：A1111 的 API 之所以成为标准，是因为它**与 UI 共用同一套 `processing.py` 管线**，没有"API 是二等公民"的分裂。这个"单一管线、双出口"原则值得直接套用。
- **反向启发（血泪教训）**：`launch.py` 运行时 git clone 上游 = 把别人的仓库可用性变成你的运行时依赖。它近两年的全部维护成本都花在这上面。**教训：构建期依赖不要放到运行时拉取。**

**今天还该用它吗？** 需要老插件（尤其 ControlNet 老版本）或要复现 2023–2024 的工作流 → 用它；新建生产管线 → 优先 ComfyUI（节点化、活跃）或 Forge / reForge（A1111 分支但持续维护）。

## 🧠 源码深度解读（3 个核心模块）

### 1) 插件调度系统 — `modules/scripts.py`

真实抓取的文件开头已经暴露了整套设计：

```python
from modules import (shared, paths, script_callbacks, extensions,
                     script_loading, scripts_postprocessing, errors, timer, util)

topological_sort = util.topological_sort   # 插件顺序 = 拓扑排序，而非注册序

AlwaysVisible = object()                   # 哨兵：标记"常驻 UI"的扩展

class MaskBlendArgs:                       # 回调参数对象化
    def __init__(self, current_latent, nmask, init_latent, mask,
                 blended_latent, denoiser=None, sigma=None):
        ...
        self.is_final_blend = denoiser is None   # 用参数缺省推断阶段
class PostSampleArgs: ...
class PostprocessImageArgs: ...
class PostProcessMaskOverlayArgs: ...
```

三个可直接借鉴的设计决策：
- **回调参数封装成类**而非长参数列表 → 后续给回调加字段不破坏已有插件签名（这是插件生态能撑 3 年的关键）。
- **`AlwaysVisible` 用 `object()` 哨兵**而非布尔/字符串 → 不与任何合法值冲突。
- **拓扑排序决定插件顺序** → 插件可声明依赖关系，而不是靠文件名前缀排序这种脆弱手段。

### 2) 猴补丁层 — `modules/sd_hijack*.py` 家族（14 个文件）

真实文件清单本身就是架构说明书：

```
sd_hijack.py               # 总入口，统一 apply / undo
sd_hijack_clip.py          # 替换 CLIP 文本编码（支持 75+ token 分块、权重语法）
sd_hijack_clip_old.py      # 兼容旧上游版本 —— 按版本分叉而非 if/else 堆积
sd_hijack_open_clip.py     # open_clip（SD2.x）单独处理
sd_hijack_optimizations.py # 注意力优化（xformers / sdp / sub-quadratic）
sd_hijack_unet.py          # UNet 精度与 dtype 干预
sd_hijack_ip2p.py          # instruct-pix2pix 特化
sd_hijack_xlmr.py          # 多语言文本编码器
sd_hijack_checkpoint.py    # gradient checkpointing
sd_hijack_utils.py         # 补丁工具（CondFunc 条件替换）
```

**为什么必须 hijack？** 原生 CLIP 有 77 token 硬上限，而 SD 用户要写长 prompt 并带 `(word:1.2)` 权重。A1111 用 `sd_hijack_clip.py` 把长 prompt 切块、分别编码、再拼接，同时接管权重解析（配合 `prompt_parser.py` / `sd_emphasis.py`）。这个能力上游从未提供，却是所有 SD 用户的日常——**这是 A1111 不可替代性的真正来源，也是 README 完全不会告诉你的事**。

### 3) 生成主流程与显存降级 — `processing.py` + `lowvram.py` + `devices.py`

`processing.py` 是全仓库最核心的单文件，定义 `StableDiffusionProcessing` 及 txt2img / img2img 两个子类，把"参数 → 潜空间 → 采样 → VAE 解码 → 后处理"串成一条可被插件在多个 hook 点切入的流水线。配套：

- `lowvram.py`：按模块（cond_stage / first_stage / UNet）动态在 CPU↔GPU 间搬运权重，实现 `--lowvram` / `--medvram`。
- `devices.py` + `torch_utils.py`：设备/dtype 统一抽象；`npu_specific.py` 与 `mac_specific.py` 说明它已扩展到昇腾 NPU 与 Apple MPS。
- `rng.py` + `rng_philox.py`：**自实现 Philox 随机数发生器**，目的是让同一 seed 在不同 GPU/平台产出一致图像——这是"可复现性"的硬工程，也是很多同类工具做不到的细节。

## 🌐 社区口碑与维护现状（关键，含硬数据）

| 信号 | 实测值 | 解读 |
|---|---|---|
| `master` 最后提交 | **2024-07-27**（"changelog"） | 主分支约 2 年无推进 |
| 最新 Release | **v1.10.1（2025-02-09）**，v1.10.0（2024-07-27） | v1.10.1 为补丁版，非功能版 |
| `dev` 最后提交 | 2026-03-02 | 仍有心跳，但内容全是依赖急救 |
| dev 近期提交主题 | `pip install 'setuptools<70'` 修复；CLIP 安装失败修复（#17201/#17284/#17287）；`stable_diffusion_repo` URL 更新；linux uv 修复 | **无一条是功能** |
| 开放 Issue | 2,503 | 长期积压 |
| 贡献者集中度 | AUTOMATIC1111 3,630 / w-e-w 314 / dfaker 168 / akx 155 / catboxanon 132 | 极度依赖单一作者 |
| 分支现状 | 存在大量未合并特性分支（`SD3-Lora-page-filter---detection-not-implemented`、`cu126-10-series-gpu`、`canvas-undo-hotkey` 等） | 有人在写，但合并通道停滞 |

**研判**：分支名 `SD3-Lora-page-filter---detection-not-implemented` 本身就说明 SD3 支持停在半成品；`cu126-10-series-gpu` 说明新显卡/CUDA 适配靠零散分支而非主线。社区共识（多处公开讨论一致）是**生态重心已迁移到 ComfyUI（新建工作流）与 Forge/reForge（A1111 兼容 + 持续维护）**。

⚠️ 注：本节仅使用可验证的仓库信号（commit/release/branch/contributor），未引用任何无法核实的评测数字。

## ⚔️ 竞品对比

| 项目 | 范式 | 相对 A1111 的优势 | 劣势 / 代价 |
|---|---|---|---|
| **ComfyUI** | 节点图工作流 | 活跃维护、显存效率高、工作流可导出复现、新模型支持快 | 学习曲线陡，简单出图更繁琐 |
| **Forge / reForge** | A1111 的 fork | 保留插件生态与 UI 习惯，同时持续维护、优化显存与新硬件 | 与 A1111 上游已分叉，部分插件需适配 |
| **InvokeAI** | 产品化 UI + 节点 | 工程规范、Canvas 编辑体验好、商业支持 | 插件生态远小于 A1111 |
| **SD.Next** | A1111 衍生 | 多后端（diffusers）、更新积极 | 社区规模较小 |
| **Fooocus** | 极简预设 | 几乎零配置出好图 | 可控性弱，不适合精调 |

**选型结论**：要插件生态与历史复现 → A1111（或直接上 Forge）；要生产管线与新模型 → ComfyUI；要开箱即用 → Fooocus。

## 🎯 核心研判

- **采用建议**：把 A1111 当作**兼容层与历史基座**使用，不要当作演进中的上游。新项目若看重 A1111 的插件资产，**首选 Forge / reForge** —— 既保留生态又有维护。
- **最大风险（三条，按严重度）**：
  1. **安装链脆弱**：`launch.py` 运行时 git clone 上游 + 未锁死的 pip 依赖，导致"昨天能装今天装不上"。dev 分支近两年全部提交都在打这个补丁，本身就是最强证据。
  2. **AGPL-3.0 传染性**：以网络服务形式提供时需开放源码。做商业 SaaS 前必须过法务，这一点极易被忽略。
  3. **插件安全无沙箱**：扩展是任意 Python 代码，`scripts/custom_code.py` 更是直接允许执行用户代码。装第三方扩展等同于授予完全本机权限。
- **借鉴价值（可直接迁移到自己的项目）**：① 零注册目录式插件系统 + 回调参数对象化 + 拓扑排序；② 猴补丁的工程化管理（集中、可撤销、按上游版本分叉）；③ UI 与 API 共用同一管线；④ 自实现 RNG 换取跨平台可复现性；⑤ 反面教材——别把上游仓库拉取放进运行时。
- **一句话**：A1111 用"目录即插件 + 猴补丁跟上游"两招定义了 SD 前端的第一个时代，如今主线已冻结、只靠 dev 分支做依赖急救；它的代码依然是插件架构与可复现性工程的一流教材，但生产选型应转向 ComfyUI 或 Forge。

## 📂 关键文件路径速查

| 路径 | 作用 |
|---|---|
| `launch.py` / `webui.py` | 启动入口；前者做依赖自举（含 clone 上游到 `repositories/`），后者做初始化 |
| `modules/processing.py` | **生成主流程核心**，`StableDiffusionProcessing` 及 txt2img/img2img |
| `modules/scripts.py` · `script_callbacks.py` | 插件调度与生命周期回调（`AlwaysVisible`、拓扑排序） |
| `modules/sd_hijack*.py`（14 个） | 猴补丁层：CLIP 长 prompt/权重、注意力优化、UNet dtype |
| `modules/sd_samplers_*.py` · `sd_schedulers.py` | 采样器与调度器抽象层 |
| `modules/extra_networks*.py` | Lora / Hypernetwork / Textual Inversion 接入 |
| `modules/lowvram.py` · `devices.py` · `npu_specific.py` · `mac_specific.py` | 显存降级与多后端设备抽象 |
| `modules/rng.py` · `rng_philox.py` | 跨平台可复现随机数 |
| `modules/api/api.py` · `api/models.py` | HTTP API（行业事实标准契约） |
| `modules/prompt_parser.py` · `sd_emphasis.py` | prompt 权重与语法解析 |
| `extensions-builtin/`（Lora, LDSR, SwinIR, ScuNET, hypertile, soft-inpainting, canvas-zoom-and-pan, mobile, extra-options-section, prompt-bracket-checker, postprocessing-for-training） | 官方内置扩展，最佳插件写法示例 |
| `scripts/xyz_grid.py` | 多维参数网格实验（强烈推荐研读） |
| `scripts/custom_code.py` | ⚠️ 允许执行任意用户代码，安全边界示例 |
| `requirements_versions.txt` · `requirements_npu.txt` | 版本锁定现状（安装问题的排查起点） |
| `CHANGELOG.md` | 版本演进史（停在 v1.10.x） |

## 🧪 研究方法与数据来源

- GitHub API 仓库元数据：stars 164,759 / forks 30,558 / open issues 2,503 / AGPL-3.0 / 默认分支 `master` / size 36,552KB / topics
- `git/trees` + `contents` API 真实抓取根目录、`modules/`（约 130 文件）、`extensions-builtin/`、`scripts/`、`modules/api/` 完整清单
- `modules/scripts.py` 源码实抓（导入表、`AlwaysVisible`、`topological_sort`、回调参数类）
- Commits API 对比 `master` 与 `dev` 双分支时间线；Releases API 取 v1.10.1 / v1.10.0 / v1.10.0-RC / v1.9.4；Branches API 取未合并特性分支名
- Contributors API 取贡献集中度
- 未使用任何无法核实的第三方评测数字；所有维护现状结论均可由上述 API 复现
