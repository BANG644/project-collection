# 🔬 index-tts/index-tts - 全方位深度调研

## 项目全景
- **仓库**：`index-tts/index-tts`
- **一句话定位**：An Industrial-Level Controllable and Efficient Zero-Shot Text-To-Speech System
- **基础指标**：Stars=21040 / Forks=2601 / 默认分支=`main`
- **Topics**：bigvgan, cross-lingual, indextts, text-to-speech, tts, voice-clone, zero-shot-tts
- **Homepage**：数据不可用

## 核心架构
### 目录结构判断
- 顶层目录分布（递归树抽样汇总）：indextts(207), examples(14), assets(8), tools(5), tests(4), checkpoints(2), .gitattributes(1), .github(1), .gitignore(1), .python-version(1)
- 关键文件候选：pyproject.toml, README.md, tests/padding_test.py, tests/regression_test.py

### 设计亮点研判
- 存在 Python 工程入口，通常意味着自动化流水线、服务端或研究脚本由 Python 主导。
- 仓库包含测试代码，说明作者至少为关键行为建立了回归验证。
- 仓库包含 .github 目录，通常意味着 CI、issue 模板或自动发布流程已被工程化。

## 源码深度解读
### README / 说明文档要点
<div align="center">
<img src='assets/index_icon.png' width="250"/>
</div>

<div align="center">
<a href="docs/README_zh.md" style="font-size: 24px">简体中文</a> | 
<a href="README.md" style="font-size: 24px">English</a>
</div>

## The repository history has been reset. Please delete your local copy and re-clone.
## （仓库历史已重置。请删除本地副本并重新克隆。）

## 👉🏻 IndexTTS2 👈🏻

<center><h3>IndexTTS2: A Breakthrough in Emotionally Expressive and Duration-Controlled Auto-Regressive Zero-Shot Text-to-Speech</h3></center>

[![IndexTTS2](assets/IndexTTS2_banner.png)](assets/IndexTTS2_banner.png)


<div align="center">
  <a href='https://arxiv.org/abs/2506.21619'>
    <img src='https://img.shields.io/badge/ArXiv-2506.21619-red?logo=arxiv'/>
  </a>
  <br/>
  <a href='https://github.com/index-tts/index-tts'>
    <img src='https://img.shields.io/badge/GitHub-Code-orange?logo=github'/>
  </a>
  <a href='https://index-tts.github.io/index-tts2.github.io/'>
    <img src='https://img.shields.io/badge/GitHub-Demo-orange?logo=github'/>
  </a>
  <br/>
  <a href='https://huggingface.co/spaces/IndexTeam/IndexTTS-2-Demo'>
    <img src='https://img.shields.io/badge/HuggingFace-Demo-blue?logo=huggingface'/>
  </a>
  <a href='https://huggingface.co/IndexTeam/IndexTTS-2'>
    <img src='https://img.shields.io/badge/HuggingFace-Model-blue?logo=huggingface' />
  </a>
  <br/>
  <a href='https://modelscope.cn/studios/IndexTeam/IndexTTS-2-Demo'>
    <img src='https://img.shields.io/badge/ModelScope-Demo-purple?logo=modelscope'/>
  </>
  <a href='https://modelscope.cn/models/IndexTeam/IndexTTS-2'>
    <img src='https://img.shields.io/badge/ModelScope-Model-purple?logo=modelscope'/>
  </a>
</div>


### Abstract

Existing autoregressive large-scale text-to-speech (TTS) models have advantages in speech naturalness, but their token-by-token generation mechanism makes it difficult to precisely control the duration of synthesized speech. This becomes a significant limitation in applications requiring strict audio-visual synchronization, such as video dubbing.

This paper introduces IndexTTS2, which proposes a novel, general, and autoregressive model-friendly method for speech duration control.

The method supports two generation modes: one explicitly specifies the number of generated tokens to precisely control speech duration; the other freely generates speech in an autoregressive manner without specifying the number of tokens, while faithfully reproducing the prosodic features of the input prompt.

Furthermore, 
...[truncated]

