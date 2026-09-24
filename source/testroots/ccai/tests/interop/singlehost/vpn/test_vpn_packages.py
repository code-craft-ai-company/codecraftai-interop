"""
    .. module:: test_vpn_packages
    :platform: Darwin, Linux, Unix, Windows
    :synopsis: Tests for the exports of the ``ccai.interop.vpn`` packages.  The control-plane classes moved to
               the 'codecraftai-restclient-*' packages and their modules were deleted, so the packages no longer
               carry lazy shims for ``TailscaleControlPlane`` / ``TwingateControlPlane``.
"""

import importlib

import ccai.testbase as testbase


PACKAGE_REMOVED_NAMES = [
    ("ccai.interop.vpn", "TwingateControlPlane"),
    ("ccai.interop.vpn.tailscale", "TailscaleControlPlane"),
    ("ccai.interop.vpn.twingate", "TwingateControlPlane"),
]

PACKAGE_EXPORTS = [
    ("ccai.interop.vpn", ["TwingateClient"]),
    ("ccai.interop.vpn.tailscale", ["TailscaleClient"]),
    ("ccai.interop.vpn.twingate", ["TwingateClient", "AspectsTwingate", "DEFAULT_TWINGATE_ASPECTS"]),
]


def test_removed_control_plane_names_are_plain_missing_attributes():
    """
        The removed control-plane names are ordinary missing attributes: ``hasattr`` is False and ``getattr``
        raises AttributeError, instead of a module ``__getattr__`` shim raising ImportError for a module
        that no longer exists.
    """
    for package_name, removed_name in PACKAGE_REMOVED_NAMES:
        package = importlib.import_module(package_name)

        testbase.assert_equal(hasattr(package, removed_name), False)

        raised = None
        try:
            getattr(package, removed_name)
        except AttributeError as xcpt:
            raised = xcpt

        testbase.assert_true(raised is not None, f"AttributeError raised for {package_name}.{removed_name}")
        testbase.assert_equal(removed_name in package.__all__, False)
        testbase.assert_equal("__getattr__" in vars(package), False)

    return


def test_package_exports_resolve():
    """
        Every name a VPN package exports in ``__all__`` resolves.
    """
    for package_name, expected_exports in PACKAGE_EXPORTS:
        package = importlib.import_module(package_name)

        testbase.assert_equal(sorted(package.__all__), sorted(expected_exports))
        for export_name in package.__all__:
            testbase.assert_true(getattr(package, export_name) is not None, f"{package_name}.{export_name} resolves")

    return
