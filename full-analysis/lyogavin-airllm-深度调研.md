# AirLLM 深度调研

> 仓库：`lyogavin/airllm` ｜ 语言：Jupyter Notebook / Python ｜ 许可：Apache-2.0 ｜ Stars：≈36.3k（2026-10-11 抓取，当日仍在 Trending）
> 定位一句话：**用「逐层流式卸载」让 70B+ 大模型在单张 4GB 显卡上推理（无需量化/蒸馏/剪枝），并支持小显存训练的开源库。**

---

## 1. 项目亮点（差异化）

1. **极小显存跑超大模型**：70B 满精度 Llama3 仅 ~4GB、DeepSeek-V3 671B ~12GB、Kimi K3（2.8T）~3.72GB、Qwen3-235B ~3GB——瓶颈在「单层大小」而非模型总大小。
2. **保精度路线**：默认**不量化、不蒸馏、不剪枝**；可选 block-wise 4/8bit 压缩仅作用于磁盘加载体积（提速 ~3x，精度几乎无损）。
3. **通用流式底座**：`transformers` 驱动 forward，新架构即插即用——只有非标准模块布局才需专门子类（`ARCH_OVERRIDES` 仅覆盖 ChatGLM/QWen/Baichuan/InternLM/KimiK3/Qwen3.5/Qwen4Exp 等少数）。
4. **MoE 逐专家流式**：只加载 token 实际路由到的专家，Kimi K3 单层专家展开 ~55GB，单 token 实际仅 ~1GB 落卡。
5. **小显存训练**：冻结基座逐层流式 + 仅 adapter 常驻，Qwen3.8-Flash-Next 125B 训练 <6GB、Qwen3.8-27B <2GB（seq 512）。

---

## 2. 核心架构

核心思想：**模型以 `meta` 设备（零显存）实例化，transformers 拥有完整 forward/generate 逻辑；AirLLM 仅给每个大模块挂 forward pre/post hook，在模块运行前把权重从磁盘流式搬入 GPU、运行后立刻释放回 meta，并用单 worker 线程预取下一层**。

- 磁盘侧：首次推理把 checkpoint 按层切开成 shard（`layer_shards_saving_path` 可指定；`delete_original` 可删原档省一半盘）。
- 运行侧：`max_pinned_layer_bytes = 2GB` 上限控制 pinned 内存；`ThreadPoolExecutor(max_workers=1)` 做层间预取重叠。
- 训练侧：`install_hooks=False`，由训练循环自己管理 load/evict（hook 调 `module.to('meta')` 会打断 backward）。

---

## 3. 应用场景与启发（重点）

- **消费级/笔记本跑大模型**：RTX 3060 Ti（6GB）训 125B、RTX 3090（24GB）跑 27B VL，把「显存墙」从硬件门槛降为「磁盘速度」门槛。
- **边缘与穷玩场景**：4GB 卡跑 70B 做本地私有演示、教学、论文复现，无需 A100/H100 集群。
- **给同类需求的解决思路**：
  - 「**meta 实例化 + hook 流式**」是把任意 HF 模型塞进小显存的通用范式，比手写逐层逻辑可维护得多；
  - 「**通用子类兜底 + 特例覆盖**」（`AirLLMBaseModel` 默认 + `ARCH_OVERRIDES` 例外）让新模型发布当天即可用；
  - MoE 的「**逐专家卸载**」思路可迁移到任何稀疏激活大模型，是显存优化的关键一招。

---

## 4. 源码深度解读

**`air_llm/airllm/auto_model.py`** ——  dispatcher 与通用兜底：

```python
ARCH_OVERRIDES = {
    "ChatGLMForConditionalGeneration": "AirLLMChatGLM",
    "KimiK3ForConditionalGeneration": "AirLLMKimiK3",
    "Qwen4ExpForConditionalGeneration": "AirLLMQwen4Exp",
    # ...仅非标准布局才需专门子类
}
# get_module_class: 读 config.architectures[0]，命中则用特例，否则统一回退
cls_name = ARCH_OVERRIDES.get(arch) or "AirLLMBaseModel"
```

