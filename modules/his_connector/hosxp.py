"""HOSxP Connector — reads from HOSxP MySQL database (READ-ONLY).

WARNING: This connector MUST use a read-only database account with SELECT-only
privileges. Writing to HOSxP could corrupt hospital operations.

Tables accessed (read-only): ipt, iptdiag, iptoprt, patient
"""

import logging
from datetime import datetime

from core.models import ClaimInput
from modules.his_connector.base import BaseHISConnector

logger = logging.getLogger(__name__)

try:
    import aiomysql
except ImportError:
    aiomysql = None


class HOSxPConnector(BaseHISConnector):
    """Connector for HOSxP HIS via MySQL (read-only)."""

    async def _get_connection(self):
        if aiomysql is None:
            raise ImportError("aiomysql is required for HOSxP connector")
        return await aiomysql.connect(
            host=self.settings.hosxp_db_host,
            port=self.settings.hosxp_db_port,
            db=self.settings.hosxp_db_name,
            user=self.settings.hosxp_db_user,
            password=self.settings.hosxp_db_password,
            autocommit=True,
        )

    async def fetch_discharges(self, since: datetime) -> list[ClaimInput]:
        conn = await self._get_connection()
        try:
            async with conn.cursor(aiomysql.DictCursor) as cur:
                await cur.execute(
                    """SELECT p.hn, i.an, i.pdx AS principal_dx, i.ward,
                              i.regdate AS admit_date, i.dchdate AS discharge_date
                       FROM ipt i JOIN patient p ON p.hn = i.hn
                       WHERE i.dchdate >= %s ORDER BY i.dchdate DESC""",
                    (since,)
                )
                rows = await cur.fetchall()

            claims = []
            for row in rows:
                an = str(row["an"])
                sdx = await self._fetch_secondary_dx(conn, an)
                procs = await self._fetch_procedures(conn, an)
                raw = {
                    "hn": str(row["hn"]), "an": an,
                    "principal_dx": row.get("principal_dx", ""),
                    "secondary_dx": sdx, "procedures": procs,
                    "ward": row.get("ward"),
                    "admit_date": row.get("admit_date"),
                    "discharge_date": row.get("discharge_date"),
                }
                claims.append(self.normalize(raw))
            return claims
        finally:
            conn.close()

    async def _fetch_secondary_dx(self, conn, an: str) -> list[str]:
        async with conn.cursor() as cur:
            await cur.execute("SELECT diagcode FROM iptdiag WHERE an = %s AND diagtype != 1", (an,))
            return [row[0] for row in await cur.fetchall()]

    async def _fetch_procedures(self, conn, an: str) -> list[str]:
        async with conn.cursor() as cur:
            await cur.execute("SELECT opercode FROM iptoprt WHERE an = %s", (an,))
            return [row[0] for row in await cur.fetchall()]

    async def fetch_claim(self, hn: str, an: str) -> ClaimInput:
        conn = await self._get_connection()
        try:
            async with conn.cursor(aiomysql.DictCursor) as cur:
                await cur.execute(
                    """SELECT p.hn, i.an, i.pdx AS principal_dx, i.ward,
                              i.regdate AS admit_date, i.dchdate AS discharge_date
                       FROM ipt i JOIN patient p ON p.hn = i.hn WHERE i.an = %s""",
                    (an,)
                )
                row = await cur.fetchone()
            if row is None:
                raise ValueError(f"Claim AN={an} not found in HOSxP")
            sdx = await self._fetch_secondary_dx(conn, an)
            procs = await self._fetch_procedures(conn, an)
            raw = {
                "hn": str(row["hn"]), "an": str(row["an"]),
                "principal_dx": row.get("principal_dx", ""),
                "secondary_dx": sdx, "procedures": procs,
                "ward": row.get("ward"),
                "admit_date": row.get("admit_date"),
                "discharge_date": row.get("discharge_date"),
            }
            return self.normalize(raw)
        finally:
            conn.close()

    async def health_check(self) -> bool:
        try:
            conn = await self._get_connection()
            conn.close()
            return True
        except Exception as e:
            logger.warning("HOSxP health check failed: %s", e)
            return False
