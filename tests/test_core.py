"""
Tests for core process management functionality
"""

import unittest
import psutil
from unittest.mock import patch, MagicMock
from core.core import inspect_processes, show_process_info, terminate_process, show_top_processes, export_snapshot

class TestCore(unittest.TestCase):

    def setUp(self):
        """Set up test fixtures"""
        self.mock_proc = MagicMock()
        self.mock_proc.info = {
            'pid': 1234,
            'name': 'test_process',
            'username': 'testuser',
            'cpu_percent': 5.0,
            'memory_percent': 10.0,
            'cmdline': ['test_process', '--arg']
        }

    @patch('psutil.process_iter')
    @patch('core.core.print_table')
    @patch('core.core.print_success')
    def test_inspect_processes(self, mock_print_success, mock_print_table, mock_process_iter):
        """Test process inspection"""
        mock_process_iter.return_value = [self.mock_proc]

        inspect_processes('test')

        mock_print_table.assert_called_once()
        mock_print_success.assert_called_once()

    @patch('psutil.Process')
    @patch('core.core.print_success')
    def test_show_process_info(self, mock_print_success, mock_process):
        """Test showing process information"""
        mock_proc_instance = MagicMock()
        mock_proc_instance.name.return_value = 'test_process'
        mock_proc_instance.as_dict.return_value = {
            'pid': 1234,
            'name': 'test_process',
            'username': 'testuser',
            'cpu_percent': 5.0,
            'memory_percent': 10.0,
            'num_threads': 4,
            'create_time': 1609459200.0,
            'cmdline': ['test_process'],
            'exe': '/usr/bin/test_process',
            'cwd': '/home/user'
        }
        mock_proc_instance.children.return_value = []
        mock_process.return_value = mock_proc_instance

        show_process_info(1234)

        mock_print_success.assert_called()

    @patch('core.privilege_check.is_admin')
    @patch('builtins.input')
    @patch('psutil.Process')
    def test_terminate_process_admin_required(self, mock_process, mock_input, mock_is_admin):
        """Test process termination requires admin"""
        mock_is_admin.return_value = False
        mock_proc_instance = MagicMock()
        mock_process.return_value = mock_proc_instance

        terminate_process(1234)

        # Should not attempt termination without admin
        mock_proc_instance.terminate.assert_not_called()

    @patch('psutil.process_iter')
    @patch('core.core.print_table')
    @patch('core.core.print_success')
    def test_show_top_processes(self, mock_print_success, mock_print_table, mock_process_iter):
        """Test showing top processes"""
        mock_process_iter.return_value = [self.mock_proc]

        show_top_processes('cpu')

        mock_print_table.assert_called_once()
        mock_print_success.assert_called_once()

    @patch('psutil.process_iter')
    @patch('builtins.open')
    @patch('core.core.print_success')
    def test_export_snapshot_csv(self, mock_print_success, mock_open, mock_process_iter):
        """Test snapshot export to CSV"""
        mock_process_iter.return_value = [self.mock_proc]

        export_snapshot('csv', 'test.csv')

        # Check that open was called for the CSV file (first call)
        self.assertTrue(mock_open.called)
        mock_print_success.assert_called_once()

    @patch('psutil.process_iter')
    @patch('builtins.open')
    @patch('core.core.print_success')
    def test_export_snapshot_json(self, mock_print_success, mock_open, mock_process_iter):
        """Test snapshot export to JSON"""
        mock_process_iter.return_value = [self.mock_proc]

        export_snapshot('json', 'test.json')

        # Check that open was called for the JSON file (first call)
        self.assertTrue(mock_open.called)
        mock_print_success.assert_called_once()

if __name__ == '__main__':
    unittest.main()