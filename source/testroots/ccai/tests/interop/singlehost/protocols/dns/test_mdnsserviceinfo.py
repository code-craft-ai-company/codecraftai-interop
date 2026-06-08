import os
import socket
import ccai.testbase as testbase
from ccai.interop.protocols.dns.mdnsserviceinfo import MdnsServiceInfo


def test_first_ipv4_address_returns_first_ipv4() -> None:
    info = MdnsServiceInfo()
    info._addresses = [
        socket.inet_pton(socket.AF_INET6, "2001:db8::1"),
        socket.inet_aton("1.2.3.4"),
        socket.inet_aton("5.6.7.8"),
    ]
    testbase.assert_equal(info.first_ipv4_address, "1.2.3.4")
    return


def test_first_ipv4_address_none_when_no_ipv4() -> None:
    info = MdnsServiceInfo()
    info._addresses = [socket.inet_pton(socket.AF_INET6, "2001:db8::1")]
    testbase.assert_equal(info.first_ipv4_address, None)
    return


def test_detail_lines_and_str_formatting() -> None:
    info = MdnsServiceInfo()
    info._svc_name = "svc"
    info._svc_type = "_test._tcp.local"
    info._addresses = [socket.inet_aton("1.2.3.4")]
    info._properties = {"b": "two", "a": b"one"}

    lines = info.detail_lines()
    expected_lines = [
        "svc_name: svc",
        "svc_type: _test._tcp.local",
        "ipv4_addr: 1.2.3.4",
        "properties",
        "    a: 'one'",
        "    b: 'two'",
    ]
    testbase.assert_equal(lines, expected_lines)
    testbase.assert_equal(str(info), os.linesep.join(expected_lines))
    return
