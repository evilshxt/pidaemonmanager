"""
Core process management functionality for ProcSight
"""

import psutil
import os
import sys
from datetime import datetime
from core.utils import print_table, print_success, print_error, print_warning, setup_logging

def inspect_processes(pattern):
    """Search for processes by name or command pattern"""
    try:
        matching_processes = []
        for proc in psutil.process_iter(['pid', 'name', 'username', 'cpu_percent', 'memory_percent', 'cmdline']):
            try:
                name = proc.info['name'] or ''
                cmdline = ' '.join(proc.info['cmdline'] or [])
                if pattern.lower() in name.lower() or pattern.lower() in cmdline.lower():
                    matching_processes.append({
                        'PID': proc.info['pid'],
                        'Name': name,
                        'User': proc.info['username'] or 'N/A',
                        'CPU%': f"{proc.info['cpu_percent']:.1f}",
                        'Memory%': f"{proc.info['memory_percent']:.1f}",
                        'Command': cmdline[:50] + '...' if len(cmdline) > 50 else cmdline
                    })
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue

        if not matching_processes:
            print_warning(f"No processes found matching '{pattern}'")
            return

        headers = ['PID', 'Name', 'User', 'CPU%', 'Memory%', 'Command']
        print_table(matching_processes, headers)
        print_success(f"Found {len(matching_processes)} matching processes")

        # Interactive selection for termination
        if matching_processes:
            print(f"\n{Fore.YELLOW}Process Management Options:{Style.RESET_ALL}")
            print(f"{Fore.GREEN}Enter process number to terminate (1-{len(matching_processes)}), 'a' for all, or Enter to skip:{Style.RESET_ALL}")

            for i, proc in enumerate(matching_processes, 1):
                print(f"{Fore.CYAN}{i}.{Style.RESET_ALL} PID {proc['PID']}: {proc['Name']}")

            choice = input(f"\n{Fore.YELLOW}Choice: {Style.RESET_ALL}").strip().lower()

            if choice == 'a':
                # Terminate all matching processes
                print_warning(f"Terminating ALL {len(matching_processes)} matching processes...")
                for proc in matching_processes:
                    pid = proc['PID']
                    print(f"Terminating PID {pid} ({proc['Name']})...")
                    terminate_process(pid, force=False)
            elif choice and choice.isdigit():
                idx = int(choice) - 1
                if 0 <= idx < len(matching_processes):
                    proc = matching_processes[idx]
                    pid = proc['PID']
                    print(f"Terminating PID {pid} ({proc['Name']})...")
                    terminate_process(pid, force=False)
                else:
                    print_error("Invalid process number")
            else:
                print_info("No processes terminated")

    except Exception as e:
        print_error(f"Error inspecting processes: {e}")
        setup_logging().error(f"inspect_processes error: {e}")

