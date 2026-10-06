# openGym — 你真正拥有的自托管健身 / 自重训练追踪器

> 调研日期：2026-10-06 ｜ Stars：4,305 ｜ 语言：JavaScript（前端 React/Vite PWA，后端 Node 无框架）｜ License：AGPL-3.0 ｜ 维护者：DuarteSantos8
> 仓库：https://github.com/DuarteSantos8/openGym ｜ 演示：https://opengym.duarte-santos.ch/demo/

---

## 一、项目亮点（差异化）

1. **数据真正归你**：`docker compose up` 一键起，数据存在你控制的文件夹里，无订阅、无广告、无遥测；可 fork 改。
2. **Passkey（WebAuthn）登录 + 跨设备合并同步**：Face ID / 指纹登录；两台设备同时编辑会**合并而非覆盖**（sync 协议）。
3. **无框架后端**：`api/server.js` 用 Node 原生 `http` + 手写 JSON 文件存储 + 签名 session cookie，零运行时依赖框架——可读、可审计、易自托管。
4. **训练科学到位**：进程规则（线性 / Greyskull LP / 双进程 / 加时）、估算 1RM 曲线、结构平衡比（Poliquin/Thibaudeau/ATG）、年热力图、肌肉图三模式（训练量 / 恢复中 / 去训练）。
5. **可选 AI Coach + 只读 MCP**：AI Coach（Anthropic/OpenAI/Gemini/Ollama，你自己的 key）起草周计划并按你记录建议调整；MCP server 让 Claude Desktop 等只读回答你的训练历史——均**默认关闭、不进 Docker 镜像**。

---

## 二、核心架构

```
┌─────────────────────────────────────────────┐
│ frontend (React + Vite PWA, Capacitor 安卓)   │  HashRouter 多视图
└──────────────────────┬──────────────────────┘
                       │  /api (nginx 反代到 :3000)
┌──────────────────────┴──────────────────────┐
│ api (Node 原生 http, 无框架)                  │
│   server.js  ← 路由 + WebAuthn + session     │
│   passkeys-store.js / password.js / device-link.js │
│   media.js (自定义动作媒体) / rate-limit.js   │
│   coach/ (AI Coach: config/routes/cadence)   │
│   数据存储: JSON 文件 (DATA_DIR=/data)        │
└─────────────────────────────────────────────┘
        │ 可选
   mcp/ (只读 MCP server, 不进 Docker 镜像)
```

- **自托管三栈**：web（nginx 反代）+ api（Node）通过 `docker-compose.yml` 拉预构建镜像（amd64+arm64），也支持 GHCR 与本地 build；K8s / Cloudflare Tunnel / Caddy / Traefik / nginx 文档齐。
- **配置全走 `.env`**：`RP_ID` / `ORIGIN` / `WEB_PORT` / `PORT` / `SESSION_DAYS` / `INVITE_ONLY` / `ALLOW_GUEST` / `PASSWORD_LOGIN` / `TRUST_PROXY` 等。

---

## 三、源码深度解读（关键模块）

### 1. 后端入口：WebAuthn + JSON 存储 + 签名 cookie — `api/server.js`

```ts
/* opencod... 实为 openGym-api — passkey (WebAuthn) auth + per-user state storage
   No framework, JSON-file storage, signed session cookies. */
import { generateRegistrationOptions, verifyRegistrationResponse,
         generateAuthenticationOptions, verifyAuthenticationResponse } from '@simplewebauthn/server'
import { createBackoff, createWindow } from './rate-limit.js'

const PORT = +(process.env.PORT || 3000);
const DATA = process.env.DATA_DIR || '/data';
const RP_ID = process.env.RP_ID || 'localhost';
const ORIGIN = process.env.ORIGIN || 'http://localhost:8080';
const ADMIN_UIDS = (process.env.ADMIN_UIDS || '').split(',').map(s => s.trim()).filter(Boolean);
const INVITE_ONLY = /^(1|true|yes)/i.test(process.env.INVITE_ONLY || '');
```

要点：零框架但把认证（WebAuthn）、限流（backoff/window）、管理员、邀请制都做全；`DATA_DIR` 默认 `/data` 即 compose 挂载卷——"数据在你控制的文件夹"由架构保证。

### 2. AI Coach 凭证形状（实例 vs 档案）— `api/coach/config.js`

```ts
/* Credentials have two shapes, and the difference is the whole reason this file is careful:
     instance  — one account, stored here, encrypted. 单档案实例的便利默认。
     profile   — one account per profile. 多档案实例必须用，否则某人订阅被别人花。
   openGym does not interpret any provider's terms on a self-hoster's behalf...
   in instance mode a *personal* credential binds to the first profile that uses it,
   and any other profile is refused rather than warned. */
const DATA = process.env.DATA_DIR || '/data';
const FILE = path.join(DATA, 'coach.json');
```

要点：多租户自托管下"个人订阅凭证"被首用者绑定、他人拒绝——这是把"合规责任交还用户"的谨慎设计，而非替用户解释供应商条款。`COACH_DISABLED` 是运维kill switch。

### 3. 前端入口：媒体同步 + Service Worker + 原生键盘 — `frontend/src/main.jsx`

