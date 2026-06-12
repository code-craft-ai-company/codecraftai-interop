"""
    .. module:: dnsinboundmessage
    :platform: Darwin, Linux, Unix, Windows
    :synopsis: Contains the DnsIncoming object which is used to represent an incoming DNS packet and to provide
    methods for processing the packet.
    
    .. moduleauthor:: Myron Walker <myron.walker@gmail.com>
"""

__author__ = "Myron Walker"
__copyright__ = "Copyright 2025, Code Craft AI LLC"
__credits__ = []



from typing import List, Optional, Tuple, Union

from ccai.xmodules.xlogging.enhancedloggers import getEnhancedLogger
import os
import struct

from ccai.interop.protocols.dns.dnsconst import (
    DnsQr,
    DnsRecordType,
    DnsRecordClass,
    DNS_COMP_MASK,
    DNS_OFFSET_MASK
)

from ccai.interop.protocols.dns.dnsflags import DnsFlags
from ccai.interop.protocols.dns.exceptions import DnsDecodeError

from ccai.interop.protocols.dns.dnsaddress import DnsAddress
from ccai.interop.protocols.dns.dnshostinfo import DnsHostInfo
from ccai.interop.protocols.dns.dnspointer import DnsPointer
from ccai.interop.protocols.dns.dnsquestion import DnsQuestion
from ccai.interop.protocols.dns.dnsrecord import DnsRecord
from ccai.interop.protocols.dns.dnsservice import DnsService
from ccai.interop.protocols.dns.dnsmailexchange import DnsMailExchange
from ccai.interop.protocols.dns.dnstext import DnsText
from ccai.interop.protocols.dns.dnsnaptr import DnsNaptr
from ccai.interop.protocols.dns.dnssoa import DnsSoa

logger = getEnhancedLogger()

