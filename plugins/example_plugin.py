"""
Example plugin for ProcSight
This demonstrates how to create custom plugins
"""

def register():
    """Register this plugin with ProcSight"""
    return {
        'name': 'example',
        'version': '1.0.0',
        'description': 'Example plugin demonstrating ProcSight extensibility',
        'commands': {
            'hello': hello_command,
            'system_info': system_info_command
        }
    }

def hello_command(name="World"):
    """Say hello to someone"""
    from core.utils import print_success
    print_success(f"Hello, {name}!")
    return True

def system_info_command():
    """Show basic system information"""
    import platform
    from ..core.utils import print_info, print_table

    print_info("System Information:")

    info_data = [
        {'Property': 'OS', 'Value': platform.system()},
        {'Property': 'Platform', 'Value': platform.platform()},
        {'Property': 'Processor', 'Value': platform.processor()},
        {'Property': 'Python Version', 'Value': platform.python_version()}
    ]

    headers = ['Property', 'Value']
    print_table(info_data, headers)
    return True