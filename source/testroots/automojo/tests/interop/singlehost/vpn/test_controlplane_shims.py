"""
Tests for the M3b backward-compatibility re-export shims under
``automojo.interop.vpn``.

The M3 control-plane classes (``TailscaleControlPlane`` and
``TwingateControlPlane``) were extracted into the dedicated
``automojo-restclient-tailscale`` / ``automojo-restclient-twingate`` packages
during milestone M3b. The legacy import paths are kept alive for one release
cycle by thin shim modules that emit a :class:`DeprecationWarning`. These tests
verify the shim wiring: a one-shot warning and a correct re-export identity.
"""

import importlib
import warnings

from automojo.restclient.tailscale.tailscaleclient import TailscaleClient
from automojo.restclient.twingate.twingateclient import TwingateClient

import automojo.interop.vpn._shim as vpn_shim


def test_tailscale_shim_emits_deprecation_warning_once():
    """
        Importing the legacy ``tailscalecontrolplane`` module must emit
        exactly one :class:`DeprecationWarning`, even across repeated reloads.
    """
    module_path = "automojo.interop.vpn.tailscale.tailscalecontrolplane"

    vpn_shim._WARNED.discard(module_path)

    with warnings.catch_warnings(record=True) as caught:
        warnings.simplefilter("always")
        legacy_module = importlib.import_module(module_path)
        importlib.reload(legacy_module)
        importlib.reload(legacy_module)

    deprecations = []
    for warning_entry in caught:
        if issubclass(warning_entry.category, DeprecationWarning):
            deprecations.append(warning_entry)

    assert len(deprecations) == 1
    assert module_path in str(deprecations[0].message)
    return


def test_twingate_shim_emits_deprecation_warning_once():
    """
        Importing the legacy ``twingatecontrolplane`` module must emit
        exactly one :class:`DeprecationWarning`, even across repeated reloads.
    """
    module_path = "automojo.interop.vpn.twingate.twingatecontrolplane"

    vpn_shim._WARNED.discard(module_path)

    with warnings.catch_warnings(record=True) as caught:
        warnings.simplefilter("always")
        legacy_module = importlib.import_module(module_path)
        importlib.reload(legacy_module)
        importlib.reload(legacy_module)

    deprecations = []
    for warning_entry in caught:
        if issubclass(warning_entry.category, DeprecationWarning):
            deprecations.append(warning_entry)

    assert len(deprecations) == 1
    assert module_path in str(deprecations[0].message)
    return


def test_tailscale_shim_is_subclass_of_new_client():
    """
        The legacy ``TailscaleControlPlane`` name must resolve to a subclass
        of the new :class:`TailscaleClient`. A thin subclass (rather than a
        plain alias) is required because the M3 class raised ``SemanticError``
        for a bad credential whereas ``TailscaleClient`` raises
        ``ConfigurationError``.
    """
    from automojo.interop.vpn.tailscale.tailscalecontrolplane import (
        TailscaleControlPlane
    )

    is_subclass = issubclass(TailscaleControlPlane, TailscaleClient)
    assert is_subclass is True
    return


def test_twingate_shim_is_alias_of_new_client():
    """
        The legacy ``TwingateControlPlane`` name must resolve to exactly the
        new :class:`TwingateClient` — the constructors match, so a plain alias
        is used.
    """
    from automojo.interop.vpn.twingate.twingatecontrolplane import (
        TwingateControlPlane
    )

    assert TwingateControlPlane is TwingateClient
    return
