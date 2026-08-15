# Soup 深度调研

> 调研日期：2026-08-16 ｜ 星标：1,572 ⭐ ｜ 协议：Apache-2.0 ｜ 语言：Python
> 仓库：`MakazhanAlpamys/Soup` ｜ 默认分支：`main` ｜ 官网：trysoup.dev ｜ 最近活跃：2026-08-15
> 定位：一条 YAML、一条命令完成 LLM 微调/后训练；其 **Layer Streaming（层流式训练）** 让 8B 模型在 4GB 笔记本显卡上微调

## 一、项目定位（一句话）

**「把 LLM 微调的工程地狱变成一条 `soup.yaml` + `soup train`」的开源训练框架**——自动处理批大小、GPU 探测、量化；其实验性但惊艳的 **Layer Streaming** 把冻结基座模型冻结在 CPU RAM/NVMe，按 decoder layer 逐层流式拷入 VRAM，使 **Llama-3.1-8B + NF4 在 4GB 显卡上以 3.32GB 峰值微调**（峰值显存 ≈ 单层 + 适配器）。

## 二、项目亮点（差异化）

1. **零 SSH、零配置地狱**：`pip install "soup-cli[train]"` → `soup init --template chat` → `soup train`，量化/批大小/GPU 检测全自动。
2. **Layer Streaming（核心创新，BETA）**：基座不入 VRAM，按层流式喂给 GPU；实测 RTX 3050 Laptop 4GB 上 8B+NF4 **119.6 tok/s、3.32GB 峰值**，与常驻运行 bit-exact（有 Colab T4 可复现 notebook）。
3. **诚实的工程文化**：发布说明公开列出「撤回的读数」「噪声地板」「greedy 在 GPU 上非确定」等细节；`soup ship` 发布门禁用 `--noise-floor N` 拒绝把小于实测抖动的 delta 当「改进」。
4. **偏好损失也对流式开放**：DPO/ORPO/SimPO 复用「同一份流式基座 + 关掉适配器」当参考模型，仅 0.914× SFT 峰值，避免第二份权重翻倍显存。
5. **奖励合成（reward synth）**：从参考输出反推确定性 verifier 并产出可读 `.py` 奖励函数，且**拒绝**为无法区分好坏的参考输出生成奖励——校准报告是护城河。

## 三、核心架构

Soup 分两层：

- **Light CLI（无 torch 依赖）**：`soup init / data / mcp` 等，导入不触发训练栈（源码注释明确：No top-level torch/peft/transformers —— all lazy）。
- **Training stack（`training/stream_layers` + `soup_cli/utils/`）**：Layer Streaming 运行时。

Layer Streaming 的数据平面由四个角色组成（均见 `layer_stream_runtime.py`）：

- **`RamSource` / `DiskSource`（Tier 1 / Tier 2）**：基座权重的「源」。RAM 源把每层 safetensors 一次性 `copy_` 进预分配的 pinned CPU 内存；Disk 源用 safetensors 内存映射按需读盘，接口与 RAM 源一致（`get(idx, name)` + `nbytes`）。
- **`LayerBufferPool`（Tier 0，VRAM）**：N 个（默认 2）预分配的 per-layer VRAM 缓冲，循环内零分配，避免 allocator 碎片化。
- **`StreamPrefetcher`**：驱动预取，前向 0..L-1、反向 L-1..0，方向由调用顺序推断。
- **`StreamedDecoderLayer`**：用 `torch.func.functional_call` + `checkpoint` 包装的真实层，在 `wait(i)` 拿到本层权重、`prefetch(i±1)` 预取下层的窗口内训练。

## 四、应用场景与启发

**典型场景**：消费级显卡（4–8GB）上微调 7B/8B 模型、笔记本本地后训练、教育资源受限下的 LLM 定制、作为「显存不够但想训大点」的折中方案。

**架构启发（可复用）**：
- **「冻结大模型驻留慢存储 + 逐层流式进快存储」是显存墙的通用解法**：峰值显存从「整个模型」降到「单层 + 增量」，对任何「大模型推理/训练受限于显存」的场景（MoE 卸载、长上下文 KV、Agent 上下文压缩）都是同一思路。
- **双缓冲 + CUDA stream 预取 + 所有权 tripwire**：`LayerBufferPool` 用 `n_buffers=2` 循环缓冲、`load_async` 在独立 stream 上 `non_blocking` 拷贝、`wait()` 用 ownership 检查防止「缓冲被回收而 autograd 节点仍引用 → 静默错误梯度」，这套并发模式可直接迁移到任何流式权重加载。
- **诚实发布文化**：把「噪声地板 / 撤回读数」写进 changelog，是 ML 工具可信度的稀缺品质。

