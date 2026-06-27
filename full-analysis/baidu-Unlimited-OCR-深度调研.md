# 🔬 baidu/Unlimited-OCR — 全方位深度调研

## 📌 一句话定位

百度推出的**无限长度 OCR 视觉语言模型**——基于 DeepSeek-OCR 改进的"一次推理、长程解析"方案，创新性地通过 R-SWA（旋转滑动窗口注意力）将 KV 缓存压缩为恒定大小，使单次推理可处理数十页文档而不溢出显存。MIT 开源，3B/0.5B 激活参数。

## ⭐ 项目亮点

- **不限制页数的"无限"OCR**：核心创新在于 R-SWA 机制将 KV 缓存从 O(N) 压缩到 O(1)，论文声称能处理"unlimited pages"——实测 105 页编辑类 PDF 可一次性解析，无需分页处理
- **OmniDocBench v1.5 SOTA**：比 DeepSeek-OCR 高出 6.22 个综合分（Overall 指标），在长程文档解析场景优势明显
- **双推理路径**：同时支持 Transformers（适合单图/小批量）和 SGLang（适合并发/大批量），且提供了预编译的 SGLang wheel
- **超低参数量**：仅 3B 总参数、0.5B 激活参数即可达到前沿效果，推理门槛远低于同类 VLM 方案
- **中文社区的快速响应**：百度团队（MurphyYin 等）在 Issue 中回复活跃，24 小时内对多个问题给出了官方回应

## 🏗️ 项目架构全景

### 目录结构

```
baidu/Unlimited-OCR/
├── README.md               # 完整的使用说明
├── infer.py                # 批量并发推理脚本（SGLang 后端）
├── LICENSE                 # MIT
├── CONTRIBUTING.md         # 贡献指南
├── Unlimited-OCR.pdf       # 论文 PDF
├── wheel/                  # 预编译的 SGLang wheel
│   └── sglang-*.whl
└── assets/                 # 图片资源
```

### 架构设计哲学

这个项目本身不是一个完整的工程框架，而是一个**研究级模型的工程化部署工具包**。设计上非常务实：

- **Transformers 路径**：主打零配置快速体验，一行 pip install 即可用
- **SGLang 路径**：主打高性能并发推理，通过 `infer.py` 脚本封装了完整的工作流（启动服务 → 提交任务 → 收集结果 → 关闭服务）
- **不搞微服务、不搞编排**：保持了推理脚本的极简主义，但对生产使用场景的支持（如 `--resume`、`--results_jsonl`）仍有欠缺

### 依赖图谱

- **核心依赖**：torch 2.10+、transformers 4.57+、Pillow、einops
- **可选加速**：SGLang（需预编译 wheel）、PyMuPDF（PDF 转图片）、sgl-kernel（CUDA 加速）
- **显存需求**：Transformers 路径约 6.3GB（bfloat16）、SGLang 路径略低

## 💡 应用场景与启发

### 典型使用场景

1. **大批量文档数字化**：合同、论文、报告等长篇文档的 OCR 提取，支持一次性处理整个 PDF（105 页测试下来约 71% 提取率）
2. **RAG 预处理管线**：Issue #32 有用户将 Unlimited-OCR 接入 Qdrant + FAISS 的融合 pipeline（68K chunks），做视觉检索增强生成
3. **扫描 PDF 的文本化**：以 300 DPI 渲染 PDF 页作为图像输入，配合 `ngram_window=1024` 抑制重复生成
4. **学术论文图表提取**：对包含图表、公式、多栏排版的学术 PDF 尤其适合（这是 OmniDocBench 评测的重点场景）

### 可借鉴的解决方案模式

- **恒定 KV 缓存（R-SWA）**：这个思路不仅对 OCR 有效，对任何需要处理超长序列的 VLM 场景（长视频理解、长文档分析）都有参考价值
- **双推理路径设计**：Transformers（易用） + SGLang（高性能）的并行走法，值得其他 AI 项目参考
- **自定义 Logit Processor**：SGLang 的 `DeepseekOCRNoRepeatNGramLogitProcessor` 用一个 ngram 窗口抑制重复生成，比 temperature 控制更精准

### 同类需求的可参考思路

如果要做类似的长文档理解模型，从 Unlimited-OCR 可以学到：
1. 在现有 SOTA 模型上做定向增强（不是说从零训练）
2. KV 缓存压缩是最值得投入的方向（单张 24GB 卡就能跑几十页）
3. 中文 + 英文先做好，多语言靠社区收集数据

