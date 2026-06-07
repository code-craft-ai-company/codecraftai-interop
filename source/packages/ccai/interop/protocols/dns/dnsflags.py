
"""
    .. module:: dnsflags
    :platform: Darwin, Linux, Unix, Windows
    :synopsis: dnsflags module.
    
    .. moduleauthor:: Myron Walker <myron.walker@gmail.com>
"""

__author__ = "Myron Walker"
__copyright__ = "Copyright 2025, Code Craft AI LLC"
__credits__ = []

from typing import Optional


from ccai.interop.protocols.dns.dnsconst import DnsQr, DnsOpCode, DnsRespCode


class DnsFlags:
    """
        Note: The bits are in order specified below

           1  1  1  1  1  1
           5  4  3  2  1  0  9  8  7  6  5  4  3  2  1  0
          +--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+
          |QR|   Opcode  |AA|TC|RD|RA|   Z    |   RCODE   |
          +--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+
 
    """

    def __init__(self, *, qr: DnsQr, opcode: DnsOpCode, aa: bool, tc: bool, rd: bool, ra: bool, rcode: DnsRespCode, z: int=0, flags: Optional[int]=None):
        """
            Sets the flags for the DNS header.

            :param qr: Indicates if the message is a query or a response
            :param opcode: Specifies the opcode for the message
            :param aa: Specifies that the message is an authoritative answer
            :param tc: Specifies that the message is truncated
            :param rd: Specifies that recursion is desired (set in queries only)
            :param ra: Specifies that recursion is available (set in responses only)
            :param rcode: The response code associated with the message
            :param z: Not used, should be zero
            :param flags: Only used by DnsFlags.parse to bypass duplicate work of rebuilding a flags int.

        """
        self._qr = qr
        self._opcode = opcode
        self._aa = aa
        self._tc = tc
        self._rd = rd
        self._ra = ra
        self._rcode = rcode
        self._z = z
       
        if flags is not None:
            self._flags = self._compile_flags(flags)

        return

    @property
    def aa(self) -> bool:
        """
            Indicates that the messgae is an authoritative answer.
        """
        return self._aa

    @property
    def opcode(self) -> DnsOpCode:
        """
            The opcode for the message.
        """
        return self._opcode
    
    @property
    def qr(self) -> DnsQr:
        """
            Indicates if the message is a query or response.
        """
        return self._qr
    
    @property
    def ra(self) -> bool:
        """
            Specifies that recursion is available (set in responses only).
        """
        return self._ra
    
    @property
    def rcode(self) -> DnsRespCode:
        """
            The response code associated with the message
        """
        return self._rcode

    @property
    def rd(self) -> bool:
        """
            Specifies that recursion is desired (set in queries only).
        """
        return self._rd


    @property
    def tc(self) -> bool:
        """
            Specifies that the message is truncated.
        """
        return self._tc
    
    @property
    def z(self) -> int:
        """
            Not used, should be zero.
        """
        return self._z

    def flags(self) -> int:
        """
            Converts a :class:`DnsFlags` object to a flags integer.
        """
        
        flags: int = (self._qr << 15) & 0x8000
        flags |= (self._opcode << 11) & 0x7800
        flags |= (int(self._aa) << 10) & 0x0400
        flags |= (int(self._tc) << 9) & 0x0200
        flags |= (int(self._rd) << 8) & 0x0100
        flags |= (int(self._ra) << 7) & 0x0080
        flags |= (self._z << 4) & 0x0070
        flags |= self._rcode & 0x000F

        return flags

    def _compile_flags(self, flags: int):
        """
            Decomposes a flags integer into the individual flag fields.

            :param flags: Integer containing the encoded flag bits.
        """

        self._qr = DnsQr((flags & 0x8000) >> 15)
        self._opcode = DnsOpCode((flags & 0x7800) >> 11)
        self._aa = True if (flags & 0x0400) >> 10 else False
        self._tc = True if (flags & 0x0200) >> 9 else False
        self._rd = True if (flags & 0x0100) >> 8 else False
        self._ra = True if (flags & 0x0080) >> 7 else False
        self._z = (flags & 0x0070) >> 4
        self._rcode = DnsRespCode(flags & 0x000F)

        return flags

    @classmethod
    def parse(cls, flags: int) -> "DnsFlags":
        """
            Parses a flags integer and converts it to a :class:`DnsFlags` object.
        """
        qr = DnsQr((flags & 0x8000) >> 15)
        opcode = DnsOpCode((flags & 0x7800) >> 11)
        aa = True if (flags & 0x0400) >> 10 else False
        tc = True if (flags & 0x0200) >> 9 else False
        rd = True if (flags & 0x0100) >> 8 else False
        ra = True if (flags & 0x0080) >> 7 else False
        z = (flags & 0x0070) >> 4
        rcode = DnsRespCode(flags & 0x000F)

        fobj = DnsFlags(qr=qr, opcode=opcode, aa=aa, tc=tc, rd=rd, ra=ra, rcode=rcode, z=z, flags=flags)

        return fobj
    
    def __repr__(self):
        """
            Provides a reproducible string representation of the instance.

            :returns: A string that can be used to reconstruct the object.
        """

        repval = (
            f"DnsFlags(qr={self._qr}, opcode={self._opcode}, aa={self._aa}, tc={self._tc},"
            f" rd={self._rd}, ra={self._ra}, rcode={self._rcode}, z={self._z})"
        )

        return repval

    def __str__(self) -> str:
        """
            Returns a user friendly string representation of the instance.

            :returns: Readable string describing the flags.
        """
        return repr(self)


DEFAULT_DNS_FLAGS_QUERY = DnsFlags(qr=DnsQr.Query, opcode=DnsOpCode.Query, aa=False, tc=False, rd=False, ra=False, rcode=DnsRespCode.NoError)
