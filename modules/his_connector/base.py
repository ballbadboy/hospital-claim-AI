"""Base class for all HIS connectors."""

from abc import ABC, abstractmethod
from datetime import datetime

from core.models import ClaimInput, Fund


class BaseHISConnector(ABC):
    def __init__(self, settings):
        self.settings = settings

    @abstractmethod
    async def fetch_discharges(self, since: datetime) -> list[ClaimInput]:
        """Fetch new discharge cases since given time."""

    @abstractmethod
    async def fetch_claim(self, hn: str, an: str) -> ClaimInput:
        """Fetch a single claim by HN and AN."""

    @abstractmethod
    async def health_check(self) -> bool:
        """Check if the HIS connection is healthy."""

    def normalize(self, raw_data: dict) -> ClaimInput:
        """Transform HIS-specific raw data into standard ClaimInput."""
        fund_str = raw_data.get("fund", "uc")
        try:
            fund = Fund(fund_str)
        except ValueError:
            fund = Fund.UC

        return ClaimInput(
            hn=str(raw_data.get("hn", "")),
            an=raw_data.get("an"),
            principal_dx=str(raw_data.get("principal_dx", "")),
            secondary_dx=raw_data.get("secondary_dx", []),
            procedures=raw_data.get("procedures", []),
            fund=fund,
            admit_date=raw_data.get("admit_date"),
            discharge_date=raw_data.get("discharge_date"),
            submit_date=raw_data.get("submit_date"),
            ward=raw_data.get("ward"),
            authen_code=raw_data.get("authen_code"),
            devices=raw_data.get("devices", []),
            clinical_docs=raw_data.get("clinical_docs", {}),
        )
