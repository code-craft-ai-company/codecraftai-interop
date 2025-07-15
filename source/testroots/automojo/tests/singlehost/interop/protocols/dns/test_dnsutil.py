import automojo.testbase as testbase
from automojo.interop.protocols.dns.dnsutil import service_type_name
from automojo.interop.protocols.dns.exceptions import DnsBadTypeInNameError
from automojo.interop.protocols.dns import dnsutil
from unittest import mock


def test_service_type_name_returns_fqname() -> None:
    result = service_type_name("_http._tcp.local.")
    testbase.assert_equal(result, "_http._tcp.local.")
    return


def test_service_type_name_calls_validate_service_name() -> None:
    with mock.patch.object(dnsutil, "validate_service_name") as vsn:
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
