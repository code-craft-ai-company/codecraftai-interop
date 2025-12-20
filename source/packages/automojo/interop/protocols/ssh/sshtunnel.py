"""
    .. module:: sshtunnel
    :platform: Darwin, Linux, Unix, Windows
    :synopsis: Module containing the :class:`SshTunnel` class.
    
    .. moduleauthor:: Myron Walker <myron.walker@gmail.com>
    
"""

__author__ = "Myron Walker"
__copyright__ = "Copyright 2025, Automation Mojo LLC"
__credits__ = []


from typing import Optional, Union
from types import TracebackType
import socket
import threading

import paramiko
from paramiko.forward import local_forward_tunnel

from automojo.xmodules.xlogging.enhancedloggers import getEnhancedLogger

logger = getEnhancedLogger()


class SshTunnel:
    """
        The :class:`SshTunnel` represents a single SSH port forwarding tunnel for connecting to a remote service
        through an SSH connection. Each SshTunnel instance manages exactly one port forward.
        
        Note: SshTunnel instances should only be created through SshAgent.open_tunnel() method.
    """

    def __init__(self, ssh_client: paramiko.SSHClient, local_port: int, remote_host: str, remote_port: int, _internal_create: bool = False):
        """
            Initialize an :class:`SshTunnel` instance with an existing SSH client and tunnel parameters.
            
            Note: This constructor should not be called directly. Use SshAgent.open_tunnel() instead.

            :param ssh_client: An established paramiko SSHClient connection.
            :param local_port: Local port to bind for forwarding. If 0, an available port will be chosen.
            :param remote_host: Remote host to forward to.
            :param remote_port: Remote port to forward to.
            :param _internal_create: Internal flag to prevent direct instantiation.
        """
        if not _internal_create:
            raise RuntimeError("SshTunnel instances should only be created through SshAgent.open_tunnel() method")
        
        self._ssh_client = ssh_client
        self._local_port = local_port
        self._remote_host = remote_host
        self._remote_port = remote_port
        self._actual_local_port = None
        self._local_socket = None
        self._forward_thread = None
        self._active = False
        self._owns_ssh_client = True  # This tunnel owns the SSH client and should close it
        
        # Start the tunnel immediately
        self._start_tunnel()
        return

    @classmethod
    def _create_internal(cls, ssh_client: paramiko.SSHClient, local_port: int, remote_host: str, remote_port: int) -> 'SshTunnel':
        """
            Internal method for creating SshTunnel instances. Only used by SshAgent.

            :param ssh_client: An established paramiko SSHClient connection.
            :param local_port: Local port to bind for forwarding. If 0, an available port will be chosen.
            :param remote_host: Remote host to forward to.
            :param remote_port: Remote port to forward to.

            :returns: A new SshTunnel instance.
        """
        return cls(ssh_client, local_port, remote_host, remote_port, _internal_create=True)

    def __enter__(self):
        """
            Method that implements the __enter__ semantics used for 'with' statements.
        """
        return self

    def __exit__(self, ex_type: type, ex_val: Exception, ex_tb: TracebackType) -> bool:
        """
            Method that implements the __exit__ semantics used for 'with' statements.
            Shuts down the tunnel and cleans up all threads and resources.

            :returns: Returns false indicating that exceptions are not handled.
        """
        self.shutdown()
        handled = False
        return handled

    def close(self):
        """
            Closes all port forwards and cleans up resources. Does not close the SSH client.
            This is an alias for shutdown() for backward compatibility.
        """
        self.shutdown()
        return

    def shutdown(self):
        """
            Shuts down the tunnel by stopping the port forward and cleaning up all threads and resources.
            Also closes the SSH client since this tunnel owns it.
        """
        logger.info(f"Shutting down SSH tunnel 127.0.0.1:{self._actual_local_port} -> {self._remote_host}:{self._remote_port}")
        
        # Mark as inactive
        self._active = False
        
        # Close the listening socket to stop accepting new connections
        if self._local_socket:
            try:
                self._local_socket.close()
            except Exception as e:
                logger.debug(f"Error closing socket: {e}")
            finally:
                self._local_socket = None
        
        # Wait for the forwarding thread to complete
        if self._forward_thread and self._forward_thread.is_alive():
            logger.debug("Waiting for forwarding thread to complete...")
            self._forward_thread.join(timeout=10.0)
            if self._forward_thread.is_alive():
                logger.warning("Forwarding thread did not complete within timeout")
        
        # Close the SSH client since this tunnel owns it
        if self._owns_ssh_client and self._ssh_client:
            try:
                self._ssh_client.close()
                logger.debug("SSH client closed")
            except Exception as e:
                logger.warning(f"Error closing SSH client: {e}")
            finally:
                self._ssh_client = None
        
        logger.info("SSH tunnel shutdown complete")
        return

    def _start_tunnel(self):
        """
            Private method that starts the port forwarding tunnel.
        """
        # Create a local socket to listen on
        self._local_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._local_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        
        # If local_port is 0, let the OS choose an available port
        self._local_socket.bind(('127.0.0.1', self._local_port))
        self._actual_local_port = self._local_socket.getsockname()[1]
        self._local_socket.listen(5)
        
        # Mark as active
        self._active = True
        
        # Start the forwarding loop in a separate daemon thread
        self._forward_thread = threading.Thread(
            target=self._forward_loop,
            daemon=True
        )
        self._forward_thread.start()
        
        logger.info(f"SSH tunnel port forward started: 127.0.0.1:{self._actual_local_port} -> {self._remote_host}:{self._remote_port}")
        return

    def _forward_loop(self):
        """
            Private method that handles the port forwarding loop using paramiko's local_forward_tunnel.
        """
        transport = self._ssh_client.get_transport()
        
        try:
            while self._active:
                try:
                    # Accept incoming connections
                    conn, addr = self._local_socket.accept()
                    logger.debug(f"Accepted connection from {addr} for tunnel to {self._remote_host}:{self._remote_port}")
                    
                    # Use paramiko's built-in forwarding mechanism in a separate thread
                    threading.Thread(
                        target=local_forward_tunnel,
                        args=(conn, self._remote_host, self._remote_port, transport),
                        daemon=True
                    ).start()
                    
                except socket.error as e:
                    if self._active:
                        logger.error(f"Socket error in port forward: {e}")
                    break
                except Exception as e:
                    if self._active:
                        logger.error(f"Error in port forward: {e}")
                    break
                    
        except Exception as e:
            logger.error(f"Port forward thread error: {e}")
        finally:
            try:
                if self._local_socket:
                    self._local_socket.close()
            except:
                pass

    @property
    def local_port(self) -> int:
        """
            Returns the actual local port being used for the tunnel.

            :returns: The local port number.
        """
        return self._actual_local_port

    @property
    def remote_host(self) -> str:
        """
            Returns the remote host being forwarded to.

            :returns: The remote host.
        """
        return self._remote_host

    @property
    def remote_port(self) -> int:
        """
            Returns the remote port being forwarded to.

            :returns: The remote port number.
        """
        return self._remote_port

    @property
    def is_active(self) -> bool:
        """
            Returns whether the tunnel is currently active.

            :returns: True if active, False otherwise.
        """
        return self._active

    def get_connection_string(self, database: str = None, username: str = None, db_type: str = 'postgresql') -> str:
        """
            Helper method to generate database connection strings for use with SQLAlchemy or other ORMs.

            :param database: Optional database name.
            :param username: Optional username for the connection string.
            :param db_type: Database type (postgresql, mysql, etc.).

            :returns: A connection string template for the tunneled connection.
        """
        base_url = f"127.0.0.1:{self._actual_local_port}"
        
        conn_str: str

        if username and database:
            conn_str = f"{db_type}://{username}@{base_url}/{database}"
        elif database:
            conn_str = f"{db_type}://127.0.0.1:{self._actual_local_port}/{database}"
        else:
            conn_str = f"127.0.0.1:{self._actual_local_port}"

        return conn_str