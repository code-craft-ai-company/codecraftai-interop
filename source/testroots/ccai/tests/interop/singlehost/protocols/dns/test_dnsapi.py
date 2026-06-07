import ccai.testbase as testbase
from ccai.interop.protocols.dns.dnsconst import DnsRecordType, DnsRecordClass
from ccai.interop.protocols.dns import dnsapi
from ccai.testbase.mocking import Mock, create_module_patch


def test_dns_query_name_returns_query_string():
    with create_module_patch(dnsapi, "DnsQuestion") as mock_question:
        instance = Mock(recursive=True)
        mock_question.configure(return_value=instance)
        instance.as_dns_string.configure(return_value="query")
        result = dnsapi.dns_query_name("example.com", DnsRecordType.A, DnsRecordClass.IN)
        mock_question.assert_called_once_with("example.com", DnsRecordType.A, DnsRecordClass.IN)
        instance.as_dns_string.assert_called_once_with()
        testbase.assert_equal(result, "query")
    return


def test_dns_query_services_starts_server_and_waits():
    with create_module_patch(dnsapi, "DnsServer") as mock_server:
        instance = Mock(recursive=True)
        mock_server.configure(return_value=instance)
        dnsapi.dns_query_services(["_http._tcp.local"])
        mock_server.assert_called_once_with()
        instance.start.assert_called_once_with()
        instance.wait.assert_called_once_with()
    return
