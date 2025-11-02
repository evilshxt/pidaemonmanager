"""
Plugin system for ProcSight extensibility
"""

import os
import importlib.util
import sys
from core.utils import print_success, print_error, print_warning, print_info, setup_logging

class PluginManager:
    """Manages loading and execution of plugins"""

    def __init__(self):
        self.plugins = {}
        self.commands = {}
        self.plugin_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'plugins')

    def load_plugins(self):
        """Load all plugins from the plugins directory"""
        if not os.path.exists(self.plugin_dir):
            print_warning(f"Plugins directory not found: {self.plugin_dir}")
            return

        try:
            plugin_files = [f for f in os.listdir(self.plugin_dir) if f.endswith('.py') and not f.startswith('__')]

            for plugin_file in plugin_files:
                plugin_path = os.path.join(self.plugin_dir, plugin_file)
                plugin_name = plugin_file[:-3]  # Remove .py extension

                try:
                    # Load the plugin module
                    spec = importlib.util.spec_from_file_location(plugin_name, plugin_path)
                    if spec and spec.loader:
                        module = importlib.util.module_from_spec(spec)
                        spec.loader.exec_module(module)

                        # Check if it has a register function
                        if hasattr(module, 'register'):
                            plugin_info = module.register()
                            if plugin_info:
                                self.plugins[plugin_name] = {
                                    'module': module,
                                    'info': plugin_info,
                                    'commands': plugin_info.get('commands', {})
                                }

                                # Register commands
                                for cmd_name, cmd_func in plugin_info.get('commands', {}).items():
                                    self.commands[cmd_name] = {
                                        'function': cmd_func,
                                        'plugin': plugin_name,
                                        'description': plugin_info.get('description', '')
                                    }

                                print_success(f"Loaded plugin: {plugin_name}")
                        else:
                            print_warning(f"Plugin {plugin_name} missing register() function")

                except Exception as e:
                    print_error(f"Failed to load plugin {plugin_name}: {e}")
                    setup_logging().error(f"Plugin load error {plugin_name}: {e}")

            if self.plugins:
                print_info(f"Loaded {len(self.plugins)} plugins with {len(self.commands)} commands")
            else:
                print_info("No plugins loaded")

        except Exception as e:
            print_error(f"Error loading plugins: {e}")
            setup_logging().error(f"Plugin loading error: {e}")

    def list_plugins(self):
        """List all loaded plugins"""
        if not self.plugins:
            print_warning("No plugins loaded")
            return

        table_data = []
        for name, plugin_data in self.plugins.items():
            info = plugin_data['info']
            table_data.append({
                'Name': name,
                'Version': info.get('version', 'N/A'),
                'Description': info.get('description', 'N/A'),
                'Commands': ', '.join(plugin_data['commands'].keys())
            })

        from .utils import print_table
        headers = ['Name', 'Version', 'Description', 'Commands']
        print_table(table_data, headers, "Loaded Plugins")

    def list_commands(self):
        """List all available plugin commands"""
        if not self.commands:
            print_warning("No plugin commands available")
            return

        table_data = []
        for cmd_name, cmd_info in self.commands.items():
            table_data.append({
                'Command': cmd_name,
                'Plugin': cmd_info['plugin'],
                'Description': cmd_info['description']
            })

        from .utils import print_table
        headers = ['Command', 'Plugin', 'Description']
        print_table(table_data, headers, "Plugin Commands")

    def execute_command(self, command_name, *args, **kwargs):
        """Execute a plugin command"""
        if command_name not in self.commands:
            print_error(f"Unknown plugin command: {command_name}")
            return False

        try:
            cmd_info = self.commands[command_name]
            func = cmd_info['function']

            # Execute the command
            result = func(*args, **kwargs)

            # Log the execution
            setup_logging().info(f"Executed plugin command: {command_name} from {cmd_info['plugin']}")

            return result

        except Exception as e:
            print_error(f"Error executing plugin command {command_name}: {e}")
            setup_logging().error(f"Plugin command error {command_name}: {e}")
            return False

    def get_plugin_info(self, plugin_name):
        """Get information about a specific plugin"""
        if plugin_name not in self.plugins:
            print_error(f"Plugin not found: {plugin_name}")
            return None

        return self.plugins[plugin_name]['info']

# Global plugin manager instance
_plugin_manager = None

def get_plugin_manager():
    """Get the global plugin manager instance"""
    global _plugin_manager
    if _plugin_manager is None:
        _plugin_manager = PluginManager()
    return _plugin_manager

def load_plugins():
    """Load all plugins (convenience function)"""
    manager = get_plugin_manager()
    manager.load_plugins()
    return manager

def execute_plugin_command(command_name, *args, **kwargs):
    """Execute a plugin command (convenience function)"""
    manager = get_plugin_manager()
    return manager.execute_command(command_name, *args, **kwargs)