### 关键文件精读
### `pyproject.toml`
```
[project]
name = "indextts"
version = "2.0.0"
description = "IndexTTS2: A Breakthrough in Emotionally Expressive and Duration-Controlled Auto-Regressive Zero-Shot Text-to-Speech"
authors = [{ name = "Bilibili IndexTTS Team" }]
license = "LicenseRef-Bilibili-IndexTTS"
license-files = ["LICEN[CS]E*", "INDEX_MODEL_LICENSE*"]
readme = "README.md"
classifiers = [
  "Development Status :: 5 - Production/Stable",

  "Intended Audience :: Science/Research",
  "Intended Audience :: Developers",

  "Topic :: Scientific/Engineering",
  "Topic :: Scientific/Engineering :: Artificial Intelligence",

  "Natural Language :: English",
  "Natural Language :: Chinese (Simplified)",

  "Programming Language :: Python :: 3",

  "Operating System :: OS Independent",
]
requires-python = ">=3.10"
dependencies = [
  # IMPORTANT: Always run `uv lock` or `uv lock --upgrade` to resolve dependencies
  # and update the lockfile after editing anything below.
  # WARNING: Ensure that you don't have a local `uv.toml`
...[truncated]
```

### `README.md`
```
<div align="center">
<img src='assets/index_icon.png' width="250"/>
</div>

<div align="center">
<a href="docs/README_zh.md" style="font-size: 24px">简体中文</a> | 
<a href="README.md" style="font-size: 24px">English</a>
</div>

## The repository history has been reset. Please delete your local copy and re-clone.
## （仓库历史已重置。请删除本地副本并重新克隆。）

## 👉🏻 IndexTTS2 👈🏻

<center><h3>IndexTTS2: A Breakthrough in Emotionally Expressive and Duration-Controlled Auto-Regressive Zero-Shot Text-to-Speech</h3></center>

[![IndexTTS2](assets/IndexTTS2_banner.png)](assets/IndexTTS2_banner.png)


<div align="center">
  <a href='https://arxiv.org/abs/2506.21619'>
    <img src='https://img.shields.io/badge/ArXiv-2506.21619-red?logo=arxiv'/>
  </a>
  <br/>
  <a href='https://github.com/index-tts/index-tts'>
    <img src='https://img.shields.io/badge/GitHub-Code-orange?logo=github'/>
  </a>
  <a href='https://index-tts.github.io/index-tts2.github.io/'>
    <img src='https://img.shields.io/badge/GitHub-Demo-orange?l
...[truncated]
```

### `tests/padding_test.py`
```
import torch
import torchaudio
from indextts.infer import IndexTTS
from indextts.utils.feature_extractors import MelSpectrogramFeatures
from torch.nn import functional as F

if __name__ == "__main__":
    """
    Test the padding of text tokens in inference.
    ```
    python tests/padding_test.py checkpoints
    python tests/padding_test.py IndexTTS-1.5
    ```
    """
    import transformers
    transformers.set_seed(42)
    import sys
    sys.path.append("..")
    if len(sys.argv) > 1:
        model_dir = sys.argv[1]
    else:
        model_dir = "checkpoints"
    audio_prompt="tests/sample_prompt.wav"
    tts = IndexTTS(cfg_path=f"{model_dir}/config.yaml", model_dir=model_dir, use_fp16=False, use_cuda_kernel=False)
    text = "晕 XUAN4 是 一 种 not very good GAN3 觉"
    text_tokens = tts.tokenizer.encode(text)
    text_tokens = torch.tensor(text_tokens, dtype=torch.int32, device=tts.device).unsqueeze(0) # [1, L]

    audio, sr = torchaudio.load(audio_prompt)
    audio = torch.mean(aud
...[truncated]
```

### `tests/regression_test.py`
```
from indextts.infer import IndexTTS

if __name__ == "__main__":
    prompt_wav="tests/sample_prompt.wav"
    tts = IndexTTS(cfg_path="checkpoints/config.yaml", model_dir="checkpoints", use_fp16=True, use_cuda_kernel=False)
    # 单音频推理测试
    text="晕 XUAN4 是 一 种 GAN3 觉"
    tts.infer(audio_prompt=prompt_wav, text=text, output_path=f"outputs/{text[:20]}.wav", verbose=True)
    text='大家好，我现在正在bilibili 体验 ai 科技，说实话，来之前我绝对想不到！AI技术已经发展到这样匪夷所思的地步了！'
    tts.infer(audio_prompt=prompt_wav, text=text, output_path=f"outputs/{text[:20]}.wav", verbose=True)
    text="There is a vehicle arriving in dock number 7?"
    tts.infer(audio_prompt=prompt_wav, text=text, output_path=f"outputs/{text[:20]}.wav", verbose=True)
    text = "“我爱你！”的英语是“I love you!”"
    tts.infer(audio_prompt=prompt_wav, text=text, output_path=f"outputs/{text[:20]}.wav", verbose=True)
    text = "Joseph Gordon-Levitt is an American actor"
    tts.infer(audio_prompt=prompt_wav, text=text, output_path=f"outputs/{text[:20]}.wav", ver
...[truncated]
```

