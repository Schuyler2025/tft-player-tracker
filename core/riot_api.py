"""
Riot API客户端封装
实现TFT相关接口调用和速率限制控制
"""
import time
from typing import Optional, Dict, List, Any
from collections import deque
import requests
from tenacity import retry, stop_after_attempt, wait_exponential
from loguru import logger

from config import settings


class RateLimiter:
    """API速率限制器"""

    def __init__(self, max_per_second: int, max_per_2min: int):
        self.max_per_second = max_per_second
        self.max_per_2min = max_per_2min
        self.second_window = deque(maxlen=max_per_second)
        self.two_min_window = deque(maxlen=max_per_2min)

    def acquire(self):
        """获取API调用许可"""
        now = time.time()

        # 清理1秒窗口
        while self.second_window and now - self.second_window[0] > 1:
            self.second_window.popleft()

        # 清理2分钟窗口
        while self.two_min_window and now - self.two_min_window[0] > 120:
            self.two_min_window.popleft()

        # 检查是否超限
        if len(self.second_window) >= self.max_per_second:
            sleep_time = 1 - (now - self.second_window[0])
            if sleep_time > 0:
                logger.debug(f"Speed limit reached, waiting {sleep_time:.2f} seconds")
                time.sleep(sleep_time)

        if len(self.two_min_window) >= self.max_per_2min:
            sleep_time = 120 - (now - self.two_min_window[0])
            if sleep_time > 0:
                logger.warning(f"2-minute rate limit reached, waiting {sleep_time:.2f} seconds")
                time.sleep(sleep_time)

        # 记录调用时间
        now = time.time()
        self.second_window.append(now)
        self.two_min_window.append(now)


class RiotAPIClient:
    """Riot API客户端"""

    BASE_URL_TEMPLATE = "https://{region}.api.riotgames.com"

    def __init__(self):
        self.api_key = settings.riot_api_key
        self.region = settings.riot_api_region
        self.routing = settings.riot_api_routing
        self.rate_limiter = RateLimiter(
            settings.riot_api_rate_limit_per_second,
            settings.riot_api_rate_limit_per_2min
        )
        self.session = requests.Session()
        self.session.headers.update({
            'X-Riot-Token': self.api_key,
            'Accept': 'application/json'
        })

    def _get_base_url(self, use_routing: bool = False) -> str:
        """获取API基础URL"""
        region = self.routing if use_routing else self.region
        return self.BASE_URL_TEMPLATE.format(region=region)

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=2, max=10))
    def _request(self, endpoint: str, use_routing: bool = False) -> Optional[Dict]:
        """执行API请求（带重试机制）"""
        self.rate_limiter.acquire()

        url = f"{self._get_base_url(use_routing)}{endpoint}"

        try:
            response = self.session.get(url, timeout=10)

            if response.status_code == 200:
                return response.json()
            elif response.status_code == 404:
                logger.warning(f"Resource not found: {endpoint}")
                return None
            elif response.status_code == 429:
                retry_after = int(response.headers.get('Retry-After', 60))
                logger.warning(f"Rate limit exceeded, retrying after {retry_after}s")
                time.sleep(retry_after)
                raise Exception("Rate limit exceeded")
            elif response.status_code in (401, 403):
                base = self._get_base_url(use_routing)
                logger.error(
                    f"Unauthorized/Forbidden (status {response.status_code}). "
                    f"Check RIOT_API_KEY validity and region/routing. url={base}{endpoint}"
                )
                return None
            else:
                logger.error(f"API request failed: {response.status_code} - {response.text}")
                return None

        except requests.RequestException as e:
            logger.error(f"Request error: {str(e)}")
            raise

    # 新增：统一校验召唤师对象必须包含 id 与 puuid
    def _validate_summoner(self, summoner: Optional[Dict[str, Any]]) -> Optional[Dict[str, Any]]:
        # if not summoner:
        #     return None
        # if 'id' not in summoner or 'puuid' not in summoner:
        #     logger.warning(f"Summoner payload missing keys: {list(summoner.keys())}")
        #     return None
        return summoner

    def get_summoner_by_name(self, game_name: str, tag_line: str) -> Optional[Dict[str, Any]]:
        """通过游戏名称和标签获取召唤师信息（Riot ID），必要时回退为平台区按召唤师名查询"""
        # 1) 先用 routing 查 Riot ID → 取 puuid
        account_ep = f"/riot/account/v1/accounts/by-riot-id/{game_name}/{tag_line}"
        account_data = self._request(account_ep, use_routing=True)

        # 2) 若拿到 puuid，则用平台区查 TFT Summoner
        if account_data and account_data.get('puuid'):
            puuid = account_data['puuid']
            summoner_ep = f"/tft/summoner/v1/summoners/by-puuid/{puuid}"
            summoner = self._request(summoner_ep)
            summoner = self._validate_summoner(summoner)
            if summoner:
                return summoner
            logger.warning(f"PUUID lookup failed for {game_name}#{tag_line}, trying platform by-name fallback")

        # 3) 回退：直接按平台区的召唤师名查询（无 tag）
        # fallback = self._request(f"/tft/summoner/v1/summoners/by-name/{game_name}")
        # fallback = self._validate_summoner(fallback)
        # if not fallback:
        #     logger.warning(f"Platform by-name lookup failed for {game_name}")
        return summoner

    def get_league_entries(self, puuid: str) -> List[Dict[str, Any]]:
        """获取召唤师排位信息"""
        endpoint = f"/tft/league/v1/by-puuid/{puuid}"
        result = self._request(endpoint)
        return result if result else []

    def get_match_ids(self, puuid: str, count: int = 20) -> List[str]:
        """获取玩家最近的对局ID列表"""
        endpoint = f"/tft/match/v1/matches/by-puuid/{puuid}/ids?count={count}"
        result = self._request(endpoint, use_routing=True)
        return result if result else []

    def get_match_details(self, match_id: str) -> Optional[Dict[str, Any]]:
        """获取对局详情"""
        endpoint = f"/tft/match/v1/matches/{match_id}"
        return self._request(endpoint, use_routing=True)

    def get_summoner_rank_data(self, game_name: str, tag_line: str) -> Optional[Dict[str, Any]]:
        """获取召唤师完整Rank数据（封装方法），避免 KeyError"""
        summoner = self.get_summoner_by_name(game_name, tag_line)
        summoner = self._validate_summoner(summoner)
        if not summoner:
            logger.warning(f"Summoner not found or invalid payload: {game_name}#{tag_line}")
            return None

        # 安全访问 id
        puuid = summoner.get('puuid')
        if not puuid:
            logger.warning(f"Summoner missing id/puuid: {game_name}#{tag_line}")
            return None

        league_entries = self.get_league_entries(puuid)

        # 找到TFT排位数据（过滤出RANKED_TFT队列）
        tft_ranked = next(
            (entry for entry in league_entries if entry.get('queueType') == 'RANKED_TFT'),
            None
        )

        if not tft_ranked:
            logger.info(f"No ranked data found for {game_name}#{tag_line}")
            return None

        return {
            'puuid': puuid,
            'summoner_name': f"{game_name}#{tag_line}",
            'tier': tft_ranked.get('tier'),
            'rank': tft_ranked.get('rank'),
            'league_points': tft_ranked.get('leaguePoints'),
            'wins': tft_ranked.get('wins'),
            'losses': tft_ranked.get('losses'),
            'veteran': tft_ranked.get('veteran', False),
            'hot_streak': tft_ranked.get('hotStreak', False),
            'fresh_blood': tft_ranked.get('freshBlood', False)
        }
