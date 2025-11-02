"""
Real-time process monitoring functionality for ProcSight
"""

import time
import psutil
import os
from core.utils import print_table, print_success, print_error, print_warning, print_info, setup_logging, show_progress

def watch_process(pattern, interval=1.0, duration=None):
    """Monitor a process in real-time"""
    try:
        # Find the process
        target_proc = None
        target_pid = None

        # Check if pattern is a PID
        try:
            pid = int(pattern)
            target_proc = psutil.Process(pid)
            target_pid = pid
        except ValueError:
            # Pattern is a name, find matching processes
            for proc in psutil.process_iter(['pid', 'name']):
                try:
                    if pattern.lower() in proc.info['name'].lower():
                        target_proc = proc
                        target_pid = proc.info['pid']
                        break
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    continue

        if not target_proc:
            print_error(f"Process '{pattern}' not found")
            return

        print_success(f"Monitoring process: {target_proc.name()} (PID: {target_pid})")
        print_info("Press Ctrl+C to stop monitoring")

        # Initial stats
        prev_cpu = target_proc.cpu_percent()
        prev_io = target_proc.io_counters()
        prev_net = psutil.net_io_counters()

        start_time = time.time()
        iteration = 0

        try:
            while True:
                iteration += 1

                # Get current stats
                try:
                    cpu_percent = target_proc.cpu_percent()
                    memory_percent = target_proc.memory_percent()
                    num_threads = target_proc.num_threads()

                    # IO stats
                    io_counters = target_proc.io_counters()
                    io_read = io_counters.read_bytes - prev_io.read_bytes if prev_io else 0
                    io_write = io_counters.write_bytes - prev_io.write_bytes if prev_io else 0

                    # Network stats (system-wide, not per-process)
                    net_counters = psutil.net_io_counters()
                    net_sent = net_counters.bytes_sent - prev_net.bytes_sent if prev_net else 0
                    net_recv = net_counters.bytes_recv - prev_net.bytes_recv if prev_net else 0

                    # Update previous values
                    prev_io = io_counters
                    prev_net = net_counters

                    # Display stats
                    print(f"\n--- Iteration {iteration} ---")
                    print(f"CPU: {cpu_percent:.1f}%")
                    print(f"Memory: {memory_percent:.1f}%")
                    print(f"Threads: {num_threads}")
                    print(f"IO Read: {io_read} bytes")
                    print(f"IO Write: {io_write} bytes")
                    print(f"Net Sent: {net_sent} bytes")
                    print(f"Net Recv: {net_recv} bytes")

                    # Check if process still exists
                    if not target_proc.is_running():
                        print_warning("Process has terminated")
                        break

                except psutil.NoSuchProcess:
                    print_warning("Process has terminated")
                    break
                except psutil.AccessDenied:
                    print_error("Access denied to process stats")
                    break
                except Exception as e:
                    print_error(f"Error getting process stats: {e}")
                    break

                # Check duration limit
                if duration and (time.time() - start_time) >= duration:
                    print_info(f"Monitoring completed after {duration} seconds")
                    break

                time.sleep(interval)

        except KeyboardInterrupt:
            print_info("\nMonitoring stopped by user")

    except Exception as e:
        print_error(f"Error monitoring process: {e}")
        setup_logging().error(f"watch_process error: {e}")

def monitor_system(interval=2.0, duration=60):
    """Monitor system-wide resource usage"""
    try:
        print_success("Starting system monitoring")
        print_info(f"Monitoring for {duration} seconds with {interval}s intervals")
        print_info("Press Ctrl+C to stop")

        start_time = time.time()
        iteration = 0

        # Initial system stats
        prev_net = psutil.net_io_counters()
        prev_disk = psutil.disk_io_counters()

        try:
            while (time.time() - start_time) < duration:
                iteration += 1

                # CPU
                cpu_percent = psutil.cpu_percent(interval=None)

                # Memory
                memory = psutil.virtual_memory()
                memory_percent = memory.percent

                # Disk
                disk = psutil.disk_usage('/')
                disk_percent = disk.percent

                # Network
                net = psutil.net_io_counters()
                net_sent = net.bytes_sent - prev_net.bytes_sent if prev_net else 0
                net_recv = net.bytes_recv - prev_net.bytes_recv if prev_net else 0

                # Disk IO
                disk_io = psutil.disk_io_counters()
                disk_read = disk_io.read_bytes - prev_disk.read_bytes if prev_disk else 0
                disk_write = disk_io.write_bytes - prev_disk.write_bytes if prev_disk else 0

                # Update previous values
                prev_net = net
                prev_disk = disk_io

                # Display
                print(f"\n--- System Stats (Iteration {iteration}) ---")
                print(f"CPU: {cpu_percent:.1f}%")
                print(f"Memory: {memory_percent:.1f}% ({memory.used//1024//1024}MB/{memory.total//1024//1024}MB)")
                print(f"Disk: {disk_percent:.1f}% ({disk.used//1024//1024//1024}GB/{disk.total//1024//1024//1024}GB)")
                print(f"Network: ↑{net_sent}B ↓{net_recv}B")
                print(f"Disk IO: R{disk_read}B W{disk_write}B")

                time.sleep(interval)

        except KeyboardInterrupt:
            print_info("\nSystem monitoring stopped by user")

        print_success("System monitoring completed")

    except Exception as e:
        print_error(f"Error monitoring system: {e}")
        setup_logging().error(f"monitor_system error: {e}")