**`air_llm/airllm/airllm_base.py`** —— 流式 hook 核心（`AirLLMBaseModel` 类文档与 `_install_streaming_hooks`/`_pre_hook`/`_post_hook`）：

```python
def _install_streaming_hooks(self):
    for idx in self._streamed_indices:
        module = self.layers[idx]
        module.register_forward_pre_hook(self._pre_hook)   # 运行前搬入 GPU
        module.register_forward_hook(self._post_hook)      # 运行后释放回 meta

def _pre_hook(self, module, args):
    state_dict = self._load_streamed_layer(module._airllm_idx)   # 或取预取结果
    module._airllm_moved = self.move_layer_to_device(state_dict)
    if self.prefetching:                                        # 单线程预取下一层
        self._prefetch_future = self._executor.submit(self._load_streamed_layer, nxt)

def _post_hook(self, module, args, output):
    module.to('meta'); clean_memory()                           # 释放回 meta 设备
```

MoE 逐专家流式（`_setup_expert_streaming`）：给每个 expert 模块单独挂 hook，forward 时只 `load_layer_subset` 该 token 路由到的专家张量——Kimi K3 一层 55GB 展开量，单 token 实际 ~1GB 落卡。

---

## 5. 全网口碑

- GitHub ≈36.3k stars，作者 Gavin Li，有 Discord / Patreon / 个人博客（medium + gavinliblog）。
- 长期迭代（2023-11 初始版 → 2026-09 训练支持），更新日志密集，社区围绕「4GB 跑 70B」「MacOS 跑大模型」形成大量教程与 Colab。
- 局限性也被反复讨论：速度受磁盘 I/O 制约（远慢于同卡量化方案）、对新模型强依赖特定 `transformers` 构建（如 Qwen4Exp 需 in-tree `qwen4_exp`、Kimi K3 需 flash-attn + CUDA12 + transformers 4.56.x）。

---

## 6. 竞品对比 + 核心研判

| 方案 | 路线 | 适用 |
|---|---|---|
| **AirLLM** | meta+hook 逐层流式，默认不量化 | 单卡极小显存推理/训练、demo、研究 |
| llama.cpp (GGUF) | C++ + 量化权重 | 本地高性价比推理、跨平台 |
| bitsandbytes / 4bit | 权重量化 | 训练/推理显存压缩 |
| accelerate `device_map` | 朴素分层到多卡 | 多卡但不省单卡峰值 |
| vLLM / TGI | 高吞吐服务化 | 生产级并发服务 |

**核心研判**：AirLLM 是「显存极致压榨」里工程巧思最强、实用性最高的开源方案之一——它的价值不在速度，而在「让穷设备也能跑起来」与「保精度的流式范式」。代价是推理慢（磁盘瓶颈）、对 transformers 版本敏感、MoE/Flash 类需特殊构建。适合个人研究、教学演示、低成本私有部署；不适合生产高并发服务（那种场景应上 vLLM）。对「显存墙」研究者和边缘 AI 爱好者是必看仓库。

---

## 7. 关键文件路径速查

- `air_llm/airllm/auto_model.py` —— `AutoModel` dispatcher + `ARCH_OVERRIDES`
- `air_llm/airllm/airllm_base.py` —— `AirLLMBaseModel`：流式 hook、MoE 逐专家卸载、训练支持
- `air_llm/airllm/airllm_qwen4_exp.py` / `airllm_kimi_k3.py` —— 特例子类
- `air_llm/airllm/utils.py` —— `load_layer` / `load_layer_subset` / `layer_tensor_names`（safetensors 分片读取）
- `air_llm/airllm/lora_linear.py` / `airllm_lora.py` —— 小显存 LoRA 训练
- `air_llm/examples/*.ipynb` —— 各模型推理/训练示例