def show_process_info(pid):
    """Show detailed information for a specific process"""
    try:
        proc = psutil.Process(pid)
        info = proc.as_dict(attrs=['pid', 'name', 'username', 'cpu_percent', 'memory_percent',
                                   'num_threads', 'create_time', 'cmdline', 'exe', 'cwd'])

        print_success(f"Process Information for PID {pid}")
        print(f"Name: {info['name']}")
        print(f"PID: {info['pid']}")
        print(f"User: {info['username'] or 'N/A'}")
        print(f"CPU Usage: {info['cpu_percent']:.1f}%")
        print(f"Memory Usage: {info['memory_percent']:.1f}%")
        print(f"Threads: {info['num_threads']}")
        print(f"Created: {datetime.fromtimestamp(info['create_time']).strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"Executable: {info['exe'] or 'N/A'}")
        print(f"Working Directory: {info['cwd'] or 'N/A'}")
        print(f"Command Line: {' '.join(info['cmdline'] or [])}")

        # Show child processes
        try:
            children = proc.children(recursive=True)
            if children:
                print(f"\nChild Processes ({len(children)}):")
                for child in children:
                    print(f"  - PID {child.pid}: {child.name()}")
        except:
            pass

    except psutil.NoSuchProcess:
        print_error(f"Process with PID {pid} not found")
    except psutil.AccessDenied:
        print_error(f"Access denied to process {pid} (try running as administrator)")
    except Exception as e:
        print_error(f"Error getting process info: {e}")
        setup_logging().error(f"show_process_info error: {e}")

def terminate_process(pid, force=False):
    """Terminate a process safely"""
    try:
        proc = psutil.Process(pid)

        # Check if we have permission
        from .privilege_check import is_admin
        if not is_admin():
            print_warning("Termination requires administrator privileges")
            print("On Windows: Run terminal as Administrator")
            print("On Linux/macOS: Use 'sudo python procsight.py terminate --pid {pid}'")
            return

        # Confirm termination
        name = proc.name()
        response = input(f"Terminate process '{name}' (PID {pid})? [y/N]: ")
        if response.lower() not in ['y', 'yes']:
            print("Termination cancelled")
            return

        if force:
            proc.kill()
            print_success(f"Force killed process {pid} ({name})")
        else:
            proc.terminate()
            print_success(f"Terminated process {pid} ({name})")

        # Log the action
        logger = setup_logging()
        logger.info(f"Terminated process PID={pid} Name={name} Force={force}")

    except psutil.NoSuchProcess:
        print_error(f"Process with PID {pid} not found")
    except psutil.AccessDenied:
        print_error(f"Access denied to terminate process {pid}")
    except Exception as e:
        print_error(f"Error terminating process: {e}")
        setup_logging().error(f"terminate_process error: {e}")

def show_top_processes(sort_by='cpu'):
    """Show top processes by resource usage"""
    try:
        processes = []
        for proc in psutil.process_iter(['pid', 'name', 'cpu_percent', 'memory_percent']):
            try:
                processes.append({
                    'pid': proc.info['pid'],
                    'name': proc.info['name'],
                    'cpu': proc.info['cpu_percent'],
                    'memory': proc.info['memory_percent']
                })
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue

        if sort_by == 'cpu':
            processes.sort(key=lambda x: x['cpu'], reverse=True)
        elif sort_by == 'memory':
            processes.sort(key=lambda x: x['memory'], reverse=True)

        top_processes = processes[:20]  # Show top 20

        table_data = []
        for proc in top_processes:
            table_data.append({
                'PID': proc['pid'],
                'Name': proc['name'],
                'CPU%': f"{proc['cpu']:.1f}",
                'Memory%': f"{proc['memory']:.1f}"
            })

        headers = ['PID', 'Name', 'CPU%', 'Memory%']
        print_table(table_data, headers)
        print_success(f"Top {len(top_processes)} processes by {sort_by.upper()} usage")

    except Exception as e:
        print_error(f"Error showing top processes: {e}")
        setup_logging().error(f"show_top_processes error: {e}")

def export_snapshot(format_type='csv', output_file=None):
    """Export system snapshot to CSV or JSON"""
    try:
        import csv
        import json

        # Collect process data
        processes = []
        for proc in psutil.process_iter(['pid', 'name', 'username', 'cpu_percent', 'memory_percent', 'cmdline']):
            try:
                processes.append({
                    'pid': proc.info['pid'],
                    'name': proc.info['name'],
                    'username': proc.info['username'],
                    'cpu_percent': proc.info['cpu_percent'],
                    'memory_percent': proc.info['memory_percent'],
                    'cmdline': ' '.join(proc.info['cmdline'] or [])
                })
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue

        if not output_file:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            output_file = f"procsight_snapshot_{timestamp}.{format_type}"

        if format_type == 'csv':
            with open(output_file, 'w', newline='', encoding='utf-8') as f:
                if processes:
                    writer = csv.DictWriter(f, fieldnames=processes[0].keys())
                    writer.writeheader()
                    writer.writerows(processes)
        elif format_type == 'json':
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(processes, f, indent=2)

        print_success(f"Snapshot exported to {output_file} ({len(processes)} processes)")

        # Log the export
        setup_logging().info(f"Exported snapshot to {output_file} format={format_type} processes={len(processes)}")

    except Exception as e:
        print_error(f"Error exporting snapshot: {e}")
        setup_logging().error(f"export_snapshot error: {e}")

def get_service_backend():
    """Get the appropriate service backend for the current platform"""
    try:
        import platform
        system = platform.system().lower()

        if system == 'linux':
            from ..services.systemd_backend import SystemdBackend
            backend = SystemdBackend()
            if backend.is_available():
                return backend
        elif system == 'windows':
            from ..services.windows_backend import WindowsBackend
            backend = WindowsBackend()
            if backend.is_available():
                return backend
        elif system == 'darwin':  # macOS
            from ..services.launchd_backend import LaunchdBackend
            backend = LaunchdBackend()
            if backend.is_available():
                return backend

        return None

    except Exception as e:
        print_error(f"Error getting service backend: {e}")
        return None

def list_services():
    """List system services using appropriate backend"""
    try:
        backend = get_service_backend()
        if not backend:
            print_error("No suitable service backend found for this platform")
            return

        services = backend.list_services()
        if not services:
            print_warning("No services found or access denied")
            return

        # Display services in table format
        table_data = []
        for service in services:
            if isinstance(service, dict):
                # Normalize service data across backends
                if 'name' in service:  # Windows/systemd style
                    table_data.append({
                        'Name': service.get('name', ''),
                        'Display Name': service.get('display_name', service.get('description', '')),
                        'State': service.get('state', service.get('active_state', 'Unknown')),
                        'Type': service.get('type', 'Service')
                    })
                elif 'label' in service:  # launchd style
                    table_data.append({
                        'Name': service.get('label', ''),
                        'Display Name': service.get('label', ''),
                        'State': 'Running' if service.get('pid') else 'Stopped',
                        'Type': 'LaunchD'
                    })

        if table_data:
            headers = ['Name', 'Display Name', 'State', 'Type']
            print_table(table_data, headers, "System Services")
            print_success(f"Found {len(table_data)} services")
        else:
            print_warning("No services to display")

    except Exception as e:
        print_error(f"Error listing services: {e}")
        setup_logging().error(f"list_services error: {e}")

def manage_service(action, service_name):
    """Manage a service (start, stop, restart, enable, disable)"""
    try:
        backend = get_service_backend()
        if not backend:
            print_error("No suitable service backend found for this platform")
            return False

        # Check admin privileges for service management
        from .privilege_check import is_admin
        if not is_admin():
            print_error("Service management requires administrator privileges")
            return False

        actions = {
            'start': backend.start_service,
            'stop': backend.stop_service,
            'restart': backend.restart_service,
            'enable': backend.enable_service,
            'disable': backend.disable_service
        }

        if action not in actions:
            print_error(f"Unknown action: {action}")
            return False

        return actions[action](service_name)

    except Exception as e:
        print_error(f"Error managing service: {e}")
        setup_logging().error(f"manage_service error: {e}")
        return False

def audit_system():
    """Perform security audit of the system"""
    try:
        print_success("Starting system security audit...")
        issues = []
        malware_processes = []

        # Check for suspicious processes
        print_info("Checking for suspicious processes...")
        for proc in psutil.process_iter(['pid', 'name', 'username', 'cmdline']):
            try:
                name = proc.info['name'] or ''
                cmdline = ' '.join(proc.info['cmdline'] or [])

                # Flag potentially suspicious processes
                suspicious_indicators = [
                    'miner', 'trojan', 'virus', 'malware', 'keylogger',
                    'ransomware', 'backdoor', 'rootkit', 'exploit',
                    'payload', 'shell', 'netcat', 'nc', 'meterpreter'
                ]

                is_malware = any(indicator in name.lower() or indicator in cmdline.lower() for indicator in suspicious_indicators)

                if is_malware:
                    malware_processes.append({
                        'pid': proc.info['pid'],
                        'name': name,
                        'cmdline': cmdline
                    })
                    issues.append({
                        'type': 'MALWARE DETECTED',
                        'severity': 'CRITICAL',
                        'details': f"PID {proc.info['pid']}: {name} - {cmdline[:100]}"
                    })

                # Check for unsigned binaries (basic check)
                if os.name == 'nt':  # Windows
                    try:
                        exe_path = proc.exe()
                        if exe_path and not _is_signed_binary(exe_path):
                            issues.append({
                                'type': 'Unsigned Binary',
                                'severity': 'Medium',
                                'details': f"PID {proc.info['pid']}: {exe_path}"
                            })
                    except:
                        pass

            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue

        # Check for privileged ports
        print_info("Checking for privileged ports...")
        connections = psutil.net_connections(kind='inet')
        for conn in connections:
            try:
                if conn.laddr and conn.laddr.port < 1024 and conn.status == 'LISTEN':
                    process_name = 'Unknown'
                    if conn.pid:
                        try:
                            process_name = psutil.Process(conn.pid).name()
                        except:
                            pass

                    issues.append({
                        'type': 'Privileged Port',
                        'severity': 'Low',
                        'details': f"Port {conn.laddr.port} used by {process_name} (PID {conn.pid})"
                    })
            except:
                continue

        # Check for zombie processes
        print_info("Checking for zombie processes...")
        zombie_count = 0
        for proc in psutil.process_iter(['pid', 'name', 'status']):
            try:
                if proc.info['status'] == psutil.STATUS_ZOMBIE:
                    zombie_count += 1
                    issues.append({
                        'type': 'Zombie Process',
                        'severity': 'Medium',
                        'details': f"PID {proc.info['pid']}: {proc.info['name']}"
                    })
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue

        if zombie_count > 0:
            issues.append({
                'type': 'Zombie Summary',
                'severity': 'Medium',
                'details': f"Found {zombie_count} zombie processes"
            })

        # MALWARE SPECIFIC HANDLING
        if malware_processes:
            print(f"\n{Fore.RED}{Style.BRIGHT}🚨 MALWARE DETECTED! 🚨{Style.RESET_ALL}")
            print(f"{Fore.RED}Found {len(malware_processes)} suspicious processes{Style.RESET_ALL}")

            for i, proc in enumerate(malware_processes, 1):
                print(f"{Fore.RED}{i}.{Style.RESET_ALL} PID {proc['pid']}: {proc['name']}")
                print(f"   Command: {proc['cmdline'][:100]}...")

            print(f"\n{Fore.YELLOW}Malware Termination Options:{Style.RESET_ALL}")
            print(f"{Fore.GREEN}Enter process number to kill, 'a' for all, or Enter to skip:{Style.RESET_ALL}")

            choice = input(f"{Fore.RED}CHOICE: {Style.RESET_ALL}").strip().lower()

            if choice == 'a':
                print(f"{Fore.RED}{Style.BRIGHT}⚠️  TERMINATING ALL MALWARE PROCESSES ⚠️{Style.RESET_ALL}")
                for proc in malware_processes:
                    print(f"{Fore.RED}Killing malware PID {proc['pid']} ({proc['name']})...{Style.RESET_ALL}")
                    terminate_process(proc['pid'], force=True)
                    setup_logging().critical(f"MALWARE TERMINATED: PID {proc['pid']} Name {proc['name']}")
            elif choice and choice.isdigit():
                idx = int(choice) - 1
                if 0 <= idx < len(malware_processes):
                    proc = malware_processes[idx]
                    print(f"{Fore.RED}Killing malware PID {proc['pid']} ({proc['name']})...{Style.RESET_ALL}")
                    terminate_process(proc['pid'], force=True)
                    setup_logging().critical(f"MALWARE TERMINATED: PID {proc['pid']} Name {proc['name']}")
                else:
                    print_error("Invalid malware process number")
            else:
                print_warning("Malware processes left running - HIGH RISK!")

        # Display results
        if issues:
            table_data = []
            for issue in issues:
                table_data.append({
                    'Type': issue['type'],
                    'Severity': issue['severity'],
                    'Details': issue['details'][:80] + '...' if len(issue['details']) > 80 else issue['details']
                })

            headers = ['Type', 'Severity', 'Details']
            print_table(table_data, headers, "Security Audit Results")

            # Summary
            severity_counts = {}
            for issue in issues:
                severity_counts[issue['severity']] = severity_counts.get(issue['severity'], 0) + 1

            print(f"\nAudit Summary:")
            for severity, count in severity_counts.items():
                color = Fore.RED if severity == 'CRITICAL' else Fore.YELLOW if severity == 'High' else Fore.BLUE
                print(f"  {color}{severity}: {count} issues{Style.RESET_ALL}")

            if any(issue['severity'] == 'CRITICAL' for issue in issues):
                print(f"{Fore.RED}{Style.BRIGHT}🚨 CRITICAL THREATS DETECTED - IMMEDIATE ACTION REQUIRED! 🚨{Style.RESET_ALL}")
        else:
            print_success("No security issues found")

        # Log the audit
        setup_logging().info(f"Security audit completed: {len(issues)} issues found, {len(malware_processes)} malware processes")

    except Exception as e:
        print_error(f"Error during security audit: {e}")
        setup_logging().error(f"audit_system error: {e}")

def _is_signed_binary(exe_path):
    """Basic check for signed binaries on Windows"""
    try:
        # This is a simplified check - in practice, you'd use Windows APIs
        # For now, just check if it's in system directories (likely signed)
        system_dirs = [
            os.environ.get('SystemRoot', 'C:\\Windows').lower(),
            os.environ.get('ProgramFiles', 'C:\\Program Files').lower(),
            os.environ.get('ProgramFiles(x86)', 'C:\\Program Files (x86)').lower()
        ]

        exe_dir = os.path.dirname(exe_path).lower()
        return any(exe_dir.startswith(sys_dir) for sys_dir in system_dirs)
    except:
        return False

def create_snapshot_report(output_file=None):
    """Create a comprehensive system snapshot report"""
    try:
        import json
        from .network import show_network_stats

        print_success("Creating system snapshot report...")

        snapshot = {
            'timestamp': datetime.now().isoformat(),
            'system_info': {
                'platform': os.name,
                'cpu_count': psutil.cpu_count(),
                'cpu_count_logical': psutil.cpu_count(logical=True),
                'memory_total': psutil.virtual_memory().total,
                'memory_available': psutil.virtual_memory().available,
                'disk_total': psutil.disk_usage('/').total,
                'disk_free': psutil.disk_usage('/').free
            },
            'processes': [],
            'network': {},
            'services': []
        }

        # Collect process information
        print_info("Collecting process information...")
        for proc in psutil.process_iter(['pid', 'name', 'username', 'cpu_percent', 'memory_percent', 'create_time', 'cmdline']):
            try:
                proc_info = {
                    'pid': proc.info['pid'],
                    'name': proc.info['name'],
                    'username': proc.info['username'],
                    'cpu_percent': proc.info['cpu_percent'],
                    'memory_percent': proc.info['memory_percent'],
                    'create_time': proc.info['create_time'],
                    'cmdline': ' '.join(proc.info['cmdline'] or []),
                    'status': proc.status()
                }

                # Add memory details
                try:
                    mem_info = proc.memory_info()
                    proc_info['memory_rss'] = mem_info.rss
                    proc_info['memory_vms'] = mem_info.vms
                except:
                    pass

                # Add IO counters
                try:
                    io_info = proc.io_counters()
                    proc_info['io_read_bytes'] = io_info.read_bytes
                    proc_info['io_write_bytes'] = io_info.write_bytes
                except:
                    pass

                snapshot['processes'].append(proc_info)

            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue

        # Collect network information
        print_info("Collecting network information...")
        try:
            net_stats = psutil.net_io_counters(pernic=True)
            snapshot['network']['interfaces'] = {}
            for interface, stats in net_stats.items():
                snapshot['network']['interfaces'][interface] = {
                    'bytes_sent': stats.bytes_sent,
                    'bytes_recv': stats.bytes_recv,
                    'packets_sent': stats.packets_sent,
                    'packets_recv': stats.packets_recv,
                    'errin': stats.errin,
                    'errout': stats.errout
                }

            # Network connections
            connections = psutil.net_connections(kind='inet')
            snapshot['network']['connections'] = []
            for conn in connections:
                try:
                    conn_info = {
                        'pid': conn.pid,
                        'family': str(conn.family),
                        'type': str(conn.type),
                        'status': conn.status
                    }
                    if conn.laddr:
                        conn_info['local_address'] = f"{conn.laddr.ip}:{conn.laddr.port}"
                    if conn.raddr:
                        conn_info['remote_address'] = f"{conn.raddr.ip}:{conn.raddr.port}"
                    snapshot['network']['connections'].append(conn_info)
                except:
                    continue

        except Exception as e:
            print_warning(f"Could not collect network information: {e}")

        # Collect service information
        print_info("Collecting service information...")
        try:
            backend = get_service_backend()
            if backend:
                services = backend.list_services()
                snapshot['services'] = services if services else []
        except Exception as e:
            print_warning(f"Could not collect service information: {e}")

        # Save the snapshot
        if not output_file:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            output_file = f"procsight_snapshot_{timestamp}.json"

        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(snapshot, f, indent=2, default=str)

        print_success(f"Snapshot report saved to {output_file}")
        print(f"  - Processes: {len(snapshot['processes'])}")
        print(f"  - Network interfaces: {len(snapshot['network'].get('interfaces', {}))}")
        print(f"  - Network connections: {len(snapshot['network'].get('connections', []))}")
        print(f"  - Services: {len(snapshot['services'])}")

        # Log the snapshot
        setup_logging().info(f"Created snapshot report: {output_file} processes={len(snapshot['processes'])}")

        return snapshot

    except Exception as e:
        print_error(f"Error creating snapshot report: {e}")
        setup_logging().error(f"create_snapshot_report error: {e}")
        return None