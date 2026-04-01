"""SSB Connector — connects to SSB HIS via REST API."""

import logging
from datetime import datetime

import httpx

from core.models import ClaimInput
from modules.his_connector.base import BaseHISConnector

logger = logging.getLogger(__name__)


class SSBConnector(BaseHISConnector):
    """Connector for SSB HIS via REST API."""

    def _headers(self) -> dict:
        return {
            "Authorization": f"Bearer {self.settings.ssb_api_key}",
            "Content-Type": "application/json",
        }

    async def fetch_discharges(self, since: datetime) -> list[ClaimInput]:
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{self.settings.ssb_api_url}/discharges",
                headers=self._headers(),
                params={"since": since.isoformat()},
                timeout=30,
            )
            response.raise_for_status()
            data = response.json()
            return [self.normalize(row) for row in data.get("results", [])]

    async def fetch_claim(self, hn: str, an: str) -> ClaimInput:
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{self.settings.ssb_api_url}/claims/{an}",
                headers=self._headers(),
                timeout=30,
            )
            response.raise_for_status()
            return self.normalize(response.json())

    async def health_check(self) -> bool:
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{self.settings.ssb_api_url}/health",
                    headers=self._headers(),
                    timeout=10,
                )
                return response.status_code == 200
        except Exception as e:
            logger.warning("SSB health check failed: %s", e)
            return False
