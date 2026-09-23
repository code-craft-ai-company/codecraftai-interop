from ccai.interop.protocols.dns import testmessagesipv4
from ccai.interop.protocols.dns import testmessagesipv6

def test_inbound_message_DNS_IPV4_QUERY_A_EXAMPLE() -> None:
    pkt = testmessagesipv4.DNS_IPV4_QUERY_A_EXAMPLE.encode('latin1')
    testmessagesipv4.validate_message_DNS_IPV4_QUERY_A_EXAMPLE(pkt)
    return

def test_inbound_message_DNS_RESPONSE_A_EXAMPLE() -> None:
    pkt = testmessagesipv4.DNS_RESPONSE_A_EXAMPLE.encode('latin1')
    testmessagesipv4.validate_message_DNS_RESPONSE_A_EXAMPLE(pkt)
    return

def test_inbound_message_DNS_IPV4_QUERY_CNAME_WWW() -> None:
    pkt = testmessagesipv4.DNS_IPV4_QUERY_CNAME_WWW.encode('latin1')
    testmessagesipv4.validate_message_DNS_IPV4_QUERY_CNAME_WWW(pkt)
    return

def test_inbound_message_DNS_IPV4_RESPONSE_CNAME_WWW() -> None:
    pkt = testmessagesipv4.DNS_IPV4_RESPONSE_CNAME_WWW.encode('latin1')
    testmessagesipv4.validate_message_DNS_IPV4_RESPONSE_CNAME_WWW(pkt)
    return

def test_inbound_message_DNS_IPV4_QUERY_MX_EXAMPLE() -> None:
    pkt = testmessagesipv4.DNS_IPV4_QUERY_MX_EXAMPLE.encode('latin1')
    testmessagesipv4.validate_message_DNS_IPV4_QUERY_MX_EXAMPLE(pkt)
    return

def test_inbound_message_DNS_IPV4_RESPONSE_MX_EXAMPLE() -> None:
    pkt = testmessagesipv4.DNS_IPV4_RESPONSE_MX_EXAMPLE.encode('latin1')
    testmessagesipv4.validate_message_DNS_IPV4_RESPONSE_MX_EXAMPLE(pkt)
    return

def test_inbound_message_DNS_IPV4_QUERY_TXT_EXAMPLE() -> None:
    pkt = testmessagesipv4.DNS_IPV4_QUERY_TXT_EXAMPLE.encode('latin1')
    testmessagesipv4.validate_message_DNS_IPV4_QUERY_TXT_EXAMPLE(pkt)
    return

def test_inbound_message_DNS_IPV4_RESPONSE_TXT_EXAMPLE() -> None:
    pkt = testmessagesipv4.DNS_IPV4_RESPONSE_TXT_EXAMPLE.encode('latin1')
    testmessagesipv4.validate_message_DNS_IPV4_RESPONSE_TXT_EXAMPLE(pkt)
    return

def test_inbound_message_DNS_IPV4_QUERY_NS_EXAMPLE() -> None:
    pkt = testmessagesipv4.DNS_IPV4_QUERY_NS_EXAMPLE.encode('latin1')
    testmessagesipv4.validate_message_DNS_IPV4_QUERY_NS_EXAMPLE(pkt)
    return

def test_inbound_message_DNS_IPV4_RESPONSE_NS_EXAMPLE() -> None:
    pkt = testmessagesipv4.DNS_IPV4_RESPONSE_NS_EXAMPLE.encode('latin1')
    testmessagesipv4.validate_message_DNS_IPV4_RESPONSE_NS_EXAMPLE(pkt)
    return

def test_inbound_message_DNS_IPV4_QUERY_SOA_EXAMPLE() -> None:
    pkt = testmessagesipv4.DNS_IPV4_QUERY_SOA_EXAMPLE.encode('latin1')
    testmessagesipv4.validate_message_DNS_IPV4_QUERY_SOA_EXAMPLE(pkt)
    return

