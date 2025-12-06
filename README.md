# TFT Player Tracker 🎮

[![Python](https://img.shields.io/badge/Python-3.10+-blue.svg)](https://www.python.org/)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Docker](https://img.shields.io/badge/Docker-Ready-blue.svg)](docker-compose.yml)

一个功能丰富的云顶之弈（Teamfight Tactics）选手Rank追踪系统，支持实时监控选手段位变化并通过多种渠道推送通知。

## ✨ 核心特性

- **🔍 实时追踪** - 分钟级同步选手Rank数据（段位、LP、胜率）
- **📊 智能通知** - 基于规则的自动推送系统
- **🌐 多平台支持** - Discord、微信等多渠道通知
- **⚡ 高性能** - 异步架构，支持高并发处理
- **🐳 容器化** - 完整的Docker支持，一键部署
- **🔒 合规设计** - 严格遵守Riot API限制和速率控制

## 🚀 快速开始

### 环境要求

- Python 3.10+
- Redis (可选，推荐用于生产环境)

### 安装步骤

1. **克隆项目**
   
   ```bash
   git clone https://github.com/your-username/tft-player-tracker.git
   cd tft-player-tracker
   ```

2. **安装依赖**
   
   ```bash
   pip install -r requirements.txt
   ```

3. **配置环境变量**
   
   ```bash
   cp .env.example .env
   # 编辑 .env 文件，填入你的Riot API密钥
   ```

4. **运行程序**
   
   ```bash
   python main.py
   ```

### Docker部署（推荐）

```bash
# 一键启动（包含Redis）
docker-compose up -d

# 查看日志
docker-compose logs -f app
```

## 📋 功能列表

### 追踪功能

- ✅ 实时监控选手段位变化
- ✅ LP波动检测（可配置阈值）
- ✅ 胜率统计和历史记录
- ✅ 多赛区支持（全球所有Riot服务器）

### 通知规则

- 🎯 **段位变动** - 钻石→大师、大师→宗师等
- 📈 **LP大幅波动** - 单局增减≥50LP
- 📊 **每日累计变动** - 可选功能

### 通知渠道

- 💬 **Discord** - 精美的Embed消息格式
- 📱 **微信** - 企业微信群机器人/公众号模板消息

## ⚙️ 配置说明

### 必需配置

```env
RIOT_API_KEY=your_riot_api_key
RIOT_API_REGION=na1
```

### 可选配置

```env
# Discord通知
DISCORD_BOT_TOKEN=your_bot_token
DISCORD_CHANNEL_ID=your_channel_id

# 通知规则
LP_CHANGE_THRESHOLD=50
POLLING_INTERVAL=120

# Redis缓存
REDIS_HOST=localhost
REDIS_PORT=6379
```

## 🎮 使用方法

### 交互式操作

运行 `python main.py` 后选择：

- **1. 启动追踪服务** - 开始实时监控
- **2. 添加追踪选手** - 交互式添加新选手
- **3. 查看选手历史** - 查看历史Rank记录
- **4. 退出程序**## 🤝 贡献指南

欢迎提交Issue和Pull Request！请确保：

1. 代码符合PEP8规范
2. 添加适当的测试用例
3. 更新相关文档

## 📄 许可证

本项目采用 MIT 许可证 - 查看 [LICENSE](LICENSE) 文件了解详情。

## 🙏 致谢

- [Riot Games API](https://developer.riotgames.com/) - 提供官方数据接口
- [Discord.py](https://github.com/Rapptz/discord.py) - Discord Bot框架
- [SQLAlchemy](https://www.sqlalchemy.org/) - 数据库ORM
