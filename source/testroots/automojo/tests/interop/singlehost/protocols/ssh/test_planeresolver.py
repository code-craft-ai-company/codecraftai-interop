"""
    Tests for the pure :func:`resolve_dial_target` helper used by
    :class:`SshBase` to choose the dial target on a chosen address plane.

    These tests exercise only the resolver; the SSH integration tests
    live in :mod:`test_address_plane_awareness`.
"""

import pytest

from hypothesis import given, strategies as st

import automojo.testbase as testbase

from automojo.interfaces.addressplane import AddressPlane, DeviceAddressSetSnapshot

from automojo.interop.protocols.ssh.exceptions import SSHAddressPlaneUnavailableError
from automojo.interop.protocols.ssh.planeresolver import resolve_dial_target, skipped_planes


def _snapshot(public=None, private=None, overlay=None):
    snap = DeviceAddressSetSnapshot(public_address=public, private_address=private, overlay_address=overlay)
    return snap


def test_resolve_returns_preferred_when_present():
    snap = _snapshot(public="1.2.3.4", private="10.0.0.1", overlay="100.64.0.1")
    result = resolve_dial_target(address_set=snap, preferred_plane=AddressPlane.PUBLIC, fallback_planes=None)
    testbase.assert_equal(result, "1.2.3.4")
    return


def test_resolve_each_plane_present_alone():
    snap_pub = _snapshot(public="1.2.3.4")
    snap_priv = _snapshot(private="10.0.0.1")
    snap_over = _snapshot(overlay="100.64.0.1")
    testbase.assert_equal(resolve_dial_target(address_set=snap_pub, preferred_plane=AddressPlane.PUBLIC, fallback_planes=None), "1.2.3.4")
    testbase.assert_equal(resolve_dial_target(address_set=snap_priv, preferred_plane=AddressPlane.PRIVATE, fallback_planes=None), "10.0.0.1")
    testbase.assert_equal(resolve_dial_target(address_set=snap_over, preferred_plane=AddressPlane.OVERLAY, fallback_planes=None), "100.64.0.1")
    return


def test_resolve_falls_through_to_first_available():
    snap = _snapshot(private="10.0.0.1", overlay="100.64.0.1")
    result = resolve_dial_target(address_set=snap, preferred_plane=AddressPlane.PUBLIC,
                                  fallback_planes=[AddressPlane.PRIVATE, AddressPlane.OVERLAY])
    testbase.assert_equal(result, "10.0.0.1")
    return


def test_resolve_fallback_skips_to_overlay():
    snap = _snapshot(overlay="100.64.0.1")
    result = resolve_dial_target(address_set=snap, preferred_plane=AddressPlane.PUBLIC,
                                  fallback_planes=[AddressPlane.PRIVATE, AddressPlane.OVERLAY])
    testbase.assert_equal(result, "100.64.0.1")
    return


def test_resolve_empty_string_treated_as_absent():
    snap = _snapshot(public="", private="10.0.0.1")
    result = resolve_dial_target(address_set=snap, preferred_plane=AddressPlane.PUBLIC,
                                  fallback_planes=[AddressPlane.PRIVATE])
    testbase.assert_equal(result, "10.0.0.1")
    return


def test_resolve_no_plane_available_raises():
    snap = _snapshot()
    raised = False
    try:
        resolve_dial_target(address_set=snap, preferred_plane=AddressPlane.PUBLIC,
                             fallback_planes=[AddressPlane.PRIVATE, AddressPlane.OVERLAY],
                             device_name="dev-alpha")
    except SSHAddressPlaneUnavailableError as err:
        raised = True
        msg = str(err)
        testbase.assert_equal("dev-alpha" in msg, True)
        testbase.assert_equal("PUBLIC" in msg, True)
        testbase.assert_equal("PRIVATE" in msg, True)
        testbase.assert_equal("OVERLAY" in msg, True)
    testbase.assert_equal(raised, True)
    return


def test_resolve_no_fallback_unavailable_preferred_raises():
    snap = _snapshot(private="10.0.0.1")
    raised = False
    try:
        resolve_dial_target(address_set=snap, preferred_plane=AddressPlane.PUBLIC, fallback_planes=None)
    except SSHAddressPlaneUnavailableError:
        raised = True
    testbase.assert_equal(raised, True)
    return


def test_skipped_planes_empty_when_preferred_resolves():
    snap = _snapshot(public="1.2.3.4")
    skipped = skipped_planes(address_set=snap, preferred_plane=AddressPlane.PUBLIC,
                              fallback_planes=[AddressPlane.PRIVATE])
    testbase.assert_equal(skipped, [])
    return


def test_skipped_planes_lists_skipped_in_order():
    snap = _snapshot(overlay="100.64.0.1")
    skipped = skipped_planes(address_set=snap, preferred_plane=AddressPlane.PUBLIC,
                              fallback_planes=[AddressPlane.PRIVATE, AddressPlane.OVERLAY])
    testbase.assert_equal(skipped, [AddressPlane.PUBLIC, AddressPlane.PRIVATE])
    return


# ---------------------------------------------------------------------------
# Property-style tests (hypothesis)
# ---------------------------------------------------------------------------

_PLANE_VALUES = [AddressPlane.PUBLIC, AddressPlane.PRIVATE, AddressPlane.OVERLAY]


def _addr_or_none(label):
    rtnval = st.one_of(st.none(), st.just("addr-{}".format(label)))
    return rtnval


@given(public=_addr_or_none("pub"), private=_addr_or_none("priv"), overlay=_addr_or_none("over"),
       preferred=st.sampled_from(_PLANE_VALUES))
def test_property_determinism(public, private, overlay, preferred):
    """
        Two calls with identical inputs return identical outputs (or both
        raise the same typed exception).
    """
    snap = _snapshot(public=public, private=private, overlay=overlay)
    fallback = [p for p in _PLANE_VALUES if p != preferred]

    result_a = None
    raised_a = False
    try:
        result_a = resolve_dial_target(address_set=snap, preferred_plane=preferred, fallback_planes=fallback)
    except SSHAddressPlaneUnavailableError:
        raised_a = True

    result_b = None
    raised_b = False
    try:
        result_b = resolve_dial_target(address_set=snap, preferred_plane=preferred, fallback_planes=fallback)
    except SSHAddressPlaneUnavailableError:
        raised_b = True

    testbase.assert_equal(raised_a, raised_b)
    testbase.assert_equal(result_a, result_b)
    return


@given(preferred=st.sampled_from(_PLANE_VALUES))
def test_property_totality_with_preferred_populated(preferred):
    """
        For any address set that populates the preferred plane,
        resolution succeeds and returns that plane's address.
    """
    addr_value = "host-{}".format(preferred.name)
    kwargs = {}
    if preferred == AddressPlane.PUBLIC:
        kwargs["public"] = addr_value
    elif preferred == AddressPlane.PRIVATE:
        kwargs["private"] = addr_value
    else:
        kwargs["overlay"] = addr_value
    snap = _snapshot(**kwargs)
    result = resolve_dial_target(address_set=snap, preferred_plane=preferred, fallback_planes=None)
    testbase.assert_equal(result, addr_value)
    return
