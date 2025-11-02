"""
SystemD service backend for Linux systems
"""

import subprocess
import os
from ..utils import print_success, print_error, print_warning, setup_logging

class SystemdBackend:
    """Handle systemd services on Linux"""

    def is_available(self):
        """Check if systemd is available"""
        try:
            result = subprocess.run(['systemctl', '--version'],
                                  capture_output=True, text=True, timeout=5)
            return result.returncode == 0
        except (subprocess.TimeoutExpired, FileNotFoundError):
            return False

    def list_services(self):
        """List all systemd services"""
        try:
            result = subprocess.run(['systemctl', 'list-units', '--type=service', '--all'],
                                  capture_output=True, text=True, timeout=10)

            if result.returncode != 0:
                print_error("Failed to list systemd services")
                return []

            services = []
            lines = result.stdout.strip().split('\n')

            # Skip header lines
            for line in lines[1:]:
                if line.strip() and not line.startswith('LOAD'):
                    parts = line.split()
                    if len(parts) >= 4:
                        service_name = parts[0]
                        load_state = parts[1]
                        active_state = parts[2]
                        sub_state = parts[3]

                        services.append({
                            'name': service_name,
                            'load_state': load_state,
                            'active_state': active_state,
                            'sub_state': sub_state,
                            'description': ' '.join(parts[4:]) if len(parts) > 4 else ''
                        })

            return services

        except subprocess.TimeoutExpired:
            print_error("Timeout listing systemd services")
            return []
        except Exception as e:
            print_error(f"Error listing systemd services: {e}")
            setup_logging().error(f"systemd list_services error: {e}")
            return []

    def get_service_status(self, service_name):
        """Get detailed status of a service"""
        try:
            result = subprocess.run(['systemctl', 'status', service_name],
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
            setup_logging().error(f"systemd get_service_status error: {e}")
            return None

    def start_service(self, service_name):
        """Start a systemd service"""
        try:
            result = subprocess.run(['sudo', 'systemctl', 'start', service_name],
                                  capture_output=True, text=True, timeout=30)

            success = result.returncode == 0
            if success:
                print_success(f"Started service {service_name}")
            else:
                print_error(f"Failed to start service {service_name}: {result.stderr}")

            # Log action
            setup_logging().info(f"systemd start_service: {service_name} success={success}")

            return success

        except subprocess.TimeoutExpired:
            print_error(f"Timeout starting service {service_name}")
            return False
        except Exception as e:
            print_error(f"Error starting service: {e}")
            setup_logging().error(f"systemd start_service error: {e}")
            return False

    def stop_service(self, service_name):
        """Stop a systemd service"""
        try:
            result = subprocess.run(['sudo', 'systemctl', 'stop', service_name],
                                  capture_output=True, text=True, timeout=30)

            success = result.returncode == 0
            if success:
                print_success(f"Stopped service {service_name}")
            else:
                print_error(f"Failed to stop service {service_name}: {result.stderr}")

            # Log action
            setup_logging().info(f"systemd stop_service: {service_name} success={success}")

            return success

        except subprocess.TimeoutExpired:
            print_error(f"Timeout stopping service {service_name}")
            return False
        except Exception as e:
            print_error(f"Error stopping service: {e}")
            setup_logging().error(f"systemd stop_service error: {e}")
            return False

    def restart_service(self, service_name):
        """Restart a systemd service"""
        try:
            result = subprocess.run(['sudo', 'systemctl', 'restart', service_name],
                                  capture_output=True, text=True, timeout=60)

            success = result.returncode == 0
            if success:
                print_success(f"Restarted service {service_name}")
            else:
                print_error(f"Failed to restart service {service_name}: {result.stderr}")

            # Log action
            setup_logging().info(f"systemd restart_service: {service_name} success={success}")

            return success

        except subprocess.TimeoutExpired:
            print_error(f"Timeout restarting service {service_name}")
            return False
        except Exception as e:
            print_error(f"Error restarting service: {e}")
            setup_logging().error(f"systemd restart_service error: {e}")
            return False

    def enable_service(self, service_name):
        """Enable a systemd service to start on boot"""
        try:
            result = subprocess.run(['sudo', 'systemctl', 'enable', service_name],
                                  capture_output=True, text=True, timeout=30)

            success = result.returncode == 0
            if success:
                print_success(f"Enabled service {service_name}")
            else:
                print_error(f"Failed to enable service {service_name}: {result.stderr}")

            # Log action
            setup_logging().info(f"systemd enable_service: {service_name} success={success}")

            return success

        except subprocess.TimeoutExpired:
            print_error(f"Timeout enabling service {service_name}")
            return False
        except Exception as e:
            print_error(f"Error enabling service: {e}")
            setup_logging().error(f"systemd enable_service error: {e}")
            return False

    def disable_service(self, service_name):
        """Disable a systemd service from starting on boot"""
        try:
            result = subprocess.run(['sudo', 'systemctl', 'disable', service_name],
                                  capture_output=True, text=True, timeout=30)

            success = result.returncode == 0
            if success:
                print_success(f"Disabled service {service_name}")
            else:
                print_error(f"Failed to disable service {service_name}: {result.stderr}")

            # Log action
            setup_logging().info(f"systemd disable_service: {service_name} success={success}")

            return success

        except subprocess.TimeoutExpired:
            print_error(f"Timeout disabling service {service_name}")
            return False
        except Exception as e:
            print_error(f"Error disabling service: {e}")
            setup_logging().error(f"systemd disable_service error: {e}")
            return False