## 五、源码深度解读

### 1. 数据流的物理约束：`layer_stream_runtime.py`

模块顶部注释点明核心不变量——**每一层每个 step 被读两次，无法优化掉**（因为 `dL/dx = Wᵀ · dL/dy`，反向需要 W 到达更下层）：

```python
# Data flow per step (plan 5.2)::
#     FORWARD   layer i: wait(i) -> prefetch(i+1) -> checkpoint(body_i)
#     BACKWARD  layer i: wait(i) -> prefetch(i-1) -> recompute + backward
# Each layer is read TWICE per step and that cannot be optimised away:
# ``dL/dx = W^T . dL/dy`` ... This is physics, not an implementation detail.
```

### 2. RAM 源：基座只分配一次：`RamSource`

`RamSource`（line 292）把基座冻结在 CPU RAM，**预分配最终 dtype 的 buffer 后逐张量 `copy_` 填入**，避免 `load_file → .to(dtype) → .pin_memory()` 的三次瞬态拷贝把 5.55GB 基座顶破页锁定上限：

```python
class RamSource:
    """The base held in CPU RAM, allocated ONCE and filled by ``copy_``."""
    def __init__(self, shard_dir, n_layers, spec, *, pin=True):
        self.store: list = []
        self.nbytes = 0
        for idx in range(n_layers):
            held: Dict[str, Any] = {}
            with safe_open(layer_shard_path(shard_dir, idx), framework="pt") as handle:
                for name, (shape, dtype) in spec.items():
                    dst = torch.empty(tuple(shape), dtype=_torch_dtype(dtype),
                                      pin_memory=self.pinned)
                    src = handle.get_tensor(name)
                    dst.copy_(src)                 # 一次性拷入预分配缓冲
                    del src
                    held[name] = dst
                    self.nbytes += dst.numel() * dst.element_size()
            self.store.append(held)
```

`spec_from_shard()` 强调 dtype 必须**逐张量**读取：NF4 shard 是混合的（packed nibbles / absmax 是 `uint8`，layernorm 是 float），统一 dtype 会把打包字节误读成浮点——这也是为什么 `LayerBufferPool` 的 `layer_spec` 要带每张量 dtype。

### 3. VRAM 双缓冲池：`LayerBufferPool`

`LayerBufferPool`（line 487）是「循环内零分配」的关键，`n_buffers=2` 默认即可覆盖「当前层 + 下一层」：

```python
class LayerBufferPool:
    """N pre-allocated per-layer buffers. Never allocates inside the loop —
    that is what keeps the allocator from fragmenting (plan P7)."""
    def __init__(self, layer_spec, n_buffers=2, device="cuda"):
        self.n = int(n_buffers)
        self.buffers = [{name: torch.empty(tuple(shape), dtype=_torch_dtype(dtype),
                                            device=device)
                         for name, (shape, dtype) in layer_spec.items()}
                        for _ in range(self.n)]
        self.events = [torch.cuda.Event() for _ in range(self.n)] if self.is_cuda else []
        self.owner = [None] * self.n

    def slot_for(self, idx): return idx % self.n

    def load_async(self, idx, source, stream=None):
        slot = self.slot_for(idx)
        if self.is_cuda and stream is not None:
            stream.wait_stream(torch.cuda.current_stream())
            with torch.cuda.stream(stream):
                for name, dst in self.buffers[slot].items():
                    dst.copy_(source.get(idx, name), non_blocking=True)
                self.events[slot].record(stream)
        ...
        self.owner[slot] = idx

    def wait(self, idx):
        """Block compute stream until layer idx is resident.
        The ownership check is the plan-P1 tripwire: a buffer recycled while an
        autograd node still references it produces silently WRONG gradients."""
        slot = self.slot_for(idx)
        if self.owner[slot] != idx:
            raise RuntimeError(f"layer-stream scheduler bug: buffer slot {slot} holds "
                                f"layer {self.owner[slot]}, but layer {idx} was requested. ...")
        if self.is_cuda:
            torch.cuda.current_stream().wait_event(self.events[slot])
        return self.buffers[slot]
```

`wait()` 的 ownership 检查是「防静默错误梯度」的保险丝（plan P1）——缓冲被提前回收而 autograd 仍引用，会产出**错误梯度而非崩溃**，所以必须在此大声报错。

### 4. 预取方向机：`StreamPrefetcher`

