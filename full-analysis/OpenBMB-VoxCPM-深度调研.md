# OpenBMB/VoxCPM 深度调研

> 调研日期：2026-10-24 ｜ Stars：40,157 ｜ 语言：Python（PyTorch）｜ 许可：Apache-2.0（可商用）｜ 创建：2025-09-16 ｜ 默认分支：main ｜ arXiv：2606.06928

## 一、项目定位（一句话）

OpenBMB 开源的 **「无分词器（tokenizer-free）」TTS**——端到端扩散自回归直接生成连续语音表征，VoxCPM2 为 2B 参数、200 万+ 小时多语料、30 语言、48kHz 工作室音质，支持语音设计 / 可控克隆，是 ElevenLabs 级能力的开源平替。

## 二、项目亮点（差异化，开篇呈现）

1. **无分词器端到端扩散自回归**：绕过离散 token 化，用 flow-matching（UnifiedCFM）直接建模连续语音，自然度与表现力显著高于传统「先 tokenizer 后自回归」方案。
2. **2B + 200 万小时 + 30 语言 + 48kHz**：`AudioVAE V2` 非对称编解码 + 内置超分，接收 16kHz 参考直接输出 48kHz 工作室音质，无需外部升采样器。
3. **语音设计 + 可控克隆**：纯自然语言描述（性别/年龄/情绪/语速）即可生成全新声音；短参考片段克隆 + 可选风格引导（情绪/节奏/表达）。
4. **真·开源可商用 + 实时流式 serving**：Apache-2.0 免费商用；RTF 在 RTX 4090 上低至 ~0.3，经 Nano-vLLM / vLLM-Omni（PagedAttention）加速到 ~0.13，并提供 OpenAI 兼容 API。

## 三、核心架构（克制代码量）

VoxCPM2 的声学链路是 **Local Encoder → Local DiT V2（扩散自回归）→ AudioVAE V2（解码）**，文本侧 backbone 为 **MiniCPM-4**：

- `VoxCPMLocEnc`（局部编码器）：把参考音频 / 文本编码为局部条件。
- `VoxCPMLocDiTV2` + `UnifiedCFM`（局部扩散 Transformer + 统一流匹配）：逐段生成连续语音表征，是「无分词器」的关键。
- `AudioVAEV2`：非对称 encode/decode，16kHz→48kHz 并内置超分。
- `MiniCPM4Model`（minicpm4/model.py）：文本 / 语义编码器，复用 OpenBMB 自家的 MiniCPM-4 主干。

## 四、应用场景与启发（重点）

- **本地 / 自托管高质量语音合成**：对 agent 语音交互、视频配音、无障碍朗读是现成积木——无需把文本/音频发给闭源云服务即可拿到 ElevenLabs 级输出。
- **对「错题归因 / 论文伴读」等用户 agent 系统的借鉴**：若未来要让 agent 出有声讲解、做视频配音，VoxCPM2 的「OpenAI 兼容 + vLLM-Omni 加速」是最顺滑的本地接入路径。
- **无分词器范式**：对自研语音 / 音频生成模型是明确方向信号——离散 token 瓶颈正在被「连续表征 + 流匹配」取代，值得在相关科研中跟踪。

## 五、源码深度解读（2 个核心模块）

**1. `src/voxcpm/core.py`（推理编排入口，实证）**

```python
def resolve_model_path(path_or_id, cache_dir=None, local_files_only=False) -> str:
    if os.path.isdir(path_or_id):
        return path_or_id
    return snapshot_download(repo_id=path_or_id, cache_dir=cache_dir,
                             local_files_only=local_files_only)  # HF 自动拉权重

class VoxCPM:
    def __init__(self, voxcpm_model_path, ...):
        config = json.load(open(os.path.join(voxcpm_model_path, "config.json")))
        arch = config.get("architecture", "voxcpm").lower()
        if arch == "voxcpm2":
            self.tts_model = VoxCPM2Model.from_local(...)   # 按 arch 字段自动路由
        elif arch == "voxcpm":
            self.tts_model = VoxCPMModel.from_local(...)
        # LoRA 权重加载 + ZipEnhancer 降噪 + 设备自动选择（CUDA→MPS→CPU）
```

`architecture` 字段驱动 V1.5 / V2 自动路由，LoRA 微调权重与 `torch.compile` 优化均内置，接入成本极低。

**2. `src/voxcpm/model/voxcpm2.py`（VoxCPM2 模型装配，实证）**

```python
from ..modules.audiovae import AudioVAEV2, AudioVAEConfigV2
from ..modules.layers import ScalarQuantizationLayer
from ..modules.layers.lora import apply_lora_to_named_linear_modules
from ..modules.locdit import CfmConfig, UnifiedCFM, VoxCPMLocDiTV2
from ..modules.locenc import VoxCPMLocEnc
from ..modules.minicpm4 import MiniCPM4Config, MiniCPMModel
```

顶层 import 即完整暴露了「LocEnc → LocDiT V2 + UnifiedCFM → AudioVAE V2 + MiniCPM-4 主干」的装配关系，是理解整条链路的最短路径。

## 六、全网口碑

OpenBMB（清华系，MiniCPM 同门）出品；HuggingFace Trending #1、GitHub Trending 上榜；技术报告 arXiv 2606.06928；Trendshift 高排名；权重 + 代码全 Apache-2.0 开放，社区（飞书 / Discord）活跃。属当前开源 TTS 赛道第一梯队。

## 七、竞品对比 + 核心研判

| 维度 | VoxCPM2 | ElevenLabs（闭源） | CosyVoice / Fish-Speech / ChatTTS | Meta Voicebox / Bark |
|---|---|---|---|---|
| 分词器 | **无（连续表征）** | 闭源未知 | 有（离散 token） | 有 |
| 多语言 | 30 语 | 强 | 中文强、多语弱 | 有限 |
| 音质 | 48kHz | 工作室级 | 16–24kHz | 中等 |
| 商用许可 | **Apache-2.0 免费** | 付费 | 多为非商用 | 研究 |

**核心研判**：在「多语 + 克隆 + 语音设计 + 真开源商用」四个维度同时拉满，是自建语音能力的首选开源底座；代价是 2B 模型需 GPU、自托管 serving 需一定工程量。LoRA 微调（SFT/LoRA 配置已随仓提供）与 vLLM-Omni 加速让其落地门槛可控。与同 Trending 的 `debpalash/VoiceStudio`（本地 ElevenLabs 替代前端）互补：VoxCPM2 是引擎，VoiceStudio 是工作台。

## 八、关键文件路径速查

- 推理入口：`src/voxcpm/core.py` · `src/voxcpm/cli.py`
- 模型装配：`src/voxcpm/model/voxcpm2.py` · `src/voxcpm/model/voxcpm.py`
- 核心模块：`src/voxcpm/modules/{locdit,locenc,audiovae,minicpm4,layers}/`
- 训练 / 微调：`src/voxcpm/training/` · `scripts/train_voxcpm_finetune.py` · `lora_ft_webui.py`
- 配置：`conf/voxcpm_v2/`（finetune_all / finetune_lora）
- 部署：`docker/`（Dockerfile + compose + nginx）· `app.py`（Web Demo）· 官方 vLLM-Omni serving
- 文档：https://voxcpm.readthedocs.io ｜ 技术报告：arXiv 2606.06928