## 🧠 核心源码解读

### `infer.py` — 并发推理调度

这个脚本是 SGLang 推理路径的核心，约 250 行 Python。设计模式：

```python
# 1. 服务生命周期管理（启动 → 健康检查 → 任务提交 → 关闭）
def start_server(args):
    cmd = [sys.executable, "-m", "sglang.launch_server",
           "--model", args.model_dir,
           "--enable-custom-logit-processor",
           ...]
    process = subprocess.Popen(cmd, ...)
    # 轮询 /health 端点，超时 300 秒
    while time.time() - start < SERVER_TIMEOUT:
        if server_ready(SERVER_URL):
            return process
        time.sleep(3)
    raise TimeoutError(...)

# 2. 并发请求（ThreadPoolExecutor + SSE 流式收集）
with ThreadPoolExecutor(max_workers=args.concurrency) as executor:
    futures = {
        executor.submit(infer_one, img_path, output_file, args, i): i
        for i, img_path in enumerate(sorted(image_paths))
    }
    for future in as_completed(futures):
        result = future.result()
        # 收集 token 数、解码时间、文本
```

**关键发现**：当前版本（2026-06-24）有一个已知的 tmpdir 泄漏问题（`pdf_to_images` 创建的临时目录在脚本退出后未被清理）。Issue #17 的 PR #21 已经修复了这个问题，但尚未合并。

### ngram 抑制重复机制

```python
# R-SWA + ngram 是高质量输出的关键
NO_REPEAT_NGRAM_SIZE = 35
NGRAM_WINDOW = 128  # 单图模式
# 多页模式需改为 1024（README 示例中已说明）
```

社区贡献者 kushdab 的实测验证：未启用 ngram 时，同一页输出 60KB 文本；启用 ngram（window=128）后压缩到 2.8KB——重复超过 20 倍的冗余文本被消除。

## 📐 架构决策与设计哲学

### 设计红线

| 决策 | 说明 | 来源 |
|------|------|------|
| 暂不支持多语言（仅中英） | 团队在收集多语言训练数据，未来版本会扩展 | Issue #3, #25 |
| 暂不提供量化版本 | 暂无计划，后续根据需求考虑 | Issue #9 |
| 暂不开放训练代码 | 团队在讨论 finetune 支持，有更新会同步 | Issue #25 |
| vLLM 支持开发中 | 目前仅 SGLang，vLLM 已在开发中 | Issue #7 |

### 版本演进

从 2026-06-22 开源到 2026-06-24 的 3 天内，模型收获了 11,000+ star，22 条 Issue。百度团队的响应速度优秀——核心贡献者 MurphyYin 在多个 Issue 中 24 小时内给出回应。

## 🌐 全网口碑画像

### 好评共识

- **"一次解析几十页"**：知乎文章指出传统 OCR 需要逐页切分 OCR，而 Unlimited-OCR 可以一次输入数十页。知乎评价："感觉以后做文档数字化的团队，可能会把 OCR 管线从传统方案转向 VLM 方案"
- **"推理能力很强，对小册子/知识库类场景很合适"**：HN 风格的讨论中，有用户测试了 105 页编辑类 PDF，71% 提取率
- **"比 DeepSeek-OCR 好不少"**：中文社区的对比测试普遍认为精度有明显提升

### 差评共识 & 踩坑高发区

- **Apple Silicon (MPS) 完全不支持**：Issue #18 报告了 MPS 上的 `masked_scatter_` bug，导致 Mac 用户空输出或乱码。社区贡献的 PR #34 修复了部分问题，但 Issue #18 的评论显示 M5 Max 上仍有乱码
- **SGLang wheel 兼容性差**：预编译 wheel 只包含 sm80～sm100 的 CUDA 架构，SM121（DGX Spark/GB10）不支持。用户需手动重新编译 sgl_kernel
- **多语言支持仅中英**：日文、韩文、阿拉伯文等暂不支持，国际用户反馈强烈（Issue #3 有 5+ 条讨论）
- **扫描 PDF 识别效果不佳**：Issue #16 报告扫描 PDF（非原生 PDF）识别精度不够高，"针对扫描 PDF 识别效果不佳问题"
- **中文社区有"扒代码"争议**：搜狐文章称"YY 的真实身份很可能是前 DeepSeek OCR 团队负责人魏浩然"，部分评论质疑百度是否有"挖人 + 复制"的操作

### 争议焦点

