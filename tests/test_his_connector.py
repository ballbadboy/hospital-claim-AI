import pytest
from abc import ABC
from unittest.mock import MagicMock
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
