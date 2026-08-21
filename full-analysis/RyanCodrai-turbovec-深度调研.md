# RyanCodrai/turbovec 深度调研

> 调研日期：2026-08-22 ｜ 调研方式：gh API 抓取 README + 仓库树 + 源码路径核验
> 星标：16,172 ⭐ ｜ 语言：Rust（核心）+ Python（binding）｜ 协议：MIT ｜ 默认分支：main ｜ PyPI/crates.io 已发布
> 论文基础：TurboQuant（arXiv:2504.19874, ICLR 2026）

## 一、项目定位

turbovec 是一个**基于 Google Research TurboQuant 算法的 Rust 向量索引（vector index）**，带 Python 绑定。核心卖点：**无需训练阶段、在线增量摄入、手写 SIMD 搜索内核、增量持久化、本地纯离线**。

一句话基准（README 原话）：*1000 万文档的 float32 语料占 31GB RAM，turbovec 用 4GB 装下，且搜得比 FAISS 快*。

## 二、项目亮点（差异化）

1. **在线摄入，零训练**：加向量即索引——无 train 步骤、无参数调优、语料增长无需重建。对比 FAISS `IndexPQFastScan` 必须先验训练。
2. **手写 SIMD 搜索内核**：ARM 上 NEON SDOT/SMMLA、x86 上 AVX-512 VNNI + `vpermb`，AVX2/scalar 回退；**各配置下全面击败 FAISS IndexPQFastScan，4-bit 平均 3.4×、2-bit 平均 +23%**（双架构）。
3. **增量持久化 `sync(path)`**：只持久化自上次 sync 以来的变更，每次调用一次 fsync、任意字节崩溃安全；删/追加毫秒级，与索引大小无关。
4. **搜索时过滤**：`search()` 传入 id allowlist / slot bitmask，内核在 32-vector block 粒度短路——选择性过滤避免绝大多数 SIMD 开销，不做 over-fetch、不损召回。
5. **纯本地、可气隙**：无托管服务、数据不出机器/VPC；可配任意开源 embedding 模型，组成完全 air-gapped 的 RAG 栈。
6. **框架 drop-in 替换**：LangChain / LlamaIndex / Haystack / Agno 的 in-tree 向量/文档存储直接换 import 即可接入，公开 API 与持久化语义一致。

## 三、核心架构

Rust workspace 结构：

- `turbovec/`（核心 crate）
  - `src/encode.rs` — 归一化 + 旋转 + 校准 + Lloyd-Max 量化（单向量编码主流程）
  - `src/rotation.rs` — 随机正交矩阵（使旋转后坐标分布可预测）
  - `src/codebook.rs` — Lloyd-Max codebook（从数学一次性算出最优分桶边界/质心）
  - `src/pack.rs` — 位打包（2-bit→每坐标 2 bits，1536 维 FP32 6144B→2-bit 384B，16× 压缩）
  - `src/search.rs` — SIMD 评分内核（NEON/AVX-512/AVX2/scalar，nibble-split LUT）
  - `src/io.rs` / `io_v7.rs` — 整文件 `write/load` 与增量 `sync`（v7 格式）
  - `src/id_map.rs` — `IdMapIndex`（稳定外部 uint64 id，O(1) 按 id 删除）
  - `src/convert.rs` / `error.rs` / `warning.rs` / `lib.rs`
- `turbovec-python/`（maturin 构建的 Py binding：`build.rs`/`src/lib.rs`/`par_copy.rs`）
- `benchmarks/`（真实 embedding、FAISS 对照、`create_diagrams.py` 出图）
- `examples/`（kernel roofline、encode hash、各类 SIMD probe）

**TurboQuant 编码六步**（How it works）：
1. 归一化：剥离范数存为单 float，向量变单位方向；
2. 随机旋转：乘同一随机正交矩阵，旋转后每坐标独立服从 Beta 分布（高维收敛 N(0,1/d)），与输入数据无关；
3. 逐坐标校准 TQ+：每坐标拟合 shift/scale 两标量，把经验分位数映射到 codebook 最外质心（用 ~1024 行样本 `calibrate()` 一次，之后复用，无重训）；
4. Lloyd-Max 标量量化：已知分布故可一次性算出最优分桶（2-bit=4 桶，4-bit=16 桶）；
5. 位打包：坐标变小整数，紧打包进字节；
6. 长度重归一化评分：编码时算 `||v|| / ⟨u, x̂⟩` 标量，搜索内核在堆插入前乘回，把内积估计从无偏偏置修正为无偏、零额外存储/零额外查询成本（源自 RaBitQ 思路）。

