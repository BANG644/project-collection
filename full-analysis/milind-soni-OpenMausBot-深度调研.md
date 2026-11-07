# OpenMausBot 深度调研报告

> 调研时间：2026-11-08 ｜ 编号：#574 ｜ 来源：GitHub Trending（daily）净新增
> GitHub：https://github.com/milind-soni/OpenMausBot ｜ 许可：Apache-2.0
> 语言：TypeScript ｜ ⭐ 16,760 ｜ Fork 2,378 ｜ Open Issues 799 ｜ 末次推送 2026-11-07

---

## 一、项目全景

OpenMausBot 定位为 **Grok Bot / Muse / dots / Cue 的开源替代**：一个给「bot 配脑子 + 配电脑」的多 agent 桌面/服务端应用。每个 bot 可以接入云端 Linux 桌面、**隔离的本地虚拟机（Local VM）**，或在支持的平台用浏览器/设备能力；bot 在动手前会向人请求许可。它把 Claude / Codex / Grok 等本地 CLI agent 与云端 computer agent 统一编排，并通过 stdio MCP 服务器对外暴露一支「受边界约束的团队控制面」。

---

## 二、项目亮点（差异化）

1. **「每个 bot 一台电脑」**：bot 可用云端桌面、隔离 Local VM 或浏览器，能力不再只停留在聊天。
2. **动手先问**：权限经纪（permission broker）让 bot 的关键动作经人确认，而非自主乱跑。
3. **多 provider 归一**：Claude / Codex / Grok 的本地 CLI + 云端 agent，由 driver 层归一为一条标准运行时事件流。
4. **隔离优先的本地执行**：Local VM 基于 Podman，安全/网络/持久化状态被显式建模并 fail-closed。
5. **可控的团队控制面**：对外 MCP 只暴露「巡检 / 派活 / 等待 / 切换模型 / 中断」，绝不暴露审批授予、删除、凭据、电脑生命周期。

---

## 三、核心架构

README 的架构图点明「**两个进程**」：App 自身不持有任何 transport，只发带类型的 HTTP 命令、折叠一条 SSE 事件流；harness server（默认 `127.0.0.1:8799`）拥有所有 agent 进程，并把各家 provider 的原生协议归一为一条 canonical runtime 事件流（按线程以 NDJSON 记录）。

| 层 | 位置 | 职责 |
|----|------|------|
| Drivers | `server/drivers/` | 每 provider 一个：Claude/Codex/Grok 走各自 CLI（stream-JSON / JSON-RPC / ACP），外加云端 computer agent；未知 driver 降级为「unavailable」而非拖垮整队 |
| Harness | `server/harness/` | driver 注册表（配置→实例）+ 扇入事件总线 |
| API | `server/index.ts` | bot / turn / 审批 / model catalog / 电脑生命周期 / connector / 配置，HTTP + SSE |
| Voice | `server/tts/` | ElevenLabs / Fish Audio / Grok / 内置 Mac 语音 / 本地 Chatterbox；云密钥留 harness，朗读前先把 markdown 改写成「值得听」 |
| App | `src/` | 聊天外壳，server-backed store、单一 reducer、零客户端 transport |
| Desktop | `electron/` | macOS/Windows/Ubuntu 壳，内嵌 harness；Apple 语音仅 macOS，Ubuntu Xorg 可选本地控制，Wayland 仍 fail-closed |

此外 `server/relay` / `connector` / `cloudflare` / `companion` 负责电话/渠道接入与外部连接；`local-vm-*` 系列文件实现隔离执行。

---

## 四、源码深度解读

### 1. 本地 VM 工作区控制——fail-closed 的拿权（`src/lib/local-vm-workspace.ts`）

```ts
// Atomic on the server: a read followed by a take cannot prove ownership.
const taken = await port.take(nextBotId);
if (!taken.held) throw new Error(t("vm.workspace.holdNotAcquired"));
if (taken.owned !== true) {
  return { status: "held-elsewhere", botId: nextBotId, snapshot: taken };
}
try {
  await port.setInteractive(nextContextId);
} catch (error) {
  // Fail-closed: the native manager removes a view it cannot demote.
  await port.setInteractive(null).catch(() => {});
  await port.release(nextBotId).catch(() => {});
  throw error;
}
```