### 关键逻辑总结
- 从关键文件组合看，项目更像围绕单一目标组织的任务流水线/工具链，而不是超重平台。
- 入口文件决定外部交互界面（CLI / API / UI），配置文件决定运行时依赖，测试文件暴露作者真正关心的行为边界。
- 如果用户只读 README，通常只能知道“能做什么”；而从目录与入口文件能看出“怎么做、扩展点在哪、维护成本高不高”。

## 社区口碑
### GitHub Issues 抽样
- #696 [OPEN] index-tts uninstall! how to do it?（comments=[] labels=无）
- #693 [OPEN] feature: 建议为 IndexTTS2 增加独立的 `indextts2` CLI（comments=[{'id': 'IC_kwDON1G5Ss8AAAABFAHRrA', 'author': {'login': 'CouplingArtist'}, 'authorAssociation': 'NONE', 'body': '我已经基于上述方案完成了一个初步实现, 整理了对应的 PR 分支 #694 , 目前正在继续开发Todo中的相关内容\n\n希望维护者可以先看一下这个方向是否符合项目规划。如果这个 CLI 入口, 参数设计或功能边界有需要调整的地方, 欢迎直接回复交流, 我可以根据反馈继续修改 PR以及当前CLI的开发方向。', 'createdAt': '2026-06-05T10:39:22Z', 'includesCreatedEdit': False, 'isMinimized': False, 'minimizedReason': '', 'reactionGroups': [], 'url': 'https://github.com/index-tts/index-tts/issues/693#issuecomment-4630630828', 'viewerDidAuthor': False}] labels=无）
- #690 [OPEN] bug: 使用 WebUI 时, Hugging Face 辅助模型没有按项目代码预期缓存到 ./checkpoints/hf_cache, 而是被下载到了默认用户缓存目录 C:\Users\<user>\.cache\huggingface\hub（comments=[{'id': 'IC_kwDON1G5Ss8AAAABE_LeSg', 'author': {'login': 'CouplingArtist'}, 'authorAssociation': 'NONE', 'body': '已提交一个最小修复 PR: #691 \n\n该PR 采用的是上面提到的第一种方案：在 `webui.py` 导入 `gradio` 前设置 `HF_HUB_CACHE`。\n\n修复后, WebUI 启动路径会先将 Hugging Face 缓存目录设置为 `<model_dir>/hf_cache`, 然后再导入 `gradio`。这样 `huggingface_hub` 初始化时会使用项目模型目录下的缓存, 而不是用户默认缓存目录 `C:\\Users\\<user>\\.cache\\huggingface\\hub`。\n\n为了保持最小改动，PR暂未给每个 `from_pretrained` / `hf_hub_download` 调用显式传入 `cache_dir`\n', 'createdAt': '2026-06-05T08:34:12Z', 'includesCreatedEdit': False, 'isMinimized': False, 'minimizedReason': '', 'reactionGroups': [], 'url': 'https://github.com/index-tts/index-tts/issues/690#issuecomment-4629651018', 'viewerDidAuthor': False}] labels=无）
- #689 [OPEN] LFX budget exceeded again（comments=[{'id': 'IC_kwDON1G5Ss8AAAABEkCV5Q', 'author': {'login': 'nanaoto'}, 'authorAssociation': 'COLLABORATOR', 'body': 'You can actually run the project without these large files. You just need to bypass the Git LFS download by setting the GIT_LFS_SKIP_SMUDGE=1 environment variable.\n\nFor example, you can clone the repository like this:\nGIT_LFS_SKIP_SMUDGE=1 git clone https://github.com/index-tts/index-tts.git', 'createdAt': '2026-06-02T09:49:56Z', 'includesCreatedEdit': False, 'isMinimized': False, 'minimizedReason': '', 'reactionGroups': [], 'url': 'https://github.com/index-tts/index-tts/issues/689#issuecomment-4601189861', 'viewerDidAuthor': False}] labels=无）
- #688 [CLOSED] 实现vtt字幕的文本转语音py代码（comments=[] labels=无）
- #687 [OPEN] Can someone help me adapt the index tokenizer to the Russian language?（comments=[{'id': 'IC_kwDON1G5Ss8AAAABE9CnFw', 'author': {'login': 'yunpeili'}, 'authorAssociation': 'NONE', 'body': 'Russian is not supported for current indextts2 tokenizer. Although the tokenizer of indextts2.5 supports, no Russian data is used in training.', 'createdAt': '2026-06-05T01:43:54Z', 'includesCreatedEdit': False, 'isMinimized': False, 'minimizedReason': '', 'reactionGroups': [], 'url': 'https://github.com/index-tts/index-tts/issues/687#issuecomment-4627408663', 'viewerDidAuthor': False}] labels=无）