class DnsInboundMessage:
    """
        The :class:`DnsInboundMessage` object is used to read incoming DNS packets.
    """

    def __init__(self, data: bytes, source_endpoint: Union[str, bytes, Tuple[str, int], None] = None) -> None:
        """
            Constructor from string holding bytes of packet

            :param data: Raw packet bytes to parse.
            :param source_endpoint: The address the packet was received from.
        """
        self._offset: int = 0

        self._data: bytes = data
        self._questions: List[DnsQuestion] = []
        self._answers: List[DnsRecord] = []
        self._authorities: List[DnsRecord] = []
        self._additionals: List[DnsRecord] = []

        self._id: int = 0
        self._flags: DnsFlags = None  # type: int
        self._num_questions: int = 0
        self._num_answers: int = 0
        self._num_authorities: int = 0
        self._num_additionals: int = 0
        self._valid: bool = False
        self._source = "unknown"

        if source_endpoint is not None:
            if isinstance(source_endpoint, str):
                self._source = source_endpoint
            elif isinstance(source_endpoint, bytes):
                self._source = source_endpoint.decode('utf-8')
            else:
                self._source = f"{source_endpoint[0]}:{source_endpoint[1]}"

        try:
            self._ingest_header()
            self._ingest_questions()
            self._ingest_others()

            self._valid = True

        except (IndexError, struct.error, DnsDecodeError):
            logger.error('Choked at offset %d while unpacking %r', self._offset, data, exc_info=True)
            pass

        return

    @property
    def answers(self) -> List[DnsRecord]:
        """
            List of answer records contained in the message.
        """
        return self._answers

    @property
    def authorities(self) -> List[DnsRecord]:
        """
            List of authority records contained in the message.
        """
        return self._authorities

    @property
    def additionals(self) -> List[DnsRecord]:
        """
            List of additional records contained in the message.
        """
        return self._additionals

    @property
    def data(self) -> bytes:
        """
            Raw packet bytes that were received.

            :returns: Byte string containing the DNS message.
        """
        return self._data

    @property
    def flags(self) -> DnsFlags:
        """
            Parsed DNS flags describing the message attributes.

            :returns: A :class:`DnsFlags` instance.
        """
        return self._flags

    @property
    def id(self) -> int:
        """
            Identifier associated with this DNS message.

            :returns: Numeric message id.
        """
        return self._id

    @property
    def questions(self) -> List[DnsQuestion]:
        """
            List of DNS questions contained within the message.

            :returns: List of :class:`DnsQuestion` objects.
        """
        return self._questions

    @property
    def valid(self) -> bool:
        """
            Whether the inbound message was parsed successfully and is well-formed.

            :returns: True if the message parsed without error, otherwise False.
        """
        return self._valid

    def is_query(self) -> bool:
        """
            Returns true if this is a query
        """
        result = self.flags._qr == DnsQr.Query
        return result

    def is_response(self) -> bool:
        """
            Returns true if this is a response
        """
        result = self.flags._qr == DnsQr.Response
        return result

    def _ingest_header(self) -> None:
        """
            Processes the header portion of the message
        """

        self._id = struct.unpack_from(b'!H', self._data, self._offset)[0]
        self._offset += 2

        flags_int = struct.unpack_from(b'!H', self._data, self._offset)[0]
        self._offset += 2
        self._flags = DnsFlags.parse(flags_int)
        
        self._num_questions = struct.unpack_from(b'!H', self._data, self._offset)[0]
        self._offset += 2

        self._num_answers = struct.unpack_from(b'!H', self._data, self._offset)[0]
        self._offset += 2

        self._num_authorities = struct.unpack_from(b'!H', self._data, self._offset)[0]
        self._offset += 2 

        self._num_additionals = struct.unpack_from(b'!H', self._data, self._offset)[0]
        self._offset += 2

        return

    def _ingest_questions(self) -> None:
        """
            Processes the questions section of the message
        """

        for i in range(self._num_questions):
            name = self._read_name()
            rtype, rclass = self._read_type_and_class()

            question = DnsQuestion(name, rtype, rclass)
            self._questions.append(question)
        
        return
    
    def _ingest_others(self) -> None:
        """
            Processes the answers, authorities and additionals section of the message
        """
        
        # Process Answers
        for _ in range(self._num_answers):
            rec = self._read_record()
            if rec is not None:
                self._answers.append(rec)

        # Process Authorities
        for _ in range(self._num_authorities):
            rec = self._read_record()
            if rec is not None:
                self._authorities.append(rec)

        # Process Additionals
        for _ in range(self._num_additionals):
            rec = self._read_record()
            if rec is not None:
                self._additionals.append(rec)

        return

    def _read_record(self) -> Optional[DnsRecord]:
        """
            Reads a single resource record from the current offset.
        """
        domain = self._read_name()

        rtype, rclass = self._read_type_and_class()
        ttl = self._read_ttl()
        length = self._read_unsigned_short()

        rec = None  # type: Optional[DnsRecord]

        rdata_end = self._offset + length
        if rdata_end > len(self._data):
            raise DnsDecodeError(
                f"DnsInboundMessage[{self._source}] RDATA length exceeds packet bounds. offset={self._offset} length={length}"
            )

        if rtype == DnsRecordType.SRV:
            priority = self._read_unsigned_short()
            weight = self._read_unsigned_short()
            port = self._read_unsigned_short()
            server = self._read_name()

            rec = DnsService(
                domain,
                rtype,
                rclass,
                ttl,
                priority,
                weight,
                port,
                server,
            )
        else:
            if rtype == DnsRecordType.A:
                address = self._read_string_characters(4)
                rec = DnsAddress(domain, rtype, rclass, ttl, address)

            elif rtype == DnsRecordType.AAAA:
                address = self._read_string_characters(16)
                rec = DnsAddress(domain, rtype, rclass, ttl, address)

            elif rtype == DnsRecordType.CNAME or rtype == DnsRecordType.PTR:
                alias = self._read_name()
                rec = DnsPointer(domain, rtype, rclass, ttl, alias)

            elif rtype == DnsRecordType.NS:
                alias = self._read_name()
                rec = DnsPointer(domain, rtype, rclass, ttl, alias)

            elif rtype == DnsRecordType.MX:
                preference = self._read_unsigned_short()
                exchange = self._read_name()
                rec = DnsMailExchange(domain, rtype, rclass, ttl, preference, exchange)

            elif rtype == DnsRecordType.TXT:
                text = self._read_string_characters(length)

                rec = DnsText(domain, rtype, rclass, ttl, text, is_raw_rdata=True)

            elif rtype == DnsRecordType.NAPTR:
                order = self._read_unsigned_short()
                preference = self._read_unsigned_short()
                flags = self._read_string_bounded(rdata_end).decode("utf-8", "replace")
                services = self._read_string_bounded(rdata_end).decode("utf-8", "replace")
                regexp = self._read_string_bounded(rdata_end, reserve=1).decode("utf-8", "replace")

                replacement = self._read_name()

                rec = DnsNaptr(
                    domain,
                    rtype,
                    rclass,
                    ttl,
                    order,
                    preference,
                    flags,
                    services,
                    regexp,
                    replacement,
                )

            elif rtype == DnsRecordType.SOA:
                mname = self._read_name()
                rname = self._read_name()
                serial = self._read_unsigned_int()
                refresh = self._read_unsigned_int()
                retry = self._read_unsigned_int()
                expire = self._read_unsigned_int()
                minimum = self._read_unsigned_int()

                rec = DnsSoa(
                    domain,
                    rtype,
                    rclass,
                    ttl,
                    mname,
                    rname,
                    serial,
                    refresh,
                    retry,
                    expire,
                    minimum,
                )

            elif rtype == DnsRecordType.HINFO:
                host_cpu = self._read_string().decode('utf-8')
                host_os = self._read_string().decode('utf-8')

                rec = DnsHostInfo(
                    domain,
                    rtype,
                    rclass,
                    ttl,
                    host_cpu,
                    host_os,
                )

            else:
                # Try to ignore types we don't know about
                # Skip the payload for the resource record so the next
                # records can be parsed correctly
                self._offset += length

        if self._offset < rdata_end:
            # Ensure we advance past any unread bytes inside the RDATA so the next record starts correctly.
            self._offset = rdata_end
        elif self._offset > rdata_end:
            raise DnsDecodeError(
                f"DnsInboundMessage[{self._source}] Parsed past end of RDATA. end={rdata_end} offset={self._offset}"
            )

        return rec
    

    def _read_name(self) -> str:
        """
            Reads a domain name from the packet
        """
        result = ''
        start = self._offset
        cursor = start

        result, consumed = self._read_name_at_offset(start, cursor, [])

        if consumed == 0:
            raise DnsDecodeError(f"DnsInboundMessage[{self._source}] Empty name. start={start} consumed={consumed}")

        self._offset += consumed

        return result


    def _read_name_at_offset(self, start: int, cursor: int, followed: List[int]) -> str:
        """
            Reads a domain name component starting at the specified offset.

            :param start: Offset in the packet where the name began.
            :param cursor: Current read position within the packet buffer.
            :param followed: List of offsets already followed to detect loops.

            :returns: Tuple of the decoded name fragment and bytes consumed.
        """

        result = ''
        consumed = 0

        while True:
            if cursor >= len(self._data):
                raise DnsDecodeError(
                    f"DnsInboundMessage[{self._source}] Name decoding exceeded packet length. cursor={cursor}"
                )

            first_octet = self._data[cursor]

            if first_octet == 0x00:
                if len(followed) == 0:
                    consumed += 1
                break

            comp_flags = (first_octet & DNS_COMP_MASK)

            if comp_flags == 0x00:
                comp_start = cursor + 1
                comp_length = first_octet & DNS_OFFSET_MASK
                if comp_length == 0:
                    raise DnsDecodeError(
                        f"DnsInboundMessage[{self._source}] Zero-length label encountered mid-name at offset {cursor}."
                    )

                comp_val = self._read_utf(comp_start, comp_length)
                result = f"{result}{comp_val}."

                cursor = comp_start + comp_length

                # We only consume bytes of the packet if we have not yet followed a pointer.
                if len(followed) == 0:
                    consumed += comp_length + 1

            elif comp_flags == DNS_COMP_MASK:
                if cursor + 1 >= len(self._data):
                    raise DnsDecodeError(
                        f"DnsInboundMessage[{self._source}] Incomplete name compression pointer at offset {cursor}."
                    )

                second_octet = self._data[cursor + 1]
                if len(followed) == 0:
                    consumed += 2

                offset_ptr = ((first_octet & DNS_OFFSET_MASK) << 8) + second_octet
                if offset_ptr >= start:
                    err_msg_lines = [
                        f"DnsInboundMessage[{self._source}] Invalid name compression offset pointer.",
                        f"    NAME START: {start}",
                        f"    OFFSET POINTER: {offset_ptr}",
                        f"    FOLLOWED: {followed}"
                    ]
                    err_msg = os.linesep.join(err_msg_lines)
                    raise DnsDecodeError(err_msg)
                if offset_ptr in followed:
                    err_msg_lines = [
                        f"DnsInboundMessage[{self._source}] Loop detected in name compression.",
                        f"    NAME START: {start}",
                        f"    OFFSET POINTER: {offset_ptr}",
                        f"    FOLLOWED: {followed}"
                    ]
                    err_msg = os.linesep.join(err_msg_lines)
                    raise DnsDecodeError(err_msg)

                followed.append(offset_ptr)
                comp_val, _ = self._read_name_at_offset(start, offset_ptr, followed)
                result = f"{result}{comp_val}"

                break  # Once we hit a pointer, then that is the end of the name

            else:
                err_msg_lines = [
                        f"DnsInboundMessage[{self._source}] Invalid name compression flags.",
                        f"    NAME START: {start}",
                        f"    FLAGS: {comp_flags}",
                        f"    FOLLOWED: {followed}"
                    ]
                err_msg = os.linesep.join(err_msg_lines)
                raise DnsDecodeError(err_msg)

        return result, consumed


    def _read_string(self) -> bytes:
        """
            Reads a character string from the packet
        """
        length = int(self._data[self._offset])
        self._offset += 1

        strval = self._read_string_characters(length)

        return strval

    def _read_string_bounded(self, end_offset: int, reserve: int = 0) -> bytes:
        """
            Reads a character string ensuring the read stays within a known boundary.

            :param end_offset: Absolute offset within the packet where the current
                               record's RDATA should end.
            :param reserve: Number of bytes to leave unread to allow parsing of
                            fields following the string.
        """
        if self._offset >= end_offset:
            raise DnsDecodeError(
                f"DnsInboundMessage[{self._source}] Attempt to read string past RDATA boundary. offset={self._offset} end={end_offset}"
            )

        length = int(self._data[self._offset])
        self._offset += 1

        remaining = max(0, end_offset - self._offset - reserve)
        read_length = min(length, remaining)

        strval = self._read_string_characters(read_length)

        return strval

    def _read_string_characters(self, length: int) -> bytes:
        """
            Reads a string of a given length from the packet
        """
        available = len(self._data) - self._offset
        read_length = min(length, available)

        strval = self._data[self._offset : self._offset + read_length]
        self._offset += read_length
        return strval

    def _read_ttl(self) -> int:
        """
            Reads an integer ttl from the packet
        """
        # Unpack 4 bytes as unsigned int using network byte order !I
        val = int(self._unpack(b'!I')[0])

        return val

    def _read_type_and_class(self) -> Tuple[DnsRecordType, DnsRecordClass]:
        """
            Reads an integer ttl from the packet
        """

        rtype, rclass = self._unpack(b'!HH')

        try:
            rtype = DnsRecordType(rtype)
            rclass = DnsRecordClass(rclass)
        except ValueError:
            pass # Unable to convert record and class

        return rtype, rclass

    def _read_unsigned_int(self) -> int:
        """
            Reads an integer from the packet
        """
        # Unpack 4 bytes as unsigned int using network byte order !I
        val = int(self._unpack(b'!I')[0])
        return val

    def _read_unsigned_short(self) -> int:
        """
            Reads an unsigned short from the packet
        """
        # Unpack 2 bytes as unsigned short using network byte order !H
        val = int(self._unpack(b'!H')[0])
        return val

    def _read_utf(self, offset: int, length: int) -> str:
        """
            Reads a UTF-8 string of a given length from the packet.

            :param offset: Byte offset within the packet buffer.
            :param length: Number of bytes to read.

            :returns: Decoded UTF-8 string.
        """
        utfval = str(self._data[offset : offset + length], 'utf-8', 'replace')
        return utfval

    def _unpack(self, format_: bytes) -> tuple:
        """
            Unpacks bytes from the internal buffer using the supplied format.

            :param format_: Struct format specifier for the unpack operation.

            :returns: Tuple of unpacked values.
        """

        length = struct.calcsize(format_)
        info = struct.unpack(format_, self._data[self._offset : self._offset + length])
        self._offset += length
        return info

    def __str__(self) -> str:
        """
            Returns a formatted string describing the inbound message.

            :returns: Readable representation of the message contents.
        """
        strval = '<DnsInboundMessage:{%s}>' % ', '.join(
            [
                'id=%s' % self._id,
                'flags=%s' % self._flags,
                'n_q=%s' % self._num_questions,
                'n_ans=%s' % self._num_answers,
                'n_auth=%s' % self._num_authorities,
                'n_add=%s' % self._num_additionals,
                'questions=%s' % self._questions,
                'answers=%s' % self._answers,
                'authorities=%s' % self._authorities,
                'additionals=%s' % self._additionals,
            ]
        )
        return strval



