"""
微信推送通知
基于企业微信群机器人或微信公众号模板消息
"""
import json
from typing import Dict, Any
import requests
from loguru import logger

from config import settings


class WeChatNotifier:
    """微信通知器（企业微信群机器人）"""
    
    def __init__(self, webhook_url: str = None):
        """
        Args:
            webhook_url: 企业微信群机器人Webhook地址
        """
        self.webhook_url = webhook_url
        self.enabled = bool(webhook_url)
    
    def send_notification(self, notification: Dict[str, Any]) -> bool:
        """发送微信通知"""
        if not self.enabled:
            logger.warning("WeChat notifier is not enabled")
            return False
        
        try:
            message = self._format_message(notification)
            response = requests.post(
                self.webhook_url,
                json=message,
                headers={'Content-Type': 'application/json'},
                timeout=10
            )
            
            if response.status_code == 200 and response.json().get('errcode') == 0:
                logger.info(f"WeChat notification sent: {notification.get('title')}")
                return True
            else:
                logger.error(f"WeChat notification failed: {response.text}")
                return False
                
        except Exception as e:
            logger.error(f"Failed to send WeChat notification: {str(e)}")
            return False
    
    def _format_message(self, notification: Dict[str, Any]) -> Dict[str, Any]:
        """格式化微信消息（Markdown格式）"""
        title = notification.get('title', 'TFT Rank Update')
        message = notification.get('message', '')
        new_data = notification.get('new_data', {})
        old_data = notification.get('old_data', {})
        
        # 构建Markdown内容
        content_lines = [
            f"### {title}",
            "",
            message,
            ""
        ]
        
        # 添加详细信息
        if new_data:
            tier = new_data.get('tier', '')
            rank = new_data.get('rank', '')
            rank_str = f"{tier} {rank}" if rank else tier
            lp = new_data.get('league_points', 0)
            wins = new_data.get('wins', 0)
            losses = new_data.get('losses', 0)
            total = wins + losses
            winrate = (wins / total * 100) if total > 0 else 0
            
            content_lines.extend([
                f"**当前段位**: {rank_str}",
                f"**LP**: {lp}",
                f"**胜率**: {winrate:.1f}% ({wins}W {losses}L)",
            ])
            
            # LP变动
            if old_data:
                lp_change = lp - old_data.get('league_points', 0)
                if lp_change != 0:
                    content_lines.append(f"**LP变动**: {lp_change:+d}")
        
        content_lines.append("")
        content_lines.append("> TFT Player Tracker")
        
        return {
            "msgtype": "markdown",
            "markdown": {
                "content": "\n".join(content_lines)
            }
        }


class WeChatTemplateNotifier:
    """微信公众号模板消息通知器"""
    
    def __init__(self):
        self.app_id = settings.wechat_app_id
        self.app_secret = settings.wechat_app_secret
        self.template_id = settings.wechat_template_id
        self.enabled = bool(self.app_id and self.app_secret and self.template_id)
        self.access_token = None
    
    def _get_access_token(self) -> str:
        """获取access_token"""
        url = f"https://api.weixin.qq.com/cgi-bin/token?grant_type=client_credential&appid={self.app_id}&secret={self.app_secret}"
        
        try:
            response = requests.get(url, timeout=10)
            data = response.json()
            
            if 'access_token' in data:
                self.access_token = data['access_token']
                return self.access_token
            else:
                logger.error(f"Failed to get WeChat access_token: {data}")
                return None
                
        except Exception as e:
            logger.error(f"Error getting WeChat access_token: {str(e)}")
            return None
    
    def send_notification(self, notification: Dict[str, Any], openid: str) -> bool:
        """发送模板消息"""
        if not self.enabled:
            logger.warning("WeChat template notifier is not enabled")
            return False
        
        if not self.access_token:
            self.access_token = self._get_access_token()
        
        if not self.access_token:
            return False
        
        try:
            url = f"https://api.weixin.qq.com/cgi-bin/message/template/send?access_token={self.access_token}"
            
            data = self._format_template_message(notification, openid)
            response = requests.post(url, json=data, timeout=10)
            result = response.json()
            
            if result.get('errcode') == 0:
                logger.info(f"WeChat template notification sent: {notification.get('title')}")
                return True
            else:
                logger.error(f"WeChat template notification failed: {result}")
                return False
                
        except Exception as e:
            logger.error(f"Failed to send WeChat template notification: {str(e)}")
            return False
    
    def _format_template_message(self, notification: Dict[str, Any], openid: str) -> Dict[str, Any]:
        """格式化模板消息"""
        title = notification.get('title', 'TFT Rank Update')
        new_data = notification.get('new_data', {})
        
        tier = new_data.get('tier', '')
        rank = new_data.get('rank', '')
        rank_str = f"{tier} {rank}" if rank else tier
        lp = new_data.get('league_points', 0)
        
        return {
            "touser": openid,
            "template_id": self.template_id,
            "data": {
                "first": {"value": title, "color": "#173177"},
                "keyword1": {"value": new_data.get('summoner_name', ''), "color": "#173177"},
                "keyword2": {"value": rank_str, "color": "#173177"},
                "keyword3": {"value": str(lp), "color": "#173177"},
                "remark": {"value": notification.get('message', ''), "color": "#999999"}
            }
        }


# 全局微信通知器实例（需要配置webhook_url）
# wechat_notifier = WeChatNotifier(webhook_url="your-webhook-url")
wechat_template_notifier = WeChatTemplateNotifier()
