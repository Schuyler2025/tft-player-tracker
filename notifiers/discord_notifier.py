"""
Discord推送通知
"""
from typing import Dict, Any, Optional
import discord
from discord.ext import commands
from loguru import logger

from config import settings


class DiscordNotifier:
    """Discord通知器"""

    def __init__(self):
        self.enabled = bool(settings.discord_bot_token and settings.discord_channel_id)
        self.bot = None
        self.channel = None

        if self.enabled:
            intents = discord.Intents.default()
            intents.message_content = True
            self.bot = commands.Bot(command_prefix='!', intents=intents, proxy='http://127.0.0.1:7897')
            self._setup_events()

    def _setup_events(self):
        """设置Discord事件监听"""

        @self.bot.event
        async def on_ready():
            logger.info(f'Discord bot logged in as {self.bot.user}')
            try:
                self.channel = await self.bot.fetch_channel(int(settings.discord_channel_id))
                logger.info(f'Discord channel connected: {self.channel.name}')
            except Exception as e:
                logger.error(f'Failed to connect to Discord channel: {str(e)}')
                self.enabled = False

    async def send_notification(self, notification: Dict[str, Any]) -> bool:
        """发送Discord通知"""
        if not self.enabled or not self.channel:
            logger.warning("Discord notifier is not enabled or channel is not connected")
            return False

        try:
            embed = self._create_embed(notification)
            await self.channel.send(embed=embed)
            logger.info(f"Discord notification sent: {notification.get('title')}")
            return True
        except Exception as e:
            logger.error(f"Failed to send Discord notification: {str(e)}")
            return False

    def _create_embed(self, notification: Dict[str, Any]) -> discord.Embed:
        """创建Discord Embed消息"""
        title = notification.get('title', 'TFT Rank Update')
        message = notification.get('message', '')
        notif_type = notification.get('type', 'info')

        # 根据通知类型选择颜色
        color_map = {
            'rank_change': discord.Color.gold(),
            'lp_threshold': discord.Color.blue(),
            'promotion': discord.Color.green(),
            'demotion': discord.Color.red(),
        }
        color = color_map.get(notif_type, discord.Color.blue())

        embed = discord.Embed(
            title=title,
            description=message,
            color=color,
            timestamp=discord.utils.utcnow()
        )

        # 添加详细字段
        new_data = notification.get('new_data', {})
        old_data = notification.get('old_data', {})

        if new_data:
            tier = new_data.get('tier', '')
            rank = new_data.get('rank', '')
            rank_str = f"{tier} {rank}" if rank else tier

            embed.add_field(name="当前段位", value=rank_str, inline=True)
            embed.add_field(name="LP", value=str(new_data.get('league_points', 0)), inline=True)

            wins = new_data.get('wins', 0)
            losses = new_data.get('losses', 0)
            total = wins + losses
            winrate = (wins / total * 100) if total > 0 else 0
            embed.add_field(
                name="胜率",
                value=f"{winrate:.1f}% ({wins}W {losses}L)",
                inline=True
            )

        # LP变动
        if old_data and new_data:
            lp_change = new_data.get('league_points', 0) - old_data.get('league_points', 0)
            if lp_change != 0:
                embed.add_field(
                    name="LP变动",
                    value=f"{lp_change:+d}",
                    inline=True
                )

        embed.set_footer(text="TFT Player Tracker")

        return embed

    async def start(self):
        """启动Discord Bot"""
        if not self.enabled:
            logger.warning("Discord notifier is disabled")
            return

        try:
            await self.bot.start(settings.discord_bot_token)
        except Exception as e:
            logger.error(f"Failed to start Discord bot: {str(e)}")
            self.enabled = False

    async def close(self):
        """关闭Discord Bot"""
        if self.bot:
            await self.bot.close()


# 全局Discord通知器实例
discord_notifier = DiscordNotifier()