**搜索**：查询旋转一次进同域，直接对 codebook 值打分；SIMD 内核用 nibble-split LUT 最大吞吐。Lloyd-Max codebook 失真距信息论下界（Shannon）仅 2.7×。

## 四、应用场景与启发

- **隐私/内存/延迟敏感的 RAG**：本地纯离线 + 4GB 装千万文档，适合合规/边缘/气隙场景。
- **持续增长语料的向量库**：无需停服重建（FAISS 必须 train），适合日志/文档流。
- **多租户过滤检索**：`allowlist` 在 SIMD 内核短路，SQL/BM25/时间窗候选集内做稠密 rerank 零额外开销。
- **给同类需求的解决思路**：
  - 「数据无关量化（data-oblivious quantization）」是绕开"训练阶段"的关键：用随机旋转把任意输入变成已知分布，再用数学算最优码本；
  - 增量 `sync` 的"一次 fsync + 原子 rename + 只写 diff"模式，是任何本地索引/数据库应借鉴的崩溃安全持久化范式；
  - SIMD 内核按 `is_x86_feature_detected!` 运行时选路 + 编译基线 x86-64-v2，兼顾"老 CPU 能跑、新 CPU 跑满"，比盲开 AVX-512 更稳。

## 五、源码深度解读

### 1. 编码主流程 `turbovec/src/encode.rs`
归一化→旋转→（校准）→Lloyd-Max 量化→打包，是单向量编码主路径：

```rust
// 简化骨架
pub fn encode(&mut self, v: &[f32]) -> Vec<u8> {
    let norm = v.norm();                       // 1. 剥离范数
    let u = rotate(v, &self.rot);              // 2. 随机旋转（distribution 已知）
    let calibrated = self.calibrate.map(u);    // 3. TQ+ shift/scale（若已 calibrate）
    let codes = lloyd_max_quantize(calibrated, self.codebook); // 4. 量化
    pack(codes)                                // 5. 位打包
    // 6. 存 ||v|| / <u, x_hat> 供搜索时去偏
}
```

### 2. 搜索内核 `turbovec/src/search.rs`
SIMD 评分，nibble-split LUT；过滤在 32-vector block 粒度短路：

```rust
// 简化骨架（x86 AVX-512 VNNI 路径）
unsafe fn score_block_avx512(lut: &[i16], codes: &[u8], allow: &Bitmask) -> Heap {
    if allow.block_empty() { return Heap::skip(); }  // block 内无允许 slot → 短路
    let acc = vnni_dot(lut, codes);                  // AVX-512 VNNI 点积
    heap_insert(acc * len_renorm);                   // 6. 长度重归一化去偏
}
```

### 3. 增量持久化 `turbovec/src/io_v7.rs`
`write`/`load` 整文件快照；`sync` 只写 diff、一次 fsync + 原子 rename：

```rust
// 简化骨架
pub fn sync(&mut self, path: &Path) -> io::Result<()> {
    let diff = self.dirty.take();           // 自上次 sync 的变更
    atomic_write(path, diff)?;              // fsync + rename，任意字节崩溃安全
}
```

## 六、社区口碑

- **arXiv 背书**：实现 ICLR 2026 论文 TurboQuant（Google Research），学术可信度强。
- 工程严谨度极高：大量 `tests/`（adversarial_durability 系列、`calibration_bounds`、`codebook_determinism`、`concurrent_search`、`kernel_correctness`、`input_validation` 等）；CI 用 `encode_hash` 在矩阵所有 OS 上校验跨平台字节一致性。
- 基准透明：所有数字来自 `benchmarks/suite/`（真实 embedding + FAISS 对照 + 固定环境），JSON 原始结果全公开，并**明确说明更强 baseline（FAISS IndexPQ LUT256）**而非论文里自定义 u8-LUT——诚实度高于多数"吊打 FAISS"项目。
- PyPI（`turbovec`）+ crates.io（`turbovec`）双分发，框架集成文档齐全（langchain/llama_index/haystack/agno）。
- 数据不可用：GitHub Discussions/Issue 具体口碑数字本次未抓取，未编造。

