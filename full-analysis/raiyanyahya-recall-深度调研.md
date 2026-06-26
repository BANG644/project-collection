# raiyanyahya/recall 全方位深度调研

> 调研时间：2026-06-23  
> Stars：310 ⭐ | Forks：7 | Language：Python  
> 创建时间：2026-06-19 | License：MIT  
> 类型：Claude Code Plugin（本地记忆插件）

---

## 一、项目全景

**Recall** 是一个针对 **Claude Code** 的本地记忆（memory）插件，解决 Claude Code 的"冷启动"问题——每次新建会话时，Claude Code 对项目一无所知，需要用户从头解释。

Recall 的核心思路简单而优雅：

> **不依赖 LLM，不用 API Key，纯本地算法（TF-IDF + TextRank）自动记录会话 → 生成摘要 → 下次会话自动加载**

### 数据流

```
会话期间 → .recall/history.md（增量追加，记录所有提示、回复、文件操作、命令）
会话结束 → /recall:save → 本地summarizer（TF-IDF + TextRank）→ .recall/context.md（压缩摘要）
新会话开始 → 自动加载 context.md → Claude 知道当前进度
```

### 为什么不需要 API Key？

Recall 的摘要由**纯 Python 实现的 TF-IDF + TextRank 算法**生成，完全本地运行。Numpy 为可选加速器，非必需。

---

## 二、核心架构

### 2.1 文件结构

```
.recall/
├── history.md      # 会话日志（追加写入，完整记录）
└── context.md      # 会话摘要（由本地 summarizer 定时覆盖写入，约 1-2K tokens）
```

### 2.2 两个文件的用途对比

| 文件 | 写入时机 | 大小 | 用途 |
|------|---------|------|------|
| `history.md` | 每次 Agent 操作后追加 | 持续增长 | 完整的会话历史记录 |
| `context.md` | 用户运行 `/recall:save` 或配置 auto_save | 约 1-2K tokens | 下次会话的快速恢复点 |

### 2.3 与 Claude Code 内置记忆机制的对比

| 能力 | CLAUDE.md / # 指令 | --continue / --resume | Recall |
|------|-------------------|---------------------|--------|
| 是什么 | 手写规则 | 重放完整历史对话 | 自动捕获+本地摘要 |
| 维护方式 | 手动 | 无（选对话即可） | 无——随工作自动记录 |
| 存储内容 | 需遵循的规则 | 完整对话 | 目标、文件、命令、当前进度、下一步 |
| 恢复开销 | 极小 | 大（完整重放） | 约 1-2K tokens |
| 格式 | 手动编辑的 Markdown | 本地会话状态 | `.recall/` 下的纯文本，可 diff/分享 |
| Claude 对待方式 | 作为指令 | 作为对话上下文 | 在 fence 中作为"不可信参考数据" |

---

## 三、源码深度解读

### 3.1 项目结构

```
recall/
├── .claude-plugin/plugin.json   # Claude Code Plugin 声明清单
├── hooks/hooks.json             # 三个 Hook：SessionStart / Stop / SessionEnd
├── commands/                    # 自定义命令：
│   ├── recall-save.js           #   /recall:save 命令
│   ├── recall-show.js           #   /recall:show 命令
│   └── recall-log.js            #   /recall:log 命令
├── scripts/
│   ├── summarizer.py            # 核心：TF-IDF + TextRank 本地摘要算法
│   ├── make_context.py          # 构建/覆盖 context.md
│   ├── capture.py               # 追加会话活动到 history.md
│   ├── session_start.py         # 新会话加载 context + 询问是否继续
│   ├── parse_transcript.py      # 解析会话记录 → 事件 + 渲染器
│   └── config.py / common.py / redact.py
├── tests/                       # pytest 测试套件
├── benchmarks/bench.py          # 性能 + 质量基准测试
├── recall.config.json           # 配置文件模板
└── pyproject.toml               # ruff / pytest / bandit 配置
```

### 3.2 Summarizer（核心算法）

使用 **TF-IDF（词频-逆文档频率）** + **TextRank（基于 PageRank 的句子排名）**：

