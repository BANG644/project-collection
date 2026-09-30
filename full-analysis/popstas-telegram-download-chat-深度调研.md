# popstas/telegram-download-chat 深度调研

> 调研日期：2026-10-01 ｜ 数据源：gh API（README / 目录树 / src/telegram_download_chat/mcp/server.py / .claude-plugin/plugin.json）｜ 定位：Telegram 聊天历史下载/导出/转换/过滤/分析的 CLI·GUI·WebUI·MCP·Skill 一体化工具（MIT）

## 一、项目定位（一句话）

**telegram-download-chat** 是一个「下载优先」的 Telegram 聊天历史处理工具：单一 CLI 既能导出 JSON/TXT/HTML/PDF、下载媒体、转写语音、按日期/用户/关键词/子会话过滤，又原生提供 **MCP Server** 与 **多 Agent 插件（Claude/Cursor/Codex/Skill）**，让 AI 助手能直接驱动它检索你的聊天记录。

## 二、项目亮点（差异化）

1. **四形态一体**：同一个核心（`src/telegram_download_chat/`）同时提供 CLI、GUI（`gui/`）、WebUI（`web/`）、MCP Server（`mcp/`）——不同入口共享一套下载/导出逻辑，避免重复实现。
2. **原生 MCP 集成（关键卖点）**：`python -m telegram_download_chat.mcp` 即起一个基于 `FastMCP` 的 MCP Server（支持 stdio / http 两种 transport），暴露 `telegram_get_messages` 工具，使 Claude Desktop 等可直接查你的聊天记录。
3. **单一真相源生成多 Agent 插件**：`skills/telegram-download-chat/SKILL.md` 是唯一的 skill 描述，`scripts/gen_agent_plugins.py` 据此生成 `.claude-plugin/`（marketplace.json + plugin.json）、`.cursor/rules/*.md`、`.codex/prompts/*.md`、`AGENTS.md`/`CLAUDE.md`——并配测试防止漂移。
4. **导出能力极全**：JSON（全元数据）、人/LLM 可读 TXT、Telegram 风格 HTML、PDF；媒体下载、语音转写（`--stt`，Premium 且本地缓存去重）、`--split month|year|topics`、文件夹下载、`--since-id` 增量续传。
5. **跨平台 + PyPI 一键装**：`pip install telegram-download-chat`（MCP 用 `[mcp]` 额外依赖），Windows/macOS/Linux 通吃。

## 三、核心架构

- **技术栈**：Python 3.8+ / Telethon（MTProto 客户端）/ Click 系 CLI / PySide 或类似 GUI / FastMCP（MCP）/ httpx。
- **核心包 `src/telegram_download_chat/`**：
  - `core.py`：下载/导出的核心逻辑（连接、分页、过滤、格式渲染）。
  - `cli/`：`__main__.py` + CLI 参数定义（上面那一大张 options 表）。
  - `gui/`：桌面界面（`main.py` / `windows/` / `worker.py` 异步下载）。
  - `web/`：WebUI（`main.py`）。
  - `mcp/`：`server.py`（FastMCP Server）+ `connection_manager.py`（会话管理）+ `AGENTS.md`/`CLAUDE.md`。
  - `partial.py`（增量/子会话）、`paths.py`（配置路径，Windows 落 `%APPDATA%\telegram-download-chat\config.yml`）。
- **Agent 集成层**：`.claude-plugin/`（Claude Code 插件市场）、`.cursor/rules/`（Cursor 规则）、`.codex/prompts/`（Codex slash 命令）、根 `AGENTS.md`/`CLAUDE.md`。

## 四、应用场景与启发

- **场景**：需要把 Telegram 私聊/群/频道/导出归档转成可分析文本的人；想让 Claude/Cursor/Codex 直接「读取我的 Telegram 聊天」的 Agent 用户；做聊天数据 ETL/检索的开发者。
- **启发**：
  - 它是「**传统 CLI 工具如何拥抱 Agent 生态**」的范本：核心不变，额外维护一个 `SKILL.md` 真相源，用脚本**派生**各 harness 的插件清单，并加测试防漂移——比手写多份容易腐化的配置文件稳得多。这正是用户 WorkBuddy skill 体系「单一 SKILL.md + 多 harness 分发」的同构思路。
  - MCP Server 用 `TelegramMessage`/`TelegramMessagesResponse` 等 Pydantic 模型做结构化返回 + `connection_manager` 单例管理 Telethon 会话——把「有状态长连接资源」安全地暴露给无状态 MCP 调用的范式，值得借鉴。

## 五、源码深度解读（核心模块）