## 七、竞品对比 + 核心研判

| 维度 | turbovec (TurboQuant) | FAISS IndexPQFastScan | hnswlib / HNSW | LanceDB |
|------|----------------------|----------------------|----------------|---------|
| 训练阶段 | ❌ 无 | ✅ 需 train | ❌（但需建图） | 部分 |
| 内存压缩 | 16×(2-bit) | 类似 PQ | 高（图） | 中 |
| 搜索速度 | **3.4×@4bit vs FAISS** | 基准 | 快但占内存 | 中 |
| 增量摄入 | ✅ O(1) add/remove | repack 慢 | 需重建部分 | 中 |
| 本地/气隙 | ✅ 纯本地 | ✅ | ✅ | ✅ |

**核心研判**：
- **优势**：数据无关量化消除训练门槛、SIMD 内核全面超 FAISS、增量 sync 崩溃安全、过滤内核短路——四项叠加对"持续增长 + 隐私 + 低延迟"RAG 极具吸引力；基准诚实。
- **风险**：① 仍偏早期（框架 drop-in 刚起步，生态不及 FAISS/LanceDB）；② 依赖 TurboQuant 论文假设，极低维（GloVe d=200）2-bit 仍略逊 FAISS，需 TQ+ 校准补偿；③ 高维稠密检索 recall 在 k 增大才到 1.0，浅 k 有微小 recall 折损。
- **趋势**：本地/隐私 RAG 兴起，"训练免、增量、可气隙"的量化索引会吃下 FAISS 不愿覆盖的长尾；与 LangChain 等 drop-in 集成是正确增长策略。
- **启发**：做向量检索时，「用随机旋转把输入变成已知分布 → 用数学算最优码本 → 长度重归一化去偏」这条"数据无关量化"链路，是解决"训练阶段是部署摩擦源"的优雅答案。

## 八、关键文件路径速查

- `turbovec/src/encode.rs` — 编码主流程（归一化→旋转→校准→量化→打包）
- `turbovec/src/rotation.rs` — 随机正交矩阵
- `turbovec/src/codebook.rs` — Lloyd-Max codebook（数学一次性算最优分桶）
- `turbovec/src/pack.rs` — 位打包（2/4-bit）
- `turbovec/src/search.rs` — SIMD 评分内核（NEON/AVX-512 VNNI/AVX2/scalar，nibble LUT + 过滤短路）
- `turbovec/src/io.rs` / `io_v7.rs` — 整文件 `write/load` 与增量 `sync`（v7，崩溃安全）
- `turbovec/src/id_map.rs` — `IdMapIndex`（稳定 uint64 外部 id，O(1) remove）
- `turbovec/src/convert.rs` / `error.rs` / `warning.rs` / `lib.rs`
- `turbovec-python/src/lib.rs` / `par_copy.rs` / `build.rs` — maturin Python 绑定
- `benchmarks/suite/` — 所有公开基准脚本（speed/recall/compression）；`benchmarks/results/*.json` 原始数据；`benchmarks/create_diagrams.py` 出图
- `examples/` — `insert_bench.rs`（优化内循环筛选）、`encode_hash.rs`（跨平台字节一致性）、`kernel_roofline*.rs` / `probe_*.rs`（SIMD 探针）
- `tests/` — `adversarial_durability*.rs`、`calibration_bounds.rs`、`codebook_determinism.rs`、`concurrent_search.rs`、`kernel_correctness.rs`、`input_validation*.rs`
- `docs/api.md` / `docs/integrations/{langchain,llama_index,haystack,agno}.md` — API 与框架集成文档
- `Cargo.toml` / `.cargo/config.toml`（x86-64-v2 基线 + 运行时 feature 选路）
