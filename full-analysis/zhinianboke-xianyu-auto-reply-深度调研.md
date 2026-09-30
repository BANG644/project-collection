# zhinianboke/xianyu-auto-reply 深度调研

> 调研日期：2026-10-01 ｜ 数据源：gh API（README / 目录树 / websocket/app/services/xianyu/ai_reply_engine.py 等）｜ 定位：基于 Python + FastAPI 的闲鱼自动化客服/运营系统（AGPL-3.0）

## 一、项目定位（一句话）

**xianyu-auto-reply** 是一套面向闲鱼平台的「自动化客服 + 运营」系统：用 WebSocket 实时对接闲鱼服务器收发消息，结合 LLM 做智能自动回复，并集成了自动发货、自动评价、自动擦亮（刷新曝光）等虚拟商品自动化流程。

## 二、项目亮点（差异化）

1. **WebSocket 长连接直连闲鱼**：不是轮询抓页面，而是 `websocket` 服务常驻连接闲鱼，实时接收消息、推送回复，延迟与拟人度都优于传统爬虫式方案。
2. **LLM 议价引擎**：内置 `AIReplyEngine`，支持 OpenAI 兼容 API、DashScope（通义）、Gemini 多后端；按「议价轮次递减优惠」策略生成短句回复（每句≤10 字、总≤40 字），贴近真实卖家话术。
3. **运营全链路自动化**：除回复外还覆盖自动发货（`auto_delivery_handler.py`）、自动评价、自动擦亮，对虚拟商品（卡密/教程类）可跑通无人值守闭环。
4. **工程化部署**：`docker-compose.yml` + 多服务拆分（backend-web / websocket / scheduler）+ `EXE打包构建.bat` 一键出 Windows 客户端，前端 `frontend` 提供可视化管理界面。

## 三、核心架构

- **技术栈**：Python 3 + FastAPI（backend-web / websocket / scheduler 三个独立服务）+ WebSocket 客户端 + SQLAlchemy（async）+ 前端（frontend）+ Docker / Windows EXE。
- **服务拆分**：
  - `websocket/`：核心实时层——`app/services/xianyu/` 下是闲鱼交互的全部逻辑：`ai_reply_engine.py`（AI 回复引擎，1024 行）、`auto_reply_service.py`（自动回复主服务，2390 行）、`message_handler.py`（消息路由）、`connection_manager.py`、`cookie_manager.py` / `token_manager.py` / `cookies_refresh_service.py`（账号与鉴权）、`auto_delivery_handler.py`（自动发货）、`yifan_api_handler.py`、`rate_service.py`（频控）。
  - `backend-web/`：管理后台——`app/core/`（config / http_client / paths / security）、`app/services/`、`app/api/`。
  - `scheduler/`：定时任务（擦亮、评价等）。
  - `common/`：跨服务共享的 `db`（async_session_maker）、`models`（xy_account、ai_chat_message 等）、`schemas`、`services`（ai_provider_service：多 AI 后端归一化）。
- **账号/会话治理**：多个闲鱼账号的 cookie/token 由 `cookie_manager` + `token_manager` 统一维护并支持自动刷新，避免单账号风控。

## 四、应用场景与启发

- **场景**：闲鱼虚拟商品卖家（卡密、网课、代下等）想做无人值守客服；需要批量管理多账号、统一话术与议价策略的运营方。
- **启发**：
  - 它示范了「电商 IM 自动化」的可落地形态：**WebSocket 常驻 + 单例对话引擎 + 按会话粒度加锁**，比「定时抓页面」更稳更拟人；其中 `_chat_locks` 按会话 ID 加 `asyncio.Lock` 的思路，可直接借鉴到任何 IM bot 的并发控制。
  - `AIReplyEngine` 把「意图检测（本地关键词）+ LLM 生成 + 议价轮次状态机」解耦，且通过 `common.services.ai_provider_service` 把 OpenAI/DashScope/Gemini 归一成统一接口——这种「多 LLM 后端抽象层」是做客服类 agent 的通用范式。

## 五、源码深度解读（核心模块）

**1. `websocket/app/services/xianyu/ai_reply_engine.py`：单例 AI 回复引擎 + 议价状态机**