if __name__ == "__main__":

    packet = b"\x00\x00\x84\x00\x00\x00\x00\x02\x00\x00\x00\x04'HP Color LaserJet Pro M478f-9f [834BAB]\x04_ipp\x04_tcp\x05local\x00\x00\x10\x80\x01\x00\x00\x11\x94\x02\xda\ttxtvers=15adminurl=http://HP0068EB834BAB.local./#hId-pgAirPrint\x05note=\x0bpriority=20\x08qtotal=1\x07TLS=1.2\x0crp=ipp/print)UUID=5f1123e1-7b3c-5b59-698a-e4916b1b0e1a(product=(HP Color LaserJet Pro M478f-9f)!ty=HP Color LaserJet Pro M478f-9f\nusb_MFG=HP#usb_MDL=Color LaserJet Pro M478f-9f\x07Color=T\x08Duplex=T\xfepdl=application/vnd.hp-PCL,application/vnd.hp-PCLXL,application/postscript,application/msword,application/pdf,image/jpeg,image/urf,image/pwg-raster,application/PCLm,application/vnd.openxmlformats-officedocument.wordprocessingml.document,application/vnd.m\x11PaperMax=legal-A4dURF=CP1,MT1-2-8-9-10-11,PQ3-4-5,RS600,SRGB24,OB10,W8,DEVW8,DEVRGB24,ADOBERGB24,DM3,IS19-1-2,V1.4,FN3\rkind=document\x06Scan=T\x14mopria-certified=2.0\x0erfo=ipp/faxout\x05Fax=T\xc0\x0c\x00!\x80\x01\x00\x00\x00x\x00\x17\x00\x00\x00\x00\x02w\x0eHP0068EB834BAB\xc0>\xc3;\x00\x01\x80\x01\x00\x00\x00x\x00\x04\xac\x10\x01\x03\xc3;\x00\x1c\x80\x01\x00\x00\x00x\x00\x10\xfe\x80\x00\x00\x00\x00\x00\x00\x02h\xeb\xff\xfe\x83K\xac\xc0\x0c\x00/\x80\x01\x00\x00\x11\x94\x00\t\xc0\x0c\x00\x05\x00\x00\x80\x00@\xc3;\x00/\x80\x01\x00\x00\x00x\x00\x08\xc3;\x00\x04@\x00\x00\x08"

    msg = DnsInboundMessage(packet)
