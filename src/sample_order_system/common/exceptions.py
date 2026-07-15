class DomainError(Exception):
    """도메인 계층에서 발생하는 모든 예외의 기반 클래스."""


class NotFoundError(DomainError):
    """조회 대상 엔티티가 존재하지 않을 때 발생."""


class ValidationError(DomainError):
    """입력 값이 유효하지 않을 때 발생."""


class InvalidStateTransitionError(DomainError):
    """허용되지 않는 상태 전이를 시도할 때 발생."""
