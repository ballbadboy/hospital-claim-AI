import pytest
from core.models import FDHStatus, AppealStatus


class TestFDHStatus:
    def test_all_statuses_exist(self):
        expected = {"pending", "checked", "ready", "re_checking",
                    "submitted", "approved", "denied", "cancelled"}
        assert {s.value for s in FDHStatus} == expected

    def test_string_enum(self):
        assert FDHStatus.PENDING == "pending"
        assert isinstance(FDHStatus.PENDING, str)


class TestAppealStatus:
    def test_all_statuses_exist(self):
        expected = {"none", "drafted", "submitted",
                    "approved", "rejected", "re_drafted"}
        assert {s.value for s in AppealStatus} == expected
