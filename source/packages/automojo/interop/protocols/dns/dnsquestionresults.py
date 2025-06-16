
"""
    .. module:: dnsquestionresults
    :platform: Darwin, Linux, Unix, Windows
    :synopsis: dnsquestionresults module.
    
    .. moduleauthor:: Myron Walker <myron.walker@gmail.com>
"""


__author__ = "Myron Walker"
__copyright__ = "Copyright 2025, Automation Mojo LLC"
__credits__ = []

import threading
import weakref

class DnsQuestionResults:
    """
        The :class:`DnsQuestionResults` object is utilized to formulate DNS querys and to check to
        see if a :class:`DnsRecord` answers the query provided.
    """

    def __init__(self, owner):
        """
            Constructs a :class:`DnsQuestionResults` object used to accumulate answers.

            :param owner: The object that initiated the query.
        """
        self._owner_ref = weakref.ref(owner)

        self._lock = threading.Lock()
        self._responses = []
        return
    
    @property
    def owner(self):
        """
            Object that initiated the query associated with these results.

            :returns: The query owner instance.
        """
        return self._owner_ref()

    @property
    def responses(self):
        """
            List of response records accumulated for the query.

            :returns: Copy of the list of responses.
        """
        rlist = []

        self._lock.acquire()
        try:
            rlist = [r for r in self._responses]
        finally:
            self._lock.release()

        return rlist

    def add_response(self, response):
        """
            Adds a response object to the results list.

            :param response: The response record to append.
        """
        self._responses.append(response)
        return
    
    def cleanup(self):
        """
            Placeholder for future cleanup logic.
        """
        return