1. **TF-IDF 句向量化**：计算每个句子中词语的 TF-IDF 权重
2. **余弦相似度图**：句子之间构建相似度图（n×n 矩阵）
3. **TextRank**：对句子图跑 PageRank 迭代，选出最重要的 N 个句子
4. **原文顺序保留**：选出的句子按原始顺序排列，保持可读性

### 3.3 配置项（recall.config.json）

```json
{
  "output_dir": ".recall",       // 输出目录
  "capture_history": true,       // 是否记录历史
  "auto_save_context": "off",    // 自动保存模式："off" | "on_end"
  "summary_sentences": 8,        // 摘要句子数
  "redact": true,                // 自动脱敏
  "include_git": true,           // 包含 git diff --stat
  "max_input_chars": 200000      // 最大输入字符数
}
```

### 3.4 隐私与安全设计

- **无网络调用**：没有 HTTP 请求，没有第三方依赖
- **无 API Key**：没有 `ANTHROPIC_*` 等环境变量
- **自动脱敏**：API Key、Token、`.env` 赋值、PEM Key 会被自动识别并脱敏
- **路径安全**：`output_dir` 被限制在项目目录内，阻止路径穿越
- **Git 安全**：禁用 git hooks、pager、diff.external，防止恶意仓库利用 git config 执行代码

---

## 四、社区口碑

- 项目极新（2026-06-19 创建），310 stars / 3 天，增速不错
- Claude Code 社区长期以来的痛点就是"每次会话冷启动"，Recall 提供了比 `--continue` 更轻量的方案
- 零 API Key、零外部模型调用，对订阅用户非常友好

### 潜在问题

- 仅支持 Claude Code（不兼容其他 Agent 工具如 OpenClaw、Codex、Cursor）
- 纯提取式摘要（extractive）可能丢失上下文逻辑；未来可升级为生成式摘要（abstractive）
- 1-2K tokens 的语境标记 fenced 为"不可信参考数据"，Claude Code 可能不完全信任

---

## 五、竞品对比

| 维度 | Recall | mem0 | Claude Code --continue | CLAUDE.md |
|------|--------|------|----------------------|-----------|
| 实现方式 | 本地 TextRank | LLM + 向量数据库 | 重放完整会话 | 用户手写 |
| 是否需要外部模型 | ❌ | ✅ | ❌（但消耗 tokens） | ❌ |
| 是否自动 | ✅ | ✅ | 手动选择会话 | 手动 |
| 恢复成本 | ~1-2K tokens | ~1-2K tokens | 数 K - 数十K tokens | 极小 |
| 隐私 | 完全离线 | 依赖云 | 离线 | 离线 |
| 兼容Agent | 仅 Claude Code | 通用 | 仅 Claude Code | 通用 |

---

## 六、核心研判

### 6.1 价值评估

⭐⭐⭐⭐（对本 workspace 很有参考价值）

**核心洞察**：Recall 的"本地经典算法摘要 + 插件式嵌入"方案，是当前 AI Agent 记忆问题的最佳性价比方案之一。对比 mem0 等需要 LLM+向量数据库的方案，Recall 在零成本、零配置、隐私保护方面具有独有的优势。

### 6.2 与本 workspace 的关联

本 workspace 的 OpenClaw 也有类似的记忆机制（MEMORY.md + memory 目录）。Recall 的方案提供了一个很好的参考：
- 自动会话日志 → 定时摘要 → 新会话恢复
- 经典 NLP 算法做摘要（不依赖 LLM）

---

## 七、关键文件路径速查

| 文件位置 | 说明 |
|---------|------|
| `scripts/summarizer.py` | 核心摘要算法（TF-IDF + TextRank） |
| `scripts/make_context.py` | 构建 context.md |
| `scripts/capture.py` | 会话记录追加 |
| `scripts/session_start.py` | 新会话启动逻辑 |
| `scripts/redact.py` | 脱敏处理 |
| `hooks/hooks.json` | Claude Code 插件 Hook 定义 |
| `commands/` | /recall:save, show, log 三个命令 |
| `recall.config.json` | 配置模板 |
| `.claude-plugin/plugin.json` | Claude Code 插件声明 |

---

*调研 by IMA 知识库管家 | 2026-06-23*
