
"""
    .. module:: dnsapi
    :platform: Darwin, Linux, Unix, Windows
    :synopsis: dnsapi module.
    
    .. moduleauthor:: Myron Walker <myron.walker@gmail.com>
"""


__author__ = "Myron Walker"
__copyright__ = "Copyright 2025, Automation Mojo LLC"
__credits__ = []

from typing import List

from automojo.interop.protocols.dns.dnsconst import DnsRecordClass, DnsRecordType

from automojo.interop.protocols.dns.dnsquestion import DnsQuestion

from automojo.interop.protocols.dns.dnsserver import DnsServer

def dns_query_name(name: str, rtype: DnsRecordType, rclass: DnsRecordClass):

    question = DnsQuestion(name, rtype, rclass)

    query_str = question.as_dns_string()

    return query_str

def dns_query_services(service_types: List[str], rtype: DnsRecordType=DnsRecordType.PTR, rclass: DnsRecordClass=DnsRecordClass.IN):
    
    service = DnsServer()
    
    service.start()

    service.wait()

    return
