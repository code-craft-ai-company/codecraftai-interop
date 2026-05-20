"""
    .. module:: _shim
        :platform: Darwin, Linux, Unix, Windows
        :synopsis: Helper that powers the backward-compatibility re-export
                   shims under ``automojo.interop.vpn``.

    .. moduleauthor:: Myron Walker <myron.walker@gmail.com>

    The M3 control-plane classes (``TailscaleControlPlane`` and
    ``TwingateControlPlane``) were extracted into the dedicated
    ``automojo-restclient-tailscale`` and ``automojo-restclient-twingate``
    packages during milestone M3b. The legacy import paths under
    ``automojo.interop.vpn`` are preserved for one release cycle by thin shim
    modules that delegate to :func:`install_shim`. The helper emits exactly one
    :class:`DeprecationWarning` per process per legacy import path, so
    consumers see a clear migration nudge without log noise.

    Both the shim modules and this helper are scheduled for deletion once the
    one-release deprecation cycle completes.
"""

__author__ = "Myron Walker"
__copyright__ = "Copyright 2025, Automation Mojo LLC"
__credits__ = []


import warnings

from typing import Set


_WARNED: Set[str] = set()


def install_shim(*, old_module: str, new_module: str) -> None:
    """
        Emit a one-shot :class:`DeprecationWarning` for a legacy VPN
        control-plane module that has moved to a dedicated restclient package.

        The warning fires at most once per process per ``old_module`` value, so
        repeated imports of the same legacy module do not spam consumers.

        :param old_module: Dotted module path being deprecated (typically the
                            ``__name__`` of the calling shim module).
        :param new_module: Dotted path of the replacement module that owns the
                            symbols going forward.

        :returns: ``None``.
    """
    if old_module in _WARNED:
        return

    _WARNED.add(old_module)

    msg_lines = [
        "{} is deprecated; import from {} instead.".format(old_module, new_module),
        "This shim will be removed after the current deprecation cycle.",
    ]
    msg = " ".join(msg_lines)
    warnings.warn(msg, DeprecationWarning, stacklevel=3)

    return None
