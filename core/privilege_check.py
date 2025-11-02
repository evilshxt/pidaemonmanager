"""
Privilege checking functionality for ProcSight
"""

import os
import sys
import ctypes
from core.utils import print_warning, print_error

def is_admin():
    """
    Check if the current process has administrator/root privileges
    Returns True if running with elevated privileges, False otherwise
    """
    try:
        if os.name == 'nt':  # Windows
            # Try to open a process with PROCESS_QUERY_LIMITED_INFORMATION
            # This will fail if not running as admin
            try:
                return ctypes.windll.shell32.IsUserAnAdmin() != 0
            except:
                return False
        else:  # Unix-like systems (Linux, macOS)
            return os.geteuid() == 0
    except Exception as e:
        print_error(f"Error checking privileges: {e}")
        return False

def require_admin():
    """Check if admin privileges are available, exit if not"""
    if not is_admin():
        print_error("This operation requires administrator privileges")
        if os.name == 'nt':
            print("Please run the terminal as Administrator (Right-click → Run as administrator)")
        else:
            print("Please use 'sudo' to run this command")
        sys.exit(1)

def warn_if_not_admin():
    """Warn user if not running with admin privileges"""
    if not is_admin():
        print_warning("Some operations may require administrator privileges")
        if os.name == 'nt':
            print("For full functionality, run as Administrator")
        else:
            print("For full functionality, use 'sudo'")

def get_current_user():
    """Get current username safely"""
    try:
        return os.getlogin()
    except:
        try:
            return os.environ.get('USER') or os.environ.get('USERNAME') or 'unknown'
        except:
            return 'unknown'

def can_access_process(pid):
    """Check if we can access a specific process"""
    try:
        import psutil
        proc = psutil.Process(pid)
        # Try to access basic info
        proc.name()
        return True
    except (psutil.NoSuchProcess, psutil.AccessDenied):
        return False
    except Exception:
        return False

def check_process_termination_privileges(pid):
    """Check if we can terminate a specific process"""
    try:
        import psutil
        proc = psutil.Process(pid)

        # On Windows, check if it's a system process
        if os.name == 'nt':
            # System processes (PID 4 on Windows) cannot be terminated
            if pid == 4:
                return False

        # Try to check if we can terminate (this is a best-effort check)
        # On Unix systems, root can terminate most processes
        # On Windows, admin can terminate most processes
        return is_admin()

    except (psutil.NoSuchProcess, psutil.AccessDenied):
        return False
    except Exception:
        return False