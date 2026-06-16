# smartNode (天基智枢) 全方位深度调研报告

> **仓库**: [Tong89/smartNode](https://github.com/Tong89/smartNode)
> **调研日期**: 2026-06-17
> **分类**: 空间仿真 / 天基数据回传 / 可视化平台

---

## 1. 项目定位

smartNode（天基智枢）是一个**面向天基数据回传场景的可视化仿真平台**，用于展示卫星、地面站、中继链路和内容驱动任务调度之间的协同关系。

**一句话定位**：开源的天基智能中继仿真平台。

**目标用户**：
- 航天工程研究者与学生
- 卫星通信系统教学演示
- 天基数据回传方案的预研验证
- 航天相关课程的实验平台

---

## 2. 核心架构

```
smartNode/
├─ backend/
│  ├─ app.py          后端启动入口
│  ├─ api.py          Flask API + 静态页面托管
│  └─ core.py         仿真模型、配置和调度引擎
├─ frontend/
│  ├─ assets/
│  ├─ app.js          前端逻辑
│  ├─ index.html      主页面
│  └─ styles.css      样式
├─ docker/
│  └─ entrypoint.sh   容器启动脚本
├─ Dockerfile         多阶段生产镜像
├─ docker-compose.yml 服务编排
└─ main.py            兼容入口
```

### 技术栈

| 层 | 技术 |
|----|------|
| 后端 | Python Flask + gunicorn |
| 前端 | 原生 HTML/CSS/JS |
| 容器 | Docker + docker-compose |
| 依赖管理 | pip-tools (锁定哈希) |
| 仿真引擎 | 自研 core.py |

---

## 3. 核心功能

- **三维空间态势展示** — 卫星轨道、地面站位置、中继链路的可视化
- **数据回传任务提交** — 支持用户提交仿真任务
- **资源状态监测** — 卫星、地面站、中继资源的实时状态
- **资源利用率统计** — 实时统计各资源的使用率
- **前后端分离** — Flask 提供 API + 静态文件托管
- **开放 API** — 无需密码登录，适合教学演示

### API 接口

| 方法 | 地址 | 说明 |
|------|------|------|
| GET | `/api/health` | 健康检查 |
| GET | `/api/data` | 仿真态势数据 |
| GET | `/api/resource_status` | 实时资源状态 |
| GET | `/api/resource_utilization` | 资源利用率统计 |
| POST | `/api/request` | 提交数据回传任务 |
| POST | `/api/update_ground_stations` | 调整地面站数量 |
| POST | `/api/update_leo_satellites` | 调整 LEO 卫星数量 |

---

## 4. 部署方案

### Docker 部署（推荐）

```bash
git clone https://github.com/Tong89/smartNode.git
cd smartNode
docker compose up --build
```

访问：`http://localhost:5000/frontend/`

### 环境变量

| 变量 | 默认值 | 说明 |
|------|--------|------|
| `SMARTNODE_HOST` | `127.0.0.1` | 监听地址 |
| `SMARTNODE_PORT` | `5000` | 端口 |
| `SMARTNODE_TIME_SCALE` | `10` | 仿真时间倍率 |
| `SMARTNODE_JWT_SECRET` | (示例) | JWT 签名密钥 |
| `SMARTNODE_ENV` | `development` | 运行环境 |

### 安全特性

- 非 root 运行（UID/GID 1001）
- 多阶段构建，工具不进入最终镜像
- 锁定依赖哈希
- 使用 `tini` 作为 PID-1
- `no-new-privileges` 禁止提权

---

## 5. 社区口碑

- 项目处于早期阶段，文档完善度好
- MIT 协议开源
- GitHub Actions CI 覆盖 Python 3.10/3.11/3.12
- 覆盖率门禁 60%

---

## 6. 竞品对比

| 项目 | 定位 | 技术栈 | 开源 | 适用场景 |
|------|------|--------|------|----------|
| **smartNode** | 天基仿真可视化 | Flask + JS | ✅ MIT | 教学演示、科研 |
| **STK** | 专业航天仿真 | 商业软件 | ❌ 商业 | 专业航天工程 |
| **GMAT** | 航天任务设计 | C++ | ✅ | 轨道设计优化 |
| **FreeFlyer** | 航天任务分析 | 商业软件 | ❌ 商业 | 专业分析 |

---

## 7. 核心研判

**优势**：
- 填补了开源天基仿真可视化领域的空白
- Docker 容器化一键部署，上手门槛低
- 安全实践规范（非 root、多阶段构建）
- MIT 协议，完全开放

**劣势**：
- 项目较为早期，功能深度有限
- 前端为原生 JS，无现代框架支撑
- 仿真模型可能较为简化

**适用场景**：
- 航天工程课程的教学演示
- 天基数据回传方案的快速原型验证
- 卫星通信系统的概念展示

---

## 8. 关键文件路径

| 文件 | 说明 |
|------|------|
| `backend/core.py` | 仿真核心引擎 |
| `backend/api.py` | API 定义 |
| `backend/app.py` | 应用入口 |
| `frontend/app.js` | 前端逻辑 |
| `docker-compose.yml` | 容器编排 |
| `requirements.txt` | 锁定依赖 |