def test_inbound_message_DNS_IPV4_RESPONSE_SOA_EXAMPLE() -> None:
    pkt = testmessagesipv4.DNS_IPV4_RESPONSE_SOA_EXAMPLE.encode('latin1')
    testmessagesipv4.validate_message_DNS_IPV4_RESPONSE_SOA_EXAMPLE(pkt)
    return

def test_inbound_message_DNS_IPV4_QUERY_PTR_EXAMPLE() -> None:
    pkt = testmessagesipv4.DNS_IPV4_QUERY_PTR_EXAMPLE.encode('latin1')
    testmessagesipv4.validate_message_DNS_IPV4_QUERY_PTR_EXAMPLE(pkt)
    return

def test_inbound_message_DNS_IPV4_RESPONSE_PTR_EXAMPLE() -> None:
    pkt = testmessagesipv4.DNS_IPV4_RESPONSE_PTR_EXAMPLE.encode('latin1')
    testmessagesipv4.validate_message_DNS_IPV4_RESPONSE_PTR_EXAMPLE(pkt)
    return

def test_inbound_message_DNS_IPV4_QUERY_SRV_SIP() -> None:
    pkt = testmessagesipv4.DNS_IPV4_QUERY_SRV_SIP.encode('latin1')
    testmessagesipv4.validate_message_DNS_IPV4_QUERY_SRV_SIP(pkt)
    return

def test_inbound_message_DNS_IPV4_RESPONSE_SRV_SIP() -> None:
    pkt = testmessagesipv4.DNS_IPV4_RESPONSE_SRV_SIP.encode('latin1')
    testmessagesipv4.validate_message_DNS_IPV4_RESPONSE_SRV_SIP(pkt)
    return

def test_inbound_message_DNS_IPV4_QUERY_NAPTR_EXAMPLE() -> None:
    pkt = testmessagesipv4.DNS_IPV4_QUERY_NAPTR_EXAMPLE.encode('latin1')
    testmessagesipv4.validate_message_DNS_IPV4_QUERY_NAPTR_EXAMPLE(pkt)
    return

def test_inbound_message_DNS_IPV4_RESPONSE_NAPTR_EXAMPLE() -> None:
    pkt = testmessagesipv4.DNS_IPV4_RESPONSE_NAPTR_EXAMPLE.encode('latin1')
    testmessagesipv4.validate_message_DNS_IPV4_RESPONSE_NAPTR_EXAMPLE(pkt)
    return

def test_inbound_message_DNS_IPV4_QUERY_DS_EXAMPLE() -> None:
    pkt = testmessagesipv4.DNS_IPV4_QUERY_DS_EXAMPLE.encode('latin1')
    testmessagesipv4.validate_message_DNS_IPV4_QUERY_DS_EXAMPLE(pkt)
    return

def test_inbound_message_DNS_IPV4_RESPONSE_DS_EXAMPLE() -> None:
    pkt = testmessagesipv4.DNS_IPV4_RESPONSE_DS_EXAMPLE.encode('latin1')
    testmessagesipv4.validate_message_DNS_IPV4_RESPONSE_DS_EXAMPLE(pkt)
    return

def test_inbound_message_DNS_IPV4_QUERY_DNSKEY_EXAMPLE() -> None:
    pkt = testmessagesipv4.DNS_IPV4_QUERY_DNSKEY_EXAMPLE.encode('latin1')
    testmessagesipv4.validate_message_DNS_IPV4_QUERY_DNSKEY_EXAMPLE(pkt)
    return

def test_inbound_message_DNS_IPV4_RESPONSE_DNSKEY_EXAMPLE() -> None:
    pkt = testmessagesipv4.DNS_IPV4_RESPONSE_DNSKEY_EXAMPLE.encode('latin1')
    testmessagesipv4.validate_message_DNS_IPV4_RESPONSE_DNSKEY_EXAMPLE(pkt)
    return

def test_inbound_message_DNS_IPV4_MULTI_QUERY_A_AAAA() -> None:
    pkt = testmessagesipv4.DNS_IPV4_MULTI_QUERY_A_AAAA.encode('latin1')
    testmessagesipv4.validate_message_DNS_IPV4_MULTI_QUERY_A_AAAA(pkt)
    return

