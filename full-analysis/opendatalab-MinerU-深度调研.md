# opendatalab/MinerU - 全方位深度调研

> 调研日期：2026-06-27 | Stars: ~70,000 | 语言：Python | 许可证：Apache 2.0 基础上的 MinerU 开源许可
> GitHub: https://github.com/opendatalab/MinerU

## 一句话定位

**MinerU 是 OpenDataLab（上海人工智能实验室）开源的高精度 PDF 文档解析引擎**——不只是 "PDF 转 Markdown"，而是提供 3 种推理后端、覆盖 109 种语言、支持 10+ 国产 GPU 平台、公式→LaTeX + 表格→HTML 的完整文档智能提取方案。

---

## 项目架构全景

### 目录结构

```
MinerU/
├── demo/                      ← 示例入口
│   ├── demo.py               ← 一键运行 demo
│   ├── pdfs/                 ← 示例 PDF
│   └── office_docs/          ← DOCX/PPTX/XLSX 示例
├── docker/                    ← Docker 部署
│   ├── china/                ← 国产算力 Dockerfile（昇腾/寒武纪/燧原等 10+）
│   ├── global/               ← NVIDIA GPU Dockerfile
│   └── compose.yaml          ← 一键服务编排
├── docs/                      ← 文档站源码（MkDocs）
│   └── assets/images/        ← 大量使用截图（Cherry Studio/Coze/Dify 集成）
├── .github/workflows/         ← CI/CD
│   ├── cli.yml               ← CLI 构建测试
│   ├── python-package.yml    ← Python 包测试
│   └── mkdocs.yml            ← 文档站部署
├── LICENSE.md                 ← Apache 2.0 基础上的特殊许可
└── README.md / README_zh-CN.md
```

> 注：核心源码（magic-pdf 引擎）不在本仓库根目录直接可见，而是以 Python 包形式通过 `pip install` 安装。仓库本身是入口 + 文档 + 部署配置。

### 技术栈

- **核心语言**：Python 3.10-3.12
- **OCR 引擎**：PP-OCRv6（v3.4 升级，PaddleOCR 生态）
- **VLM 模型**：MinerU2.5-Pro 系列（1.2B 参数规模）
- **布局分析**：自研 Layout 模型
- **公式识别**：UniMERNet
- **表格识别**：StructEqTable
- **部署**：Docker + Gradio WebUI + REST API + MCP Server
- **推理加速**：vLLM / LMdeploy / mlx（Apple Silicon）

### 三后端架构（核心创新）

MinerU 提供 3 种完全不同的推理后端，适配不同精度和硬件需求：

| 后端 | 原理 | OmniDocBench v1.6 精度 | GPU 显存 | 特点 |
|------|------|------------------------|----------|------|
| **pipeline** | 布局检测→OCR→公式→表格→排序流水线 | 86.47 | 4GB（纯CPU可运行） | 兼容性最好，零幻觉 |
| **hybrid-engine** | VLM + OCR 双引擎融合 | 95.39 (high) / 95.26 (medium) | 8GB | 精度最高，原生文本提取 |
| **vlm-engine** | 纯 VLM 端到端 | 95.30 | 8GB | 生态兼容好（vLLM/LMdeploy/mlx） |

**设计哲学**：不是 "一个模型打天下"，而是让用户根据硬件条件和精度需求选择后端。pipeline 后端在 4GB 显存甚至纯 CPU 上都能跑，hybrid/vlm 后端追求极致精度。

### 解析强度档位（Hybrid 后端独有）

| 档位 | 精度 | 速度提升 | 适用场景 |
|------|------|---------|----------|
| **medium**（默认） | 95.26（仅降 0.13） | +35%~220% | 日常使用 |
| **high** | 95.39 | 基准 | 极致精度 + 图片分析 |

### 解析 Pipeline 七阶段

```
PDF 输入
  → 1. 布局分析（单栏/多栏/复杂排版）
  → 2. 元素去除（页眉/页脚/脚注/页码自动去除）
  → 3. 公式识别与转换 → LaTeX
  → 4. 表格识别与转换 → HTML
  → 5. OCR 引擎（扫描件/手写体/109 种语言）
  → 6. 阅读顺序排序（人类阅读顺序）
  → 7. 多模态输出（Markdown / JSON / 中间格式）
```

---

## 核心源码解读

### 源码结构说明

MinerU 的核心解析逻辑通过 `magic-pdf` 命令行工具暴露，主要入口在 `demo/demo.py`：

