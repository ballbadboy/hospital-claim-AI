# Phase 2: HIS Connector Plugin System — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build a pluggable HIS connector system that normalizes data from any hospital information system (HOSxP, SSB, CSV) into ClaimInput, so the core engine never knows where data came from.

**Architecture:** Abstract base class + registry pattern. Each HIS gets one adapter file. Multiple connectors can be active simultaneously. CSV connector is always available as fallback.

**Tech Stack:** aiomysql (HOSxP MySQL), httpx (SSB API), existing pandas (CSV)

**Spec:** `docs/superpowers/specs/2026-03-25-full-platform-agent-design.md` (Phase 2 section)

---

### Task 1: Add Phase 2 dependencies and config settings

**Files:**
- Modify: `requirements.txt`
- Modify: `core/config.py`

- [ ] **Step 1: Add aiomysql to requirements.txt**

Append to `requirements.txt`:
```
aiomysql>=0.2.0
```

- [ ] **Step 2: Add HIS connector settings to Settings class**

In `core/config.py`, add to `Settings`:
```python
    his_connectors: list[str] = ["csv"]
    hosxp_db_host: str = ""
    hosxp_db_port: int = 3306
    hosxp_db_name: str = "hosxp_pcu"
    hosxp_db_user: str = ""
    hosxp_db_password: str = ""
    ssb_api_url: str = ""
    ssb_api_key: str = ""
```

- [ ] **Step 3: Run all tests**

Run: `python3 -m pytest tests/ -v`
Expected: All 42 tests pass.

- [ ] **Step 4: Commit**

```bash
git add requirements.txt core/config.py
git commit -m "feat(phase2): add HIS connector config settings and aiomysql dependency"
```

---

### Task 2: BaseHISConnector abstract class

**Files:**
- Create: `modules/his_connector/__init__.py`
- Create: `modules/his_connector/base.py`
- Create: `tests/test_his_connector.py`

- [ ] **Step 1: Write tests for base connector interface**

Create `tests/test_his_connector.py`:
```python
import pytest
from abc import ABC
from modules.his_connector.base import BaseHISConnector
from core.models import ClaimInput, Fund


class TestBaseHISConnector:
    def test_is_abstract(self):
        assert issubclass(BaseHISConnector, ABC)
        with pytest.raises(TypeError):
            BaseHISConnector(None)

    def test_normalize_creates_claim_input(self):
        class DummyConnector(BaseHISConnector):
            async def fetch_discharges(self, since):
                return []
            async def fetch_claim(self, hn, an):
                return ClaimInput(hn=hn, principal_dx="I21.1")
            async def health_check(self):
                return True

        from unittest.mock import MagicMock
        connector = DummyConnector(MagicMock())
        raw = {
            "hn": "12345",
            "an": "AN001",
            "principal_dx": "I21.1",
            "secondary_dx": ["E11.9"],
            "procedures": ["37.22"],
            "fund": "uc",
        }
        result = connector.normalize(raw)
        assert isinstance(result, ClaimInput)
        assert result.hn == "12345"
        assert result.principal_dx == "I21.1"
        assert result.fund == Fund.UC
```

- [ ] **Step 2: Run test, verify it fails**

Run: `python3 -m pytest tests/test_his_connector.py -v`

- [ ] **Step 3: Create base connector**

Create `modules/his_connector/__init__.py`:
```python
from modules.his_connector.base import BaseHISConnector
from modules.his_connector.registry import ConnectorRegistry

__all__ = ["BaseHISConnector", "ConnectorRegistry"]
```

Create `modules/his_connector/base.py`:
```python
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
```

- [ ] **Step 4: Run tests, verify they pass**

Run: `python3 -m pytest tests/test_his_connector.py -v`

- [ ] **Step 5: Commit**

```bash
git add modules/his_connector/ tests/test_his_connector.py
git commit -m "feat(phase2): add BaseHISConnector abstract class"
```

---

### Task 3: ConnectorRegistry

**Files:**
- Create: `modules/his_connector/registry.py`
- Modify: `tests/test_his_connector.py`

- [ ] **Step 1: Add registry tests**

