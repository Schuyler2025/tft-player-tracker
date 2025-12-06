"""
选手追踪引擎
负责定时获取选手数据、比对变化、触发通知
"""
from typing import List, Dict, Any
from datetime import datetime
from loguru import logger

from core.riot_api import RiotAPIClient
from core.rules import RuleEngine
from database.models import SessionLocal, Player, RankRecord, Notification, init_db
from database.cache import cache


class PlayerTracker:
    """选手追踪器"""
    
    def __init__(self):
        self.api_client = RiotAPIClient()
        self.rule_engine = RuleEngine()
    
    def add_player(self, game_name: str, tag_line: str) -> bool:
        """添加要追踪的选手"""
        init_db()
        db = SessionLocal()
        
        try:
            # 获取选手数据
            rank_data = self.api_client.get_summoner_rank_data(game_name, tag_line)
            
            if not rank_data:
                logger.error(f"Failed to get rank data for {game_name}#{tag_line}")
                return False
            
            # 检查是否已存在
            existing_player = db.query(Player).filter(
                Player.puuid == rank_data['puuid']
            ).first()
            
            if existing_player:
                logger.info(f"Player already tracked: {game_name}#{tag_line}")
                return True
            
            # 创建玩家记录
            player = Player(
                puuid=rank_data['puuid'],
                summoner_name=rank_data['summoner_name']
            )
            db.add(player)
            db.flush()
            
            # 创建初始Rank记录
            rank_record = RankRecord(
                player_id=player.id,
                tier=rank_data['tier'],
                rank=rank_data['rank'],
                league_points=rank_data['league_points'],
                wins=rank_data['wins'],
                losses=rank_data['losses'],
                hot_streak=rank_data['hot_streak'],
                veteran=rank_data['veteran'],
                fresh_blood=rank_data['fresh_blood']
            )
            db.add(rank_record)
            
            # 保存到缓存
            cache.set_last_rank(rank_data['puuid'], rank_data)
            
            db.commit()
            logger.info(f"Successfully added player: {game_name}#{tag_line}")
            return True
            
        except Exception as e:
            db.rollback()
            logger.error(f"Failed to add player: {str(e)}")
            return False
        finally:
            db.close()
    
    def update_player_rank(self, player: Player) -> List[Dict[str, Any]]:
        """更新单个选手的Rank数据并检查通知规则"""
        db = SessionLocal()
        notifications = []
        
        try:
            # 从缓存获取上次数据
            last_rank = cache.get_last_rank(player.puuid)
            
            # 从API获取最新数据
            game_name, tag_line = player.summoner_name.split('#')
            new_rank = self.api_client.get_summoner_rank_data(game_name, tag_line)
            
            if not new_rank:
                logger.warning(f"Failed to fetch rank data for {player.summoner_name}")
                return notifications
            
            # 评估规则
            if last_rank:
                notifications = self.rule_engine.evaluate(last_rank, new_rank)
            
            # 保存Rank记录
            rank_record = RankRecord(
                player_id=player.id,
                tier=new_rank['tier'],
                rank=new_rank['rank'],
                league_points=new_rank['league_points'],
                wins=new_rank['wins'],
                losses=new_rank['losses'],
                hot_streak=new_rank['hot_streak'],
                veteran=new_rank['veteran'],
                fresh_blood=new_rank['fresh_blood']
            )
            db.add(rank_record)
            
            # 保存通知记录
            for notif in notifications:
                notification = Notification(
                    player_id=player.id,
                    notification_type=notif['type'],
                    title=notif['title'],
                    message=notif['message'],
                    old_tier=notif['old_data'].get('tier'),
                    new_tier=notif['new_data'].get('tier'),
                    old_rank=notif['old_data'].get('rank'),
                    new_rank=notif['new_data'].get('rank'),
                    old_lp=notif['old_data'].get('league_points'),
                    new_lp=notif['new_data'].get('league_points'),
                    lp_change=notif['new_data'].get('league_points', 0) - notif['old_data'].get('league_points', 0)
                )
                db.add(notification)
            
            # 更新缓存
            cache.set_last_rank(player.puuid, new_rank)
            
            # 计算LP变动并更新每日累计
            if last_rank:
                lp_change = new_rank['league_points'] - last_rank['league_points']
                cache.add_daily_lp_change(player.puuid, lp_change)
            
            db.commit()
            
            if notifications:
                logger.info(f"Generated {len(notifications)} notifications for {player.summoner_name}")
            
        except Exception as e:
            db.rollback()
            logger.error(f"Error updating player rank: {str(e)}")
        finally:
            db.close()
        
        return notifications
    
    def track_all_players(self) -> Dict[str, List[Dict[str, Any]]]:
        """追踪所有已添加的选手"""
        db = SessionLocal()
        all_notifications = {}
        
        try:
            players = db.query(Player).all()
            logger.info(f"Tracking {len(players)} players...")
            
            for player in players:
                notifications = self.update_player_rank(player)
                if notifications:
                    all_notifications[player.summoner_name] = notifications
            
            logger.info(f"Tracking complete. Generated notifications for {len(all_notifications)} players")
            
        except Exception as e:
            logger.error(f"Error tracking players: {str(e)}")
        finally:
            db.close()
        
        return all_notifications
    
    def get_player_history(self, game_name: str, tag_line: str, limit: int = 10) -> List[Dict[str, Any]]:
        """获取选手历史记录"""
        db = SessionLocal()
        
        try:
            summoner_name = f"{game_name}#{tag_line}"
            player = db.query(Player).filter(Player.summoner_name == summoner_name).first()
            
            if not player:
                logger.warning(f"Player not found: {summoner_name}")
                return []
            
            records = db.query(RankRecord).filter(
                RankRecord.player_id == player.id
            ).order_by(RankRecord.recorded_at.desc()).limit(limit).all()
            
            return [{
                'tier': r.tier,
                'rank': r.rank,
                'league_points': r.league_points,
                'wins': r.wins,
                'losses': r.losses,
                'recorded_at': r.recorded_at.isoformat()
            } for r in records]
            
        except Exception as e:
            logger.error(f"Error fetching player history: {str(e)}")
            return []
        finally:
            db.close()