要点：控制权的获取在服务端是原子的；若无法降级视图则**释放并 fail-closed**，绝不留一个失控的 native view。

### 2. 敏感字段不进 React 状态（`sanitizeLocalVmWorkspaceStatus`）

```ts
/** UI-safe facts only: the response's secret-bearing viewer_url and diagnostics never reach React state. */
export function sanitizeLocalVmWorkspaceStatus(raw: JsonValue): LocalVmWorkspaceStatus { ... }
/** Only for the immediate main-process handoff: never in component state, logs, errors, analytics... */
export function readyLocalVmViewerUrl(raw: JsonValue): string | null { ... }
```

viewer URL 这类带凭证的字段被显式隔离：UI 只拿到 `mode/container/network/security/persistence` 等安全事实，`viewer_url` 只在主进程交接时短暂出现，永不进入组件 state / 日志 / 报错 / 埋点。

### 3. Mac 上自动拉起 Podman 机器（`server/podman-machine.ts`）

```ts
starting ??= startMachine(runner, onStart).finally(() => { starting = null; });
```

要点：并发到达的多次请求**共享同一次启动**（`starting ??=` 单例 Promise）；失败后带退避（`FAILED_START_BACKOFF_MS`），避免每轮各等一次失败启动；`machine start` 返回后 Podman socket 可能还需约 20s 才应答，于是 `recheck()` 每秒探一次。绝不擅自创建/安装 machine，只在「已配置但停了」时拉起。

---

## 五、应用场景与启发

- **想把多个 coding/聊天 agent 跑成一支「有电脑、会请示」的团队**（而不是各自裸 CLI），OpenMausBot 的「driver 归一 + 权限经纪 + 隔离 VM」是可直接借鉴的架构骨架。
- **本地隔离执行的安全建模**（security/network/persistence 三态 + fail-closed + 敏感字段不进前端）是任何「让 agent 操作本机/浏览器」项目的必学样本，尤其契合本工作区正在推进的 agent 安全边界议题。

---

## 六、社区口碑

- 正面：16.7k ⭐、2.4k fork，作为 Grok Bot 等闭源产品的开源替代话题度高；架构清晰（两进程、driver 归一、MCP 边界克制）。
- 待观察：Open Issues 799、仓库年轻、演进快；Apache-2.0 但生态/文档仍在成形，生产采用需评估成熟度与本地 VM 带来的运维成本。

---

## 七、竞品对比

| 项目 | 定位 | 与 OpenMausBot 差异 |
|------|------|---------------------|
| Grok Bot / Microsoft Copilot Studio | 闭源托管 agent 平台 | 不开源、不可自托管、本地隔离弱 |
| ChatGPT / Claude 桌面端 | 单 agent 聊天/工具 | 无多 bot 团队编排、无本地 VM |
| Droidrun / 通用 computer-use agent | 单 agent 操控设备 | 缺权限经纪与多 provider 归一 |
| **OpenMausBot** | 开源、可自托管、多 bot+多电脑+请示 | 隔离 VM + 权限经纪 + 受边界约束 MCP |

---

## 八、核心研判

OpenMausBot 把 2026 年「agent 要有手（电脑/浏览器）+ 要有缰绳（权限经纪）」的范式做成了可自托管开源实现，其**隔离执行的安全建模**是真正的技术亮点。短板是成熟度与本地 VM 运维负担。对「个人/小团队想搭一个安全可控的多 agent 工作台」这一需求，它是目前最接近成品的开源选项之一。

---

## 九、关键文件路径速查

- `README.md`（「How it works」+ 架构图 / 各层职责表）
- `src/lib/local-vm-workspace.ts`：VM 工作区控制、fail-closed、`sanitizeLocalVmWorkspaceStatus`
- `server/local-vm-inventory.ts`：VM 清单 / 显式 allow-list / 空闲清理守卫
- `server/podman-machine.ts`：Mac 上 Podman machine 自动拉起（单例/退避/重探）
- `server/drivers/`：各 provider driver；`server/harness/`：注册表 + 事件总线
- `server/index.ts`：HTTP+SSE API；`electron/`：桌面壳