```tsx
createRoot(document.getElementById("root")).render(<StrictMode><App /></StrictMode>)

// 自定义动作媒体：上传缺的、本地清理、离线保留计划文件
startMediaSync(useStore)
// Android 15 不 resize 软键盘，app 自己说覆盖多少，聚焦字段保持在上面
startNativeKeyboard()

if (!MOBILE && 'serviceWorker' in navigator && location.protocol === 'https:') {
  navigator.serviceWorker.register('sw.js').catch(() => {})
  import('./lib/media-prefetch.js').then(m => m.startMediaPrefetch(useStore)).catch(() => {})
}
```

要点：PWA 离线优先（service worker + 媒体预取），移动端用 Capacitor 原生壳；`startMediaSync` 保证"未联网也能练、联网后补媒体"——真实健身场景（健身房信号差）的刚需。

### 4. 路由与视图 — `frontend/src/App.jsx`

```tsx
import { HashRouter, Routes, Route } from 'react-router-dom'
import Home from './views/Home.jsx'
import Workout from './views/Workout.jsx'
import Stats from './views/Stats.jsx'
import Muscles from './views/Muscles.jsx'
import StructuralBalance from './views/StructuralBalance.jsx'
import CoachChat from './views/CoachChat.jsx'
// ... Login / Plan / RoutineEdit / History / Library / Settings / Admin 等
```

要点：视图齐全（首页/训练/统计/肌肉图/结构平衡/教练对话/管理台），`HashRouter` 适配静态托管与离线。

---

## 四、应用场景与启发

- **场景**：不想把训练数据交给商业化健身 App（订阅、停服、隐私）的人；想自托管、可 fork、能离线练、可跨设备合并同步。
- **启发（可借鉴点）**：
  - "零框架 + JSON 文件 + 签名 cookie"是**最小可信后端**范本：自托管友好、易审计，适合个人/小团队工具，不必一上来就上框架。
  - WebAuthn passkey 作为默认登录、密码登录可关，是 2026 年自托管应用的现代身份基线。
  - "多设备合并而非覆盖"的 sync 协议，比"后写覆盖"体验好太多——任何本地优先（local-first）应用都该有。
  - 可选 AI 能力**默认关闭、不进镜像**，把"要不要用 AI"的选择权交还自托管者。

---

## 五、社区口碑

- 4,305★、659 forks，AGPL-3.0；有 Discord、GitLab CI、覆盖率徽章、17 语言（含 RTL 阿拉伯语）、演示站与 Android APK；功能完整度在自托管健身赛道领先。
- ⚠️ 局限：AGPL-3.0 对闭源改装有传染性（商业托管需注意）；训练科学模块（进程规则/结构平衡）深度足够但非医学建议；AI Coach/MCP 为可选外挂。
- 结论：口碑正面，是"自托管健身追踪器"里完成度最高的开源选项之一。

---

## 六、竞品对比

| 维度 | openGym | FitNotes / Strong / Hevy | Graviton / TrainerDay | 纯 Excel 自记 |
|------|---------|--------------------------|-----------------------|---------------|
| 自托管 / 数据归你 | ✅ | 否（SaaS） | 部分 | ✅ |
| Passkey 登录 | ✅ | 账号制 | 视 | — |
| 跨设备合并同步 | ✅ | ✅（云） | ✅ | 否 |
| 训练科学（1RM/结构平衡） | ✅ | 部分 | 部分 | 手算 |
| 可选 AI Coach / MCP | ✅（默认关） | 个别有 | 少 | 否 |
| License | AGPL-3.0 | 专有 | 专有 | — |

**差异化**：把"数据主权 + 现代身份 + 训练科学 + 可选 AI"全部塞进一个可 fork 的自托管应用，且零框架后端降低自托管门槛。

---

## 七、核心研判

- **价值**：自托管健身追踪器的标杆实现；其"零框架可信后端 + passkey + 合并同步 + 可选 AI 默认关"的组合，是个人工具类项目的优秀参考架构。
- **风险**：① AGPL-3.0 对闭源商业化不友好；② 后端无框架意味着复杂查询/并发需自己扛，规模上去要重构；③ 训练建议非医疗，需用户自判。
- **建议**：想自托管训练记录直接部署；想学"最小可信自托管后端"重点读 `api/server.js` + `passkeys-store.js` + `coach/config.js` 三件套。

---

## 八、关键文件路径速查

| 文件 | 作用 |
|------|------|
| `api/server.js` | 后端入口：WebAuthn + JSON 存储 + 签名 cookie + 路由 |
| `api/passkeys-store.js` | Passkey 存储与管理 |
| `api/password.js` | 密码散列 / 重置码 |
| `api/device-link.js` | 新设备配对（一次性码 / QR） |
| `api/coach/config.js` `api/coach/routes.js` | AI Coach 凭证形状与路由 |
| `api/media.js` | 自定义动作媒体（上传/限流/位置剥离） |
| `frontend/src/App.jsx` `frontend/src/main.jsx` | 前端路由与入口（媒体同步 / SW / 原生键盘） |
| `mcp/README.md` | 只读 MCP server（不进 Docker 镜像） |
| `docs/SELF_HOSTING.md` `docs/AI_COACH.md` | 自托管 / AI Coach 指南 |
| `docker-compose.yml` `.env.example` | 一键部署与配置样例 |
