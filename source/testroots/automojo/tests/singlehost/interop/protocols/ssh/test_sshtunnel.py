"""
    Test module for SshTunnel functionality.
"""

import automojo.testbase as testbase
from automojo.testbase.mocking import create_module_patch

from automojo.interop.protocols.ssh import sshtunnel


class DummyTransport:
    def __init__(self):
        self.closed = False

    def close(self):
        self.closed = True


class DummySocket:
    def __init__(self, port=0):
        self._port = port if port != 0 else 5432
        self.closed = False
        self.bound_address = None
        self.listening = False

    def setsockopt(self, level, optname, value):
        pass

    def bind(self, address):
        self.bound_address = address

    def getsockname(self):
        return ('127.0.0.1', self._port)

    def listen(self, backlog):
        self.listening = True

    def close(self):
        self.closed = True

    def accept(self):
        # Mock accept that raises an exception to exit the loop
        raise OSError("Mock socket closed")


class DummySSHClient:
    def __init__(self):
        self.closed = False
        self.transport = DummyTransport()

    def get_transport(self):
        return self.transport

    def close(self):
        self.closed = True


def test_tunnel_direct_creation_fails():
    """
        Test that direct SshTunnel creation raises RuntimeError.
    """
    ssh_client = DummySSHClient()
    
    try:
        tunnel = sshtunnel.SshTunnel(ssh_client, 5433, 'localhost', 5432)
        testbase.assert_equal(True, False, "Should have raised RuntimeError")
    except RuntimeError as e:
        testbase.assert_equal("SshTunnel instances should only be created through SshAgent.open_tunnel() method" in str(e), True)
    return


def test_tunnel_internal_creation():
    """
        Test that internal tunnel creation works correctly.
    """
    ssh_client = DummySSHClient()
    
    with create_module_patch(sshtunnel.socket, "socket") as mock_socket:
        mock_socket.configure(side_effect=lambda af, sock_type: DummySocket(5433))
        
        with create_module_patch(sshtunnel.threading, "Thread") as mock_thread:
            mock_thread_instance = mock_thread.return_value
            mock_thread_instance.start = lambda: None
            
            tunnel = sshtunnel.SshTunnel._create_internal(ssh_client, 5433, 'localhost', 5432)
            
            testbase.assert_equal(tunnel.local_port, 5433)
            testbase.assert_equal(tunnel.remote_host, 'localhost')
            testbase.assert_equal(tunnel.remote_port, 5432)
            testbase.assert_equal(tunnel.is_active, True)
    return


def test_tunnel_context_manager():
    """
        Test that tunnel works as a context manager.
    """
    ssh_client = DummySSHClient()
    
    with create_module_patch(sshtunnel.socket, "socket") as mock_socket:
        mock_socket.configure(side_effect=lambda af, sock_type: DummySocket(5433))
        
        with create_module_patch(sshtunnel.threading, "Thread") as mock_thread:
            mock_thread_instance = mock_thread.return_value
            mock_thread_instance.start = lambda: None
            mock_thread_instance.is_alive = lambda: False
            
            tunnel = sshtunnel.SshTunnel._create_internal(ssh_client, 5433, 'localhost', 5432)
            
            with tunnel:
                testbase.assert_equal(tunnel.is_active, True)
            
            # Should be shut down after exiting context
            testbase.assert_equal(tunnel.is_active, False)
    return


def test_get_connection_string():
    """
        Test generating connection strings.
    """
    ssh_client = DummySSHClient()
    
    with create_module_patch(sshtunnel.socket, "socket") as mock_socket:
        mock_socket.configure(side_effect=lambda af, sock_type: DummySocket(5433))
        
        with create_module_patch(sshtunnel.threading, "Thread") as mock_thread:
            mock_thread_instance = mock_thread.return_value
            mock_thread_instance.start = lambda: None
            
            tunnel = sshtunnel.SshTunnel._create_internal(ssh_client, 5433, 'localhost', 5432)
            
            # Test PostgreSQL connection string
            conn_str = tunnel.get_connection_string('mydb', 'user', 'postgresql')
            testbase.assert_equal(conn_str, 'postgresql://user@127.0.0.1:5433/mydb')
            
            # Test MySQL connection string
            conn_str = tunnel.get_connection_string('mydb', 'user', 'mysql')
            testbase.assert_equal(conn_str, 'mysql://user@127.0.0.1:5433/mydb')
            
            # Test basic host:port
            conn_str = tunnel.get_connection_string()
            testbase.assert_equal(conn_str, '127.0.0.1:5433')
    return


def test_tunnel_properties():
    """
        Test tunnel properties.
    """
    ssh_client = DummySSHClient()
    
    with create_module_patch(sshtunnel.socket, "socket") as mock_socket:
        mock_socket.configure(side_effect=lambda af, sock_type: DummySocket(5433))
        
        with create_module_patch(sshtunnel.threading, "Thread") as mock_thread:
            mock_thread_instance = mock_thread.return_value
            mock_thread_instance.start = lambda: None
            
            tunnel = sshtunnel.SshTunnel._create_internal(ssh_client, 5433, 'db.example.com', 3306)
            
            testbase.assert_equal(tunnel.local_port, 5433)
            testbase.assert_equal(tunnel.remote_host, 'db.example.com')
            testbase.assert_equal(tunnel.remote_port, 3306)
            testbase.assert_equal(tunnel.is_active, True)
    return