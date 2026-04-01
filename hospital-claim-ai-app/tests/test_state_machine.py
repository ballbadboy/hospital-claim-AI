import pytest
from core.models import FDHStatus, AppealStatus


class TestFDHTransitions:
    def test_pending_to_checked(self):
        from core.state_machine import validate_fdh_transition
        validate_fdh_transition(FDHStatus.PENDING, FDHStatus.CHECKED)

    def test_checked_to_ready(self):
        from core.state_machine import validate_fdh_transition
        validate_fdh_transition(FDHStatus.CHECKED, FDHStatus.READY)

    def test_checked_to_re_checking(self):
        from core.state_machine import validate_fdh_transition
        validate_fdh_transition(FDHStatus.CHECKED, FDHStatus.RE_CHECKING)

    def test_submitted_to_denied(self):
        from core.state_machine import validate_fdh_transition
        validate_fdh_transition(FDHStatus.SUBMITTED, FDHStatus.DENIED)

    def test_invalid_pending_to_approved(self):
        from core.state_machine import validate_fdh_transition, InvalidStateTransition
        with pytest.raises(InvalidStateTransition):
            validate_fdh_transition(FDHStatus.PENDING, FDHStatus.APPROVED)

    def test_invalid_denied_to_ready(self):
        from core.state_machine import validate_fdh_transition, InvalidStateTransition
        with pytest.raises(InvalidStateTransition):
            validate_fdh_transition(FDHStatus.DENIED, FDHStatus.READY)

    def test_any_to_cancelled(self):
        from core.state_machine import validate_fdh_transition
        for status in FDHStatus:
            if status != FDHStatus.CANCELLED:
                validate_fdh_transition(status, FDHStatus.CANCELLED)

    def test_appeal_approved_transitions_fdh_to_approved(self):
        from core.state_machine import validate_fdh_transition
        validate_fdh_transition(FDHStatus.DENIED, FDHStatus.APPROVED)


class TestAppealTransitions:
    def test_none_to_drafted(self):
        from core.state_machine import validate_appeal_transition
        validate_appeal_transition(AppealStatus.NONE, AppealStatus.DRAFTED)

    def test_drafted_to_submitted(self):
        from core.state_machine import validate_appeal_transition
        validate_appeal_transition(AppealStatus.DRAFTED, AppealStatus.SUBMITTED)

    def test_rejected_to_re_drafted(self):
        from core.state_machine import validate_appeal_transition
        validate_appeal_transition(AppealStatus.REJECTED, AppealStatus.RE_DRAFTED)

    def test_invalid_none_to_approved(self):
        from core.state_machine import validate_appeal_transition, InvalidStateTransition
        with pytest.raises(InvalidStateTransition):
            validate_appeal_transition(AppealStatus.NONE, AppealStatus.APPROVED)
