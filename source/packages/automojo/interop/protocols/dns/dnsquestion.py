"""
    .. module:: dnsquestion
    :platform: Darwin, Linux, Unix, Windows
    :synopsis: Contains the DnsQuestion object which represents a DNS question to be posed to the DNS service.
    
    .. moduleauthor:: Myron Walker <myron.walker@gmail.com>
"""

__author__ = "Myron Walker"
__copyright__ = "Copyright 2025, Automation Mojo LLC"
__credits__ = []


from automojo.interop.protocols.dns.dnsconst import DnsRecordClass, DnsRecordType
from automojo.interop.protocols.dns.dnsrecord import DnsRecord

class DnsQuestion:
    """
        The :class:`DnsQuestion` object is utilized to formulate DNS queries and to check to
        see if a :class:`DnsRecord` answers the query provided.
    """
    def __init__(
        self,
        name: str,
        rtype: DnsRecordType,
        rclass: DnsRecordClass,
        *,
        suppress_compression: bool = False,
    ) -> None:
        """
            Constructs a DNS query question.

            :param name: Name to query.
            :param rtype: Record type.
            :param rclass: Record class with flags.
        """
        self._name = name
        self._key = name.lower()
        self._rtype = rtype
        self._rclass = DnsRecordClass(rclass & DnsRecordClass.MASK)
        self._unique = (rclass & DnsRecordClass.UNIQUE) != 0
        self._suppress_compression = suppress_compression
        return

    @property
    def name(self):
        """
            The name being queried.

            :returns: The DNS name associated with this question.
        """
        return self._name

    @property
    def rclass(self):
        """
            Record class for the query.

            :returns: The :class:`DnsRecordClass` of the query.
        """
        return self._rclass

    @property
    def rtype(self):
        """
            Record type for the query.

            :returns: The :class:`DnsRecordType` requested.
        """
        return self._rtype

    @property
    def unique(self):
        """
            Indicates whether this question expects a unique record.

            :returns: ``True`` if a unique record is requested.
        """
        return self._unique

    @property
    def suppress_compression(self) -> bool:
        """Indicates if compression should be suppressed when writing this question."""

        return self._suppress_compression

    def answered_by(self, rec: DnsRecord) -> bool:
        """
            Returns True if the question is answered by the record.

            :param rec: Record to test against this question.

            :returns: ``True`` if the record answers the question.
        """
        bval = False
        if self._rclass == rec._rclass:
            if self._rtype == rec._rtype or self._rtype == DnsRecordType.ANY:
               bval = self._key == rec.key
        return bval

    def as_query_bytes(self) -> bytes:
        """
            Formats the DNS question as a byte stream for transmission.

            :returns: Encoded question bytes.
        """

        qstr = "question\x00%s,%s" % (self._rtype.name, self._rclass.name)

        if self._unique:
            qstr += "-unique,"
        else:
            qstr += ","

        qstr += self._name

        dnsbytes = qstr.encode("utf-8")

        return dnsbytes

    def as_dns_string(self) -> str:
        """
            Formats the DNS question as a string suitable for debugging and
            testing.

            :returns: A DNS formatted string representation of this question.
        """

        qstr = "question[%s,%s" % (self._rtype.name, self._rclass.name)

        if self._unique:
            qstr += "-unique,"
        else:
            qstr += ","

        qstr += self._name
        qstr += "]"

        return qstr
