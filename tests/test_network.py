"""
Tests for network inspection functionality
"""

import unittest
from unittest.mock import patch, MagicMock
from core.network import show_ports, map_port_to_process, find_free_port

class TestNetwork(unittest.TestCase):

    def setUp(self):
        """Set up test fixtures"""
        self.mock_conn = MagicMock()
        self.mock_conn.pid = 1234
        self.mock_conn.laddr = MagicMock()
        self.mock_conn.laddr.ip = '127.0.0.1'
        self.mock_conn.laddr.port = 8080
        self.mock_conn.raddr = None
        self.mock_conn.status = 'LISTEN'
        self.mock_conn.family = 2  # AF_INET
        self.mock_conn.type = 1    # SOCK_STREAM

    @patch('psutil.net_connections')
    @patch('psutil.Process')
    @patch('core.network.print_table')
    @patch('core.network.print_success')
    def test_show_ports_listening(self, mock_print_success, mock_print_table, mock_process, mock_net_connections):
        """Test showing listening ports"""
        mock_net_connections.return_value = [self.mock_conn]
        mock_proc = MagicMock()
        mock_proc.name.return_value = 'test_server'
        mock_process.return_value = mock_proc

        show_ports(listening=True)

        mock_print_table.assert_called_once()
        mock_print_success.assert_called_once()

    @patch('psutil.net_connections')
    @patch('psutil.Process')
    @patch('core.network.print_success')
    def test_map_port_to_process(self, mock_print_success, mock_process, mock_net_connections):
        """Test mapping port to process"""
        mock_net_connections.return_value = [self.mock_conn]
        mock_proc = MagicMock()
        mock_proc.name.return_value = 'test_server'
        mock_process.return_value = mock_proc

        map_port_to_process(8080)

        mock_print_success.assert_called()

    @patch('socket.socket')
    def test_find_free_port(self, mock_socket):
        """Test finding free port"""
        mock_sock_instance = MagicMock()
        mock_sock_instance.bind.side_effect = [OSError, None]  # First port in use, second free
        mock_socket.return_value.__enter__.return_value = mock_sock_instance

        result = find_free_port(1024, 1025)

        self.assertEqual(result, 1025)
        mock_sock_instance.bind.assert_called()

if __name__ == '__main__':
    unittest.main()