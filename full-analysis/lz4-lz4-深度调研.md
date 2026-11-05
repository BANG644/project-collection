# lz4/lz4 深度调研

> 调研日期：2026-11-06 | 星标：12,322⭐（Trending 当日飙升）| 语言：C（少量汇编）| 许可：2-clause BSD（仓库 LICENSE 标为 BSD 2-Clause，GitHub API 记为 NOASSERTION）| 默认分支：dev | 最近提交：2026-11-05 | 作者：Yann Collet（Cyan4973）| 版本：v1.11.1

## 1. 项目定位（一句话）

LZ4 是**无损压缩算法 LZ4 的官方参考实现**——以「极速压缩 / 极速解压」为核心卖点：解压端几乎只做 `memcpy` 级的块拷贝，单核可达数 GB/s，被 Linux 内核、ZFS、MongoDB、Apache 生态（Hadoop/HBase/Kafka/Spark）、RocksDB、MariaDB、SquashFS、Android 等广泛采用，是业界「快」这一档压缩的事实标准。

## 2. 项目亮点（3-5 条差异化，开篇呈现）

- **解压速度封顶**：LZ4 不做熵编码（无 Huffman/ANS），压缩块由「字面量 + 匹配（offset+length）」组成，解压就是「拷贝字面量 + 带重叠处理的 `memcpy` 匹配」，单核轻松数 GB/s，是同类里**解码最快**的之一。
- **压缩/解压速度可调**：`LZ4_compress_fast(acceleration)` 用 `acceleration` 系数跳过更多候选匹配，在「更快但略低压缩率」和「更慢但更高压缩率」之间连续权衡；还有 `LZ4_compress_HC`（最优解析器）作为高压缩档。
- **双格式共存**：既有 **Block 格式**（裸压缩块，无帧头，供嵌入式/协议用），也有 **Frame 格式**（带魔数、头、块、校验和的互操作容器，`lz4frame.c`），后者是文件/网络传输的通用封装。
- **极小代码足迹 + 工业级落地**：整个库纯 C、可无缝嵌入内核态与裸机；被 Linux 内核（3.11+ 用于内核镜像压缩、pstore 等）、ZFS（默认压缩算法）直接吸收。
- **同作者衍生生态**：作者 Yann Collet 后来做出 Zstandard（zstd），二者共享大量工程思想；LZ4 仍是 zstd 内部「最快档」与字典训练加速的基石。

## 3. 核心架构

仓库分两层代码 + 一套 CLI：

```
lib/                 # 库本体（核心）
  lz4.c / lz4.h      # 块格式：压缩/解压主逻辑 + 公共 API
  lz4hc.c / lz4hc.h  # 高压缩档（HC，Binary Tree 最优解析）
  lz4frame.c / .h    # 帧格式：LZ4F_* 流式/一次性 API
  lz4file.c          # 文件级读写封装
  xxhash.c / .h      # 自带 xxHash（帧校验用）
programs/            # 命令行工具
  lz4cli.c           # CLI 入口/参数解析
  lz4io.c            # 文件 IO、多文件、管道
  bench.c            # 基准测试
```

关键架构决策：
- **匹配查找靠哈希表而非搜索**：压缩时把 4 字节序列哈希进一张表（偏移 16-bit `byU16` 或 32-bit `byU32`），O(1) 找候选匹配，这是速度的来源。
- **流式多块**：`LZ4_createStream` + `LZ4_compress_fast_continue` 把长输入切成多块，每块独立解压；帧层 `LZ4F_compressUpdate/flush/compressEnd` 还支持多线程 worker 流水线。
- **失败封闭（fail-closed）的 API 语义**：`LZ4_decompress_safe` 系列带目的缓冲容量检查，越界即返回负错误码，绝不写出缓冲——这是它能进内核与安全敏感场景的前提。

## 4. 应用场景与启发

- **「解压速度优先」场景的默认选择**：实时/流式传输、内存缓存序列化、网络协议帧、嵌入式固件、数据库块压缩（WiredTiger、RocksDB、InnoDB）、日志/列式存储——凡是不想为解压付出 CPU 的场景，LZ4 几乎是首选项。
- **给同类需求带来的思路**：
  - 「速度与比率的 Pareto 前沿」不是非此即彼：LZ4 用 `acceleration` 把压缩速度做成**连续旋钮**，zstd 再把「长距匹配 + 字典 + 多档」做到同一曲线更优处。做压缩/序列化中间件时，应暴露类似的「速度—比率」可调档位。
  - **解压端极简 = 可审计 + 可嵌入式**：不做熵编码换来了「解压逻辑可被内核/fuzz 严格验证」。设计高性能数据格式时，「让解码器简单」本身就是一种安全与可移植性投资。
  - 块格式与帧格式**分离**的范式值得借鉴：底层块保证算法纯净，上层帧负责互操作（魔数、版本、校验、流式）——协议/存储格式设计可复用该分层。

## 5. 源码深度解读（2-3 个最核心模块，每段 5-15 行）

**① 压缩主循环——哈希找匹配（`lib/lz4.c`）**

`LZ4_compress_generic` 是压缩心脏，核心是「哈希 → 取候选 → 比对 4 字节 → 命中则记匹配」的循环：

