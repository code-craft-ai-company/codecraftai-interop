"""
    .. module:: tailscalecontrolplane
        :platform: Darwin, Linux, Unix, Windows
        :synopsis: Backward-compatibility re-export shim for the M3-landed
                   ``TailscaleControlPlane`` class.

    .. moduleauthor:: Myron Walker <myron.walker@gmail.com>

    The M3 ``TailscaleControlPlane`` REST client has been superseded by
    :class:`automojo.restclient.tailscale.tailscaleclient.TailscaleClient`,
    which lives in the dedicated ``automojo-restclient-tailscale`` package
    landed in milestone M3b. ``TailscaleClient`` is wire-compatible with the
    M3 class — both implement
    :class:`automojo.interfaces.ivpncontrolplane.IVPNControlPlane`.

    This module is a thin shim retained for one release cycle. Importing it
    emits a :class:`DeprecationWarning` exactly once per process. New code
    should import :class:`TailscaleClient` directly from its new home.

    ``TailscaleControlPlane`` is exposed here as a minimal subclass of
    ``TailscaleClient`` rather than a plain alias. The only behavioural
    difference is credential validation: the M3 class raised
    :class:`automojo.errors.exceptions.SemanticError` for a non-Tailscale
    credential, whereas ``TailscaleClient`` raises
    :class:`automojo.errors.exceptions.ConfigurationError`. The subclass
    re-raises as :class:`SemanticError` so legacy call sites that catch the
    M3 exception type continue to work.
"""

__author__ = "Myron Walker"
__copyright__ = "Copyright 2025, Automation Mojo LLC"
__credits__ = []


from automojo.errors.exceptions import ConfigurationError, SemanticError

from automojo.restclient.tailscale.aspectstailscale import (
    AspectsTailscale, DEFAULT_TAILSCALE_ASPECTS
)
from automojo.restclient.tailscale.tailscaleclient import (
    TailscaleClient, TAILSCALE_API_HOST
)

from automojo.credentials.basecredential import BaseCredential

from automojo.interop.vpn._shim import install_shim


install_shim(old_module=__name__,
             new_module="automojo.restclient.tailscale.tailscaleclient")


class TailscaleControlPlane(TailscaleClient):
    """
        Deprecated re-export of
        :class:`automojo.restclient.tailscale.tailscaleclient.TailscaleClient`.

        Retained for one release cycle so that legacy
        ``from automojo.interop.vpn.tailscale.tailscalecontrolplane import
        TailscaleControlPlane`` imports keep resolving. New code should use
        :class:`TailscaleClient` directly.
    """

    def __init__(self, *, credential: BaseCredential, tailnet: str,
                 host: str = TAILSCALE_API_HOST,
                 aspects: AspectsTailscale = DEFAULT_TAILSCALE_ASPECTS):
        """
            Initialize the deprecated Tailscale control plane client.

            :param credential: Either a
                :class:`automojo.credentials.tailscaleauthkeycredential.TailscaleAuthKeyCredential`
                or a
                :class:`automojo.credentials.tailscaleoauthcredential.TailscaleOAuthCredential`.
            :param tailnet: The tailnet identifier (commonly ``"-"`` for the
                default tailnet owned by the credential).
            :param host: Override host name for the REST endpoint.
            :param aspects: Default :class:`AspectsTailscale` applied when a
                call omits an explicit aspects argument.

            :returns: ``None``.

            :raises: :class:`automojo.errors.exceptions.SemanticError` when
                ``credential`` is not a Tailscale credential type.
        """
        try:
            super().__init__(credential=credential, tailnet=tailnet,
                             host=host, aspects=aspects)
        except ConfigurationError as config_err:
            err_msg = str(config_err)
            raise SemanticError(err_msg) from None

        return


__all__ = ["TailscaleControlPlane", "TAILSCALE_API_HOST"]
