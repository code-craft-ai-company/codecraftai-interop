import gc
import weakref
import ccai.testbase as testbase
from ccai.interop.protocols.dns.dnsquestionresults import DnsQuestionResults


class DummyOwner:
    pass


def test_owner_returns_weakref() -> None:
    owner = DummyOwner()
    results = DnsQuestionResults(owner)
    testbase.assert_equal(results.owner, owner)
    # Drop the strong reference and force collection to test weakref behavior
    owner_ref = weakref.ref(owner)
    owner = None
    gc.collect()
    testbase.assert_equal(owner_ref() is None or results.owner is None, True)
    return


def test_add_response_appends_to_list() -> None:
    results = DnsQuestionResults(DummyOwner())
    resp1 = object()
    resp2 = object()
    results.add_response(resp1)
    results.add_response(resp2)
    testbase.assert_equal(results.responses, [resp1, resp2])
    return


def test_responses_returns_copy() -> None:
    results = DnsQuestionResults(DummyOwner())
    resp = object()
    results.add_response(resp)
    copy_list = results.responses
    copy_list.append('tamper')
    testbase.assert_equal(results.responses, [resp])
    return


def test_cleanup_noop() -> None:
    results = DnsQuestionResults(DummyOwner())
    results.cleanup()
    testbase.assert_equal(True, True)
    return
