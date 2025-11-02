"""
Network inspection functionality for ProcSight
"""

import psutil
import socket
from core.utils import print_table, print_success, print_error, print_warning, setup_logging

def show_ports(listening=False, pid=None):
    """Show network ports and connections"""
    try:
        connections = psutil.net_connections(kind='inet')

        if pid is not None:
            # Filter connections for specific PID
            connections = [conn for conn in connections if conn.pid == pid]
            if not connections:
                print_warning(f"No network connections found for PID {pid}")
                return

        port_data = []
        for conn in connections:
            try:
                if listening and conn.status != 'LISTEN':
                    continue

                # Get process name
                process_name = 'N/A'
                if conn.pid:
                    try:
                        process_name = psutil.Process(conn.pid).name()
                    except:
                        pass

                # Format addresses
                local_addr = f"{conn.laddr.ip}:{conn.laddr.port}" if conn.laddr else 'N/A'
                remote_addr = f"{conn.raddr.ip}:{conn.raddr.port}" if conn.raddr else 'N/A'

                # Determine protocol
                protocol = 'TCP'
                if hasattr(conn, 'type') and conn.type == socket.SOCK_DGRAM:
                    protocol = 'UDP'

                port_data.append({
                    'PID': conn.pid or 'N/A',
                    'Process': process_name,
                    'Protocol': protocol,
                    'Local Address': local_addr,
                    'Remote Address': remote_addr,
                    'Status': conn.status
                })

            except Exception as e:
                # Skip problematic connections
                continue

        if not port_data:
            if listening:
                print_warning("No listening ports found")
            else:
                print_warning("No network connections found")
            return

        headers = ['PID', 'Process', 'Protocol', 'Local Address', 'Remote Address', 'Status']
        title = f"Network Connections for PID {pid}" if pid else "Network Ports"
        print_table(port_data, headers, title)

        listening_count = sum(1 for p in port_data if p['Status'] == 'LISTEN')
        if listening_count > 0:
            print_success(f"Found {listening_count} listening ports")

        # Security check for privileged ports
        privileged_ports = [p for p in port_data if p['Status'] == 'LISTEN' and _is_privileged_port(p['Local Address'])]
        if privileged_ports:
            print_warning(f"Found {len(privileged_ports)} privileged ports (< 1024) in use")
            for port in privileged_ports[:5]:  # Show first 5
                print(f"  - {port['Local Address']} ({port['Process']})")

    except Exception as e:
        print_error(f"Error showing network ports: {e}")
        setup_logging().error(f"show_ports error: {e}")

def _is_privileged_port(address):
    """Check if port is privileged (< 1024)"""
    try:
        port_str = address.split(':')[-1]
        port = int(port_str)
        return port < 1024
    except:
        return False

def find_free_port(start_port=1024, end_port=65535):
    """Find a free port in the given range"""
    try:
        for port in range(start_port, end_port + 1):
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
                try:
                    sock.bind(('localhost', port))
                    return port
                except OSError:
                    continue
        return None
    except Exception as e:
        print_error(f"Error finding free port: {e}")
        return None

def check_port_availability(host, port):
    """Check if a specific port is available"""
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            sock.settimeout(1)
            result = sock.connect_ex((host, port))
            return result != 0  # 0 means connection successful (port in use)
    except Exception:
        return False

def get_process_connections(pid):
    """Get all network connections for a specific process"""
    try:
        proc = psutil.Process(pid)
        connections = proc.net_connections()

        connection_data = []
        for conn in connections:
            try:
                connection_data.append({
                    'Type': 'TCP' if conn.type == socket.SOCK_STREAM else 'UDP',
                    'Local': f"{conn.laddr.ip}:{conn.laddr.port}" if conn.laddr else 'N/A',
                    'Remote': f"{conn.raddr.ip}:{conn.raddr.port}" if conn.raddr else 'N/A',
                    'Status': conn.status
                })
            except:
                continue

        if connection_data:
            headers = ['Type', 'Local', 'Remote', 'Status']
            print_table(connection_data, headers, f"Network Connections for PID {pid}")
            print_success(f"Found {len(connection_data)} connections")
        else:
            print_warning(f"No network connections found for PID {pid}")

    except psutil.NoSuchProcess:
        print_error(f"Process with PID {pid} not found")
    except psutil.AccessDenied:
        print_error(f"Access denied to process {pid}")
    except Exception as e:
        print_error(f"Error getting process connections: {e}")
        setup_logging().error(f"get_process_connections error: {e}")

def show_network_stats():
    """Show network interface statistics"""
    try:
        net_stats = psutil.net_io_counters(pernic=True)

        stats_data = []
        for interface, stats in net_stats.items():
            stats_data.append({
                'Interface': interface,
                'Bytes Sent': stats.bytes_sent,
                'Bytes Received': stats.bytes_recv,
                'Packets Sent': stats.packets_sent,
                'Packets Received': stats.packets_recv,
                'Errors In': stats.errin,
                'Errors Out': stats.errout
            })

        if stats_data:
            headers = ['Interface', 'Bytes Sent', 'Bytes Received', 'Packets Sent', 'Packets Received', 'Errors In', 'Errors Out']
            print_table(stats_data, headers, "Network Interface Statistics")
        else:
            print_warning("No network statistics available")

    except Exception as e:
        print_error(f"Error showing network stats: {e}")
        setup_logging().error(f"show_network_stats error: {e}")

def map_port_to_process(port):
    """Find which process is using a specific port"""
    try:
        connections = psutil.net_connections(kind='inet')

        for conn in connections:
            try:
                if conn.laddr and conn.laddr.port == port:
                    process_name = 'N/A'
                    if conn.pid:
                        try:
                            process_name = psutil.Process(conn.pid).name()
                        except:
                            pass

                    print_success(f"Port {port} is used by:")
                    print(f"  Process: {process_name} (PID: {conn.pid})")
                    print(f"  Local Address: {conn.laddr.ip}:{conn.laddr.port}")
                    print(f"  Status: {conn.status}")
                    if conn.raddr:
                        print(f"  Remote Address: {conn.raddr.ip}:{conn.raddr.port}")
                    return
            except:
                continue

        print_warning(f"No process found using port {port}")

    except Exception as e:
        print_error(f"Error mapping port to process: {e}")
        setup_logging().error(f"map_port_to_process error: {e}")