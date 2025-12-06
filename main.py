"""
TFT Player Tracker - 主程序入口
"""
import asyncio
import sys
from loguru import logger
from apscheduler.schedulers.asyncio import AsyncIOScheduler

from config import settings
from database.models import init_db
from core.tracker import PlayerTracker
from notifiers.discord_notifier import discord_notifier
from utils.helpers import setup_logger


class TFTTrackerApp:
    """TFT追踪应用"""
    
    def __init__(self):
        self.tracker = PlayerTracker()
        self.scheduler = AsyncIOScheduler()
        self.running = False
    
    async def send_notifications(self, notifications_dict: dict):
        """发送所有通知"""
        for summoner_name, notifications in notifications_dict.items():
            for notification in notifications:
                # 发送Discord通知
                if discord_notifier.enabled:
                    await discord_notifier.send_notification(notification)
                
                # 可以在这里添加其他通知渠道
                # if wechat_notifier.enabled:
                #     wechat_notifier.send_notification(notification)
    
    async def track_job(self):
        """定时追踪任务"""
        logger.info("Starting tracking job...")
        
        try:
            # 追踪所有选手
            notifications = self.tracker.track_all_players()
            
            # 发送通知
            if notifications:
                await self.send_notifications(notifications)
            
            logger.info("Tracking job completed")
            
        except Exception as e:
            logger.error(f"Error in tracking job: {str(e)}")
    
    def add_player_interactive(self):
        """交互式添加选手"""
        print("\n=== 添加追踪选手 ===")
        game_name = input("请输入召唤师游戏名称: ").strip()
        tag_line = input("请输入标签(如NA1, KR等): ").strip()
        
        if not game_name or not tag_line:
            print("❌ 游戏名称和标签不能为空")
            return
        
        print(f"\n正在添加 {game_name}#{tag_line}...")
        success = self.tracker.add_player(game_name, tag_line)
        
        if success:
            print(f"✅ 成功添加选手: {game_name}#{tag_line}")
        else:
            print(f"❌ 添加选手失败，请检查名称是否正确")
    
    def show_player_history(self):
        """显示选手历史"""
        print("\n=== 查看选手历史 ===")
        game_name = input("请输入召唤师游戏名称: ").strip()
        tag_line = input("请输入标签: ").strip()
        
        if not game_name or not tag_line:
            print("❌ 游戏名称和标签不能为空")
            return
        
        history = self.tracker.get_player_history(game_name, tag_line, limit=10)
        
        if not history:
            print(f"❌ 未找到选手 {game_name}#{tag_line} 的历史记录")
            return
        
        print(f"\n{game_name}#{tag_line} 最近10条记录:\n")
        print(f"{'时间':<20} {'段位':<15} {'LP':<6} {'胜场':<6} {'败场':<6}")
        print("-" * 65)
        
        for record in history:
            tier = record['tier']
            rank = record.get('rank', '')
            rank_str = f"{tier} {rank}" if rank else tier
            
            print(f"{record['recorded_at'][:19]:<20} {rank_str:<15} {record['league_points']:<6} {record['wins']:<6} {record['losses']:<6}")
    
    async def start(self):
        """启动应用"""
        logger.info("Starting TFT Player Tracker...")
        
        # 初始化数据库
        init_db()
        logger.info("Database initialized")
        
        # 启动Discord Bot (如果已配置)
        if discord_notifier.enabled:
            asyncio.create_task(discord_notifier.start())
            await asyncio.sleep(2)  # 等待Bot连接
        
        # 配置定时任务
        self.scheduler.add_job(
            self.track_job,
            'interval',
            seconds=settings.polling_interval,
            id='track_players',
            replace_existing=True
        )
        
        # 启动调度器
        self.scheduler.start()
        logger.info(f"Scheduler started (interval: {settings.polling_interval}s)")
        
        self.running = True
        
        # 立即执行一次追踪
        await self.track_job()
        
        # 保持运行
        try:
            while self.running:
                await asyncio.sleep(1)
        except KeyboardInterrupt:
            logger.info("Received shutdown signal")
            await self.stop()
    
    async def stop(self):
        """停止应用"""
        logger.info("Stopping TFT Player Tracker...")
        
        self.running = False
        
        if self.scheduler.running:
            self.scheduler.shutdown()
        
        if discord_notifier.enabled:
            await discord_notifier.close()
        
        logger.info("Application stopped")


def show_menu():
    """显示菜单"""
    print("\n" + "="*50)
    print("TFT Player Tracker - 云顶之弈选手追踪系统")
    print("="*50)
    print("1. 启动追踪服务")
    print("2. 添加追踪选手")
    print("3. 查看选手历史")
    print("4. 退出")
    print("="*50)


async def main():
    """主函数"""
    # 设置日志
    setup_logger()
    
    app = TFTTrackerApp()
    
    while True:
        show_menu()
        choice = input("请选择操作 (1-4): ").strip()
        
        if choice == '1':
            print("\n启动追踪服务...")
            print(f"轮询间隔: {settings.polling_interval}秒")
            print("按 Ctrl+C 停止服务\n")
            await app.start()
            break
            
        elif choice == '2':
            app.add_player_interactive()
            
        elif choice == '3':
            app.show_player_history()
            
        elif choice == '4':
            print("\n再见！")
            sys.exit(0)
            
        else:
            print("❌ 无效选择，请重试")


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Application terminated by user")
    except Exception as e:
        logger.error(f"Fatal error: {str(e)}")
        sys.exit(1)
