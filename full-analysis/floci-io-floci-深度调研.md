# floci-io/floci 深度调研

> 调研日期：2026-11-04 ｜ 定位：免费、无鉴权、本地优先的 AWS 云服务模拟器（LocalStack 平替）
> 仓库：https://github.com/floci-io/floci ｜ Stars：≈28.6k ｜ 语言：Java ｜ 许可：MIT
> 关键词：aws-emulation / localstack / devops / testcontainers / Quarkus Native

## 一、项目定位（一句话）

Floci 是一个本地运行的 AWS 云服务模拟器，把 S3 / DynamoDB / Lambda / SQS / RDS / ElastiCache / API Gateway v2 / Cognito 等数十个 AWS 服务「搬」到你的笔记本与 CI 里——监听 `localhost:4566`，与 AWS SDK / CLI / Terraform / CDK 线协议兼容，无需云账号、无需 token、无功能门禁。它是 LocalStack Community 在 2026-03 起强制鉴权、冻结安全更新之后的「MIT 开源 Reset 按钮」。

## 二、项目亮点（差异化，开篇先看）

1. **真·无鉴权 + MIT**：LocalStack Community 自 2026-03 起每次启动都要账号 token，且安全更新冻结；Floci 永不要求 token，许可证是干净的 MIT（非 BSL），可 fork / 嵌入 / 商用。
2. **Quarkus Native 极致轻量**：用 GraalVM Mandrel 编译为原生二进制，官方宣称 24ms 启动 vs LocalStack ~3.3s，空闲 13 MiB vs 143 MiB，镜像 ~90MB vs ~1GB。
3. **不是 mock，是真实运行时**：Lambda / ECS / EC2 / CodeBuild 等用**真实 Docker 容器**执行（拉真实 runtime 镜像跑函数、起真实 k3s 跑 EKS），S3 事件触发的是真 Lambda 而非假调用。
4. **Drop-in 替换**：同端口 4566、同线协议、同 SDK 调用；把 `localstack/localstack` 镜像换成 `floci/floci` 即可，应用代码零改动，LocalStack 环境变量自动翻译。
5. **每账号隔离 + 可选 TLS**：AWS_ACCESS_KEY_ID 为 12 位数字时当作 accountId 做存储隔离；一个 `--env` 开关自签证书开 HTTPS。

## 三、核心架构（克制呈现）

技术栈为 **Quarkus 3.40.1.1（RESTEasy Reactive）**，原生镜像编译。源码根 `src/main/java/io/github/hectorvent/floci/`，呈「单服务 + 按 AWS 服务分模块」结构：

- **`services/<service>/`**：每个 AWS 服务一个包，内部按职责拆 `model/`（数据结构）+ `XxxJsonHandler` / `XxxQueryHandler`（协议处理）+ 可选 `container/`（真实 Docker 执行）。已覆盖 accessanalyzer、acm、apigateway(v1/v2)、athena、bedrock、batch、dynamodb、ecs、eks、elasticache、kms、lambda、rds、route53、s3、secretsmanager、sqs、ssm、stepfunctions 等 45+ 服务。
- **`core/common/`**：跨服务公共件——`auth/`（鉴权）、`dns/EmbeddedDnsServer`（内嵌 DNS）、`docker/`、`port/`、`tls/TlsProxyServer`、`vtl/`（Velocity 模板，模拟 AWS 变量求值）、`CloudFrontEdgeDomain`。
- **`core/storage/`**：存储抽象层（见下）。
- **`lifecycle/inithook/`**：容器启动初始化钩子（兼容 LocalStack `/etc/localstack/init/`）。

## 四、应用场景与启发

- **本地开发与 CI**：把「起一个真实 AWS 环境」降为 `docker compose up` 一行，CI 里每次测试自旋一个 emulator，避免开临时云账号。
- **SDK / IaC 兼容性回归**：官方用 1,925 项跨 6 个 SDK + 3 个 IaC 工具的兼容测试套件（宣称 100% 通过），可作「我的 SDK 调用在本地到底走不走得通」的回归基准。
- **给同类需求的启发**：① 做「云模拟器」时，**真实容器执行 > 内存假实现**——只有真跑 Lambda/容器，集成测试才可信；② **每账号隔离 + 环境变量翻译**是「平滑迁移存量用户」的关键工程点；③ Quarkus Native 把「重 JVM 中间件」压成 90MB 镜像，是 CI 友好型基础设施的范本。

## 五、源码深度解读

**1) 请求路由——`services/apigateway/AwsServiceRouter.java`**
API Gateway 集成请求通过 `arn:aws:apigateway:{region}:{service}:action/{ActionName` 形式的 URI 进来，由 `@ApplicationScoped` 的 `AwsServiceRouter` 用注入的各服务 `XxxJsonHandler` 按 action 分发：