Append to `tests/test_his_connector.py`:
```python
from modules.his_connector.registry import ConnectorRegistry


class TestConnectorRegistry:
    def setup_method(self):
        ConnectorRegistry._connectors.clear()

    def test_register_and_get(self):
        class DummyConnector(BaseHISConnector):
            async def fetch_discharges(self, since): return []
            async def fetch_claim(self, hn, an): return None
            async def health_check(self): return True

        ConnectorRegistry.register("dummy", DummyConnector)
        from unittest.mock import MagicMock
        connector = ConnectorRegistry.get("dummy", MagicMock())
        assert isinstance(connector, DummyConnector)

    def test_get_unknown_raises(self):
        from unittest.mock import MagicMock
        with pytest.raises(KeyError):
            ConnectorRegistry.get("nonexistent", MagicMock())

    def test_get_all_active(self):
        class DummyA(BaseHISConnector):
            async def fetch_discharges(self, since): return []
            async def fetch_claim(self, hn, an): return None
            async def health_check(self): return True

        class DummyB(BaseHISConnector):
            async def fetch_discharges(self, since): return []
            async def fetch_claim(self, hn, an): return None
            async def health_check(self): return True

        ConnectorRegistry.register("a", DummyA)
        ConnectorRegistry.register("b", DummyB)
        from unittest.mock import MagicMock
        settings = MagicMock()
        settings.his_connectors = ["a", "b"]
        connectors = ConnectorRegistry.get_all_active(settings)
        assert len(connectors) == 2
        assert isinstance(connectors[0], DummyA)
        assert isinstance(connectors[1], DummyB)
```

- [ ] **Step 2: Run tests, verify new ones fail**

- [ ] **Step 3: Create registry**

Create `modules/his_connector/registry.py`:
```python
"""Connector registry — register and retrieve HIS connectors by name."""

import logging
from modules.his_connector.base import BaseHISConnector

logger = logging.getLogger(__name__)


class ConnectorRegistry:
    _connectors: dict[str, type[BaseHISConnector]] = {}

    @classmethod
    def register(cls, name: str, connector_class: type[BaseHISConnector]) -> None:
        cls._connectors[name] = connector_class
        logger.info("Registered HIS connector: %s", name)

    @classmethod
    def get(cls, name: str, settings) -> BaseHISConnector:
        connector_class = cls._connectors[name]
        return connector_class(settings)

    @classmethod
    def get_all_active(cls, settings) -> list[BaseHISConnector]:
        return [cls.get(name, settings) for name in settings.his_connectors]

    @classmethod
    def available(cls) -> list[str]:
        return list(cls._connectors.keys())
```

- [ ] **Step 4: Run all tests**

Run: `python3 -m pytest tests/ -v`

- [ ] **Step 5: Commit**

```bash
git add modules/his_connector/registry.py tests/test_his_connector.py
git commit -m "feat(phase2): add ConnectorRegistry with register/get/get_all_active"
```

---

### Task 4: CSVConnector (wraps existing CSV logic)

**Files:**
- Create: `modules/his_connector/csv_connector.py`
- Modify: `tests/test_his_connector.py`

- [ ] **Step 1: Add CSV connector tests**

Append to `tests/test_his_connector.py`:
```python
import io
import pandas as pd


class TestCSVConnector:
    @pytest.fixture
    def connector(self):
        from modules.his_connector.csv_connector import CSVConnector
        from unittest.mock import MagicMock
        return CSVConnector(MagicMock())

    def test_health_check_always_true(self, connector):
        import asyncio
        result = asyncio.get_event_loop().run_until_complete(connector.health_check())
        assert result is True

    def test_parse_csv_content(self, connector):
        csv_content = "HN,AN,PDx,SDx,Procedures\n12345,AN001,I21.1,\"E11.9,I10\",\"37.22,88.56\""
        claims = connector.parse_csv(csv_content.encode())
        assert len(claims) == 1
        assert claims[0].hn == "12345"
        assert claims[0].principal_dx == "I21.1"
        assert "E11.9" in claims[0].secondary_dx
        assert "37.22" in claims[0].procedures
```

- [ ] **Step 2: Run tests, verify new ones fail**

