# TFT Player Tracker 使用指南

## 目录
- [快速开始](#快速开始)
- [Riot API密钥申请](#riot-api密钥申请)
- [配置说明](#配置说明)
- [Discord集成](#discord集成)
- [微信集成](#微信集成)
- [Docker部署](#docker部署)
- [常见问题](#常见问题)

## 快速开始

### 1. 环境准备

确保已安装：
- Python 3.10+
- Redis (可选，用于缓存)

### 2. 安装依赖

```bash
pip install -r requirements.txt
```

### 3. 配置环境变量

```bash
# 复制配置模板
cp .env.example .env

# 编辑 .env 文件
# 至少需要配置 RIOT_API_KEY
```

### 4. 运行程序

```bash
python main.py
```

## Riot API密钥申请

### 开发版API密钥（Development API Key）

1. 访问 [Riot Developer Portal](https://developer.riotgames.com/)
2. 使用你的Riot账号登录
3. 点击 "REGISTER PRODUCT" 或前往 Dashboard
4. 在 "Development API Key" 区域查看你的密钥
5. **注意**: 开发版密钥24小时过期，需要定期更新

**限制**:
- 20 请求/秒
- 100 请求/2分钟

### 生产版API密钥（Production API Key）

适用于长期运行的应用：

1. 在 Developer Portal 点击 "Apps"
2. 创建新应用并填写详细信息
3. 提交审核（通常需要1-2周）
4. 审核通过后获得生产版密钥

**限制**:
- 更高的请求限制（根据应用类型而定）
- 永久有效

## 配置说明

### 核心配置

```env
# Riot API密钥（必填）
RIOT_API_KEY=RGAPI-your-api-key-here

# 服务器区域
# 可选: na1, euw1, eun1, kr, br1, jp1, la1, la2, oc1, tr1, ru
RIOT_API_REGION=na1

# 路由区域（用于匹配历史等API）
# americas, europe, asia, sea
RIOT_API_ROUTING=americas

# 轮询间隔（秒）
POLLING_INTERVAL=120
```

### 通知规则配置

```env
# LP波动阈值（单局）
LP_CHANGE_THRESHOLD=50

# 每日LP累计变动阈值
LP_DAILY_CHANGE_THRESHOLD=100

# 启用段位变动通知
ENABLE_RANK_CHANGE_NOTIFICATION=true

# 启用LP阈值通知
ENABLE_LP_THRESHOLD_NOTIFICATION=true
```

### Redis配置（可选）

```env
REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_DB=0
REDIS_PASSWORD=
```

**提示**: 如果不使用Redis，程序会自动使用内存缓存

## Discord集成

### 1. 创建Discord Bot

1. 前往 [Discord Developer Portal](https://discord.com/developers/applications)
2. 点击 "New Application"，输入应用名称
3. 左侧导航选择 "Bot"
4. 点击 "Add Bot"
5. 复制 Bot Token

### 2. 邀请Bot到服务器

1. 左侧导航选择 "OAuth2" → "URL Generator"
2. Scopes选择：`bot`
3. Bot Permissions选择：
   - View Channels
   - Send Messages
   - Embed Links
4. 复制生成的URL，在浏览器中打开并选择服务器

### 3. 获取频道ID

1. Discord设置 → 高级 → 开启"开发者模式"
2. 右键点击要接收通知的频道 → 复制ID

### 4. 配置环境变量

```env
DISCORD_BOT_TOKEN=your-bot-token-here
DISCORD_CHANNEL_ID=your-channel-id-here
```

## 微信集成

### 方式1: 企业微信群机器人

1. 在企业微信群聊中，点击右上角 → 添加群机器人
2. 设置机器人名称和头像
3. 复制 Webhook URL
4. 在代码中配置：

```python
from notifiers.wechat_notifier import WeChatNotifier

wechat_notifier = WeChatNotifier(webhook_url="your-webhook-url")
```

### 方式2: 微信公众号模板消息

1. 注册微信公众号（需要认证）
2. 获取 AppID 和 AppSecret
3. 创建模板消息模板
4. 配置环境变量：

```env
WECHAT_APP_ID=your-app-id
WECHAT_APP_SECRET=your-app-secret
WECHAT_TEMPLATE_ID=your-template-id
```

## Docker部署

### 使用Docker Compose

```bash
# 1. 配置环境变量
cp .env.example .env
# 编辑 .env 填入配置

# 2. 启动服务
docker-compose up -d

# 3. 查看日志
docker-compose logs -f app

# 4. 停止服务
docker-compose down
```

### 使用Docker单独运行

```bash
# 构建镜像
docker build -t tft-tracker .

# 运行容器
docker run -d \
  --name tft-tracker \
  --env-file .env \
  -v $(pwd)/logs:/app/logs \
  -v $(pwd)/tft_tracker.db:/app/tft_tracker.db \
  tft-tracker
```

## 使用教程

### 添加追踪选手

运行程序后选择选项2：

```
请输入召唤师游戏名称: doublelift
请输入标签(如NA1, KR等): NA1
```

### 查看选手历史

运行程序后选择选项3：

```
请输入召唤师游戏名称: doublelift
请输入标签: NA1
```

### 启动追踪服务

运行程序后选择选项1，程序将：
1. 立即执行一次追踪
2. 按配置的间隔持续追踪
3. 检测到变化时自动推送通知

## 通知示例

### 段位晋升通知

```
🎉 晋升 - doublelift#NA1
DIAMOND I → MASTER
LP: 0
```

### LP大幅波动通知

```
📈 LP大幅增加 - doublelift#NA1
段位: MASTER
LP变动: +75 (425 → 500)
```

## 常见问题

### Q1: API密钥失效怎么办？

A: 开发版密钥24小时过期，需要：
1. 前往 Developer Portal 重新生成
2. 更新 `.env` 文件中的 `RIOT_API_KEY`
3. 重启程序

### Q2: 为什么没有收到Discord通知？

A: 检查：
1. Bot Token 和 Channel ID 是否正确
2. Bot是否已加入服务器
3. Bot是否有发送消息权限
4. 查看日志中的错误信息

### Q3: Redis连接失败怎么办？

A: Redis是可选的：
- 如果安装了Redis，确保服务正在运行：`redis-server`
- 如果不需要Redis，程序会自动降级使用内存缓存

### Q4: 如何追踪其他赛区的选手？

A: 修改 `.env` 中的配置：

```env
# 例如追踪韩服选手
RIOT_API_REGION=kr
RIOT_API_ROUTING=asia
```

### Q5: 速率限制怎么办？

A: 程序内置速率限制器，会自动控制请求频率。如果仍然遇到429错误：
1. 增加 `POLLING_INTERVAL` 值（降低轮询频率）
2. 减少追踪的选手数量
3. 考虑申请生产版API密钥

## 扩展功能

### 批量导入选手

创建 `players.txt` 文件：

```
doublelift#NA1
faker#KR
uzi#CN1
```

然后添加批量导入脚本（参考 `scripts/import_players.py`）

### 数据可视化

查看 `docs/visualization.md` 了解如何集成Chart.js展示LP曲线

### 第三方数据集成

查看 `docs/tactics_tools_integration.md` 了解如何对接Tactics.tools API

## 支持

如有问题，请查看：
- GitHub Issues
- 项目Wiki
- Discord社区
