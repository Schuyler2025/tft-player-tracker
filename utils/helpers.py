"""
工具函数
"""
import sys
import os
from loguru import logger

from config import settings


def setup_logger():
    """配置日志系统"""
    # 移除默认handler
    logger.remove()
    
    # 添加控制台输出
    logger.add(
        sys.stderr,
        format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>",
        level=settings.log_level
    )
    
    # 创建日志目录
    log_dir = os.path.dirname(settings.log_file)
    if log_dir and not os.path.exists(log_dir):
        os.makedirs(log_dir)
    
    # 添加文件输出
    logger.add(
        settings.log_file,
        rotation="100 MB",
        retention="30 days",
        compression="zip",
        format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} - {message}",
        level=settings.log_level
    )
    
    logger.info("Logger initialized")


def format_rank(tier: str, rank: str = None) -> str:
    """格式化段位显示"""
    if rank and tier in ['IRON', 'BRONZE', 'SILVER', 'GOLD', 'PLATINUM', 'DIAMOND']:
        return f"{tier} {rank}"
    return tier


def calculate_winrate(wins: int, losses: int) -> float:
    """计算胜率"""
    total = wins + losses
    if total == 0:
        return 0.0
    return (wins / total) * 100


def format_lp_change(lp_change: int) -> str:
    """格式化LP变动"""
    if lp_change > 0:
        return f"+{lp_change}"
    return str(lp_change)
