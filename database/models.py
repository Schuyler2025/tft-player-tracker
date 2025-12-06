"""
数据库模型定义
"""
from datetime import datetime
from sqlalchemy import create_engine, Column, Integer, String, DateTime, Boolean, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship

from config import settings

Base = declarative_base()


class Player(Base):
    """玩家基础信息表"""
    __tablename__ = 'players'

    id = Column(Integer, primary_key=True, autoincrement=True)
    puuid = Column(String(100), unique=True, nullable=False, index=True)
    summoner_name = Column(String(100), nullable=False)
    region = Column(String(20), default='na1')
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # 关联关系
    rank_records = relationship('RankRecord', back_populates='player', cascade='all, delete-orphan')


class RankRecord(Base):
    """排位数据记录表"""
    __tablename__ = 'rank_records'

    id = Column(Integer, primary_key=True, autoincrement=True)
    player_id = Column(Integer, ForeignKey('players.id'), nullable=False, index=True)

    # 排位数据
    tier = Column(String(20))  # IRON, BRONZE, SILVER, GOLD, PLATINUM, DIAMOND, MASTER, GRANDMASTER, CHALLENGER
    rank = Column(String(5))   # I, II, III, IV (仅适用于钻石及以下)
    league_points = Column(Integer, default=0)
    wins = Column(Integer, default=0)
    losses = Column(Integer, default=0)

    # 状态标识
    hot_streak = Column(Boolean, default=False)
    veteran = Column(Boolean, default=False)
    fresh_blood = Column(Boolean, default=False)

    # 时间戳
    recorded_at = Column(DateTime, default=datetime.utcnow, index=True)

    # 关联关系
    player = relationship('Player', back_populates='rank_records')


class Notification(Base):
    """通知记录表"""
    __tablename__ = 'notifications'

    id = Column(Integer, primary_key=True, autoincrement=True)
    player_id = Column(Integer, ForeignKey('players.id'), nullable=False, index=True)

    # 通知类型：rank_change, lp_threshold, promotion, demotion
    notification_type = Column(String(50), nullable=False)

    # 通知内容
    title = Column(String(200))
    message = Column(String(1000))

    # 变动数据
    old_tier = Column(String(20))
    new_tier = Column(String(20))
    old_rank = Column(String(5))
    new_rank = Column(String(5))
    old_lp = Column(Integer)
    new_lp = Column(Integer)
    lp_change = Column(Integer)

    # 推送状态
    sent = Column(Boolean, default=False)
    sent_at = Column(DateTime)

    # 时间戳
    created_at = Column(DateTime, default=datetime.utcnow, index=True)


# 数据库引擎和会话
engine = create_engine(settings.database_url, echo=False)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def init_db():
    """初始化数据库"""
    Base.metadata.create_all(bind=engine)


def get_db():
    """获取数据库会话"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
