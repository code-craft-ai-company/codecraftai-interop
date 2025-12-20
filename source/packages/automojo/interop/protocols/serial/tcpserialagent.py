"""
    .. module:: tcpserialagent
    :platform: Darwin, Linux, Unix, Windows
    :synopsis: Contains the TCP serial agent classes.
    
    .. moduleauthor:: Myron Walker <myron.walker@gmail.com>
"""

__author__ = "Myron Walker"
__copyright__ = "Copyright 2025, Automation Mojo LLC"
__credits__ = []


from typing import Optional, Tuple
from types import TracebackType

import telnetlib

from automojo.interop.aspects import AspectsCmd, DEFAULT_CMD_ASPECTS
from automojo.interop.interfaces.isystemcontext import ISystemContext

from automojo.xmodules.xconvert import safe_as_bytes, safe_as_str

from automojo.interop.agents.serialagentbase import SerialAgentBase


class TcpSerialBase(SerialAgentBase):
    """
        Base class for TCP serial implementations.
    """

    SERIAL_PROMPT = b"@@@&@@@&"  # We use a special prompt that is not likely to occur in our serial output
    NORMAL_PROMPT = b"#"

    def __init__(
        self, host: str, port: int, aspects: AspectsCmd = DEFAULT_CMD_ASPECTS
    ) -> None:
        """
            Constructs a :class:`TcpSerialBase` instance.
            
            :param host: Hostname or IP address of the telnet server.
            :param port: Telnet port of the remote server.
            :param aspects: Default command aspects used when executing commands.
        """
        self._host = host
        self._port = port
        self._aspects = aspects
        self._original_prompt = None  # Store the original prompt for restoration
        return

    def _create_connection(self) -> telnetlib.Telnet:
        """
            Creates a telnet connection and configures the shell prompt.
            
            :returns: A connected :class:`telnetlib.Telnet` object.
        """

        tnconn = telnetlib.Telnet(host=self._host, port=self._port)

        cmd_out = tnconn.read_until(self.NORMAL_PROMPT, self._aspects.inactivity_timeout)

        tnconn.write(b"\n")
        cmd_out = tnconn.read_until(self.NORMAL_PROMPT, self._aspects.inactivity_timeout)

        tnconn.write(b"echo $PS1\n")
        ps1_out = tnconn.read_until(self.NORMAL_PROMPT, self._aspects.inactivity_timeout)
        
        # Safely extract the original prompt with bounds checking
        ps1_lines = ps1_out.splitlines(False)
        if len(ps1_lines) > 1:
            self._original_prompt = ps1_lines[1]  # Save the original prompt
        else:
            # Fallback to default prompt if we can't extract it
            self._original_prompt = self.NORMAL_PROMPT

        tnconn.write(b'export PS1="' + self.SERIAL_PROMPT + b'"\n')

        cmd_out = tnconn.read_until(self.SERIAL_PROMPT, self._aspects.inactivity_timeout) # Read the echo of our export command
        cmd_out = tnconn.read_until(self.SERIAL_PROMPT, self._aspects.inactivity_timeout) # Read the actual prompt we set
        return tnconn

    def _restore_prompt(self, tnconn: telnetlib.Telnet) -> None:
        """
            Restores the shell prompt after a telnet session.
        """
        if self._original_prompt is not None:
            tnconn.write(b'export PS1="' + self._original_prompt + b'"\n')
            tnconn.read_until(self._original_prompt, timeout=self._aspects.inactivity_timeout)
        return