`StreamPrefetcher`（line 559）前向向上、反向向下，**方向是显式状态而非每次重算**（`prime()` 起前向，`advance()` 在 `idx < prev` 时翻转为 -1）：

```python
class StreamPrefetcher:
    def prime(self):
        self.prev = None; self.direction = 1
        self.pool.load_async(0, self.source, self.stream)
    def advance(self, idx):
        if self.prev is not None and idx < self.prev:
            self.direction = -1
        self.prev = idx
        nxt = idx + self.direction
        if 0 <= nxt < self.n_layers and self.pool.owner[self.pool.slot_for(nxt)] != nxt:
            self.pool.load_async(nxt, self.source, self.stream)
```

### 5. 只认 Llama/Qwen 形模型：`decoder_owner()`

`decoder_owner()`（line 45）刻意**不**取 CausalLM wrapper，而是下钻到持有 `.layers` 的 `LlamaModel`/`Qwen2Model` 模块——因为 PEFT 的 `LoraModel.forward` 直接调 `self.model.forward`，绕过了 wrapper 上的 `__call__` 与所有 forward hook。不支持非 Llama/Qwen 形则直接抛错（明确限制范围）。

## 六、全网口碑

- **社区反响**：dev.to、gigazine 等开发者媒体对其「4GB 显卡训 8B」的演示给出正面评价，被认为是「 democratize fine-tuning」方向的有力尝试。
- **成熟度信号**：Layer Streaming 明确为 **BETA**，仅支持约 9 种架构、文本/LoRA 场景；Issue `#331` 记录 NF4 大层「静默错误梯度」问题（正是 `wait()` ownership tripwire 要防的），说明边界 case 仍在收敛。
- **客观评价**：理念先进、工程诚实、演示惊艳；但 BETA 限制 + 架构白名单意味着生产落地前需确认目标模型在支持列表内，并关注 NF4 大层的正确性修复进度。

## 七、竞品对比与核心研判

| 维度 | Soup（Layer Streaming） | Unsloth（库内已收录） | LLaMA-Factory | Axolotl |
|------|------------------------|----------------------|---------------|---------|
| 降低显存的核心手段 | 基座流式出 VRAM（逐层） | 手写 GPU kernel + monkey-patch | 量化/梯度检查点/DeepSpeed | 同左 + 配置驱动 |
| 4GB 显卡训 8B | ✅（演示 3.32GB 峰值） | ✅（更省显存+更快） | 需更激进配置 | 需更激进配置 |
| 易用性 | ⭐⭐⭐⭐⭐（一条命令） | ⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐ |
| 架构覆盖 | ⚠️ BETA 仅 ~9 种（Llama/Qwen 形） | 广 | 广 | 广 |
| 生产成熟度 | 早期/BETA | 较成熟 | 成熟 | 成熟 |

**核心研判**：
- **优势**：「逐层流式」在「显存墙」解法上独树一帜，配合诚实发布文化，是消费级显卡微调的高潜力路径；一条命令的体验领先。
- **风险**：BETA 限制（架构白名单、文本/LoRA 为主）、NF4 大层正确性待修、Python 3.10–3.12 硬约束；与 Unsloth「kernel 级省显存」路线不同，Soup 走「存储分层」路线，二者可叠加。
- **启发**：「慢存储驻留 + 快存储流式 + 双缓冲预取 + 所有权校验」这套模式，是任何「大模型受限于显存」场景（MoE 专家卸载、长上下文、Agent 上下文压缩）都可直接借鉴的骨架。

## 八、关键文件路径速查

| 关注点 | 路径（仓库根） |
|--------|---------------|
| Layer Streaming 运行时 | `training/stream_layers/layer_stream_runtime.py`（FORWARD/BACKWARD 注释 / `RamSource` L292 / `DiskSource` L364 / `LayerBufferPool` L487 / `StreamPrefetcher` L559） |
| 层封装 | 同上 `_build_streamed_layer_class()`（L597，`StreamedDecoderLayer` + `checkpoint`） |
| 模型图导航 | 同上 `decoder_owner()`（L45，只认 `.layers` 模块） |
| NF4 量化重建 | 同上 `rebuild_quant_state()`（L91，code table 常驻） |
| 轻量 CLI 入口 | `soup_cli/`（import 不触发 torch） |
| 配置/训练 | `soup.yaml` 示例、`docs/performance-and-quantization.md`（Layer Streaming 详解） |
| 发布门禁 | `soup ship`（`--noise-floor N`）、`benchmarks/` |
| 已知边界 | Issue `#331`（NF4 大层静默错误梯度）、BETA 仅 ~9 架构 |
