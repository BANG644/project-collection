# FlashML-org/FreeToken 深度调研

> 一句话定位：edge-native 的 MoE 推理服务引擎——把 290B+ 前沿开放权重 MoE 模型跑在你已有的游戏 PC 上，以交互级速度服务 coding/tool-calling agent。
> 
> **元数据**：⭐ 15,280 ｜ 语言 Python（+Triton/CUDA/ggml 内核）｜ 许可 Apache-2.0 ｜ 默认分支 main ｜ 末提交 2026-10-30 ｜ 论文 arXiv:2608.16157 ｜ 调研日期 2026-11-02

## 一、项目亮点（差异化）

1. **带宽自适应 CPU–GPU 协同（$q^\star$ 策略）**：把异构边缘资源（GPU/CPU/主机内存/互联）视作统一弹性推理平面，按带宽动态决定专家在哪端算。
2. **全层双缓冲 prefill 流式 + 全局 LRU 专家缓存 + FTW 快速权重格式**：面向 MoE 稀疏性的专属优化，而非通用 LLM 引擎的改装。
3. **语义锚点缓存**：对循环状态与 KV 缓存做语义锚点 checkpoint，使 agentic 上下文编辑（工具调用/thinking 块）免于冗余重算。
4. **弹性显存**：运行时在专家缓存与 KV 内存间动态再分配 VRAM，无需重启/重载权重；原生支持 RTX 30/40/50 系消费卡。

## 二、核心架构

```
python/freetoken/
├── engine/        # 前向计算核心（forward / sampling）
├── scheduler/     # 重叠调度：页表、ShadowRadix 缓存分层、prefill/decode 管理
├── kernel/        # Triton(dsv4/qsa) · CUDA(ggml) · gluon(nvfp4) · csrc
├── moe/ + models/ # DeepSeek-V4/V4.1 · Qwen3.x-MoE · GLM-5.2 · Gemma4 … 配置
├── distributed/ · daemon/ · server/ · shell/ · message/ · tokenizer/
```

对外暴露 Anthropic/OpenAI 兼容 API，可无缝接入 Codex / Claude Code / OpenCode / OpenClaw / DeepSeek Harness 等 coding agent；量化支持 MXFP4/NVFP4/FP8/BF16。

## 三、应用场景与启发

- **可复用范式**：「把消费级 GPU 的空闲 CPU/主机内存当作 MoE 专家的溢出层」的 $q^\star$ 协同思路，是边端大模型服务的新方向，对「本地 agent _runtime」场景价值高。
- **工程启发**：① FTW 权重格式把权重量化/反量化与计算解耦；② 语义锚点缓存让 agent 多轮编辑上下文时可「增量复用」而非整段重算——这正是 long-context agent 的痛点解法。
- **对用户的价值**：若要在本地给自用 coding agent 配一个「能跑 200B+ MoE」的推理后端，FreeToken 是当前少数明确面向此场景的引擎（而非通用服务器引擎）。

## 四、源码深度解读

**调度器（`python/freetoken/scheduler/scheduler.py`）**——重叠调度 + 统一页表 + ShadowRadix 缓存分层：

```python
class Scheduler(SchedulerIOMixin):
    def __init__(self, config: SchedulerConfig):
        self.engine = Engine(config)
        self.stream = torch.cuda.Stream(device=self.device)   # 元数据与计算重叠
        # ONE cache manager for every model (ShadowRadix layering)
        self.cache_manager = CacheManager(
            self.engine.num_pages, config.page_size, self.engine.page_table,
            config.cache_type, linear_state_pool=self.engine.linear_state_pool,
            swa_pool=self.engine.kv_cache,
            radix_lookahead=self.spec is not None and self.spec.radix_lookahead,
        )
        self.prefill_manager = PrefillManager(self.cache_manager, self.table_manager,
                                              self.decode_manager, ...)
        # 中止墓碑：保证 abort 与更早 UserMsg 乱序到达时请求不会被复活
        self._abort_tombstones: dict[int, None] = {}
```

「一个 cache manager 服务所有模型、模型专属 tier 以插件挂载」的设计，避免了每模型一套缓存管理的膨胀，是 MoE 多模型共存的清爽抽象。

## 五、全网口碑

- 15k⭐、Apache-2.0、有正式论文（作者含 Song Han / Matei Zaharia / Kurt Keutzer / Ion Stoica 等系统/ML 顶配阵容），可信度显著高于普通「本地 LLM 加速」项目。
- 社区期待高但项目很新（2026 年中起步），公开 benchmark 数字需自行复现验证；桌面 GUI + CLI 双发行，已登 flashml.ai。

## 六、竞品对比 + 核心研判

| 维度 | FreeToken | vLLM | SGLang | llama.cpp | Ollama |
|---|---|---|---|---|---|
| 边端 MoE 专注 | ✅ 核心 | 通用 | 通用 | 通用 | 通用 |
| CPU–GPU 协同 | ✅ $q^\star$ | ❌ | ❌ | 部分 | ❌ |
| 消费卡优化 | ✅ RTX30/40/50 | 中 | 中 | ✅ | 中 |
| 语义锚点缓存 | ✅ | ❌ | ❌ | ❌ | ❌ |

**核心研判**：FreeToken 凭顶尖作者阵容与清晰的「edge-native MoE」定位，在本地大模型服务赛道有真实差异化。风险在于项目极新、声明面很广（调度/内核/量化/分布式一并自研），benchmark 需独立验证；且与 vLLM/SGLang 的成熟生态相比工程完成度尚在早期。结论：**高潜力、待验证，值得把玩但不宜作为生产唯一后端**。

## 七、关键文件路径速查

- 调度核心：`python/freetoken/scheduler/scheduler.py`（+ cache.py / prefill.py / decode.py / table.py）
- 内核：`python/freetoken/kernel/triton/qsa/`（q-star 策略）、`kernel/ggml`（CUDA）
- 模型接入：`python/freetoken/models/`（deepseek_v4 / qwen3_moe / glm5_next …）
- 服务/CLI：`python/freetoken/server/`、`python/freetoken/shell/`
- 论文：https://arxiv.org/abs/2608.16157 ｜ 官网：https://www.flashml.ai
