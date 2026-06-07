"""
    .. module:: tailscalecontrolplane
        :platform: Darwin, Linux, Unix, Windows
        :synopsis: Backward-compatibility re-export shim for the M3-landed
                   ``TailscaleControlPlane`` class.

    .. moduleauthor:: Myron Walker <myron.walker@gmail.com>

    The M3 ``TailscaleControlPlane`` REST client has been superseded by
    :class:`ccai.restclient.tailscale.tailscaleclient.TailscaleClient`,
    which lives in the dedicated ``codecraftai-restclient-tailscale`` package
    landed in milestone M3b. ``TailscaleClient`` is wire-compatible with the
    M3 class — both implement
    :class:`ccai.interfaces.ivpncontrolplane.IVPNControlPlane`.

    This module is a thin shim retained for one release cycle. Importing it
    emits a :class:`DeprecationWarning` exactly once per process. New code
    should import :class:`TailscaleClient` directly from its new home.

    ``TailscaleControlPlane`` is exposed here as a minimal subclass of
    ``TailscaleClient`` rather than a plain alias. The only behavioural
    difference is credential validation: the M3 class raised
    :class:`ccai.errors.exceptions.SemanticError` for a non-Tailscale
    credential, whereas ``TailscaleClient`` raises
    :class:`ccai.errors.exceptions.ConfigurationError`. The subclass
    re-raises as :class:`SemanticError` so legacy call sites that catch the
    M3 exception type continue to work.
"""

__author__ = "Myron Walker"
__copyright__ = "Copyright 2025, Code Craft AI LLC"
__credits__ = []


from ccai.errors.exceptions import ConfigurationError, SemanticError

from ccai.restclient.tailscale.aspectstailscale import (
    AspectsTailscale, DEFAULT_TAILSCALE_ASPECTS
)
from ccai.restclient.tailscale.tailscaleclient import (
    TailscaleClient, TAILSCALE_API_HOST
)

from ccai.credentials.basecredential import BaseCredential

from ccai.interop.vpn._shim import install_shim


install_shim(old_module=__name__,
             new_module="ccai.restclient.tailscale.tailscaleclient")


class TailscaleControlPlane(TailscaleClient):
    """
        Deprecated re-export of
        :class:`ccai.restclient.tailscale.tailscaleclient.TailscaleClient`.

        Retained for one release cycle so that legacy
        ``from ccai.interop.vpn.tailscale.tailscalecontrolplane import
        TailscaleControlPlane`` imports keep resolving. New code should use
        :class:`TailscaleClient` directly.
    """

    def __init__(self, *, credential: BaseCredential, tailnet: str,
                 host: str = TAILSCALE_API_HOST,
                 aspects: AspectsTailscale = DEFAULT_TAILSCALE_ASPECTS):
        """
            Initialize the deprecated Tailscale control plane client.

            :param credential: Either a
                :class:`ccai.credentials.tailscaleauthkeycredential.TailscaleAuthKeyCredential`
                or a
                :class:`ccai.credentials.tailscaleoauthcredential.TailscaleOAuthCredential`.
            :param tailnet: The tailnet identifier (commonly ``"-"`` for the
                default tailnet owned by the credential).
            :param host: Override host name for the REST endpoint.
            :param aspects: Default :class:`AspectsTailscale` applied when a
                call omits an explicit aspects argument.

            :returns: ``None``.

            :raises: :class:`ccai.errors.exceptions.SemanticError` when
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
