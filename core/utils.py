"""
Utility functions for ProcSight - colors, tables, logging
"""

import logging
import os
from datetime import datetime
from colorama import init, Fore, Back, Style
from prettytable import PrettyTable

# Initialize colorama
init(autoreset=True)

def print_success(message):
    """Print success message in green"""
    try:
        print(f"{Fore.GREEN}{Style.BRIGHT}✓ {message}{Style.RESET_ALL}")
    except UnicodeEncodeError:
        print(f"[SUCCESS] {message}")

def print_error(message):
    """Print error message in red"""
    try:
        print(f"{Fore.RED}{Style.BRIGHT}✗ {message}{Style.RESET_ALL}")
    except UnicodeEncodeError:
        print(f"[ERROR] {message}")

def print_warning(message):
    """Print warning message in yellow"""
    try:
        print(f"{Fore.YELLOW}{Style.BRIGHT}⚠ {message}{Style.RESET_ALL}")
    except UnicodeEncodeError:
        print(f"[WARNING] {message}")

def print_info(message):
    """Print info message in blue"""
    print(f"{Fore.BLUE}{Style.BRIGHT}ℹ {message}{Style.RESET_ALL}")

def print_table(data, headers, title=None):
    """Print data in a formatted table"""
    if not data:
        print_warning("No data to display")
        return

    try:
        table = PrettyTable()
        table.field_names = headers

        # Set alignment
        for header in headers:
            if '%' in header or any(isinstance(row.get(header, ''), (int, float)) for row in data):
                table.align[header] = 'r'  # Right align numbers
            else:
                table.align[header] = 'l'  # Left align text

        # Add rows
        for row in data:
            table_row = []
            for header in headers:
                value = row.get(header, '')
                # Truncate long values
                if isinstance(value, str) and len(value) > 60:
                    value = value[:57] + '...'
                table_row.append(value)
            table.add_row(table_row)

        if title:
            print(f"\n{Style.BRIGHT}{title}{Style.RESET_ALL}")
        print(table)

    except Exception as e:
        print_error(f"Error displaying table: {e}")
        # Fallback to simple text output
        for row in data:
            print(' | '.join(str(row.get(h, '')) for h in headers))

def setup_logging():
    """Setup logging to file and console"""
    try:
        # Create logs directory if it doesn't exist
        logs_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'logs')
        os.makedirs(logs_dir, exist_ok=True)

        log_file = os.path.join(logs_dir, 'procsight.log')

        # Create logger
        logger = logging.getLogger('procsight')
        logger.setLevel(logging.DEBUG)

        # Remove existing handlers to avoid duplicates
        logger.handlers.clear()

        # File handler
        file_handler = logging.FileHandler(log_file, encoding='utf-8')
        file_handler.setLevel(logging.DEBUG)
        file_formatter = logging.Formatter(
            '%(asctime)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        file_handler.setFormatter(file_formatter)
        logger.addHandler(file_handler)

        # Console handler (only for errors and above)
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.ERROR)
        console_formatter = logging.Formatter('%(levelname)s: %(message)s')
        console_handler.setFormatter(console_formatter)
        logger.addHandler(console_handler)

        return logger

    except Exception as e:
        print_error(f"Failed to setup logging: {e}")
        # Return a basic logger that writes to console only
        logger = logging.getLogger('procsight')
        logger.setLevel(logging.DEBUG)
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(logging.Formatter('%(levelname)s: %(message)s'))
        logger.addHandler(console_handler)
        return logger

def log_action(action, details=None, success=True):
    """Log an admin action"""
    logger = setup_logging()
    status = "success" if success else "failed"
    message = f"Action={action} Status={status}"
    if details:
        message += f" Details={details}"

    if success:
        logger.info(message)
    else:
        logger.error(message)

def format_bytes(bytes_value):
    """Format bytes to human readable format"""
    try:
        for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
            if bytes_value < 1024.0:
                return f"{bytes_value:.1f} {unit}"
            bytes_value /= 1024.0
        return f"{bytes_value:.1f} PB"
    except:
        return str(bytes_value)

def format_time(timestamp):
    """Format timestamp to readable date/time"""
    try:
        dt = datetime.fromtimestamp(timestamp)
        return dt.strftime('%Y-%m-%d %H:%M:%S')
    except:
        return str(timestamp)

def safe_getattr(obj, attr, default=None):
    """Safely get attribute from object, return default if fails"""
    try:
        return getattr(obj, attr, default)
    except:
        return default

def confirm_action(message):
    """Get user confirmation for dangerous actions"""
    try:
        response = input(f"{message} [y/N]: ").strip().lower()
        return response in ['y', 'yes']
    except KeyboardInterrupt:
        print("\nOperation cancelled")
        return False
    except:
        return False

def show_progress(current, total, prefix="Progress"):
    """Show progress bar"""
    try:
        percentage = int((current / total) * 100)
        bar_length = 30
        filled_length = int(bar_length * current / total)
        bar = '█' * filled_length + '░' * (bar_length - filled_length)
        print(f"\r{prefix}: [{bar}] {percentage}% ({current}/{total})", end='', flush=True)
        if current == total:
            print()  # New line when complete
    except:
        pass  # Silently fail for progress display