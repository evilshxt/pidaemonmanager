#!/usr/bin/env python3
"""
ProcSight - Cross-platform Process & Network Insight CLI
"""

import sys
import os
from colorama import init, Fore, Back, Style

# Add current directory to path for imports
sys.path.insert(0, os.path.dirname(__file__))

# Initialize colorama
init(autoreset=True)

def print_banner():
    """Print the ProcSight ASCII banner"""
    try:
        banner = f"""
{Fore.CYAN}{Style.BRIGHT}
███████╗██████╗  ██████╗  ██████╗███████╗██╗ ██████╗ ██╗  ██╗████████╗
██╔════╝██╔══██╗██╔═══██╗██╔════╝██╔════╝██║██╔════╝ ██║  ██║╚══██╔══╝
█████╗  ██████╔╝██║   ██║██║     ███████╗██║██║  ███╗███████║   ██║
██╔══╝  ██╔══██╗██║   ██║██║     ╚════██║██║██║   ██║██╔══██║   ██║
██║     ██║  ██║╚██████╔╝╚██████╗███████║██║╚██████╔╝██║  ██║   ██║
╚═╝     ╚═╝  ╚═╝ ╚═════╝  ╚═════╝╚══════╝╚═╝ ╚═════╝ ╚═╝  ╚═╝   ╚═╝
{Style.RESET_ALL}
{Fore.GREEN}{Style.BRIGHT}Cross-platform Process & Network Insight CLI{Style.RESET_ALL}
{Fore.YELLOW}Version 1.0.0 | Type 'help' for commands or 'quit' to exit{Style.RESET_ALL}
"""
        print(banner)
    except UnicodeEncodeError:
        # Fallback for systems that can't display Unicode
        print("ProcSight - Cross-platform Process & Network Insight CLI")
        print("Version 1.0.0 | Type 'help' for commands or 'quit' to exit")

def show_menu():
    """Show the main menu options"""
    print(f"\n{Fore.BLUE}{Style.BRIGHT}Available Commands:{Style.RESET_ALL}")
    print(f"{Fore.GREEN}1.{Style.RESET_ALL} Inspect Processes     - Search and list running processes")
    print(f"{Fore.GREEN}2.{Style.RESET_ALL} Network Ports        - View network connections and ports")
    print(f"{Fore.GREEN}3.{Style.RESET_ALL} Monitor Process      - Real-time process monitoring")
    print(f"{Fore.GREEN}4.{Style.RESET_ALL} Process Info         - Detailed process information")
    print(f"{Fore.GREEN}5.{Style.RESET_ALL} Terminate Process    - Safely terminate processes")
    print(f"{Fore.GREEN}6.{Style.RESET_ALL} Top Processes        - Show resource-intensive processes")
    print(f"{Fore.GREEN}7.{Style.RESET_ALL} System Services      - Manage system services")
    print(f"{Fore.GREEN}8.{Style.RESET_ALL} Security Audit       - Perform system security audit")
    print(f"{Fore.GREEN}9.{Style.RESET_ALL} System Snapshot      - Create comprehensive system report")
    print(f"{Fore.GREEN}10.{Style.RESET_ALL} Export Data          - Export process data to CSV/JSON")
    print(f"{Fore.GREEN}11.{Style.RESET_ALL} Plugin Management    - Manage and run plugins")
    print(f"{Fore.RED}0.{Style.RESET_ALL} Exit/Quit            - Exit ProcSight")
    print()

def get_user_choice():
    """Get user menu choice"""
    try:
        choice = input(f"{Fore.YELLOW}Enter your choice (0-11): {Style.RESET_ALL}").strip()
        return choice
    except KeyboardInterrupt:
        print(f"\n{Fore.YELLOW}Goodbye!{Style.RESET_ALL}")
        sys.exit(0)
    except EOFError:
        print(f"\n{Fore.YELLOW}Goodbye!{Style.RESET_ALL}")
        sys.exit(0)

