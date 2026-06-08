import ccai.testbase as testbase
from ccai.interop.protocols.dns.dnsutil import service_type_name
from ccai.interop.protocols.dns.exceptions import DnsBadTypeInNameError
from ccai.interop.protocols.dns import dnsutil
from ccai.testbase.mocking import create_module_patch


def test_service_type_name_returns_fqname() -> None:
    result = service_type_name("_http._tcp.local.")
    testbase.assert_equal(result, "_http._tcp.local.")
    return


def test_service_type_name_calls_validate_service_name() -> None:
    with create_module_patch(dnsutil, "validate_service_name") as vsn:
        service_type_name("_http._tcp.local", allow_underscores=True)
        vsn.assert_called_once_with("_http", allow_underscores=True)
    return


def test_service_type_name_missing_parts_raises() -> None:
    exc = None
    try:
        service_type_name("_tcp.local")
    except DnsBadTypeInNameError as err:
        exc = err
    testbase.assert_equal(isinstance(exc, DnsBadTypeInNameError), True)
    return


def test_service_type_name_non_local_domain_raises() -> None:
    exc = None
    try:
        service_type_name("_http._tcp.example")
    except DnsBadTypeInNameError as err:
        exc = err
    testbase.assert_equal(isinstance(exc, DnsBadTypeInNameError), True)
    return


def test_service_type_name_subtype_requires_name() -> None:
    exc = None
    try:
        service_type_name("_sub._http._tcp.local")
    except DnsBadTypeInNameError as err:
        exc = err
    testbase.assert_equal(isinstance(exc, DnsBadTypeInNameError), True)
    return


def test_service_type_name_extra_part_validated() -> None:
    long_part = "a" * 64
    exc = None
    try:
        service_type_name(f"{long_part}._http._tcp.local")
    except DnsBadTypeInNameError as err:
        exc = err
    testbase.assert_equal(isinstance(exc, DnsBadTypeInNameError), True)
    return


def test_service_type_name_control_character_raises() -> None:
    exc = None
    try:
        service_type_name("\x01bad._http._tcp.local")
    except DnsBadTypeInNameError as err:
        exc = err
    testbase.assert_equal(isinstance(exc, DnsBadTypeInNameError), True)
    return


def test_service_type_name_subtype_control_character_raises_with_message() -> None:
    subtype = "good\x01bad"
    exc = None
    try:
        service_type_name(f"{subtype}._sub._http._tcp.local")
    except DnsBadTypeInNameError as err:
        exc = err
    expected_message = "Ascii control character 0x00-0x1F and 0x7F illegal in '%s'" % subtype
    testbase.assert_equal(isinstance(exc, DnsBadTypeInNameError), True)
    testbase.assert_equal(str(exc), expected_message)
    return