def test_inbound_message_DNS_IPV6_QUERY_AAAA_EXAMPLE() -> None:
    pkt = testmessagesipv6.DNS_IPV6_QUERY_AAAA_EXAMPLE.encode('latin1')
    testmessagesipv6.validate_message_DNS_IPV6_QUERY_AAAA_EXAMPLE(pkt)
    return

def test_inbound_message_DNS_IPV6_RESPONSE_AAAA_EXAMPLE() -> None:
    pkt = testmessagesipv6.DNS_IPV6_RESPONSE_AAAA_EXAMPLE.encode('latin1')
    testmessagesipv6.validate_message_DNS_IPV6_RESPONSE_AAAA_EXAMPLE(pkt)
    return

def test_inbound_message_DNS_IPV6_QUERY_CNAME_WWW() -> None:
    pkt = testmessagesipv6.DNS_IPV6_QUERY_CNAME_WWW.encode('latin1')
    testmessagesipv6.validate_message_DNS_IPV6_QUERY_CNAME_WWW(pkt)
    return

def test_inbound_message_DNS_IPV6_RESPONSE_CNAME_WWW() -> None:
    pkt = testmessagesipv6.DNS_IPV6_RESPONSE_CNAME_WWW.encode('latin1')
    testmessagesipv6.validate_message_DNS_IPV6_RESPONSE_CNAME_WWW(pkt)
    return

def test_inbound_message_DNS_IPV6_QUERY_MX_EXAMPLE() -> None:
    pkt = testmessagesipv6.DNS_IPV6_QUERY_MX_EXAMPLE.encode('latin1')
    testmessagesipv6.validate_message_DNS_IPV6_QUERY_MX_EXAMPLE(pkt)
    return

def test_inbound_message_DNS_IPV6_RESPONSE_MX_EXAMPLE() -> None:
    pkt = testmessagesipv6.DNS_IPV6_RESPONSE_MX_EXAMPLE.encode('latin1')
    testmessagesipv6.validate_message_DNS_IPV6_RESPONSE_MX_EXAMPLE(pkt)
    return

def test_inbound_message_DNS_IPV6_QUERY_TXT_EXAMPLE() -> None:
    pkt = testmessagesipv6.DNS_IPV6_QUERY_TXT_EXAMPLE.encode('latin1')
    testmessagesipv6.validate_message_DNS_IPV6_QUERY_TXT_EXAMPLE(pkt)
    return

def test_inbound_message_DNS_IPV6_RESPONSE_TXT_EXAMPLE() -> None:
    pkt = testmessagesipv6.DNS_IPV6_RESPONSE_TXT_EXAMPLE.encode('latin1')
    testmessagesipv6.validate_message_DNS_IPV6_RESPONSE_TXT_EXAMPLE(pkt)
    return

def test_inbound_message_DNS_IPV6_QUERY_NS_EXAMPLE() -> None:
    pkt = testmessagesipv6.DNS_IPV6_QUERY_NS_EXAMPLE.encode('latin1')
    testmessagesipv6.validate_message_DNS_IPV6_QUERY_NS_EXAMPLE(pkt)
    return

def test_inbound_message_DNS_IPV6_RESPONSE_NS_EXAMPLE() -> None:
    pkt = testmessagesipv6.DNS_IPV6_RESPONSE_NS_EXAMPLE.encode('latin1')
    testmessagesipv6.validate_message_DNS_IPV6_RESPONSE_NS_EXAMPLE(pkt)
    return

def test_inbound_message_DNS_IPV6_QUERY_SOA_EXAMPLE() -> None:
    pkt = testmessagesipv6.DNS_IPV6_QUERY_SOA_EXAMPLE.encode('latin1')
    testmessagesipv6.validate_message_DNS_IPV6_QUERY_SOA_EXAMPLE(pkt)
    return

def test_inbound_message_DNS_IPV6_RESPONSE_SOA_EXAMPLE() -> None:
    pkt = testmessagesipv6.DNS_IPV6_RESPONSE_SOA_EXAMPLE.encode('latin1')
    testmessagesipv6.validate_message_DNS_IPV6_RESPONSE_SOA_EXAMPLE(pkt)
    return

