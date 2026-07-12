import httpx
from app.core.config import settings


class ZAPService:

    def __init__(self):
        self.base_url = settings.zap_api_url
        self.api_key  = settings.zap_api_key

    def _get(self, endpoint: str, params: dict = {}) -> dict:
        params["apikey"] = self.api_key
        response = httpx.get(
            f"{self.base_url}/JSON/{endpoint}",
            params=params,
            timeout=60,    # increased from 30 to 60
        )
        response.raise_for_status()
        return response.json()

    def start_spider(self, target: str) -> str:
        result = self._get(
            "spider/action/scan/",
            {"url": target, "recurse": "true"}
        )
        return result["scan"]

    def get_spider_status(self, scan_id: str) -> int:
        result = self._get(
            "spider/view/status/",
            {"scanId": scan_id}
        )
        return int(result["status"])

    def start_active_scan(self, target: str) -> str:
        result = self._get(
            "ascan/action/scan/",
            {"url": target, "recurse": "true"}
        )
        return result["scan"]

    def get_active_scan_status(self, scan_id: str) -> int:
        result = self._get(
            "ascan/view/status/",
            {"scanId": scan_id}
        )
        return int(result["status"])

    def get_alerts(self) -> list:
        result = self._get("core/view/alerts/")
        return result["alerts"]

    def clear_session(self):
        self._get("core/action/newSession/")


zap_service = ZAPService()