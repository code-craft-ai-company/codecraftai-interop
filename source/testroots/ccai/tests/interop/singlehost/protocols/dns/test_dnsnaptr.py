
import struct
import ccai.testbase as testbase
from ccai.interop.protocols.dns.dnsinboundmessage import DnsInboundMessage
from ccai.interop.protocols.dns.dnsnaptr import DnsNaptr

def test_naptr_parsing_resolves_compression_in_replacement():
    """
    Verify that DnsInboundMessage correctly handles DNS name compression within the
    NAPTR record "replacement" field.
    """
    # 1. Header: ID=0x1234, Flags=Response, ANCOUNT=1
    header = struct.pack('!HHHHHH', 0x1234, 0x8400, 0, 1, 0, 0)
    
    # 2. Answer Record
    # Name: "example.com" at offset 12
    # \x07example\x03com\x00
    name_bytes = b'\x07example\x03com\x00'
    name_offset = 12
    
    # Type: NAPTR (35), Class: IN (1), TTL: 60
    rtype = 35
    rclass = 1
    ttl = 60
    
    # RDATA Construction
    order = 100
    preference = 10
    flags = b'u'
    services = b'sip+D2U'
    regexp = b''
    
    # Pack fixed parts
    # Flags, Services, Regexp are <character-string> (len byte + content)
    rdata_fixed = struct.pack('!HH', order, preference)
    rdata_fixed += struct.pack('!B', len(flags)) + flags
    rdata_fixed += struct.pack('!B', len(services)) + services
    rdata_fixed += struct.pack('!B', len(regexp)) + regexp
    
    # REPLACEMENT: <domain-name>
    # We want to use compression pointing back to "example.com" at offset 12.
    # Pointer: 0xC000 | 12 => 0xC00C
    rdata_replacement = struct.pack('!H', 0xC000 | name_offset)
    
    rdata = rdata_fixed + rdata_replacement
    rdlength = len(rdata)
    
    # Assemble Record
    record = name_bytes + struct.pack('!HHIH', rtype, rclass, ttl, rdlength) + rdata
    
    packet = header + record
    
    # Parse
    msg = DnsInboundMessage(packet)
    testbase.assert_greater(len(msg.answers), 0, "Should have parsed answers")
    
    naptr = msg.answers[0]
    testbase.assert_type(naptr, DnsNaptr, "Expected DnsNaptr record")
    
    testbase.assert_equal(naptr.replacement, "example.com.", "Replacement field did not resolve compression correctly")
    
    return