def handle_inspect_processes():
    """Handle process inspection"""
    try:
        pattern = input("Enter process name or pattern to search: ").strip()
        if not pattern:
            print(f"{Fore.RED}Error: Pattern cannot be empty{Style.RESET_ALL}")
            return

        from core.core import inspect_processes
        inspect_processes(pattern)
    except KeyboardInterrupt:
        print(f"\n{Fore.YELLOW}Cancelled{Style.RESET_ALL}")

def handle_network_ports():
    """Handle network port operations"""
    try:
        print("Network Options:")
        print("1. Show listening ports")
        print("2. Show connections for specific PID")
        choice = input("Choose option (1-2): ").strip()

        from core.network import show_ports

        if choice == '1':
            show_ports(listening=True)
        elif choice == '2':
            try:
                pid = int(input("Enter PID: ").strip())
                show_ports(pid=pid)
            except ValueError:
                print(f"{Fore.RED}Error: Invalid PID{Style.RESET_ALL}")
        else:
            print(f"{Fore.RED}Error: Invalid choice{Style.RESET_ALL}")
    except KeyboardInterrupt:
        print(f"\n{Fore.YELLOW}Cancelled{Style.RESET_ALL}")

def handle_monitor_process():
    """Handle process monitoring"""
    try:
        pattern = input("Enter process name or PID to monitor: ").strip()
        if not pattern:
            print(f"{Fore.RED}Error: Pattern cannot be empty{Style.RESET_ALL}")
            return

        from core.monitor import watch_process
        watch_process(pattern)
    except KeyboardInterrupt:
        print(f"\n{Fore.YELLOW}Cancelled{Style.RESET_ALL}")

def handle_process_info():
    """Handle detailed process information"""
    try:
        pid_str = input("Enter Process ID: ").strip()
        try:
            pid = int(pid_str)
        except ValueError:
            print(f"{Fore.RED}Error: Invalid PID{Style.RESET_ALL}")
            return

        from core.core import show_process_info
        show_process_info(pid)
    except KeyboardInterrupt:
        print(f"\n{Fore.YELLOW}Cancelled{Style.RESET_ALL}")

def handle_terminate_process():
    """Handle process termination"""
    try:
        pid_str = input("Enter Process ID to terminate: ").strip()
        try:
            pid = int(pid_str)
        except ValueError:
            print(f"{Fore.RED}Error: Invalid PID{Style.RESET_ALL}")
            return

        force = input("Force termination? (y/N): ").strip().lower() == 'y'

        from core.core import terminate_process
        terminate_process(pid, force=force)
    except KeyboardInterrupt:
        print(f"\n{Fore.YELLOW}Cancelled{Style.RESET_ALL}")

def handle_top_processes():
    """Handle top processes display"""
    try:
        print("Sort by:")
        print("1. CPU usage")
        print("2. Memory usage")
        choice = input("Choose option (1-2): ").strip()

        sort_by = 'cpu'
        if choice == '2':
            sort_by = 'memory'

        from core.core import show_top_processes
        show_top_processes(sort_by)
    except KeyboardInterrupt:
        print(f"\n{Fore.YELLOW}Cancelled{Style.RESET_ALL}")

def handle_system_services():
    """Handle system service management"""
    try:
        print("Service Options:")
        print("1. List all services")
        print("2. Start service")
        print("3. Stop service")
        print("4. Restart service")
        print("5. Enable service")
        print("6. Disable service")
        choice = input("Choose option (1-6): ").strip()

        from core.core import list_services, manage_service

        if choice == '1':
            list_services()
        elif choice in ['2', '3', '4', '5', '6']:
            service_name = input("Enter service name: ").strip()
            if not service_name:
                print(f"{Fore.RED}Error: Service name cannot be empty{Style.RESET_ALL}")
                return

            actions = {'2': 'start', '3': 'stop', '4': 'restart', '5': 'enable', '6': 'disable'}
            action = actions[choice]
            manage_service(action, service_name)
        else:
            print(f"{Fore.RED}Error: Invalid choice{Style.RESET_ALL}")
    except KeyboardInterrupt:
        print(f"\n{Fore.YELLOW}Cancelled{Style.RESET_ALL}")