- [ ] **Step 3: Create CSVConnector**

Create `modules/his_connector/csv_connector.py`:
```python
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
        return True  # CSV is always available

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
```

- [ ] **Step 4: Run all tests**

- [ ] **Step 5: Commit**

```bash
git add modules/his_connector/csv_connector.py tests/test_his_connector.py
git commit -m "feat(phase2): add CSVConnector wrapping existing CSV parse logic"
```

---

### Task 5: HOSxPConnector

**Files:**
- Create: `modules/his_connector/hosxp.py`
- Modify: `tests/test_his_connector.py`

- [ ] **Step 1: Add HOSxP connector tests (mocked DB)**

Append to `tests/test_his_connector.py`:
```python
from unittest.mock import AsyncMock, MagicMock, patch


class TestHOSxPConnector:
    @pytest.fixture
    def settings(self):
        s = MagicMock()
        s.hosxp_db_host = "192.168.1.100"
        s.hosxp_db_port = 3306
        s.hosxp_db_name = "hosxp_pcu"
        s.hosxp_db_user = "readonly"
        s.hosxp_db_password = "pass"
        return s

    @pytest.fixture
    def connector(self, settings):
        from modules.his_connector.hosxp import HOSxPConnector
        return HOSxPConnector(settings)

    @pytest.mark.asyncio
    async def test_health_check_success(self, connector):
        with patch("modules.his_connector.hosxp.aiomysql") as mock_mysql:
            mock_conn = AsyncMock()
            mock_conn.__aenter__ = AsyncMock(return_value=mock_conn)
            mock_conn.__aexit__ = AsyncMock(return_value=False)
            mock_mysql.connect = AsyncMock(return_value=mock_conn)
            result = await connector.health_check()
            assert result is True

    @pytest.mark.asyncio
    async def test_health_check_failure(self, connector):
        with patch("modules.his_connector.hosxp.aiomysql") as mock_mysql:
            mock_mysql.connect = AsyncMock(side_effect=Exception("Connection refused"))
            result = await connector.health_check()
            assert result is False

    def test_normalize_hosxp_row(self, connector):
        raw = {
            "hn": "HN001",
            "an": "AN001",
            "principal_dx": "I21.1",
            "secondary_dx": ["E11.9"],
            "procedures": ["37.22"],
            "fund": "uc",
            "ward": "CCU",
        }
        claim = connector.normalize(raw)
        assert claim.hn == "HN001"
        assert claim.ward == "CCU"
```

- [ ] **Step 2: Run tests, verify new ones fail**

- [ ] **Step 3: Create HOSxPConnector**