```python
# 最简使用示例（demo.py）
from magic_pdf.pipe.UNIPipe import UNIPipe
from magic_pdf.rw.DiskReaderWriter import DiskReaderWriter

# 读取 PDF → 解析 → 输出 Markdown
pipe = UNIPipe(pdf_bytes, jso_useful_key={}, image_writer=DiskReaderWriter(local_image_dir))
pipe.pipe_classify()        # 分类 PDF 类型
pipe.pipe_parse()           # 执行全流水线
content_list = pipe.pipe_mk_uni_format(image_dir, drop_mode="none")
content_md = pipe.pipe_mk_markdown(image_dir, drop_mode="none")
```

### 国产算力支持（10+ 平台）

这是 MinerU 区别于海外竞品的最大差异化优势——支持中国国产 GPU 全系：

| 平台 | Dockerfile 路径 | 厂商 |
|------|----------------|------|
| 昇腾 NPU | `china/npu.Dockerfile` | 华为 |
| 寒武纪 MLU | `china/mlu.Dockerfile` | 寒武纪 |
| 燧原 GCU | `china/gcu.Dockerfile` | 燧原科技 |
| 沐曦 MACA | `china/maca.Dockerfile` | 沐曦 |
| 摩尔线程 MUSA | `china/musa.Dockerfile` | 摩尔线程 |
| 昆仑芯 XPU | `china/kxpu.Dockerfile` | 百度 |
| 海光 DCU | `china/dcu.Dockerfile` | 海光 |
| 太初元碁 PPU | `china/ppu.Dockerfile` | 太初元碁 |
| 天数智芯 | `china/corex.Dockerfile` | 天数智芯 |

### DOCX/PPTX/XLSX 原生解析（v3.1.0 新增）

关键架构决策：MinerU 不把 Office 文档先转 PDF 再解析，而是**原生解析 DOCX/PPTX/XLSX**：

- DOCX → 直接读取 XML 结构，提取文本、表格、图片
- PPTX → 按幻灯片逐页提取
- XLSX → 表格数据直接提取

这个决策避免了 "PDF 转换中间损耗"——Office→PDF→Markdown 会比 Office→Markdown 多丢失一轮信息。

### 集成方式全矩阵

| 场景 | 集成方式 | 说明 |
|------|---------|------|
| AI 编程工具 | MCP Server | Cursor / Claude Desktop / Windsurf 直接调用 |
| RAG 框架 | LangChain / LlamaIndex / RAGFlow / Dify / FastGPT | 作为文档加载器 |
| 开发集成 | Python / Go / TypeScript SDK + CLI + REST API | 程序化调用 |
| 零代码 | mineru.net 在线版 / Gradio WebUI / 桌面客户端 | 非技术人员使用 |
| 容器化 | Docker Compose 一键部署 | 生产环境 |

---

## 全网口碑画像

### 好评共识

1. **"照进 RAG 黑暗中的一道光"** — CSDN 用户实测后如此评价，指 MinerU 解决了 RAG 场景下 PDF 解析质量差的核心痛点
2. **公式转 LaTeX 精度极高** — 知乎用户 "参同艾修司" 实测：2025 年发表的 25 页论文几秒解析完成，公式→LaTeX "比较实用"
3. **扫描版 PDF 也能处理** — 192 页老扫描版 PDF，3090 单卡 5 分钟完成，整体效果 "挺好"
4. **Docker 一键安装极简** — `docker run` 一行命令即可使用，显存占用仅 4GB（3090）
5. **OmniDocBench SOTA 分数** — Hybrid 后端 95.39 分，是目前开源方案中的最高水平

### 差评共识与踩坑

1. **安装有一定复杂度** — 虽然 Docker 简化了使用，但原生 Python 安装涉及 PaddlePaddle/PyTorch 等重依赖
2. **部分老旧扫描版有识别错误** — 知乎用户测试 2000 年前的扫描版 PDF 时发现 "有部分内容识别错误"
3. **许可协议变更历史** — v3.1.0 从 AGPLv3 切换到 Apache 2.0 基础上的特殊许可，部分用户对许可条款仍有疑虑
4. **加密 PDF 支持待验证** — 知乎评测中明确标记为 "待测试项"
5. **模型下载** — 首次使用需要下载较大的模型文件（数 GB），国内网络可能较慢

### 争议焦点

- **"最强"标签**：70K Stars 的体量让 MinerU 被视为 "最强开源 PDF 解析"，但有声音指出 OmniDocBench 评测只覆盖特定类型文档，实际效果因文档类型而异
- **国产 GPU 支持的实质**：10+ Dockerfile 虽然覆盖全面，但每个平台的推理性能差异大，文档对非 NVIDIA 平台的精度数据披露不足

---

## 竞品对比

