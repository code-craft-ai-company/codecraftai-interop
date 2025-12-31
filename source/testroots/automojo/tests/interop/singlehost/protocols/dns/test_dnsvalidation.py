import automojo.testbase as testbase
from automojo.interop.protocols.dns.dnsvalidation import validate_service_name
from automojo.interop.protocols.dns.exceptions import DnsBadTypeInNameError


def test_validate_service_name_accepts_valid() -> None:
    # A basic service name should be accepted.
    validate_service_name("_http")
    return


def test_validate_service_name_rejects_missing_leading_underscore() -> None:
    exc = None
    try:
        validate_service_name("http")
    except Exception as err:
        exc = err
    testbase.assert_equal(isinstance(exc, DnsBadTypeInNameError), True)
    return


def test_validate_service_name_rejects_too_long() -> None:
    # 16 characters after the underscore should be rejected
    name = "_" + "a" * 16
    exc = None
    try:
        validate_service_name(name)
    except Exception as err:
        exc = err
    testbase.assert_equal(isinstance(exc, DnsBadTypeInNameError), True)
    return


def test_validate_service_name_rejects_double_hyphen() -> None:
    exc = None
    try:
        validate_service_name("_ab--cd")
    except Exception as err:
        exc = err
    testbase.assert_equal(isinstance(exc, DnsBadTypeInNameError), True)
    return


def test_validate_service_name_rejects_start_or_end_hyphen() -> None:
    for name in ["_-abc", "_abc-"]:
        exc = None
        try:
            validate_service_name(name)
        except Exception as err:
            exc = err
        testbase.assert_equal(isinstance(exc, DnsBadTypeInNameError), True)
    return


def test_validate_service_name_requires_letter() -> None:
    exc = None
    try:
        validate_service_name("_12345")
    except Exception as err:
        exc = err
    testbase.assert_equal(isinstance(exc, DnsBadTypeInNameError), True)
    return


def test_validate_service_name_allows_underscore_only_when_enabled() -> None:
    exc = None
    try:
        validate_service_name("_foo_bar")
    except Exception as err:
        exc = err
    testbase.assert_equal(isinstance(exc, DnsBadTypeInNameError), True)

    # When allowed, underscores should pass
    validate_service_name("_foo_bar", allow_underscores=True)
    return


def test_validate_service_name_rejects_disallowed_characters() -> None:
    exc = None
    try:
        validate_service_name("_foo$bar")
    except Exception as err:
        exc = err
    testbase.assert_equal(isinstance(exc, DnsBadTypeInNameError), True)
    return
