"""
LaunchD service backend for macOS systems
"""

import subprocess
import os
from ..utils import print_success, print_error, print_warning, setup_logging

class LaunchdBackend:
    """Handle launchd services on macOS"""

    def is_available(self):
        """Check if launchd is available (macOS)"""
        return os.uname().sysname == 'Darwin'

    def list_services(self):
        """List all launchd services"""
        try:
            # Use launchctl to list services
            result = subprocess.run(['launchctl', 'list'],
                                  capture_output=True, text=True, timeout=10)

            if result.returncode != 0:
                print_error("Failed to list launchd services")
                return []

            services = []
            lines = result.stdout.strip().split('\n')

            # Skip header line
            for line in lines[1:]:
                if line.strip():
                    parts = line.split('\t')
                    if len(parts) >= 3:
                        pid = parts[0].strip()
                        status = parts[1].strip()
                        label = parts[2].strip()

                        # Convert PID to int if possible
                        try:
                            pid_int = int(pid) if pid != '-' else None
                        except ValueError:
                            pid_int = None

                        services.append({
                            'label': label,
                            'pid': pid_int,
                            'status': status,
                            'last_exit_code': pid if pid != '-' else None
                        })

            return services

        except subprocess.TimeoutExpired:
            print_error("Timeout listing launchd services")
            return []
        except Exception as e:
            print_error(f"Error listing launchd services: {e}")
            setup_logging().error(f"launchd list_services error: {e}")
            return []

    def get_service_status(self, service_label):
        """Get detailed status of a launchd service"""
        try:
            result = subprocess.run(['launchctl', 'print', service_label],
                                  capture_output=True, text=True, timeout=10)

            return {
                'label': service_label,
                'exit_code': result.returncode,
                'stdout': result.stdout,
                'stderr': result.stderr
            }

        except subprocess.TimeoutExpired:
            print_error(f"Timeout getting status for {service_label}")
            return None
        except Exception as e:
            print_error(f"Error getting service status: {e}")
            setup_logging().error(f"launchd get_service_status error: {e}")
            return None

    def start_service(self, service_label):
        """Start a launchd service"""
        try:
            result = subprocess.run(['sudo', 'launchctl', 'start', service_label],
                                  capture_output=True, text=True, timeout=30)

            success = result.returncode == 0
            if success:
                print_success(f"Started service {service_label}")
            else:
                print_error(f"Failed to start service {service_label}: {result.stderr}")

            # Log action
            setup_logging().info(f"launchd start_service: {service_label} success={success}")

            return success

        except subprocess.TimeoutExpired:
            print_error(f"Timeout starting service {service_label}")
            return False
        except Exception as e:
            print_error(f"Error starting service: {e}")
            setup_logging().error(f"launchd start_service error: {e}")
            return False

    def stop_service(self, service_label):
        """Stop a launchd service"""
        try:
            result = subprocess.run(['sudo', 'launchctl', 'stop', service_label],
                                  capture_output=True, text=True, timeout=30)

            success = result.returncode == 0
            if success:
                print_success(f"Stopped service {service_label}")
            else:
                print_error(f"Failed to stop service {service_label}: {result.stderr}")

            # Log action
            setup_logging().info(f"launchd stop_service: {service_label} success={success}")

            return success

        except subprocess.TimeoutExpired:
            print_error(f"Timeout stopping service {service_label}")
            return False
        except Exception as e:
            print_error(f"Error stopping service: {e}")
            setup_logging().error(f"launchd stop_service error: {e}")
            return False

    def restart_service(self, service_label):
        """Restart a launchd service"""
        try:
            # Stop and start
            stop_result = subprocess.run(['sudo', 'launchctl', 'stop', service_label],
                                       capture_output=True, text=True, timeout=30)

            start_result = subprocess.run(['sudo', 'launchctl', 'start', service_label],
                                        capture_output=True, text=True, timeout=30)

            success = start_result.returncode == 0
            if success:
                print_success(f"Restarted service {service_label}")
            else:
                print_error(f"Failed to restart service {service_label}: {start_result.stderr}")

            # Log action
            setup_logging().info(f"launchd restart_service: {service_label} success={success}")

            return success

        except subprocess.TimeoutExpired:
            print_error(f"Timeout restarting service {service_label}")
            return False
        except Exception as e:
            print_error(f"Error restarting service: {e}")
            setup_logging().error(f"launchd restart_service error: {e}")
            return False

    def enable_service(self, service_label):
        """Enable a launchd service (load plist)"""
        try:
            # Find the plist file
            plist_paths = [
                f'/Library/LaunchDaemons/{service_label}.plist',
                f'/System/Library/LaunchDaemons/{service_label}.plist',
                f'/Library/LaunchAgents/{service_label}.plist',
                f'/System/Library/LaunchAgents/{service_label}.plist'
            ]

            plist_file = None
            for path in plist_paths:
                if os.path.exists(path):
                    plist_file = path
                    break

            if not plist_file:
                print_error(f"Could not find plist file for {service_label}")
                return False

            result = subprocess.run(['sudo', 'launchctl', 'load', plist_file],
                                  capture_output=True, text=True, timeout=30)

            success = result.returncode == 0
            if success:
                print_success(f"Enabled service {service_label}")
            else:
                print_error(f"Failed to enable service {service_label}: {result.stderr}")

            # Log action
            setup_logging().info(f"launchd enable_service: {service_label} success={success}")

            return success

        except subprocess.TimeoutExpired:
            print_error(f"Timeout enabling service {service_label}")
            return False
        except Exception as e:
            print_error(f"Error enabling service: {e}")
            setup_logging().error(f"launchd enable_service error: {e}")
            return False

    def disable_service(self, service_label):
        """Disable a launchd service (unload plist)"""
        try:
            # Find the plist file
            plist_paths = [
                f'/Library/LaunchDaemons/{service_label}.plist',
                f'/System/Library/LaunchDaemons/{service_label}.plist',
                f'/Library/LaunchAgents/{service_label}.plist',
                f'/System/Library/LaunchAgents/{service_label}.plist'
            ]

            plist_file = None
            for path in plist_paths:
                if os.path.exists(path):
                    plist_file = path
                    break

            if not plist_file:
                print_error(f"Could not find plist file for {service_label}")
                return False

            result = subprocess.run(['sudo', 'launchctl', 'unload', plist_file],
                                  capture_output=True, text=True, timeout=30)

            success = result.returncode == 0
            if success:
                print_success(f"Disabled service {service_label}")
            else:
                print_error(f"Failed to disable service {service_label}: {result.stderr}")

            # Log action
            setup_logging().info(f"launchd disable_service: {service_label} success={success}")

            return success

        except subprocess.TimeoutExpired:
            print_error(f"Timeout disabling service {service_label}")
            return False
        except Exception as e:
            print_error(f"Error disabling service: {e}")
            setup_logging().error(f"launchd disable_service error: {e}")
            return False