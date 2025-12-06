"""
推送规则引擎
根据配置的规则判断是否触发通知
"""
from typing import Dict, Any, List, Optional
from datetime import datetime
from loguru import logger

from config import settings
from database.cache import cache


class NotificationRule:
    """通知规则基类"""
    
    def __init__(self, name: str):
        self.name = name
    
    def should_notify(self, old_data: Dict[str, Any], new_data: Dict[str, Any]) -> bool:
        """判断是否应该触发通知"""
        raise NotImplementedError
    
    def generate_message(self, old_data: Dict[str, Any], new_data: Dict[str, Any]) -> Dict[str, str]:
        """生成通知消息"""
        raise NotImplementedError


class RankChangeRule(NotificationRule):
    """段位变动规则"""
    
    TIER_ORDER = ['IRON', 'BRONZE', 'SILVER', 'GOLD', 'PLATINUM', 'DIAMOND', 'MASTER', 'GRANDMASTER', 'CHALLENGER']
    RANK_ORDER = ['IV', 'III', 'II', 'I']
    
    def __init__(self):
        super().__init__('rank_change')
    
    def _get_tier_index(self, tier: str) -> int:
        """获取段位等级索引"""
        return self.TIER_ORDER.index(tier) if tier in self.TIER_ORDER else -1
    
    def _get_rank_index(self, rank: str) -> int:
        """获取段位小级别索引"""
        return self.RANK_ORDER.index(rank) if rank in self.RANK_ORDER else -1
    
    def should_notify(self, old_data: Dict[str, Any], new_data: Dict[str, Any]) -> bool:
        if not settings.enable_rank_change_notification:
            return False
        
        old_tier = old_data.get('tier')
        new_tier = new_data.get('tier')
        old_rank = old_data.get('rank')
        new_rank = new_data.get('rank')
        
        # 段位大变动（跨段位）
        if old_tier != new_tier:
            return True
        
        # 段位小变动（同段位内的级别变化，如钻石IV到钻石III）
        if old_rank != new_rank and old_tier in ['IRON', 'BRONZE', 'SILVER', 'GOLD', 'PLATINUM', 'DIAMOND']:
            return True
        
        return False
    
    def generate_message(self, old_data: Dict[str, Any], new_data: Dict[str, Any]) -> Dict[str, str]:
        old_tier = old_data.get('tier', '')
        new_tier = new_data.get('tier', '')
        old_rank = old_data.get('rank', '')
        new_rank = new_data.get('rank', '')
        summoner_name = new_data.get('summoner_name', 'Unknown')
        
        # 判断是晋升还是降级
        old_tier_idx = self._get_tier_index(old_tier)
        new_tier_idx = self._get_tier_index(new_tier)
        
        if new_tier_idx > old_tier_idx:
            direction = "🎉 晋升"
        elif new_tier_idx < old_tier_idx:
            direction = "⚠️ 降级"
        else:
            # 同段位内变化
            old_rank_idx = self._get_rank_index(old_rank)
            new_rank_idx = self._get_rank_index(new_rank)
            direction = "🎉 晋升" if new_rank_idx > old_rank_idx else "⚠️ 降级"
        
        old_rank_str = f"{old_tier} {old_rank}" if old_rank else old_tier
        new_rank_str = f"{new_tier} {new_rank}" if new_rank else new_tier
        
        return {
            'title': f'{direction} - {summoner_name}',
            'message': f'{old_rank_str} → {new_rank_str}\nLP: {new_data.get("league_points", 0)}'
        }


class LPThresholdRule(NotificationRule):
    """LP波动阈值规则"""
    
    def __init__(self):
        super().__init__('lp_threshold')
    
    def should_notify(self, old_data: Dict[str, Any], new_data: Dict[str, Any]) -> bool:
        if not settings.enable_lp_threshold_notification:
            return False
        
        old_lp = old_data.get('league_points', 0)
        new_lp = new_data.get('league_points', 0)
        lp_change = abs(new_lp - old_lp)
        
        # 单局LP波动超过阈值
        return lp_change >= settings.lp_change_threshold
    
    def generate_message(self, old_data: Dict[str, Any], new_data: Dict[str, Any]) -> Dict[str, str]:
        old_lp = old_data.get('league_points', 0)
        new_lp = new_data.get('league_points', 0)
        lp_change = new_lp - old_lp
        summoner_name = new_data.get('summoner_name', 'Unknown')
        
        emoji = "📈" if lp_change > 0 else "📉"
        direction = "增加" if lp_change > 0 else "减少"
        
        tier = new_data.get('tier', '')
        rank = new_data.get('rank', '')
        rank_str = f"{tier} {rank}" if rank else tier
        
        return {
            'title': f'{emoji} LP大幅{direction} - {summoner_name}',
            'message': f'段位: {rank_str}\nLP变动: {lp_change:+d} ({old_lp} → {new_lp})'
        }


class DailyLPThresholdRule(NotificationRule):
    """每日LP累计变动规则"""
    
    def __init__(self):
        super().__init__('daily_lp_threshold')
    
    def should_notify(self, old_data: Dict[str, Any], new_data: Dict[str, Any]) -> bool:
        puuid = new_data.get('puuid')
        if not puuid:
            return False
        
        daily_change = cache.get_daily_lp_change(puuid)
        
        # 每日累计变动超过阈值
        return abs(daily_change) >= settings.lp_daily_change_threshold
    
    def generate_message(self, old_data: Dict[str, Any], new_data: Dict[str, Any]) -> Dict[str, str]:
        puuid = new_data.get('puuid')
        summoner_name = new_data.get('summoner_name', 'Unknown')
        daily_change = cache.get_daily_lp_change(puuid)
        
        emoji = "🔥" if daily_change > 0 else "❄️"
        status = "连胜中" if daily_change > 0 else "连败中"
        
        return {
            'title': f'{emoji} 今日{status} - {summoner_name}',
            'message': f'今日LP累计变动: {daily_change:+d}'
        }


class RuleEngine:
    """规则引擎"""
    
    def __init__(self):
        self.rules: List[NotificationRule] = [
            RankChangeRule(),
            LPThresholdRule(),
            # DailyLPThresholdRule(),  # 可选：需要配合缓存使用
        ]
    
    def evaluate(self, old_data: Optional[Dict[str, Any]], new_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """评估所有规则，返回应该发送的通知列表"""
        if not old_data:
            logger.debug("No old data, skipping rule evaluation")
            return []
        
        notifications = []
        
        for rule in self.rules:
            try:
                if rule.should_notify(old_data, new_data):
                    message = rule.generate_message(old_data, new_data)
                    notifications.append({
                        'type': rule.name,
                        'title': message['title'],
                        'message': message['message'],
                        'old_data': old_data,
                        'new_data': new_data
                    })
                    logger.info(f"Rule triggered: {rule.name} - {message['title']}")
            except Exception as e:
                logger.error(f"Error evaluating rule {rule.name}: {str(e)}")
        
        return notifications
