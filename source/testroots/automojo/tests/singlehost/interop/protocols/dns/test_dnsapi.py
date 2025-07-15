import automojo.testbase as testbase
from automojo.interop.protocols.dns.dnsconst import DnsRecordType, DnsRecordClass
from automojo.interop.protocols.dns import dnsapi
from unittest import mock


def test_dns_query_name_returns_query_string():
    with mock.patch.object(dnsapi, "DnsQuestion", autospec=True) as mock_question:
        instance = mock_question.return_value
        instance.as_dns_string.return_value = "query"
        result = dnsapi.dns_query_name("example.com", DnsRecordType.A, DnsRecordClass.IN)
        mock_question.assert_called_once_with("example.com", DnsRecordType.A, DnsRecordClass.IN)
        instance.as_dns_string.assert_called_once_with()
        testbase.assert_equal(result, "query")
    return


def test_dns_query_services_starts_server_and_waits():
    with mock.patch.object(dnsapi, "DnsServer", autospec=True) as mock_server:
        instance = mock_server.return_value
        dnsapi.dns_query_services(["_http._tcp.local"])
        mock_server.assert_called_once_with()
        instance.start.assert_called_once_with()
        instance.wait.assert_called_once_with()
    return