def handle_security_audit():
    """Handle security audit"""
    try:
        from core.core import audit_system
        audit_system()
    except KeyboardInterrupt:
        print(f"\n{Fore.YELLOW}Cancelled{Style.RESET_ALL}")

def handle_system_snapshot():
    """Handle system snapshot creation"""
    try:
        output_file = input("Enter output filename (optional): ").strip()
        if not output_file:
            output_file = None

        from core.core import create_snapshot_report
        create_snapshot_report(output_file)
    except KeyboardInterrupt:
        print(f"\n{Fore.YELLOW}Cancelled{Style.RESET_ALL}")

def handle_export_data():
    """Handle data export"""
    try:
        print("Export Options:")
        print("1. Export to CSV")
        print("2. Export to JSON")
        choice = input("Choose format (1-2): ").strip()

        format_type = 'csv'
        if choice == '2':
            format_type = 'json'

        output_file = input("Enter output filename (optional): ").strip()
        if not output_file:
            output_file = None

        from core.core import export_snapshot
        export_snapshot(format_type, output_file)
    except KeyboardInterrupt:
        print(f"\n{Fore.YELLOW}Cancelled{Style.RESET_ALL}")

def handle_plugin_management():
    """Handle plugin management"""
    try:
        print("Plugin Options:")
        print("1. List plugins")
        print("2. List plugin commands")
        print("3. Run plugin command")
        choice = input("Choose option (1-3): ").strip()

        from core.plugins import get_plugin_manager, load_plugins
        manager = get_plugin_manager()
        load_plugins()

        if choice == '1':
            manager.list_plugins()
        elif choice == '2':
            manager.list_commands()
        elif choice == '3':
            command_name = input("Enter command name: ").strip()
            if not command_name:
                print(f"{Fore.RED}Error: Command name cannot be empty{Style.RESET_ALL}")
                return

            args_str = input("Enter arguments (optional): ").strip()
            args = args_str.split() if args_str else []

            manager.execute_command(command_name, *args)
        else:
            print(f"{Fore.RED}Error: Invalid choice{Style.RESET_ALL}")
    except KeyboardInterrupt:
        print(f"\n{Fore.YELLOW}Cancelled{Style.RESET_ALL}")

def main():
    """Main interactive menu function"""
    print_banner()

    while True:
        try:
            show_menu()
            choice = get_user_choice()

            if choice in ['0', 'quit', 'exit', 'q']:
                print(f"\n{Fore.GREEN}Thank you for using ProcSight!{Style.RESET_ALL}")
                break
            elif choice == '1':
                handle_inspect_processes()
            elif choice == '2':
                handle_network_ports()
            elif choice == '3':
                handle_monitor_process()
            elif choice == '4':
                handle_process_info()
            elif choice == '5':
                handle_terminate_process()
            elif choice == '6':
                handle_top_processes()
            elif choice == '7':
                handle_system_services()
            elif choice == '8':
                handle_security_audit()
            elif choice == '9':
                handle_system_snapshot()
            elif choice == '10':
                handle_export_data()
            elif choice == '11':
                handle_plugin_management()
            else:
                print(f"{Fore.RED}Error: Invalid choice. Please select 0-11.{Style.RESET_ALL}")

            input(f"\n{Fore.CYAN}Press Enter to continue...{Style.RESET_ALL}")

        except KeyboardInterrupt:
            print(f"\n{Fore.GREEN}Thank you for using ProcSight!{Style.RESET_ALL}")
            break
        except Exception as e:
            print(f"{Fore.RED}Error: {e}{Style.RESET_ALL}")
            input(f"\n{Fore.CYAN}Press Enter to continue...{Style.RESET_ALL}")

if __name__ == '__main__':
    # Check if arguments provided (for backward compatibility)
    if len(sys.argv) > 1:
        # Fall back to command-line mode for scripts/automation
        print("Command-line mode detected. Use 'python procsight.py' without arguments for interactive menu.")
        # Could implement the old argparse logic here if needed
        sys.exit(1)
    else:
        main()

if __name__ == '__main__':
    main()