Create `modules/his_connector/hosxp.py`:
```python
"""HOSxP Connector — reads from HOSxP MySQL database (READ-ONLY).

WARNING: This connector MUST use a read-only database account with SELECT-only
privileges. Writing to HOSxP could corrupt hospital operations.

Tables accessed (read-only):
- ipt: inpatient admissions
- iptdiag: diagnoses
- iptoprt: procedures
- patient: patient demographics
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
            raise ImportError("aiomysql is required for HOSxP connector. Install with: pip install aiomysql")
        return await aiomysql.connect(
            host=self.settings.hosxp_db_host,
            port=self.settings.hosxp_db_port,
            db=self.settings.hosxp_db_name,
            user=self.settings.hosxp_db_user,
            password=self.settings.hosxp_db_password,
            autocommit=True,
        )

    async def fetch_discharges(self, since: datetime) -> list[ClaimInput]:
        """Fetch discharge cases from HOSxP since given time."""
        conn = await self._get_connection()
        try:
            async with conn.cursor(aiomysql.DictCursor) as cur:
                await cur.execute(
                    """
                    SELECT
                        p.hn, i.an, i.pdx AS principal_dx,
                        i.ward, i.regdate AS admit_date,
                        i.dchdate AS discharge_date
                    FROM ipt i
                    JOIN patient p ON p.hn = i.hn
                    WHERE i.dchdate >= %s
                    ORDER BY i.dchdate DESC
                    """,
                    (since,)
                )
                rows = await cur.fetchall()

            claims = []
            for row in rows:
                an = str(row["an"])
                sdx = await self._fetch_secondary_dx(conn, an)
                procs = await self._fetch_procedures(conn, an)
                raw = {
                    "hn": str(row["hn"]),
                    "an": an,
                    "principal_dx": row.get("principal_dx", ""),
                    "secondary_dx": sdx,
                    "procedures": procs,
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
            await cur.execute(
                "SELECT diagcode FROM iptdiag WHERE an = %s AND diagtype != 1",
                (an,)
            )
            return [row[0] for row in await cur.fetchall()]

    async def _fetch_procedures(self, conn, an: str) -> list[str]:
        async with conn.cursor() as cur:
            await cur.execute(
                "SELECT opercode FROM iptoprt WHERE an = %s",
                (an,)
            )
            return [row[0] for row in await cur.fetchall()]

    async def fetch_claim(self, hn: str, an: str) -> ClaimInput:
        """Fetch a single claim from HOSxP."""
        conn = await self._get_connection()
        try:
            async with conn.cursor(aiomysql.DictCursor) as cur:
                await cur.execute(
                    """
                    SELECT p.hn, i.an, i.pdx AS principal_dx,
                           i.ward, i.regdate AS admit_date,
                           i.dchdate AS discharge_date
                    FROM ipt i
                    JOIN patient p ON p.hn = i.hn
                    WHERE i.an = %s
                    """,
                    (an,)
                )
                row = await cur.fetchone()

            if row is None:
                raise ValueError(f"Claim AN={an} not found in HOSxP")

            sdx = await self._fetch_secondary_dx(conn, an)
            procs = await self._fetch_procedures(conn, an)
            raw = {
                "hn": str(row["hn"]),
                "an": str(row["an"]),
                "principal_dx": row.get("principal_dx", ""),
                "secondary_dx": sdx,
                "procedures": procs,
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
```

- [ ] **Step 4: Run all tests**

- [ ] **Step 5: Commit**

```bash
git add modules/his_connector/hosxp.py tests/test_his_connector.py
git commit -m "feat(phase2): add HOSxPConnector with read-only MySQL access"
```

---

### Task 6: SSBConnector

**Files:**
- Create: `modules/his_connector/ssb.py`
- Modify: `tests/test_his_connector.py`

- [ ] **Step 1: Add SSB connector tests**

Append to `tests/test_his_connector.py`:
```python
class TestSSBConnector:
    @pytest.fixture
    def settings(self):
        s = MagicMock()
        s.ssb_api_url = "https://ssb.hospital.local/api"
        s.ssb_api_key = "test-key"
        return s

    @pytest.fixture
    def connector(self, settings):
        from modules.his_connector.ssb import SSBConnector
        return SSBConnector(settings)

    @pytest.mark.asyncio
    async def test_health_check_success(self, connector):
        with patch("modules.his_connector.ssb.httpx.AsyncClient") as MockClient:
            mock_client = AsyncMock()
            mock_client.__aenter__ = AsyncMock(return_value=mock_client)
            mock_client.__aexit__ = AsyncMock(return_value=False)
            mock_response = MagicMock()
            mock_response.status_code = 200
            mock_client.get = AsyncMock(return_value=mock_response)
            MockClient.return_value = mock_client
            result = await connector.health_check()
            assert result is True

    @pytest.mark.asyncio
    async def test_health_check_failure(self, connector):
        with patch("modules.his_connector.ssb.httpx.AsyncClient") as MockClient:
            mock_client = AsyncMock()
            mock_client.__aenter__ = AsyncMock(return_value=mock_client)
            mock_client.__aexit__ = AsyncMock(return_value=False)
            mock_client.get = AsyncMock(side_effect=Exception("timeout"))
            MockClient.return_value = mock_client
            result = await connector.health_check()
            assert result is False
```

- [ ] **Step 2: Create SSBConnector**

Create `modules/his_connector/ssb.py`:
```python
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
```

- [ ] **Step 3: Run all tests**

- [ ] **Step 4: Commit**

```bash
git add modules/his_connector/ssb.py tests/test_his_connector.py
git commit -m "feat(phase2): add SSBConnector with REST API integration"
```

