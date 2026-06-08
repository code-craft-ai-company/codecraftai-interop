"""
Tests for the M3b backward-compatibility re-export shims under
``ccai.interop.vpn``.

The M3 control-plane classes (``TailscaleControlPlane`` and
``TwingateControlPlane``) were extracted into the dedicated
``codecraftai-restclient-tailscale`` / ``codecraftai-restclient-twingate`` packages
during milestone M3b. The legacy import paths are kept alive for one release
cycle by thin shim modules that emit a :class:`DeprecationWarning`. These tests
verify the shim wiring: a one-shot warning and a correct re-export identity.
"""

import importlib
import warnings

from ccai.restclient.tailscale.tailscaleclient import TailscaleClient
from ccai.restclient.twingate.twingateclient import TwingateClient

import ccai.interop.vpn._shim as vpn_shim


def _plain_import_emits_no_deprecation(module_path: str) -> bool:
    """
        Import ``module_path`` fresh in a subprocess and report whether the
        import emitted any :class:`DeprecationWarning`.

        :param module_path: The dotted package path to import.

        :returns: ``True`` when no DeprecationWarning was emitted.
    """
    import subprocess
    import sys

    script_lines = [
        "import warnings",
        "with warnings.catch_warnings(record=True) as caught:",
        "    warnings.simplefilter('always')",
        "    import {}".format(module_path),
        "deps = [w for w in caught if issubclass(w.category, DeprecationWarning)]",
        "raise SystemExit(1 if len(deps) > 0 else 0)",
    ]
    script = "\n".join(script_lines)
    completed = subprocess.run(
        [sys.executable, "-c", script],
        capture_output=True,
    )
    rtnval = completed.returncode == 0
    return rtnval


def test_plain_import_of_vpn_package_emits_no_deprecation_warning():
    """
        Regression for audit IL-H1: a plain ``import ccai.interop.vpn``
        must not eagerly load the control-plane shims and therefore must not
        fire a :class:`DeprecationWarning`.
    """
    no_warning = _plain_import_emits_no_deprecation("ccai.interop.vpn")
    assert no_warning is True
    return


def test_plain_import_of_tailscale_package_emits_no_deprecation_warning():
    """
        Regression for audit IL-H1: a plain
        ``import ccai.interop.vpn.tailscale`` must not fire a
        :class:`DeprecationWarning`.
    """
    no_warning = _plain_import_emits_no_deprecation(
        "ccai.interop.vpn.tailscale"
    )
    assert no_warning is True
    return


def test_plain_import_of_twingate_package_emits_no_deprecation_warning():
    """
        Regression for audit IL-H1: a plain
        ``import ccai.interop.vpn.twingate`` must not fire a
        :class:`DeprecationWarning`.
    """
    no_warning = _plain_import_emits_no_deprecation(
        "ccai.interop.vpn.twingate"
    )
    assert no_warning is True
    return


def test_tailscale_shim_emits_deprecation_warning_once():
    """
        Importing the legacy ``tailscalecontrolplane`` module must emit
        exactly one :class:`DeprecationWarning`, even across repeated reloads.
    """
    module_path = "ccai.interop.vpn.tailscale.tailscalecontrolplane"

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
    module_path = "ccai.interop.vpn.twingate.twingatecontrolplane"

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
    from ccai.interop.vpn.tailscale.tailscalecontrolplane import (
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
    from ccai.interop.vpn.twingate.twingatecontrolplane import (
        TwingateControlPlane
    )

    assert TwingateControlPlane is TwingateClient
    return
