"""
    .. module:: twingateconnector
        :platform: Darwin, Linux, Unix, Windows
        :synopsis: Module that contains the :class:`TwingateConnector` data
                   class representing a connector entity from the Twingate
                   GraphQL API.

    .. moduleauthor:: Myron Walker <myron.walker@gmail.com>
"""

__author__ = "Myron Walker"
__copyright__ = "Copyright 2025, Automation Mojo LLC"
__credits__ = []


from dataclasses import dataclass


@dataclass
class TwingateConnector:
    """
        Typed projection of a Twingate ``Connector`` node returned by the
        GraphQL ``connectors`` query.

        :param connector_id: Provider-assigned stable identifier.
        :param name: Display name of the connector.
        :param remote_network_id: Identifier of the parent ``RemoteNetwork``.
        :param state: Connector state token (for example ``ALIVE``).
    """
    connector_id: str
    name: str
    remote_network_id: str
    state: str


__all__ = ["TwingateConnector"]