### Pull Requests 抽样
- PR #699 [OPEN] Constrain Python version for llvmlite compatibility
- PR #698 [OPEN] Fix WebUI Hugging Face cache path initialization
- PR #697 [CLOSED] feat(cli): add JSONL batch synthesis for `indextts2`
- PR #695 [CLOSED] feat(cli): add validated emotion vector support
- PR #694 [OPEN] Add a dedicated `indextts2` CLI for IndexTTS2

### Releases 抽样
- v1.5.0（published=2025-09-01T10:38:01Z latest=True）

### 真实反馈与维护信号研判
- 抽样 issue 中 open/closed 约为 7/1，可作为维护响应速度的弱信号。
- 近期 PR 抽样里可见已合并项 0 个，说明项目并非完全冻结。
- 存在 release 记录，说明作者具备版本化交付意识。
- 高频问题通常比 README 更能暴露真实落地难点：安装、兼容性、性能边界、文档歧义、平台限制。
- 若外部搜索数据不可用，本报告明确以 GitHub issue/PR/release 作为一手社区信号，不伪造站外口碑。

## 竞品对比
| 维度 | index-tts | 竞品/替代 |
|---|---|---|
| 定位 | 面向仓库作者设定的具体场景，通常更垂直 | Coqui TTS / Piper / Bark 往往更通用或生态更大 |
| 学习曲线 | 依赖其内部脚本/配置约定 | 通用方案学习成本更高，但生态更成熟 |
| 差异化 | 仓库通常以“快上手、场景专用、意见化实现”为卖点 | 通用方案强调可扩展、稳定性、跨场景能力 |
| 风险 | 作者驱动、文档深度可能不足、接口稳定性不确定 | 大项目更稳定，但改造成本更高 |

## 核心研判
### 项目优势
- 对目标问题有强意见化实现，落地路径通常比“从零搭建通用栈”更短。
- 如果核心文件少而清晰，二次阅读和定制成本较低。
- GitHub 原生 issue / release / PR 能直接帮助判断项目是否仍在演进。

### 项目风险
- 若 stars、forks、release 或 PR 活跃度偏低，意味着长期维护能力要谨慎评估。
- 如果关键逻辑过于集中在单文件脚本中，后续扩展会受到可维护性约束。
- 若缺少测试/CI/配置 schema，生产环境采用前应先做自测和边界验证。

### 适用场景
- 需要快速验证该仓库所解决的问题是否值得投入。
- 团队愿意接受一定的作者意见化设计，以换取更快交付。
- 适合作为参考实现、内部 PoC、垂直任务工具，而非默认直接替代成熟平台。

### 不适用场景
- 对 SLA、兼容矩阵、长期 LTS 有强要求的核心生产系统。
- 需要极高社区冗余、插件生态或企业级支持的场景。

## 关键文件路径速查
- `pyproject.toml`
- `README.md`
- `tests/padding_test.py`
- `tests/regression_test.py`

## 3 条关键发现
- 代码入口/骨架集中在：pyproject.toml, README.md, tests/padding_test.py, tests/regression_test.py
- Issue 抽样显示近期关注点包括：index-tts uninstall! how to do it?；feature: 建议为 IndexTTS2 增加独立的 `indextts2` CLI
- 版本交付可从最新 release 观察：v1.5.0

## 研究方法与数据来源
- GitHub Repo API / README / 默认分支递归文件树
- 关键源码文件抽样精读
- Issues / PRs / Releases 社区活动抽样
- 说明：若外部搜索数据不可用，则明确标注并不伪造口碑结论