class TcpSerialSession(TcpSerialBase):
    """
        Context manager for an interactive TCP serial session.
    """

    def __init__(
        self,
        host: str,
        port: int,
        session_basis: Optional["TcpSerialSession"] = None,
        aspects: AspectsCmd = DEFAULT_CMD_ASPECTS,
    ):
        """
            Initialize a TCP serial session.
            
            :param host: Hostname of the serial concentrator.
            :param port: TCP port number.
            :param session_basis: Optional existing session to base new session on.
            :param aspects: Default command aspects for operations.
            
            :returns: None
        """

        super().__init__(host, port=port, aspects=aspects)
        self._session_basis = session_basis
        self._telnet_conn = None
        return

    def __enter__(self):
        """
            Method that implements the __enter__ symantics used for 'with' statements.
        """
        self._telnet_conn = self._create_connection()

        return self

    def __exit__(self, ex_type: type, ex_val: Exception, ex_tb: TracebackType) -> bool:
        """
            Method that implements the __exit__ symantics used for 'with' statements.
            
            :returns: Returns false indicating that exceptions are not handled.
        """
        self.close()
        handled = False
        return handled

    def close(self):
        """
            Closes the telnet session and the associated connection.  If this
            session owns the connection, the command prompt is restored before
            the connection is closed.
        """
        # Only restore the prompt and close if this session owns the client
        if self._session_basis is None and self._telnet_conn is not None:
            self._restore_prompt(self._telnet_conn)
            self._telnet_conn.close()
        
        # Always clear the connection reference regardless of ownership
        self._telnet_conn = None
        return

    def run_cmd(
        self, command: str, aspects: Optional[AspectsCmd] = None
    ) -> Tuple[int, str, str]:
        """
            Runs a command over the telnet connection held open by this
            session.  The command is executed without restoring the command
            prompt or closing the connection so that multiple commands can be
            run within the session scope.

            :param command: The command to run.
            :param aspects: The run aspects to use when running the command.

            :returns: The status, stdout and stderr from the command that was run.
        """

        if aspects is None:
            aspects = self._aspects

        status = None
        stdout = None
        stderr = None

        if self._telnet_conn is None:
            self._telnet_conn = self._create_connection()

        command = safe_as_bytes("%s 2> $TNSTDERR\n" % command)

        tnconn = self._telnet_conn
        tnconn.write(b"export TNSTDERR=/tmp/tnstderr\n")
        tnconn.read_until(self.SERIAL_PROMPT, timeout=aspects.inactivity_timeout)

        tnconn.write(command)
        stdout_raw = tnconn.read_until(self.SERIAL_PROMPT, timeout=aspects.completion_timeout)

        tnconn.write(b"echo $?\n")
        status_raw = tnconn.read_until(self.SERIAL_PROMPT, timeout=aspects.inactivity_timeout)
        
        # Safely extract the status with bounds checking
        status_lines = status_raw.splitlines(False)
        if len(status_lines) > 1:
            status_bytes = status_lines[1]
        else:
            raise RuntimeError(f"Unable to read exit status from telnet response: {status_raw}")

        tnconn.write(b"cat $TNSTDERR\n")
        stderr_raw = tnconn.read_until(self.SERIAL_PROMPT, timeout=aspects.inactivity_timeout)

        stdout = "\n".join(safe_as_str(stdout_raw).splitlines(False)[1:-1])
        stderr = "\n".join(safe_as_str(stderr_raw).splitlines(False)[1:-1])
        
        try:
            status = int(status_bytes)
        except ValueError:
            raise RuntimeError(f"Unable to parse exit status as integer: {status_bytes}")

        return status, stdout, stderr

    def open_session(
        self,
        session_basis: Optional[ISystemContext] = None,
        aspects: Optional[AspectsCmd] = None,
        **kwargs
    ) -> ISystemContext:  # pylint: disable=arguments-differ
        """
            Provides a mechanism to create a :class:`TcpSerialSession` object with derived settings.  This method allows various
            parameters for the session to be overridden.  This allows for the performing of a series of TCP Serial operations under
            a particular set of shared settings or command behaviors.
            
            :param session_basis: An optional existing TcpSerialSession instance to use as a basis for the new session.
            :param aspects: The default run aspects to use for the operations performed by the session.

            :returns: A newly created :class:`TcpSerialSession` instance.
        """

        if aspects is None:
            session_aspects = self._aspects
        else:
            session_aspects = aspects

        session = None
        if session_basis is not None:
            session = TcpSerialSession(
                session_basis._host,
                port=session_basis._port,
                session_basis=session_basis,
                aspects=session_aspects,
            )
        else:
            session = TcpSerialSession(
                self._host, port=self._port, aspects=session_aspects
            )

        return session

    def _create_connection(self) -> telnetlib.Telnet:
        """
            Create an Telnet connection if one is not already open and available.
            
            :returns: An :class:`telnetlib.Telnet` object connected to the remote Tcp Serial concentrator.
        """
        tnconn = None

        if self._session_basis is not None and self._session_basis._telnet_conn is not None:
            tnconn = self._session_basis._telnet_conn
        else:
            tnconn = super()._create_connection()

        return tnconn