- **是否真的"unlimited"**：技术上 R-SWA 使 KV 缓存恒定，但实际使用受限于总 token 数（context length=32768），超长文档仍需分批次
- **从 DeepSeek-OCR 改进的正当性**：百度明确说明"基于 DeepSeek-OCR，主要改进是 R-SWA + MHA 替换 + 更多训练数据"，但部分社区声音认为应该在论文中更明确地归因

## ⚔️ 竞品对比

| 维度 | Unlimited-OCR | DeepSeek-OCR | PaddleOCR | Tesseract |
|------|--------------|-------------|-----------|-----------|
| **定位** | 长程文档 VLM OCR | 通用文档 VLM OCR | 传统端到端 OCR | 传统 OCR 引擎 |
| **长文档处理** | ✅ R-SWA 恒定缓存 | ❌ KV 随页数增长 | ❌ 逐页处理 | ❌ 逐页处理 |
| **OmniDocBench** | 90+ Overall（SOTA） | 约 84 Overall | 不适用 | 不适用 |
| **参数量** | 3B（激活 0.5B） | 约 3B | 轻量 | 极轻量 |
| **语言支持** | 中英为主 | 多语言 | 多语言（80+） | 100+ |
| **开源协议** | MIT | MIT | Apache 2.0 | Apache 2.0 |
| **推理后端** | SGLang + Transformers | SGLang + Transformers | 自研 | 无需后端 |
| **硬件需求** | 6GB+ VRAM | 6GB+ VRAM | 低 | 极低 |
| **社区** | ⭐ 11K, 2 周 | ⭐ 30K+, 长期 | ⭐ 40K+, 成熟 | ⭐ 65K+, 极成熟 |

### 选择建议

- 需要**长文档一次性解析** → **Unlimited-OCR**（唯一的选择）
- 需要**多语言 + 高精度通用 OCR** → DeepSeek-OCR（语言覆盖更广）
- 需要**轻量级 + 低延迟的在线识别** → PaddleOCR（百度自家产品，工程成熟）
- 需要**极轻量 + 离线运行** → Tesseract（无需 GPU）

## 🎯 核心研判

### 项目优势

1. **R-SWA 技术路线正确**：KV 缓存压缩是长文档 VLM 的关键瓶颈，百度在这个方向做出了实质性贡献
2. **MIT 开源诚意足**：百度没有搞"开源但不让商用"的把戏，直接 MIT 协议
3. **社区热度极高**：11K star/2 周的增长速度说明需求真实且强烈

### 项目风险

1. **MPS/非主流 GPU 支持差**：Apple Silicon 用户暂时被排除在外，CUDA 架构兼容范围有限
2. **多语言支持滞后**：国际用户（日韩、阿拉伯等）期待已久，但百度团队回应"正在收集数据"——何时推出不明朗
3. **工程化程度不足**：没有 Docker 镜像（社区贡献了但未官方化）、没有 vLLM 支持（开发中）、训练代码未开源
4. **来自 DeepSeek-OCR 的舆论压力**：部分中文社区对"百度挖 DeepSeek 团队"有负面看法

### 适用场景 & 不适用场景

**适用**：
- 大批量 PDF/文档数字化（合同、论文、报告）
- RAG/知识库的文档预处理管线
- 需要一次性解析长文档的 VLM 应用

**不适用**：
- Apple Silicon（MPS）用户的文档 OCR 需求
- 多语言文档（日、韩、阿拉伯等）
- 手机端/边缘端部署（3B 参数还是太大）
- 生产环境需要稳定 Docker 镜像 + vLLM 的场景

### 趋势判断

🟢 **快速上升期**。作为百度在长文档 VLM OCR 领域的首次开源，Unlimited-OCR 的技术方向正确、社区热度高、迭代速度快。预计 1-2 个月内会补齐 Docker 镜像、多语言支持、vLLM 后端等关键工程化短板。

## 📂 关键文件路径速查

| 文件 | 作用 |
|------|------|
| `README.md` | 完整的使用说明、推理示例、依赖安装 |
| `infer.py` | SGLang 并发推理脚本（含服务管理） |
| `wheel/sglang-*.whl` | 预编译的 SGLang wheel（指定架构） |
| `Unlimited-OCR.pdf` | 论文 PDF |
| 模型权重 | HuggingFace: `baidu/Unlimited-OCR` |
| HF Demo | https://huggingface.co/spaces/baidu/Unlimited-OCR |
| arXiv 论文 | https://arxiv.org/abs/2606.23050 |
