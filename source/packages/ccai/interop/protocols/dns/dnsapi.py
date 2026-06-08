
"""
    .. module:: dnsapi
    :platform: Darwin, Linux, Unix, Windows
    :synopsis: dnsapi module.
    
    .. moduleauthor:: Myron Walker <myron.walker@gmail.com>
"""


__author__ = "Myron Walker"
__copyright__ = "Copyright 2025, Code Craft AI LLC"
__credits__ = []

from typing import List

from ccai.interop.protocols.dns.dnsconst import DnsRecordClass, DnsRecordType

from ccai.interop.protocols.dns.dnsquestion import DnsQuestion

from ccai.interop.protocols.dns.dnsserver import DnsServer

def dns_query_name(name: str, rtype: DnsRecordType, rclass: DnsRecordClass):

    """
        Builds a DNS query string for a single name.

        :param name: The name to query.
        :param rtype: Record type to request.
        :param rclass: Record class to request.

        :returns: A string formatted for DNS query transmission.
    """

    question = DnsQuestion(name, rtype, rclass)

    query_str = question.as_dns_string()

    return query_str

def dns_query_services(service_types: List[str], rtype: DnsRecordType=DnsRecordType.PTR, rclass: DnsRecordClass=DnsRecordClass.IN):
    """
        Queries for DNS services of the specified types using mDNS.

        :param service_types: List of service types to query.
        :param rtype: DNS record type used for the query.
        :param rclass: DNS record class used for the query.

        :returns: ``None``
    """

    service = DnsServer()

    service.start()

    service.wait()

    return
