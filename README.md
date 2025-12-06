# TFT Player Tracker - 云顶之弈选手Rank追踪系统

## 核心功能

- ✅ **实时追踪**：分钟级同步选手Rank数据（段位、LP、胜率）
- ✅ **智能推送**：LP波动±50、段位变动自动通知
- ✅ **多渠道支持**：Discord、微信推送
- ✅ **合规设计**：基于Riot官方API

## 快速开始

### 1. 安装依赖

```bash
pip install -r requirements.txt
```

### 2. 配置环境变量

```bash
cp .env.example .env
# 编辑 .env 填入你的API密钥
```

### 3. 运行程序

```bash
python main.py
```

## 架构说明

```
├── config/          # 配置管理
├── core/            # 核心业务逻辑
│   ├── riot_api.py  # Riot API封装
│   ├── tracker.py   # 追踪引擎
│   └── rules.py     # 推送规则引擎
├── database/        # 数据层
│   ├── models.py    # 数据模型
│   └── cache.py     # Redis缓存
├── notifiers/       # 推送层
│   ├── discord.py   # Discord推送
│   └── wechat.py    # 微信推送
└── utils/           # 工具函数
```

## 推送规则

支持以下触发条件：

1. **段位变动**：钻石→大师、大师1→宗师等
2. **LP波动**：单局增减≥50、单日累计≥100
3. **关键节点**：晋级赛开启/结束

## License

MIT
