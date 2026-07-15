from sample_order_system.common.exceptions import (
    DomainError,
    InvalidStateTransitionError,
    NotFoundError,
    ValidationError,
)


def test_not_found_error_is_domain_error():
    assert issubclass(NotFoundError, DomainError)


def test_validation_error_is_domain_error():
    assert issubclass(ValidationError, DomainError)


def test_invalid_state_transition_error_is_domain_error():
    assert issubclass(InvalidStateTransitionError, DomainError)


def test_domain_error_is_exception():
    assert issubclass(DomainError, Exception)