```java
@ApplicationScoped
public class AwsServiceRouter {
    private final StepFunctionsJsonHandler stepFunctionsHandler;
    private final DynamoDbJsonHandler dynamoDbHandler;
    private final SqsJsonHandler sqsHandler;
    // ... 十几个 handler 通过 @Inject 构造器注入
    // 解析 ARN -> 选择 handler -> 调用
}
```
这是典型的 **CDI 依赖注入 + 每服务 handler 表** 模式：新增 AWS 服务 = 新增一个 `XxxJsonHandler` 并注入，路由对开放封闭。

**2) 存储抽象——`core/storage/HybridStorage.java`**
`HybridStorage<K,V>` 实现 `StorageBackend`，写先落内存 `ConcurrentHashMap`，再用 `ScheduledExecutorService` **周期性异步刷盘**（`flushIfDirty`），兼顾读写性能与持久化：

```java
public class HybridStorage<K, V> implements StorageBackend<K, V> {
    private volatile ConcurrentHashMap<K, V> store = new ConcurrentHashMap<>();
    private final AtomicBoolean dirty = new AtomicBoolean(false);
    public synchronized void put(K key, V value) { store.put(key, value); dirty.set(true); }
}
```
同层还有 `InMemoryStorage` / `PartitionedFileStorage` / `WalStorage`（写前日志）/ `AccountAwareStorageBackend`（账号隔离）/ `StorageQuarantine` / `PersistentPathValidator`，构成一套「可插拔、可持久化、可隔离」的存储后端矩阵——这正是多服务共享状态又不串号的底座。

## 六、社区口碑（全网口碑）

- **强正面信号**：2026 年多篇文章（floci.io 官方对比、systemadministration.net、worldprogramming.org、megaoneai 等）将其定位为「LocalStack 强制鉴权后的免费替代」，集中好评在「无 token、轻量、MIT、Drop-in」。官方对比表列了 Lambda 真容器、RDS/ElastiCache/API Gateway v2/Cognito 等 LocalStack Community 不免费给的能力。
- **冷静提醒（第三方）**：① worldprogramming.org 实测独立基准约 ~130ms 而非 24ms（营销数字取最佳情形）；② 生态成熟度、企业支持、长期维护确定性仍不如经营多年的 LocalStack；③ 本地模拟器**永远不等于 AWS**——权限、时序、配额、事件一致性、托管服务行为有微妙差异，上生产前仍需真云验证。
- **小结**：开发者对「关键本地工具被账号/token 绑定」普遍不满，Floci 把「本地测试环境应当易起、易毁、免费」这件事重新带回视野，是 2026 年云模拟器赛道最值得关注的新变量。

## 七、竞品对比

| 维度 | Floci | LocalStack Community（2026-03 后） | Moto（Python） | 真 AWS |
|------|-------|-----------------------------------|---------------|--------|
| 鉴权 | 永不要求 | 强制 token | 无（单进程库） | 账号体系 |
| 许可 | MIT | 受限 / BSL | Apache-2.0 | — |
| 启动/内存 | 24ms / 13MiB（官方） | 3.3s / 143MiB | 进程内，轻 | — |
| 真实容器执行 | ✓（Lambda/ECS/EC2…） | Pro 才有 | ✗（纯内存 mock） | ✓ |
| 适用 | 本地+CI 集成测试 | 企业/需支持 | pytest 单元级 mock | 生产 |

Moto 是 Python 单测级 mock（无真实容器、无独立服务），与 Floci 定位不同；LocalStack 胜在生态深、第三方集成多、有商业 SLA。

## 八、核心研判

- **价值判断**：对「本地/CI 跑 AWS 集成测试、不想管 token、预算敏感」的个人与中小团队，Floci 是当前默认推荐；对「深度依赖 LocalStack 专属工具链 / 要 SLA 支持」的团队，LocalStack Pro 仍合理。
- **风险点**：① 项目较新，大规模项目长期稳定性待验证；② 营销基准与真实基准有落差，选型时要自测；③ AWS 持续演进，模拟器跟进速度决定其生命力。
- **采用建议**：先用 `docker compose up` 跑通「S3→Lambda→DynamoDB」最小链路做 PoC，确认你的 SDK 调用在本地 100% 走通再铺开；生产验证仍留真云。

## 九、关键文件路径速查

- `src/main/java/io/github/hectorvent/floci/services/apigateway/AwsServiceRouter.java` — API Gateway 集成请求路由
- `src/main/java/io/github/hectorvent/floci/services/sqs/SqsJsonHandler.java` — SQS 协议处理（典型服务 handler 范式）
- `src/main/java/io/github/hectorvent/floci/core/storage/HybridStorage.java` — 混合存储（内存+异步刷盘）
- `src/main/java/io/github/hectorvent/floci/core/storage/AccountAwareStorageBackend.java` — 每账号隔离
- `src/main/java/io/github/hectorvent/floci/core/common/dns/EmbeddedDnsServer.java` — 内嵌 DNS
- `src/main/java/io/github/hectorvent/floci/config/TlsProxyServer.java` — 可选 HTTPS
- `pom.xml`（`quarkus.platform.version=3.40.1.1`）— 框架与原生编译配置
- `compatibility-tests/` — 跨 SDK / IaC 的兼容测试套件