| 维度 | MinerU | Marker (VikParuchuri) | PyMuPDF4LLM | Unstructured.io |
|------|--------|----------------------|-------------|-----------------|
| **公式支持** | ★★★★★ LaTeX 完整 | ★★★ 基础 | ★ 不支持 | ★★ 基础 |
| **表格支持** | ★★★★★ HTML 输出 | ★★★★ 结构化 | ★★ 文本 | ★★★ 结构化 |
| **多语言** | ★★★★★ 109 种 | ★★★ 主流 | ★★★★ 多语言 | ★★★★ 多语言 |
| **国产 GPU** | ★★★★★ 10+ 平台 | ★ 不支持 | ★ 不支持 | ★ 不支持 |
| **OmniDocBench** | ★★★★★ 95.39 | ★★★★ 参考值 | 数据不可用 | 数据不可用 |
| **安装难度** | ★★★ Docker 还行 | ★★★★ 简单 | ★★★★★ pip install | ★★★★★ pip install |
| **Office 文档** | ★★★★★ DOCX/PPTX/XLSX | ★ 不支持 | ★★ DOCX | ★★★ DOCX/PPTX |
| **速度** | ★★★★ 中等 | ★★★ 较慢 | ★★★★★ 极快 | ★★★★ 快 |
| **许可证** | Apache 2.0 基础上 | GPLv3 | AGPL | Apache 2.0 |

### 选择建议

- **选 MinerU**：你需要高精度公式/表格提取，或部署在国产 GPU 平台
- **选 Marker**：你需要纯 GPL 兼容的开源方案，对公式精度要求不高
- **选 PyMuPDF4LLM**：你的 PDF 是纯文本为主，需要极速处理
- **选 Unstructured**：你已经在用它的完整 RAG pipeline

---

## 核心研判

### 项目优势（不可替代的价值）

1. **国产 GPU 全系覆盖是真正的护城河**——没有任何海外竞品做到 10+ 国产算力平台，这在信创场景下是硬需求
2. **Hybrid 后端精度 SOTA**——95.39 的 OmniDocBench 分数说明后端融合策略的有效性
3. **Office 原生解析**——DOCX/PPTX/XLSX 不转 PDF 直接解析是实用的架构决策
4. **集成矩阵完整**——从 MCP Server 到 RAGFlow/Dify，从 Python SDK 到 WebUI，覆盖所有使用场景

### 项目风险

1. **核心模型是黑箱**——MinerU2.5-Pro 虽然是开源的，但训练数据和训练过程透明度不足
2. **OpenDataLab 作为单一维护者**——项目重度依赖上海 AI Lab 的持续投入，商业化方向不明确
3. **快速迭代可能牺牲稳定性**——从 v1.2.2（知乎评测时）到 v3.4（当前），API 和安装方式的频繁变更可能困扰长期用户
4. **70K Stars 与贡献者集中的矛盾**——Commit 历史高度集中在少数核心开发者

### 趋势判断

**快速上升期，但需要关注可持续性**。MinerU 在 PDF 解析赛道的技术领先地位稳固，但：国产 GPU 支持是政策红利，不是市场驱动；70K Stars 中很大一部分来自 "国产开源替代" 的叙事效应。长期看，核心问题是能否形成独立于上海 AI Lab 的可持续社区。

### 适用场景
- RAG 系统的 PDF 预处理管线
- 学术论文/技术文档的批量结构化提取
- 信创/国产化环境的文档解析需求
- 多语言（含中日韩）文档的 OCR 和结构化

### 不适用场景
- 纯文本 PDF 的简单提取（PyMuPDF4LLM 更快）
- 商业合规要求严格的场景（许可协议需仔细审查）
- 对实时性要求极高的在线服务（pipeline 后端有固定延迟）

---

## 关键文件路径速查

| 文件 | 用途 | 重要度 |
|------|------|--------|
| `README_zh-CN.md` | 中文文档入口 | ⭐⭐⭐⭐⭐ |
| `demo/demo.py` | 最简使用示例 | ⭐⭐⭐⭐⭐ |
| `docker/china/` | 国产 GPU Dockerfile | ⭐⭐⭐⭐ |
| `docker/global/Dockerfile` | NVIDIA GPU 部署 | ⭐⭐⭐⭐ |
| `docker/compose.yaml` | 一键服务编排 | ⭐⭐⭐⭐ |
| `docs/` | MkDocs 文档站源码 | ⭐⭐⭐ |
| `.github/workflows/cli.yml` | CLI CI 配置 | ⭐⭐⭐ |
| `MinerU_CLA.md` | 贡献者许可协议 | ⭐⭐⭐ |
| `SECURITY.md` | 安全策略 | ⭐⭐ |
