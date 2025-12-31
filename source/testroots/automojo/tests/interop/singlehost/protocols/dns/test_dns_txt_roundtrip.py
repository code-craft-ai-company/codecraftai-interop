
import struct
import automojo.testbase as testbase
from automojo.interop.protocols.dns.dnsinboundmessage import DnsInboundMessage
from automojo.interop.protocols.dns.dnsoutboundmessage import DnsOutboundMessage
from automojo.interop.protocols.dns.dnsflags import DnsFlags
from automojo.interop.protocols.dns.dnstext import DnsText

def test_txt_record_roundtrip_preserves_rdata():
    """
    Verify that a TXT record parsed from a packet is re-serialized correctly without
    double-encoding the character strings in the RDATA.
    """
    # Construct a raw DNS packet with a TXT record
    # ID: 0x1234
    # Flags: 0x8400 (Response, Authoritative, No Error)
    # QDCOUNT: 0
    # ANCOUNT: 1
    # NSCOUNT: 0
    # ARCOUNT: 0
    
    header = struct.pack('!HHHHHH', 0x1234, 0x8400, 0, 1, 0, 0)
    
    # Answer Record:
    # Name: example.com (0x07example0x03com0x00)
    # Type: TXT (16)
    # Class: IN (1)
    # TTL: 60
    # RDLENGTH: 8
    # RDATA: \x03foo\x03bar
    
    name = b'\x07example\x03com\x00'
    rtype = 16
    rclass = 1
    ttl = 60
    # The RDATA contains two character-strings: "foo" (len 3) and "bar" (len 3)
    rdata = b'\x03foo\x03bar'
    rdlength = len(rdata)
    
    record = name + struct.pack('!HHIH', rtype, rclass, ttl, rdlength) + rdata
    
    original_packet_data = header + record
    
    # Parse the packet
    msg = DnsInboundMessage(original_packet_data)
    testbase.assert_greater(len(msg.answers), 0, "Should have parsed at least one answer")

    txt_record = msg.answers[0]
    testbase.assert_type(txt_record, DnsText, "Answer should be a DnsText record")
    
    # Verify the internal storage matches the raw RDATA (because we set is_raw_rdata=True)
    # Note: Depending on implementation, DnsText._text might be the raw bytes or parsed.
    # In the fix, we passed the raw bytes from _read_string_characters which reads the whole RDATA.
    testbase.assert_equal(txt_record.text, rdata, "Parsed text payload should match raw RDATA")
    
    # Create outbound message
    out_flags = DnsFlags.parse(0) 
    out_msg = DnsOutboundMessage(out_flags, id=0x1234, multicast=False)
    
    # Add the parsed record to answers
    out_msg.add_answer(txt_record)
    
    # Serialize
    packets = out_msg.packets()
    new_packet_data = packets[0]
    
    # Now validte the new packet data contains the correct RDATA
    # We can parse it again to be sure
    new_msg = DnsInboundMessage(new_packet_data)
    testbase.assert_greater(len(new_msg.answers), 0, "Should have parsed answers from new packet")
    
    new_txt_record = new_msg.answers[0]
    new_rdata = new_txt_record.text
    
    testbase.assert_equal(new_rdata, rdata, "Round-tripped RDATA should match original RDATA")
    
    return
