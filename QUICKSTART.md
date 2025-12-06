# 快速开始指南

## 5分钟快速部署

### 步骤1: 获取Riot API密钥

1. 访问 https://developer.riotgames.com/
2. 登录并复制你的 Development API Key

### 步骤2: 配置环境

```bash
# 创建配置文件
cp .env.example .env

# 编辑 .env 文件，至少填入以下配置：
# RIOT_API_KEY=你的API密钥
# RIOT_API_REGION=na1  (或其他赛区)
```

### 步骤3: 安装依赖

```bash
pip install -r requirements.txt
```

### 步骤4: 启动Redis（可选）

```bash
# Windows (使用 Memurai 或 WSL)
# Linux/Mac
redis-server
```

没有Redis也可以运行，程序会使用内存缓存。

### 步骤5: 运行程序

```bash
python main.py
```

按提示操作：
- 选择 `2` 添加要追踪的选手
- 选择 `1` 启动追踪服务

## Docker快速部署

```bash
# 1. 配置 .env
cp .env.example .env
# 编辑 .env 填入 RIOT_API_KEY

# 2. 启动
docker-compose up -d

# 3. 查看日志
docker-compose logs -f app
```

## 配置Discord通知

1. 创建Discord Bot: https://discord.com/developers/applications
2. 复制Bot Token
3. 邀请Bot到服务器
4. 获取频道ID（需开启开发者模式）
5. 在 `.env` 中配置：
   ```
   DISCORD_BOT_TOKEN=你的Bot Token
   DISCORD_CHANNEL_ID=你的频道ID
   ```

## 批量导入选手

```bash
# 1. 创建选手列表
cp players.txt.example players.txt
# 编辑 players.txt

# 2. 批量导入
python scripts/import_players.py players.txt
```

## 常用命令

```bash
# 运行主程序
python main.py

# 批量导入选手
python scripts/import_players.py players.txt

# 使用Docker
docker-compose up -d          # 启动
docker-compose logs -f app    # 查看日志
docker-compose down           # 停止
docker-compose restart app    # 重启
```

## 赛区配置

| 赛区 | RIOT_API_REGION | RIOT_API_ROUTING |
|------|-----------------|------------------|
| 北美 | na1 | americas |
| 欧洲西 | euw1 | europe |
| 欧洲北东 | eun1 | europe |
| 韩国 | kr | asia |
| 日本 | jp1 | asia |
| 巴西 | br1 | americas |
| 拉丁美洲北 | la1 | americas |
| 拉丁美洲南 | la2 | americas |
| 大洋洲 | oc1 | sea |
| 土耳其 | tr1 | europe |
| 俄罗斯 | ru | europe |

## 下一步

- 查看 [USAGE.md](USAGE.md) 了解详细使用说明
- 查看 [README.md](README.md) 了解架构设计
- 遇到问题请查看日志文件 `logs/tft_tracker.log`