---

### Task 7: Register connectors and add HIS API endpoints

**Files:**
- Modify: `modules/his_connector/__init__.py` — register all connectors
- Create: `api/routes_his.py` — HIS connector API endpoints
- Modify: `api/main.py` — include HIS router

- [ ] **Step 1: Update __init__.py to register connectors**

```python
from modules.his_connector.base import BaseHISConnector
from modules.his_connector.registry import ConnectorRegistry
from modules.his_connector.csv_connector import CSVConnector
from modules.his_connector.hosxp import HOSxPConnector
from modules.his_connector.ssb import SSBConnector

ConnectorRegistry.register("csv", CSVConnector)
ConnectorRegistry.register("hosxp", HOSxPConnector)
ConnectorRegistry.register("ssb", SSBConnector)

__all__ = ["BaseHISConnector", "ConnectorRegistry"]
```

- [ ] **Step 2: Create HIS API routes**

Create `api/routes_his.py`:
```python
"""HIS connector API endpoints."""

import logging
from datetime import datetime, timedelta, timezone

from fastapi import APIRouter, Depends, HTTPException

from core.config import get_settings
from core.models import ClaimInput
from modules.his_connector import ConnectorRegistry
from api.auth.middleware import get_current_user, require_role

logger = logging.getLogger(__name__)

his_router = APIRouter(prefix="/api/v1/his", tags=["his"])


@his_router.get("/connectors")
async def list_connectors(user: dict = Depends(get_current_user)):
    """List all registered and active HIS connectors."""
    settings = get_settings()
    return {
        "available": ConnectorRegistry.available(),
        "active": settings.his_connectors,
    }


@his_router.get("/health")
async def his_health_check(user: dict = Depends(get_current_user)):
    """Check health of all active HIS connectors."""
    settings = get_settings()
    results = {}
    for name in settings.his_connectors:
        try:
            connector = ConnectorRegistry.get(name, settings)
            results[name] = await connector.health_check()
        except KeyError:
            results[name] = False
        except Exception as e:
            logger.error("Health check failed for %s: %s", name, e)
            results[name] = False
    return {"connectors": results}


@his_router.get("/fetch/{connector_name}")
async def fetch_discharges(
    connector_name: str,
    hours: int = 24,
    admin: dict = Depends(require_role("admin", "coder")),
):
    """Fetch recent discharges from a specific HIS connector."""
    settings = get_settings()
    try:
        connector = ConnectorRegistry.get(connector_name, settings)
    except KeyError:
        raise HTTPException(404, f"Connector '{connector_name}' not found")

    since = datetime.now(timezone.utc) - timedelta(hours=hours)
    try:
        claims = await connector.fetch_discharges(since)
        return {"connector": connector_name, "count": len(claims), "claims": claims}
    except NotImplementedError as e:
        raise HTTPException(400, str(e))
    except Exception as e:
        logger.error("Fetch failed for %s: %s", connector_name, e)
        raise HTTPException(502, f"Failed to fetch from {connector_name}: {str(e)}")
```

- [ ] **Step 3: Add HIS router to main.py**

In `api/main.py`, add import and include:
```python
from api.routes_his import his_router
# ...
app.include_router(his_router)
```

- [ ] **Step 4: Run all tests**

Run: `python3 -m pytest tests/ -v`

- [ ] **Step 5: Commit**

```bash
git add modules/his_connector/__init__.py api/routes_his.py api/main.py
git commit -m "feat(phase2): register connectors, add HIS API endpoints"
```

---

### Task 8: Update health check and final verification

**Files:**
- Modify: `api/routes.py` — add HIS status to /health endpoint

- [ ] **Step 1: Update /health to include HIS connector status**

In `api/routes.py`, update the health endpoint's services dict to add:
```python
            "his_connectors": settings.his_connectors,
```

- [ ] **Step 2: Run full test suite**

Run: `python3 -m pytest tests/ -v`
Expected: All tests pass.

- [ ] **Step 3: Commit**

```bash
git add api/routes.py
git commit -m "feat(phase2): add HIS connector info to health endpoint"
```
