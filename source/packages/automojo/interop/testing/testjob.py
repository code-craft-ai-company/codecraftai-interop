"""
    .. module:: testjob
    :platform: Darwin, Linux, Unix, Windows
    :synopsis: Module containing :class:`InteropLibraryTestJob`, the
               interop-tier base class for test jobs that participate in
               a landscape-managed environment.

    .. moduleauthor:: Myron Walker <myron.walker@gmail.com>
"""

__author__ = "Myron Walker"
__copyright__ = "Copyright 2025, Automation Mojo LLC"
__credits__ = []


from typing import Any

from automojo.testbase.testjob import TestJob
from automojo.testbase.sequencing.testsequencer import TestSequencer


class InteropLibraryTestJob(TestJob):
    """
        Interop-tier test-job base class.

        Extends :class:`automojo.testbase.testjob.TestJob` (single-host) with
        the **landscape-activation lifecycle** required by any test job that
        runs against a real environment described through the landscape model
        — devices, services, coordinators, control points, integration
        couplings.  It overrides the five hooks that the parent class leaves
        as stubs:

        * ``fire_attach_to_environment(tseq)`` — passes the landscape to
          ``tseq.attach_to_environment`` so registered integrations can
          connect to the live environment.
        * ``fire_attach_to_framework(tseq)`` — passes the landscape to
          ``tseq.attach_to_framework`` so integrations can register with the
          test framework.
        * ``fire_activate_configuration()`` — calls
          ``landscape.activate_configuration()``.
        * ``fire_activate_integration()`` — calls
          ``landscape.activate_integration()``.
        * ``fire_activate_operations()`` — calls
          ``landscape.activate_operations()``.

        **Landscape sourcing.** ``automojo-interop`` deliberately does NOT
        depend on ``automojo-landscaping`` (landscaping depends on interop,
        not the other way around).  Concrete subclasses therefore source the
        landscape object themselves by overriding :meth:`_get_landscape`.
        The base raises :class:`NotImplementedError` so the abstract nature
        of the hook is explicit at construction time rather than at the
        first ``fire_*`` call.

        Concrete subclasses live in packages that DO depend on
        ``automojo-landscaping`` — for example
        ``automojo-testplus.DistributedTestJob`` overrides
        :meth:`_get_landscape` to return ``LandscapeSingleton()``.
    """

    def _get_landscape(self) -> Any:
        """
            Returns the landscape object used by the activation /
            attachment hooks.

            Concrete subclasses must override this method to return the
            landscape instance their environment is built from
            (typically ``LandscapeSingleton()`` from
            ``automojo.landscaping.wellknown``).

            :returns: A landscape object whose interface includes
                      ``activate_configuration``,
                      ``activate_integration``,
                      ``activate_operations``, and which can be passed as
                      the ``landscape`` keyword argument to the test
                      sequencer's ``attach_to_environment`` /
                      ``attach_to_framework`` methods.

            :raises NotImplementedError: When called on a class that does
                                         not override the hook.
        """
        err_msg_lines = [
            "InteropLibraryTestJob subclasses must override _get_landscape().",
            "    SUBCLASS: {}".format(type(self).__name__),
        ]
        err_msg = "\n".join(err_msg_lines)
        raise NotImplementedError(err_msg)

    def fire_attach_to_environment(self, tseq: TestSequencer) -> None:
        """
            Provides the sequencer with the landscape so registered
            integrations can attach to the live environment.

            :param tseq: The sequencer controlling the test run.

            :returns: ``None``
        """
        landscape = self._get_landscape()
        tseq.attach_to_environment(landscape=landscape)
        return

    def fire_attach_to_framework(self, tseq: TestSequencer) -> None:
        """
            Provides the sequencer with the landscape so registered
            integrations can attach to the automation framework.

            :param tseq: The sequencer controlling the test run.

            :returns: ``None``
        """
        landscape = self._get_landscape()
        tseq.attach_to_framework(landscape=landscape)
        return

    def fire_activate_configuration(self) -> None:
        """
            Activates the configuration phase of the landscape.

            :returns: ``None``
        """
        landscape = self._get_landscape()
        landscape.activate_configuration()
        return

    def fire_activate_integration(self) -> None:
        """
            Activates the integration phase of the landscape.

            :returns: ``None``
        """
        landscape = self._get_landscape()
        landscape.activate_integration()
        return

    def fire_activate_operations(self) -> None:
        """
            Activates the operations phase of the landscape.

            :returns: ``None``
        """
        landscape = self._get_landscape()
        landscape.activate_operations()
        return
