"""
配置管理模块
"""
import os
from typing import Optional
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """应用配置"""
    
    # Riot API配置
    riot_api_key: str = Field(..., env='RIOT_API_KEY')
    riot_api_region: str = Field(default='na1', env='RIOT_API_REGION')
    riot_api_routing: str = Field(default='americas', env='RIOT_API_ROUTING')
    riot_api_rate_limit_per_second: int = Field(default=20, env='RIOT_API_RATE_LIMIT_PER_SECOND')
    riot_api_rate_limit_per_2min: int = Field(default=100, env='RIOT_API_RATE_LIMIT_PER_2MIN')
    
    # 轮询配置
    polling_interval: int = Field(default=120, env='POLLING_INTERVAL')
    
    # Redis配置
    redis_host: str = Field(default='localhost', env='REDIS_HOST')
    redis_port: int = Field(default=6379, env='REDIS_PORT')
    redis_db: int = Field(default=0, env='REDIS_DB')
    redis_password: Optional[str] = Field(default=None, env='REDIS_PASSWORD')
    
    # 数据库配置
    database_url: str = Field(default='sqlite:///./tft_tracker.db', env='DATABASE_URL')
    
    # Discord配置
    discord_bot_token: Optional[str] = Field(default=None, env='DISCORD_BOT_TOKEN')
    discord_channel_id: Optional[str] = Field(default=None, env='DISCORD_CHANNEL_ID')
    
    # 微信配置
    wechat_app_id: Optional[str] = Field(default=None, env='WECHAT_APP_ID')
    wechat_app_secret: Optional[str] = Field(default=None, env='WECHAT_APP_SECRET')
    wechat_template_id: Optional[str] = Field(default=None, env='WECHAT_TEMPLATE_ID')
    
    # 通知规则
    lp_change_threshold: int = Field(default=50, env='LP_CHANGE_THRESHOLD')
    lp_daily_change_threshold: int = Field(default=100, env='LP_DAILY_CHANGE_THRESHOLD')
    enable_rank_change_notification: bool = Field(default=True, env='ENABLE_RANK_CHANGE_NOTIFICATION')
    enable_lp_threshold_notification: bool = Field(default=True, env='ENABLE_LP_THRESHOLD_NOTIFICATION')
    
    # 日志配置
    log_level: str = Field(default='INFO', env='LOG_LEVEL')
    log_file: str = Field(default='logs/tft_tracker.log', env='LOG_FILE')
    
    model_config = SettingsConfigDict(env_file='.env', env_file_encoding='utf-8')


# 全局配置实例
settings = Settings()
