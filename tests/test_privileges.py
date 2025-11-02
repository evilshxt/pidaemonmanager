"""
Tests for privilege checking functionality
"""

import unittest
from unittest.mock import patch
from core.privilege_check import is_admin, require_admin, get_current_user

class TestPrivileges(unittest.TestCase):

    @patch('os.name', 'nt')
    @patch('ctypes.windll.shell32.IsUserAnAdmin')
    def test_is_admin_windows_true(self, mock_is_admin):
        """Test admin check on Windows returns True"""
        mock_is_admin.return_value = 1

        result = is_admin()
        self.assertTrue(result)

    @patch('os.name', 'nt')
    @patch('ctypes.windll.shell32.IsUserAnAdmin')
    def test_is_admin_windows_false(self, mock_is_admin):
        """Test admin check on Windows returns False"""
        mock_is_admin.return_value = 0

        result = is_admin()
        self.assertFalse(result)

    @patch('os.name', 'posix')
    @patch('os.geteuid', create=True)
    def test_is_admin_unix_root(self, mock_geteuid):
        """Test admin check on Unix returns True for root"""
        mock_geteuid.return_value = 0

        result = is_admin()
        self.assertTrue(result)

    @patch('os.name', 'posix')
    @patch('os.geteuid', create=True)
    def test_is_admin_unix_non_root(self, mock_geteuid):
        """Test admin check on Unix returns False for non-root"""
        mock_geteuid.return_value = 1000

        result = is_admin()
        self.assertFalse(result)

    @patch('core.privilege_check.is_admin')
    def test_require_admin_success(self, mock_is_admin):
        """Test require_admin doesn't exit when admin"""
        mock_is_admin.return_value = True

        # Should not raise SystemExit
        try:
            require_admin()
        except SystemExit:
            self.fail("require_admin() raised SystemExit when admin")

    @patch('core.privilege_check.is_admin')
    @patch('sys.exit')
    def test_require_admin_failure(self, mock_exit, mock_is_admin):
        """Test require_admin exits when not admin"""
        mock_is_admin.return_value = False

        require_admin()

        mock_exit.assert_called_once_with(1)

    @patch('os.getlogin')
    def test_get_current_user_login(self, mock_getlogin):
        """Test getting current user via getlogin"""
        mock_getlogin.return_value = 'testuser'

        result = get_current_user()
        self.assertEqual(result, 'testuser')

    @patch('os.getlogin', side_effect=OSError)
    @patch.dict('os.environ', {'USER': 'envuser'})
    def test_get_current_user_env_user(self, mock_getlogin):
        """Test getting current user via USER env var"""
        result = get_current_user()
        self.assertEqual(result, 'envuser')

    @patch('os.getlogin', side_effect=OSError)
    @patch.dict('os.environ', {}, clear=True)
    @patch.dict('os.environ', {'USERNAME': 'winuser'})
    def test_get_current_user_env_username(self, mock_getlogin):
        """Test getting current user via USERNAME env var"""
        result = get_current_user()
        self.assertEqual(result, 'winuser')

if __name__ == '__main__':
    unittest.main()