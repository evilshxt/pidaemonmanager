"""
Windows service backend using native Windows APIs
"""

import os
import subprocess
import ctypes
from ctypes import wintypes, byref
import winreg
from ..utils import print_success, print_error, print_warning, setup_logging

# Windows API constants and structures
SC_MANAGER_ALL_ACCESS = 0xF003F
SERVICE_ALL_ACCESS = 0xF01FF
SERVICE_WIN32_OWN_PROCESS = 0x10
SERVICE_WIN32_SHARE_PROCESS = 0x20
SERVICE_KERNEL_DRIVER = 0x1
SERVICE_FILE_SYSTEM_DRIVER = 0x2
SERVICE_INTERACTIVE_PROCESS = 0x100

SERVICE_ACTIVE = 0x1
SERVICE_INACTIVE = 0x2
SERVICE_STATE_ALL = SERVICE_ACTIVE | SERVICE_INACTIVE

class WindowsBackend:
    """Handle Windows services using native APIs and sc.exe"""

    def is_available(self):
        """Check if running on Windows"""
        return os.name == 'nt'

    def list_services(self):
        """List all Windows services"""
        try:
            # Use sc.exe to query services
            result = subprocess.run(['sc.exe', 'query', 'type=', 'service', 'state=', 'all'],
                                  capture_output=True, text=True, timeout=30)

            if result.returncode != 0:
                print_error("Failed to list Windows services")
                return []

            services = []
            lines = result.stdout.split('\n')
            current_service = {}

            for line in lines:
                line = line.strip()
                if line.startswith('SERVICE_NAME:'):
                    if current_service:
                        services.append(current_service)
                    current_service = {'name': line.split(':', 1)[1].strip()}
                elif line.startswith('DISPLAY_NAME:'):
                    current_service['display_name'] = line.split(':', 1)[1].strip()
                elif line.startswith('TYPE:'):
                    current_service['type'] = line.split(':', 1)[1].strip()
                elif line.startswith('STATE:'):
                    current_service['state'] = line.split(':', 1)[1].strip()

            if current_service:
                services.append(current_service)

            return services

        except subprocess.TimeoutExpired:
            print_error("Timeout listing Windows services")
            return []
        except Exception as e:
            print_error(f"Error listing Windows services: {e}")
            setup_logging().error(f"windows list_services error: {e}")
            return []

    def get_service_status(self, service_name):
        """Get detailed status of a Windows service"""
        try:
            result = subprocess.run(['sc.exe', 'query', service_name],
                                  capture_output=True, text=True, timeout=10)

            return {
                'name': service_name,
                'exit_code': result.returncode,
                'stdout': result.stdout,
                'stderr': result.stderr
            }

        except subprocess.TimeoutExpired:
            print_error(f"Timeout getting status for {service_name}")
            return None
        except Exception as e:
            print_error(f"Error getting service status: {e}")
            setup_logging().error(f"windows get_service_status error: {e}")
            return None

    def start_service(self, service_name):
        """Start a Windows service"""
        try:
            result = subprocess.run(['sc.exe', 'start', service_name],
                                  capture_output=True, text=True, timeout=30)

            success = result.returncode == 0
            if success:
                print_success(f"Started service {service_name}")
            else:
                print_error(f"Failed to start service {service_name}: {result.stderr}")

            # Log action
            setup_logging().info(f"windows start_service: {service_name} success={success}")

            return success

        except subprocess.TimeoutExpired:
            print_error(f"Timeout starting service {service_name}")
            return False
        except Exception as e:
            print_error(f"Error starting service: {e}")
            setup_logging().error(f"windows start_service error: {e}")
            return False

    def stop_service(self, service_name):
        """Stop a Windows service"""
        try:
            result = subprocess.run(['sc.exe', 'stop', service_name],
                                  capture_output=True, text=True, timeout=30)

            success = result.returncode == 0
            if success:
                print_success(f"Stopped service {service_name}")
            else:
                print_error(f"Failed to stop service {service_name}: {result.stderr}")

            # Log action
            setup_logging().info(f"windows stop_service: {service_name} success={success}")

            return success

        except subprocess.TimeoutExpired:
            print_error(f"Timeout stopping service {service_name}")
            return False
        except Exception as e:
            print_error(f"Error stopping service: {e}")
            setup_logging().error(f"windows stop_service error: {e}")
            return False

    def restart_service(self, service_name):
        """Restart a Windows service"""
        try:
            # Stop and start
            stop_result = subprocess.run(['sc.exe', 'stop', service_name],
                                       capture_output=True, text=True, timeout=30)
            if stop_result.returncode != 0:
                print_error(f"Failed to stop service {service_name} for restart")
                return False

            start_result = subprocess.run(['sc.exe', 'start', service_name],
                                        capture_output=True, text=True, timeout=30)

            success = start_result.returncode == 0
            if success:
                print_success(f"Restarted service {service_name}")
            else:
                print_error(f"Failed to restart service {service_name}: {start_result.stderr}")

            # Log action
            setup_logging().info(f"windows restart_service: {service_name} success={success}")

            return success

        except subprocess.TimeoutExpired:
            print_error(f"Timeout restarting service {service_name}")
            return False
        except Exception as e:
            print_error(f"Error restarting service: {e}")
            setup_logging().error(f"windows restart_service error: {e}")
            return False

    def enable_service(self, service_name):
        """Enable a Windows service to start automatically"""
        try:
            result = subprocess.run(['sc.exe', 'config', service_name, 'start=', 'auto'],
                                  capture_output=True, text=True, timeout=30)

            success = result.returncode == 0
            if success:
                print_success(f"Enabled service {service_name}")
            else:
                print_error(f"Failed to enable service {service_name}: {result.stderr}")

            # Log action
            setup_logging().info(f"windows enable_service: {service_name} success={success}")

            return success

        except subprocess.TimeoutExpired:
            print_error(f"Timeout enabling service {service_name}")
            return False
        except Exception as e:
            print_error(f"Error enabling service: {e}")
            setup_logging().error(f"windows enable_service error: {e}")
            return False

    def disable_service(self, service_name):
        """Disable a Windows service from starting automatically"""
        try:
            result = subprocess.run(['sc.exe', 'config', service_name, 'start=', 'disabled'],
                                  capture_output=True, text=True, timeout=30)

            success = result.returncode == 0
            if success:
                print_success(f"Disabled service {service_name}")
            else:
                print_error(f"Failed to disable service {service_name}: {result.stderr}")

            # Log action
            setup_logging().info(f"windows disable_service: {service_name} success={success}")

            return success

        except subprocess.TimeoutExpired:
            print_error(f"Timeout disabling service {service_name}")
            return False
        except Exception as e:
            print_error(f"Error disabling service: {e}")
            setup_logging().error(f"windows disable_service error: {e}")
            return False

    def get_service_config(self, service_name):
        """Get service configuration using registry (advanced)"""
        try:
            # Open service key in registry
            key_path = f"SYSTEM\\CurrentControlSet\\Services\\{service_name}"
            key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, key_path)

            # Read common configuration values
            config = {}
            try:
                config['DisplayName'] = winreg.QueryValueEx(key, 'DisplayName')[0]
            except FileNotFoundError:
                pass

            try:
                start_type = winreg.QueryValueEx(key, 'Start')[0]
                start_types = {2: 'Automatic', 3: 'Manual', 4: 'Disabled'}
                config['StartType'] = start_types.get(start_type, f'Unknown ({start_type})')
            except FileNotFoundError:
                pass

            try:
                config['Description'] = winreg.QueryValueEx(key, 'Description')[0]
            except FileNotFoundError:
                pass

            winreg.CloseKey(key)
            return config

        except Exception as e:
            # Registry access might fail without admin rights
            return {}