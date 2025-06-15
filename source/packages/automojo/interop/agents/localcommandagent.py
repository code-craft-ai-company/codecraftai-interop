"""
    .. module:: localcommandagent
    :platform: Darwin, Linux, Unix, Windows
    :synopsis: Module containing the :class:`LocalCommandAgent` class used to
    execute commands on the local host.
    
    .. moduleauthor:: Myron Walker <myron.walker@gmail.com>
"""

__author__ = "Myron Walker"
__copyright__ = "Copyright 2023, Myron W Walker"
__credits__ = []


from typing import Optional, Sequence, Tuple, Union

import subprocess
import threading
import time

from logging import getLogger

from automojo.waiting import TimeoutContext

from automojo.errors.exceptions import SemanticError

from automojo.interop.interfaces.isystemcontext import ISystemContext
from automojo.interop.aspects import AspectsCmd, DEFAULT_CMD_ASPECTS, ActionPattern, LoggingPattern

from automojo.foundation.xformatting import indent_lines, format_command_result
from automojo.foundation.xlogging.scopemonitoring import MonitoredScope

logger = getLogger()

class LocalCommandAgent(ISystemContext):
    """
        Provides command execution capabilities on the local host without
        relying on a remote connection.
    """
    def __init__(self, aspects: AspectsCmd = DEFAULT_CMD_ASPECTS):
        """
            Initializes a :class:`LocalCommandAgent` instance.

            :param aspects: The default :class:`AspectsCmd` object to use when
                             running commands.
        """

        self._aspects = aspects
        return

    @property
    def aspects(self) -> AspectsCmd:
        """
            The logging, iteration and other aspects that have been assigned to
            be used with interacting with the remote SSH service.
        """
        return self._aspects

    def open_session(self, sysctx: Optional[ISystemContext] = None, aspects: Optional[AspectsCmd] = None, **kwargs) -> ISystemContext:  # pylint: disable=arguments-differ
        """
            Create and return a system context for executing commands locally.

            :param sysctx: Optional :class:`ISystemContext` instance to reuse.
            :param aspects: Execution aspects to apply for the session.

            :returns: The current :class:`LocalCommandAgent` instance.
        """
        return self

    def run_cmd(self, command: str, exp_status: Union[int, Sequence] = 0, aspects: Optional[AspectsCmd] = None) -> Tuple[int, str, str]:
        """
            Runs a command on the designated host using the specified
            parameters.

            :param command: The command to run.
            :param exp_status: An integer or sequence of integers that specify
                               the set of expected status codes from the
                               command.
            :param aspects: The run aspects to use when running the command.

            :returns: The status, stdout and stderr from the command that was
                      run.
        """
        # Go through the overrides and if they are not passed use the agent defaults.

        if aspects is None:
            aspects = self._aspects

        completion_toctx = TimeoutContext(aspects.completion_timeout, aspects.completion_interval)
        
        inactivity_timeout = aspects.inactivity_timeout
        inactivity_interval = aspects.inactivity_interval
        monitor_delay = aspects.monitor_delay
        logging_pattern = aspects.logging_pattern

        status, stdout, stderr = None, None, None

        this_thr = threading.current_thread()
        monmsg= "Thread failed to exit monitored scope. thid=%s thname=%s cmd=%s" % (this_thr.ident, this_thr.name, command)

        # Run the command using the SINGULAR pattern, we run it once and then return the result
        if aspects.action_pattern == ActionPattern.SINGLE_CALL:

            # Setup a monitored scope for the call to the remote device in case of timeout failure
            with MonitoredScope("RUNCMD-SINGULAR", monmsg, completion_toctx, notify_delay=monitor_delay) as _:

                proc = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
                stdout, stderr = proc.communicate(timeout=inactivity_timeout)
                status = proc.returncode


            stdout = stdout.decode('utf8')
            stderr = stderr.decode('utf8')
            self._log_command_result(command, status, stdout, stderr, exp_status, logging_pattern)

        # DO_UNTIL_SUCCESS, run the command until we get a successful expected result or a completion timeout has occured
        elif aspects.action_pattern == ActionPattern.DO_UNTIL_SUCCESS:

            completion_toctx.mark_begin()

            while True:

                # Setup a monitored scope for the call to the remote device in case of timeout failure
                with MonitoredScope("RUNCMD-DO_UNTIL_SUCCESS", monmsg, completion_toctx, notify_delay=monitor_delay) as _:
                    proc = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
                    stdout, stderr = proc.communicate(timeout=inactivity_timeout)
                    status = proc.returncode

                stdout = stdout.decode('utf8')
                stderr = stderr.decode('utf8')
                self._log_command_result(command, status, stdout, stderr, exp_status, logging_pattern)

                if isinstance(exp_status, int):
                    if status == exp_status:
                        break
                elif status in exp_status:
                    break

                if completion_toctx.final_attempt:
                    what_for="command success"
                    details = [
                        "CMD: %s" % command,
                        "STDOUT:",
                        indent_lines(stdout, 1),
                        "STDERR:",
                        indent_lines(stderr, 1),
                    ]
                    toerr = completion_toctx.create_timeout(what_for=what_for, detail=details)
                    raise toerr

                elif not completion_toctx.should_continue():
                    completion_toctx.mark_final_attempt()

                time.sleep(completion_toctx.interval)

        # DO_WHILE_SUCCESS, run the command while it is succeeds or a completion timeout has occured
        elif aspects.action_pattern == ActionPattern.DO_WHILE_SUCCESS:

            completion_toctx.mark_begin()

            while True:

                with MonitoredScope("RUNCMD-DO_WHILE_SUCCESS", monmsg, completion_toctx, notify_delay=monitor_delay) as _:
                    proc = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
                    stdout, stderr = proc.communicate(timeout=inactivity_timeout)
                    status = proc.returncode

                stdout = stdout.decode('utf8')
                stderr = stderr.decode('utf8')
                self._log_command_result(command, status, stdout, stderr, exp_status, logging_pattern)

                if isinstance(exp_status, int):
                    if status != exp_status:
                        break
                elif status not in exp_status:
                    break

                if completion_toctx.final_attempt:
                    what_for="command failure"
                    details = [
                        "CMD: %s" % command,
                        "STDOUT:",
                        indent_lines(stdout, 1),
                        "STDERR:",
                        indent_lines(stderr, 1),
                    ]
                    toerr = completion_toctx.create_timeout(what_for=what_for, detail=details)
                    raise toerr

                elif not completion_toctx.should_continue():
                    completion_toctx.mark_final_attempt()

                time.sleep(completion_toctx.interval)

        elif aspects.action_pattern == ActionPattern.SINGLE_CONNECTED_CALL or aspects.action_pattern == ActionPattern.DO_UNTIL_CONNECTION_FAILURE:
            errmsg = "LocalAgent currently does not support the SINGLE_CONNECTED_CALL or DO_UNTIL_CONNECTION_FAILURE action patterns."
            raise SemanticError(errmsg) from None
        else:
            errmsg = "LocalAgent: Unknown ActionPattern encountered. action_pattern={}".format(aspects.action_pattern)
            raise SemanticError(errmsg) from None

        return status, stdout, stderr

    def verify_connectivity(self) -> bool:
        """
            Method that can be used to verify connectivity to the target
            computer.

            :returns: A boolean value indicating whether connectivity with the
                      remote machine was successful.
        """
        return True

    def _log_command_result(self, command: str, status: int, stdout: str, stderr: str, exp_status: Union[int, Sequence[int]],
                            logging_pattern: LoggingPattern):
        """
            Private method that handles the logging of command results based on
            the expected status and logging pattern specified.

            :param command: The command that was run.
            :param status: The status code returned from running the command.
            :param stdout: The contents of the standard output from running the
                           command.
            :param stderr: The contents of the error output from running the
                           command.
            :param exp_status: The status code or possible status codes that was
                               expected to be returned from running the command.
            :param logging_pattern: The result logging pattern (:class:`LoggingPattern`) to use when logging.
        """
        # pylint: disable=no-self-use

        msg = "Error running command on a local agent.".format(command)

        if isinstance(exp_status, int):
            if status == exp_status:
                if logging_pattern == LoggingPattern.ALL_RESULTS or logging_pattern == LoggingPattern.SUCCESS_ONLY:
                    fullmsg = format_command_result(msg, command, status, stdout, stderr)
                    logger.info(fullmsg)
        else:
            if status in exp_status:
                if logging_pattern == LoggingPattern.ALL_RESULTS or logging_pattern == LoggingPattern.SUCCESS_ONLY:
                    fullmsg = format_command_result(msg, command, status, stdout, stderr)
            else:
                if logging_pattern == LoggingPattern.ALL_RESULTS or logging_pattern == LoggingPattern.FAILURE_ONLY:
                    fullmsg = format_command_result(msg, command, status, stdout, stderr)

        return

