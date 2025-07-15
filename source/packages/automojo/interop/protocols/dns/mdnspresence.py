"""
    .. module:: mdnspresence
    :platform: Darwin, Linux, Unix, Windows
    :synopsis: Implements an mDNS presence service for responding to DNS queries.

    .. moduleauthor:: Myron Walker <myron.walker@gmail.com>
"""

__author__ = "Myron Walker"
__copyright__ = "Copyright 2025, Automation Mojo LLC"
__credits__ = []

from typing import Dict, List, Optional, Tuple

import socket
import threading

from automojo.networking.multicast import create_multicast_listener_socket
from automojo.networking.constants import MDNS_GROUP_ADDR, MDNS_PORT

from automojo.interop.protocols.dns.dnsconst import (
    DNS_RECEIVE_BUFFER,
    DnsRecordClass,
    DnsRecordType,
)
from automojo.interop.protocols.dns.dnsflags import DnsFlags, DnsQr, DnsOpCode, DnsRespCode
from automojo.interop.protocols.dns.dnsinboundmessage import DnsInboundMessage
from automojo.interop.protocols.dns.dnsoutboundmessage import DnsOutboundMessage
from automojo.interop.protocols.dns.dnsquestion import DnsQuestion
from automojo.interop.protocols.dns.dnsrecord import DnsRecord
from automojo.interop.protocols.dns.dnsservice import DnsService
from automojo.interop.protocols.dns.dnspointer import DnsPointer
from automojo.interop.protocols.dns.dnstext import DnsText
from automojo.interop.protocols.dns.dnsaddress import DnsAddress


class MdnsPresence:
    """Simple mDNS presence service for advertising a single service."""

    def __init__(
        self,
        instance_name: str,
        service_type: str,
        port: int,
        *,
        address: str = "127.0.0.1",
        txt: bytes = b"",
        multicast_address: str = MDNS_GROUP_ADDR,
        multicast_port: int = MDNS_PORT,
        ttl: int = 60,
    ) -> None:
        self._instance_name = instance_name.rstrip(".")
        self._service_type = service_type.rstrip(".") + "."
        self._port = port
        self._host_name = f"{self._instance_name}.local."
        self._ip_address = address

        self._multicast_address = multicast_address
        self._multicast_port = multicast_port
        self._ttl = ttl

        self._lock = threading.Lock()
        self._running = False

        self._presence_sock: Optional[socket.socket] = None
        self._presence_thread: Optional[threading.Thread] = None

        self._records: List[DnsRecord] = []
        self._build_records(txt)
        return

    def _build_records(self, txt: bytes) -> None:
        svc_instance = f"{self._instance_name}.{self._service_type}"
        self._ptr_record = DnsPointer(
            self._service_type,
            DnsRecordType.PTR,
            DnsRecordClass.IN,
            self._ttl,
            svc_instance,
        )
        self._srv_record = DnsService(
            svc_instance,
            DnsRecordType.SRV,
            DnsRecordClass.IN,
            self._ttl,
            priority=0,
            weight=0,
            port=self._port,
            server=self._host_name,
        )
        self._txt_record = DnsText(
            svc_instance,
            DnsRecordType.TXT,
            DnsRecordClass.IN,
            self._ttl,
            txt,
        )
        self._a_record = DnsAddress(
            self._host_name,
            DnsRecordType.A,
            DnsRecordClass.IN,
            self._ttl,
            socket.inet_aton(self._ip_address),
        )
        self._records = [
            self._ptr_record,
            self._srv_record,
            self._txt_record,
            self._a_record,
        ]
        return

    def start(self) -> None:
        if self._running:
            raise RuntimeError("mDNS Presence already running")

        sgate = threading.Event()
        sgate.clear()

        self._presence_thread = threading.Thread(
            target=self._presence_thread_entry,
            name="am-mdns-presence",
            args=(sgate,),
            daemon=True,
        )
        self._presence_thread.start()
        sgate.wait()
        return

    def stop(self) -> None:
        self._running = False
        if self._presence_thread is not None:
            self._presence_thread.join(timeout=2)
            self._presence_thread = None
        if self._presence_sock is not None:
            self._presence_sock.close()
            self._presence_sock = None
        return

    def _get_presence_socket(self) -> socket.socket:
        sock = None
        self._lock.acquire()
        try:
            if self._presence_sock is None:
                self._presence_sock = create_multicast_listener_socket(
                    self._multicast_address,
                    self._multicast_port,
                    family=socket.AF_INET,
                    ttl=self._ttl,
                )
            sock = self._presence_sock
        finally:
            self._lock.release()
        return sock

    def _presence_thread_entry(self, sgate: threading.Event):
        self._running = True
        self._presence_sock = create_multicast_listener_socket(
            self._multicast_address,
            self._multicast_port,
            family=socket.AF_INET,
            ttl=self._ttl,
        )
        sgate.set()

        while self._running:
            sock = self._get_presence_socket()
            try:
                msg_in, addr = sock.recvfrom(DNS_RECEIVE_BUFFER)
                self._process_query(addr, msg_in)
            except socket.timeout:
                pass
            except Exception:
                self._lock.acquire()
                try:
                    if sock is not None:
                        sock.close()
                    self._presence_sock = None
                finally:
                    self._lock.release()
        return

    def _process_query(self, from_endpoint: Tuple[str, int], msg_bytes: bytes) -> None:
        msg = DnsInboundMessage(msg_bytes, source_endpoint=from_endpoint)
        if not msg.valid:
            return
        if msg.flags.qr != DnsQr.Query:
            return

        response_flags = DnsFlags(
            qr=DnsQr.Response,
            opcode=msg.flags.opcode,
            aa=True,
            tc=False,
            rd=False,
            ra=False,
            rcode=DnsRespCode.NoError,
        )
        response = DnsOutboundMessage(response_flags, id=msg.id, multicast=True)

        answers: List[DnsRecord] = []
        for q in msg.questions:
            for rec in self._records:
                if q.answered_by(rec):
                    answers.append(rec)
                    break
        for ans in answers:
            response.add_answer(ans)
            if ans is self._ptr_record:
                response.add_additional_answer(self._srv_record)
                response.add_additional_answer(self._txt_record)
                response.add_additional_answer(self._a_record)
            elif ans is self._srv_record:
                response.add_additional_answer(self._a_record)

        if response.answers:
            sock = self._get_presence_socket()
            packets = response.packets()
            for pkt in packets:
                sock.sendto(pkt, from_endpoint)
        return


if __name__ == "__main__":
    svc = MdnsPresence("am-mdns", "_automation._tcp.local", 8000)
    svc.start()
    try:
        while True:
            threading.Event().wait(1)
    except KeyboardInterrupt:
        pass
    svc.stop()

