import pytest
from abc import ABC
from unittest.mock import MagicMock
from modules.his_connector.base import BaseHISConnector
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