def test_inbound_message_DNS_IPV6_QUERY_PTR_EXAMPLE() -> None:
    pkt = testmessagesipv6.DNS_IPV6_QUERY_PTR_EXAMPLE.encode('latin1')
    testmessagesipv6.validate_message_DNS_IPV6_QUERY_PTR_EXAMPLE(pkt)
    return

def test_inbound_message_DNS_IPV6_RESPONSE_PTR_EXAMPLE() -> None:
    pkt = testmessagesipv6.DNS_IPV6_RESPONSE_PTR_EXAMPLE.encode('latin1')
    testmessagesipv6.validate_message_DNS_IPV6_RESPONSE_PTR_EXAMPLE(pkt)
    return

def test_inbound_message_DNS_IPV6_QUERY_SRV_SIP() -> None:
    pkt = testmessagesipv6.DNS_IPV6_QUERY_SRV_SIP.encode('latin1')
    testmessagesipv6.validate_message_DNS_IPV6_QUERY_SRV_SIP(pkt)
    return

def test_inbound_message_DNS_IPV6_RESPONSE_SRV_SIP() -> None:
    pkt = testmessagesipv6.DNS_IPV6_RESPONSE_SRV_SIP.encode('latin1')
    testmessagesipv6.validate_message_DNS_IPV6_RESPONSE_SRV_SIP(pkt)
    return

def test_inbound_message_DNS_IPV6_QUERY_NAPTR_EXAMPLE() -> None:
    pkt = testmessagesipv6.DNS_IPV6_QUERY_NAPTR_EXAMPLE.encode('latin1')
    testmessagesipv6.validate_message_DNS_IPV6_QUERY_NAPTR_EXAMPLE(pkt)
    return

def test_inbound_message_DNS_IPV6_RESPONSE_NAPTR_EXAMPLE() -> None:
    pkt = testmessagesipv6.DNS_IPV6_RESPONSE_NAPTR_EXAMPLE.encode('latin1')
    testmessagesipv6.validate_message_DNS_IPV6_RESPONSE_NAPTR_EXAMPLE(pkt)
    return

def test_inbound_message_DNS_IPV6_QUERY_DS_EXAMPLE() -> None:
    pkt = testmessagesipv6.DNS_IPV6_QUERY_DS_EXAMPLE.encode('latin1')
    testmessagesipv6.validate_message_DNS_IPV6_QUERY_DS_EXAMPLE(pkt)
    return

def test_inbound_message_DNS_IPV6_RESPONSE_DS_EXAMPLE() -> None:
    pkt = testmessagesipv6.DNS_IPV6_RESPONSE_DS_EXAMPLE.encode('latin1')
    testmessagesipv6.validate_message_DNS_IPV6_RESPONSE_DS_EXAMPLE(pkt)
    return

def test_inbound_message_DNS_IPV6_QUERY_DNSKEY_EXAMPLE() -> None:
    pkt = testmessagesipv6.DNS_IPV6_QUERY_DNSKEY_EXAMPLE.encode('latin1')
    testmessagesipv6.validate_message_DNS_IPV6_QUERY_DNSKEY_EXAMPLE(pkt)
    return

def test_inbound_message_DNS_IPV6_RESPONSE_DNSKEY_EXAMPLE() -> None:
    pkt = testmessagesipv6.DNS_IPV6_RESPONSE_DNSKEY_EXAMPLE.encode('latin1')
    testmessagesipv6.validate_message_DNS_IPV6_RESPONSE_DNSKEY_EXAMPLE(pkt)
    return

def test_inbound_message_DNS_IPV6_MULTI_QUERY_A_AAAA() -> None:
    pkt = testmessagesipv6.DNS_IPV6_MULTI_QUERY_A_AAAA.encode('latin1')
    testmessagesipv6.validate_message_DNS_IPV6_MULTI_QUERY_A_AAAA(pkt)
    return