def watch_multiple_processes(patterns, interval=2.0, duration=30):
    """Monitor multiple processes simultaneously"""
    try:
        processes = []

        # Find all matching processes
        for pattern in patterns:
            for proc in psutil.process_iter(['pid', 'name']):
                try:
                    if pattern.lower() in proc.info['name'].lower():
                        processes.append({
                            'proc': proc,
                            'pid': proc.info['pid'],
                            'name': proc.info['name'],
                            'pattern': pattern
                        })
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    continue

        if not processes:
            print_warning("No matching processes found")
            return

        print_success(f"Monitoring {len(processes)} processes")
        for p in processes:
            print(f"  - {p['name']} (PID: {p['pid']})")

        print_info("Press Ctrl+C to stop")

        # Get initial CPU percentages
        for p in processes:
            try:
                p['prev_cpu'] = p['proc'].cpu_percent()
            except:
                p['prev_cpu'] = 0

        start_time = time.time()
        iteration = 0

        try:
            while (time.time() - start_time) < duration:
                iteration += 1

                print(f"\n--- Multi-Process Stats (Iteration {iteration}) ---")

                active_processes = []
                for p in processes:
                    try:
                        if p['proc'].is_running():
                            cpu = p['proc'].cpu_percent()
                            memory = p['proc'].memory_percent()
                            threads = p['proc'].num_threads()

                            print(f"{p['name']} (PID:{p['pid']}): CPU {cpu:.1f}%, Mem {memory:.1f}%, Threads {threads}")
                            active_processes.append(p)
                        else:
                            print_warning(f"Process {p['name']} (PID:{p['pid']}) has terminated")
                    except (psutil.NoSuchProcess, psutil.AccessDenied):
                        print_warning(f"Lost access to {p['name']} (PID:{p['pid']})")

                if not active_processes:
                    print_warning("All processes have terminated")
                    break

                time.sleep(interval)

        except KeyboardInterrupt:
            print_info("\nMulti-process monitoring stopped by user")

    except Exception as e:
        print_error(f"Error monitoring multiple processes: {e}")
        setup_logging().error(f"watch_multiple_processes error: {e}")

def log_performance_snapshot(log_file=None, interval=60, duration=3600):
    """Log performance snapshots to file"""
    try:
        if not log_file:
            from datetime import datetime
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            log_file = f"performance_log_{timestamp}.csv"

        print_success(f"Starting performance logging to {log_file}")
        print_info(f"Logging every {interval}s for {duration}s total")

        start_time = time.time()
        logged_count = 0

        with open(log_file, 'w') as f:
            # Write header
            f.write("timestamp,cpu_percent,memory_percent,disk_percent,net_sent,net_recv\n")

            try:
                while (time.time() - start_time) < duration:
                    timestamp = time.time()

                    # Collect stats
                    cpu = psutil.cpu_percent()
                    memory = psutil.virtual_memory().percent
                    disk = psutil.disk_usage('/').percent

                    net = psutil.net_io_counters()
                    net_sent = net.bytes_sent
                    net_recv = net.bytes_recv

                    # Write to file
                    f.write(f"{timestamp},{cpu},{memory},{disk},{net_sent},{net_recv}\n")
                    logged_count += 1

                    # Progress indicator
                    elapsed = time.time() - start_time
                    show_progress(int(elapsed), duration, "Logging")

                    time.sleep(interval)

            except KeyboardInterrupt:
                print_info("\nPerformance logging stopped by user")

        print_success(f"Logged {logged_count} snapshots to {log_file}")

    except Exception as e:
        print_error(f"Error logging performance: {e}")
        setup_logging().error(f"log_performance_snapshot error: {e}")