"""State machine transition validators for claim lifecycle."""

from core.models import FDHStatus, AppealStatus


class InvalidStateTransition(Exception):
    def __init__(self, current: str, target: str):
        super().__init__(f"Invalid transition: {current} → {target}")
        self.current = current
        self.target = target


_FDH_TRANSITIONS: dict[FDHStatus, set[FDHStatus]] = {
    FDHStatus.PENDING: {FDHStatus.CHECKED, FDHStatus.CANCELLED},
    FDHStatus.CHECKED: {FDHStatus.READY, FDHStatus.RE_CHECKING, FDHStatus.CANCELLED},
    FDHStatus.READY: {FDHStatus.SUBMITTED, FDHStatus.RE_CHECKING, FDHStatus.CANCELLED},
    FDHStatus.RE_CHECKING: {FDHStatus.CHECKED, FDHStatus.CANCELLED},
    FDHStatus.SUBMITTED: {FDHStatus.APPROVED, FDHStatus.DENIED, FDHStatus.CANCELLED},
    FDHStatus.APPROVED: {FDHStatus.CANCELLED},
    FDHStatus.DENIED: {FDHStatus.APPROVED, FDHStatus.CANCELLED},
    FDHStatus.CANCELLED: set(),
}

_APPEAL_TRANSITIONS: dict[AppealStatus, set[AppealStatus]] = {
    AppealStatus.NONE: {AppealStatus.DRAFTED},
    AppealStatus.DRAFTED: {AppealStatus.SUBMITTED},
    AppealStatus.SUBMITTED: {AppealStatus.APPROVED, AppealStatus.REJECTED},
    AppealStatus.APPROVED: set(),
    AppealStatus.REJECTED: {AppealStatus.RE_DRAFTED},
    AppealStatus.RE_DRAFTED: {AppealStatus.SUBMITTED},
}


def validate_fdh_transition(current: FDHStatus, target: FDHStatus) -> None:
    allowed = _FDH_TRANSITIONS.get(current, set())
    if target not in allowed:
        raise InvalidStateTransition(current.value, target.value)


def validate_appeal_transition(current: AppealStatus, target: AppealStatus) -> None:
    allowed = _APPEAL_TRANSITIONS.get(current, set())
    if target not in allowed:
        raise InvalidStateTransition(current.value, target.value)