**1. `src/telegram_download_chat/mcp/server.py`：用 FastMCP 暴露聊天检索工具**

```python
from mcp.server.fastmcp import FastMCP
from pydantic import BaseModel, Field

class TelegramMessage(BaseModel):
    id: int = Field(description="Message ID")
    date: str = Field(description="ISO format datetime of the message")
    text: str = Field(description="Message text content")
    user_name: str = Field(description="Display name of the sender")
    reply_to_msg_id: Optional[int] = Field(default=None, ...)

# 全局连接管理器（单例，跨 MCP 客户端会话存活）
_manager: Optional[TelegramConnectionManager] = None
_manager_lock: Optional[asyncio.Lock] = None

async def _get_manager() -> TelegramConnectionManager:   # 懒加载单例
    ...
# 注册工具 telegram_get_messages：按聊天+时间过滤拉取消息
```

Server 用 `FastMCP` 声明工具，返回强类型的 `TelegramMessage` 列表；`TelegramConnectionManager` 以单例形式保活 Telethon 会话，解决「MCP 调用无状态、但 Telegram 连接有状态」的矛盾。

**2. `.claude-plugin/plugin.json`：声明式触发词**

```json
{
  "name": "telegram-download-chat",
  "description": "Download, export, convert, filter, and analyze Telegram chats ...",
  "keywords": ["telegram","export","cli","chat","download"],
  "homepage": "https://github.com/popstas/telegram-download-chat"
}
```

配合 `scripts/gen_agent_plugins.py` 从 `SKILL.md` 生成，README 明确「a test fails if they drift（一旦派生文件与真相源不一致，测试就失败）」——这是多 Agent 插件维护的关键纪律。

**3. `core.py` + `cli/`：下载/导出内核**

所有形态（CLI/GUI/Web/MCP）最终都收敛到 `core.py` 的下载与格式渲染；`--since-id` 增量、`--split` 拆分、`--stt` 转写缓存等特性都在内核层实现一次，前端只做编排。

## 六、社区口碑

- 218⭐、MIT、最近提交 2026-09-16（活跃，但体量小）；README 极其详尽（777 行，含完整 options 表与多平台配置）；作者 Stanislav Popov，背靠同作者的 `telegram-assistant`/`telegram-resender` 生态。
- 定位清晰：本工具**只下载不发送**，发送类需求指向兄弟项目，避免功能膨胀。

## 七、竞品对比 + 核心研判

| 维度 | telegram-download-chat | Telethon 自己写脚本 | Telegram 官方导出 | 商业备份 SaaS |
|---|---|---|---|---|
| 多格式导出(TXT/HTML/PDF) | ✅ | ⚠️ 自己写 | ⚠️ JSON/HTML | ✅ |
| 媒体/语音转写 | ✅ | ❌ | ❌ | ⚠️ |
| 原生 MCP Server | ✅ | ❌ | ❌ | ❌ |
| 多 Agent 插件(Claude/Cursor/Codex) | ✅ 单源派生 | ❌ | ❌ | ❌ |
| 开源免费 | ✅ MIT | ✅ | ✅ | ❌ |

**研判**：作为「Telegram 数据导出」工具本身已很完整；但真正值得借鉴的是它**把 CLI 工具 Agent 化**的做法——`SKILL.md` 单源 + 脚本派生多 harness 插件 + 防漂移测试，几乎是「给现有工具加 MCP/Skill 支持」的标准答案。风险：①star 数低、维护者单一，长期可持续性存疑；②依赖 Telethon 与 Telegram 私有协议，账号有风控/封号可能；③MCP 当前仅 1 个工具（`telegram_get_messages`），能力面尚窄。与用户的「MCP/Skill 工具链」兴趣高度契合，是可照抄的集成范式样例。

## 八、关键文件路径速查

- 仓库根：`https://github.com/popstas/telegram-download-chat`
- 核心：`src/telegram_download_chat/core.py`、`src/telegram_download_chat/__main__.py`、`cli/`、`partial.py`、`paths.py`
- GUI/Web：`src/telegram_download_chat/gui/`、`src/telegram_download_chat/web/`
- MCP：`src/telegram_download_chat/mcp/server.py`、`mcp/connection_manager.py`、`mcp/AGENTS.md`、`mcp/CLAUDE.md`
- Agent 插件：`skills/telegram-download-chat/SKILL.md`、`scripts/gen_agent_plugins.py`、`.claude-plugin/`（marketplace.json/plugin.json）、`.cursor/rules/telegram-download-chat.mdc`、`.codex/prompts/telegram-download-chat.md`
- 配置：Windows `%APPDATA%\telegram-download-chat\config.yml`