```python
class AIReplyEngine:
    _instance: Optional["AIReplyEngine"] = None
    def __init__(self):
        self._init_default_prompts()
        self._chat_locks: Dict[str, asyncio.Lock] = {}
        self._chat_locks_max_size = 10000      # 最大锁数量
        self._chat_locks_expire_time = 7200     # 锁过期时间（2 小时）
    @classmethod
    def get_instance(cls) -> "AIReplyEngine":   # 全局单例
        if cls._instance is None:
            cls._instance = AIReplyEngine()
        return cls._instance
    # 默认 prompt 按意图分桶：price（议价）/ tech（技术）/ default（客服）
    # price 策略：根据议价次数递减优惠——第1次小幅、第2次中等、第3次最大；
    # 接近轮数上限时坚持底线、强调商品价值；优惠不超过最大百分比/金额。
```

引擎以单例存在，每个会话（买家）持有一把 `asyncio.Lock`，防止同会话并发回复发乱；`price` prompt 内置「议价次数递减优惠」的话术约束，是该项目最贴近真实卖家的设计点。

**2. `websocket/app/services/xianyu/auto_reply_service.py`：自动回复主服务**

2390 行的主服务把「消息接收 → 意图判断 → 调用 AIReplyEngine → 擦亮/发货联动」串成流水线，并接 `rate_service` 做频控、`cookies_refresh_service` 做账号保活——是整套系统从「能回复」到「能稳定运营」的关键层。

**3. `common/services/ai_provider_service.py`：多 LLM 后端归一化**

对外暴露 `build_anthropic_url` / `build_gemini_url` / `normalize_ai_provider_type` / `read_ai_enabled` 等，把 OpenAI 兼容、Anthropic、Gemini 三种上游封装成统一调用面，使 `AIReplyEngine` 无需关心具体厂商。

## 六、社区口碑

- 7.4k⭐、AGPL-3.0、最近提交 2026-09-24（活跃）；中文闲鱼自动化圈口碑较好，README 配有详细部署说明与 `启动.bat`/`停止.bat` 一键脚本，对 Windows 用户友好。
- 注意：AGPL-3.0 是强 Copyleft，二次分发/联机服务须开源衍生代码，商用需评估合规。

## 七、竞品对比 + 核心研判

| 维度 | xianyu-auto-reply | 通用客服机器人（如 ChatGPT 接入） | 闲鱼第三方代运营工具 |
|---|---|---|---|
| 直连闲鱼 WebSocket | ✅ 原生 | ❌ 需自建通道 | ⚠️ 黑盒 |
| 议价话术状态机 | ✅ 内置 | ❌ 需自己写 | ⚠️ |
| 自动发货/擦亮 | ✅ | ❌ | ⚠️ 收费 |
| 开源可审计 | ✅ AGPL | 视方案 | ❌ |
| 多账号治理 | ✅ | ❌ | ⚠️ |

**研判**：对闲鱼虚拟商品卖家，它是少见的「开源 + 直连 + 议价 + 运营」全链路实现，工程完整度高于一般脚本。风险：①AGPL-3.0 强 Copyleft，闭源商用有合规压力；②依赖闲鱼私有 WebSocket 协议，平台改版/风控升级可能随时失效，需持续跟进；③自动擦亮/发货触碰平台规则，有封号风险。与用户的「自动化/agent 工具链」兴趣契合，其「单例引擎 + 会话锁 + 多 LLM 抽象」架构可直接借鉴。

## 八、关键文件路径速查

- 仓库根：`https://github.com/zhinianboke/xianyu-auto-reply`
- 实时层：`websocket/main.py`、`websocket/app/services/xianyu/`（ai_reply_engine.py / auto_reply_service.py / message_handler.py / cookie_manager.py / auto_delivery_handler.py / rate_service.py）
- 管理后台：`backend-web/app/`（core/ api/ services/）
- 定时任务：`scheduler/`
- 公共层：`common/`（db/ models/ schemas/ services/ai_provider_service.py）
- 前端/部署：`frontend/`、`docker-compose.yml`、`EXE打包构建.bat`
