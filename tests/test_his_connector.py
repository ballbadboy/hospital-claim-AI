import pytest
from abc import ABC
from unittest.mock import AsyncMock, MagicMock, patch
from modules.his_connector.base import BaseHISConnector
from modules.his_connector.registry import ConnectorRegistry
from core.models import ClaimInput, Fund


class TestBaseHISConnector:
    def test_is_abstract(self):
        assert issubclass(BaseHISConnector, ABC)
        with pytest.raises(TypeError):
            BaseHISConnector(None)

    def test_normalize_creates_claim_input(self):
        class DummyConnector(BaseHISConnector):
            async def fetch_discharges(self, since): return []
            async def fetch_claim(self, hn, an): return ClaimInput(hn=hn, principal_dx="I21.1")
            async def health_check(self): return True

        connector = DummyConnector(MagicMock())
        raw = {
            "hn": "12345", "an": "AN001", "principal_dx": "I21.1",
            "secondary_dx": ["E11.9"], "procedures": ["37.22"], "fund": "uc",
        }
        result = connector.normalize(raw)
        assert isinstance(result, ClaimInput)
        assert result.hn == "12345"
        assert result.principal_dx == "I21.1"
        assert result.fund == Fund.UC


class TestConnectorRegistry:
    def setup_method(self):
        ConnectorRegistry._connectors.clear()

    def test_register_and_get(self):
        class DummyConnector(BaseHISConnector):
            async def fetch_discharges(self, since): return []
            async def fetch_claim(self, hn, an): return None
            async def health_check(self): return True

        ConnectorRegistry.register("dummy", DummyConnector)
        connector = ConnectorRegistry.get("dummy", MagicMock())
        assert isinstance(connector, DummyConnector)

    def test_get_unknown_raises(self):
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
        settings = MagicMock()
        settings.his_connectors = ["a", "b"]
        connectors = ConnectorRegistry.get_all_active(settings)
        assert len(connectors) == 2


class TestCSVConnector:
    @pytest.fixture
    def connector(self):
        from modules.his_connector.csv_connector import CSVConnector
        return CSVConnector(MagicMock())

    @pytest.mark.asyncio
    async def test_health_check_always_true(self, connector):
        result = await connector.health_check()
        assert result is True

    def test_parse_csv_content(self, connector):
        csv_content = b'HN,AN,PDx,SDx,Procedures\n12345,AN001,I21.1,"E11.9,I10","37.22,88.56"'
        claims = connector.parse_csv(csv_content)
        assert len(claims) == 1
        assert claims[0].hn == "12345"
        assert claims[0].principal_dx == "I21.1"
        assert "E11.9" in claims[0].secondary_dx
        assert "37.22" in claims[0].procedures

    @pytest.mark.asyncio
    async def test_fetch_discharges_raises(self, connector):
        with pytest.raises(NotImplementedError):
            await connector.fetch_discharges(None)


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
        raw = {"hn": "HN001", "an": "AN001", "principal_dx": "I21.1",
               "secondary_dx": ["E11.9"], "procedures": ["37.22"], "fund": "uc", "ward": "CCU"}
        claim = connector.normalize(raw)
        assert claim.hn == "HN001"
        assert claim.ward == "CCU"


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