class TcpSerialAgent(TcpSerialBase):
    """
        The :class:`TcpSerialAgent` provides access to serial port hosted on a TCP/IP network.  The
        remote endpoint might be a host and port for a serial port hosted on a serial concentrator.
        It could be the host and port of a serial port hosted on a linux box via USB and ser2net.
        
        .. note::
        An example ser2net configuration might look like the configuration below.
        
        BANNER:banner:\r\nser2net port \p device \d [\s] (Debian GNU/Linux)\r\n\r\n
        3333:telnet:0:/dev/ttyUSB0:115200 8DATABITS NONE 1STOPBIT banner
    """

    def __init__(
        self, host: str, port: int, aspects: AspectsCmd = DEFAULT_CMD_ASPECTS
    ) -> None:
        """
            Creates a :class:`TcpSerialAgent` instance.
            
            :param host: Hostname or IP address of the TCP serial concentrator.
            :param port: Port on the concentrator to connect to.
            :param aspects: Default command aspects for command execution.
        """
        super().__init__(host, port=port, aspects=aspects)
        return

    def open_session(
        self,
        session_basis: Optional[ISystemContext] = None,
        aspects: Optional[AspectsCmd] = None,
    ) -> ISystemContext:  # pylint: disable=arguments-differ
        """
            Provides a mechanism to create a :class:`TcpSerialSession` object with derived settings.  This method allows various
            parameters for the session to be overridden.  This allows for the performing of a series of TCP Serial operations under
            a particular set of shared settings or command behaviors.
            
            :param session_basis: An optional existing TcpSerialSession instance to use as a basis for the new session.
            :param aspects: The default run aspects to use for the operations performed by the session.

            :returns: A newly created :class:`TcpSerialSession` instance.
        """

        if aspects is None:
            session_aspects = self._aspects
        else:
            session_aspects = aspects

        session = None
        if session_basis is not None:
            session = TcpSerialSession(
                session_basis._host,
                port=session_basis._port,
                session_basis=session_basis,
                aspects=session_aspects,
            )
        else:
            session = TcpSerialSession(
                self._host, port=self._port, aspects=session_aspects
            )

        return session

    def run_cmd(
        self, command: str, aspects: Optional[AspectsCmd] = None
    ) -> Tuple[int, str, str]:
        """
            Runs a command on the designated host using the specified parameters.
            
            :param command: The command to run.
            :param aspects: The run aspects to use when running the command.
            
            :returns: The status, stderr and stdout from the command that was run.
        """
        if aspects is None:
            aspects = self._aspects

        status = None
        stdout = None
        stderr = None

        command = safe_as_bytes("%s 2> $TNSTDERR\n" % command)

        tnconn = self._create_connection()
        try:
            tnconn.write(b"export TNSTDERR=/tmp/tnstderr\n")
            tnconn.read_until(self.SERIAL_PROMPT, timeout=aspects.inactivity_timeout)

            tnconn.write(command)
            stdout_raw = tnconn.read_until(self.SERIAL_PROMPT, timeout=aspects.completion_timeout)

            tnconn.write(b"echo $?\n")
            status_raw = tnconn.read_until(self.SERIAL_PROMPT, timeout=aspects.inactivity_timeout)
            
            # Safely extract the status with bounds checking
            status_lines = status_raw.splitlines(False)
            if len(status_lines) > 1:
                status_bytes = status_lines[1]
            else:
                raise RuntimeError(f"Unable to read exit status from telnet response: {status_raw}")

            tnconn.write(b"cat $TNSTDERR\n")
            stderr_raw = tnconn.read_until(self.SERIAL_PROMPT, timeout=aspects.inactivity_timeout)

            stdout = "\n".join(safe_as_str(stdout_raw).splitlines(False)[1:-1])
            stderr = "\n".join(safe_as_str(stderr_raw).splitlines(False)[1:-1])
            
            try:
                status = int(status_bytes)
            except ValueError:
                raise RuntimeError(f"Unable to parse exit status as integer: {status_bytes}")
        finally:
            if tnconn is not None:
                self._restore_prompt(tnconn)
            tnconn.close()

        return status, stdout, stderr
