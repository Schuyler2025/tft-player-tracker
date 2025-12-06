"""
Redis缓存管理
"""
import json
from typing import Optional, Dict, Any
import redis
from loguru import logger

from config import settings


class RedisCache:
    """Redis缓存管理器"""
    
    def __init__(self):
        self.redis_client = redis.Redis(
            host=settings.redis_host,
            port=settings.redis_port,
            db=settings.redis_db,
            password=settings.redis_password,
            decode_responses=True
        )
        self._test_connection()
    
    def _test_connection(self):
        """测试Redis连接"""
        try:
            self.redis_client.ping()
            logger.info("Redis connection established")
        except redis.ConnectionError as e:
            logger.error(f"Redis connection failed: {str(e)}")
            logger.warning("Running without Redis cache")
            self.redis_client = None
    
    def get_player_data(self, puuid: str) -> Optional[Dict[str, Any]]:
        """获取玩家缓存数据"""
        if not self.redis_client:
            return None
        
        try:
            key = f"player:{puuid}"
            data = self.redis_client.get(key)
            return json.loads(data) if data else None
        except Exception as e:
            logger.error(f"Failed to get player data from cache: {str(e)}")
            return None
    
    def set_player_data(self, puuid: str, data: Dict[str, Any], expire: int = 300):
        """设置玩家缓存数据"""
        if not self.redis_client:
            return
        
        try:
            key = f"player:{puuid}"
            self.redis_client.setex(key, expire, json.dumps(data))
        except Exception as e:
            logger.error(f"Failed to set player data in cache: {str(e)}")
    
    def get_last_rank(self, puuid: str) -> Optional[Dict[str, Any]]:
        """获取上次记录的Rank数据"""
        if not self.redis_client:
            return None
        
        try:
            key = f"last_rank:{puuid}"
            data = self.redis_client.get(key)
            return json.loads(data) if data else None
        except Exception as e:
            logger.error(f"Failed to get last rank from cache: {str(e)}")
            return None
    
    def set_last_rank(self, puuid: str, rank_data: Dict[str, Any]):
        """设置上次记录的Rank数据（不过期）"""
        if not self.redis_client:
            return
        
        try:
            key = f"last_rank:{puuid}"
            self.redis_client.set(key, json.dumps(rank_data))
        except Exception as e:
            logger.error(f"Failed to set last rank in cache: {str(e)}")
    
    def increment_api_call_count(self, window: str = "second") -> int:
        """增加API调用计数"""
        if not self.redis_client:
            return 0
        
        try:
            key = f"api_calls:{window}"
            expire = 1 if window == "second" else 120
            pipe = self.redis_client.pipeline()
            pipe.incr(key)
            pipe.expire(key, expire)
            result = pipe.execute()
            return result[0]
        except Exception as e:
            logger.error(f"Failed to increment API call count: {str(e)}")
            return 0
    
    def get_daily_lp_change(self, puuid: str) -> int:
        """获取今日LP累计变动"""
        if not self.redis_client:
            return 0
        
        try:
            key = f"daily_lp:{puuid}"
            value = self.redis_client.get(key)
            return int(value) if value else 0
        except Exception as e:
            logger.error(f"Failed to get daily LP change: {str(e)}")
            return 0
    
    def add_daily_lp_change(self, puuid: str, lp_change: int):
        """添加今日LP变动（自动在24小时后过期）"""
        if not self.redis_client:
            return
        
        try:
            key = f"daily_lp:{puuid}"
            pipe = self.redis_client.pipeline()
            pipe.incrby(key, lp_change)
            pipe.expire(key, 86400)  # 24小时过期
            pipe.execute()
        except Exception as e:
            logger.error(f"Failed to add daily LP change: {str(e)}")


# 全局缓存实例
cache = RedisCache()
