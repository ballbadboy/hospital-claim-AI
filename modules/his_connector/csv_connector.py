"""CSV Connector — wraps existing CSV upload logic into the connector interface."""

import io
import logging
from datetime import datetime

import pandas as pd

from core.models import ClaimInput
from modules.his_connector.base import BaseHISConnector

logger = logging.getLogger(__name__)


class CSVConnector(BaseHISConnector):
    """Always-available fallback connector for manual CSV uploads."""

    async def fetch_discharges(self, since: datetime) -> list[ClaimInput]:
        raise NotImplementedError("CSV connector does not support automatic fetching. Use parse_csv() instead.")

    async def fetch_claim(self, hn: str, an: str) -> ClaimInput:
        raise NotImplementedError("CSV connector does not support single claim lookup.")

    async def health_check(self) -> bool:
        return True

    def parse_csv(self, content: bytes) -> list[ClaimInput]:
        """Parse CSV content into ClaimInput list."""
        df = pd.read_csv(io.BytesIO(content))
        claims = []
        for _, row in df.iterrows():
            sdx_raw = row.get("SDx")
            sdx = str(sdx_raw).split(",") if pd.notna(sdx_raw) and sdx_raw else []
            proc_raw = row.get("Procedures")
            procs = str(proc_raw).split(",") if pd.notna(proc_raw) and proc_raw else []

            raw = {
                "hn": str(row.get("HN", "")),
                "an": str(row.get("AN", "")) if pd.notna(row.get("AN")) else None,
                "principal_dx": str(row.get("PDx", row.get("Primary Diagnosis", ""))),
                "secondary_dx": sdx,
                "procedures": procs,
            }
            claims.append(self.normalize(raw))
        return claims