```c
do {
    U32 const h = forwardH;
    U32 const current = (U32)(forwardIp - base);
    U32 matchIndex = LZ4_getIndexOnHash(h, cctx->hashTable, tableType);
    ip = forwardIp; forwardIp += step;
    step = (searchMatchNb++ >> LZ4_skipTrigger);   // acceleration 控制跳步
    if (unlikely(forwardIp > mflimitPlusOne)) goto _last_literals;
    match = base + matchIndex;
    forwardH = LZ4_hashPosition(forwardIp, tableType);
    LZ4_putIndexOnHash(current, h, cctx->hashTable, tableType);
    if ((matchIndex+LZ4_DISTANCE_MAX < current)) continue;   // 太远，跳过
    if (LZ4_read32(match) == LZ4_read32(ip)) {               // 4 字节命中
        /* 进入字面量/匹配编码 */
    }
} while (...);
```

`acceleration << LZ4_skipTrigger` 把 `step` 放大，即「每 `acceleration` 次才认真比对一次」——这就是 `LZ4_compress_fast` 调速度的机制。

**② 帧格式流式 API（`lib/lz4frame.h` / `lz4frame.c`）**

```c
LZ4FLIB_API size_t LZ4F_compressFrame(void* dstBuffer, size_t dstCapacity,
                                      const void* srcBuffer, size_t srcSize,
                                      const LZ4F_preferences_t* prefsPtr);
// 流式：createCompressionContext → compressBegin → compressUpdate（可多次）
//      → flush / compressEnd（worker 线程可并行，输出滞后于输入）
LZ4F_compressionContext_t cctx;
LZ4F_createCompressionContext(&cctx, LZ4F_VERSION);
```

`LZ4F_compressFrame` 一次性产出带魔数头+块+校验的完整帧；`compressUpdate` 支持「输出滞后于输入、最多 ~2×nbWorkers 个 job 在飞」，是多线程压缩的基础。`LZ4F_compressFrameBound()` 保证目标容量足够即必成功——典型的「容量预算即安全」设计。

**③ 公共 API 形态（`lib/lz4.h`）**

```c
LZ4LIB_API int LZ4_compress_default(const char* src, char* dst, int srcSize, int dstCapacity);
LZ4LIB_API int LZ4_compress_fast (const char* src, char* dst, int srcSize, int dstCapacity, int acceleration);
LZ4LIB_API int LZ4_decompress_safe(const char* src, char* dst, int compressedSize, int dstCapacity);
LZ4LIB_API int LZ4_compressBound(int inputSize);   // 最坏输出上界，用于容量预算
```

`compressBound` + `decompress_safe` 这对组合是「调用方永远能安全分配缓冲」的契约，也是它被内核/数据库信任的根因。

## 6. 全网口碑

- 星标高且来源硬核：12k+⭐（Trending 当日飙升），但更重要的是**它不在「星标榜」而在「依赖树」里**——Linux 内核、ZFS、MongoDB WiredTiger、RocksDB、MariaDB/MySQL、Apache Hadoop/HBase/Kafka/Spark、SquashFS、Android、Qt、大量游戏引擎都直接链接它。
- 工程口碑：以「极致解压速度 + 极小代码 + 稳定 ABI」著称；社区长期维护（2011 至今，v1.11.1），issue/PR 活跃。
- 局限讨论（社区共识）：压缩率明显低于 zstd/gzip/brotli，纯 LZ4 不适合「省带宽/省磁盘」优先的场景；也有人指出其块格式缺标准帧头时互操作性差（因此官方力推 Frame 格式）。

## 7. 竞品对比 + 核心研判

| 项目 | 解压速度 | 压缩率 | 定位差异 |
|------|---------|--------|---------|
| **LZ4** | 🥇 最快档 | 较低 | 极致解压速度、极小足迹，内核/嵌入式首选 |
| zstd（同作者） | 很快 | 高 | 现代默认：长距匹配+字典+多档，比率/速度曲线更优 |
| Snappy（Google） | 很快 | 较低 | 类似定位，比率略逊，无标准帧格式 |
| LZO | 很快 | 中 | 更老，商业许可约束 |
| zlib/gzip | 慢 | 高 | 比率优先，CPU 贵 |
| brotli | 慢 | 高 | Web 文本压缩，比率优先 |

**核心研判**：
- LZ4 的护城河是「**解压速度的绝对天花板 + 代码可进内核的极简**」，在实时/内存/嵌入式/协议场景无可替代。
- 对**新项目**：若既要速度又要更好比率，zstd 通常是更优的现代默认（且同作者、思想同源）；但 LZ4 在「解码端不能有负担」的约束下仍是首选。
- 启发：一个算法能在 15 年里持续被内核吸收，靠的不是功能多，而是「把一件事做到对手无法在同等约束下追上」。做基础设施工具时，这种「极致单点 + 严格安全语义」的策略值得复用。

## 8. 关键文件路径速查

- `lib/lz4.c` / `lib/lz4.h` — 块格式压缩/解压主体 + 公共 API（起点）
- `lib/lz4hc.c` — 高压缩档（Binary Tree 最优解析）
- `lib/lz4frame.c` / `lib/lz4frame.h` — 帧格式流式/一次性 API
- `lib/lz4file.c` — 文件级封装
- `programs/lz4cli.c` / `programs/lz4io.c` — 命令行工具与文件 IO
- `xxhash.c` — 自带 xxHash（帧校验）
- `lib/LICENSE` — 2-clause BSD
