#!/usr/bin/env python3
"""
LightBox Service Manager - Install, configure, and manage the systemd service
"""

import subprocess
import sys
import os
from pathlib import Path
import shutil

class ServiceManager:
    def __init__(self):
        self.service_name = "lightbox.service"
        self.service_file = Path(__file__).parent / self.service_name
        self.system_service_path = Path("/etc/systemd/system") / self.service_name
        self.current_user = os.getenv("USER", "unknown")
        
    def check_sudo(self):
        """Check if running with sudo privileges"""
        if os.geteuid() != 0:
            print("❌ This operation requires sudo privileges")
            print(f"   Run with: sudo python3 {sys.argv[0]} {' '.join(sys.argv[1:])}")
            return False
        return True
    
    def update_service_paths(self):
        """Update service file with current user and paths"""
        current_path = Path(__file__).parent.absolute()
        
        # Read the service file
        service_content = self.service_file.read_text()
        
        # Update paths for current user
        if "fieldjoshua" in service_content:
            service_content = service_content.replace(
                "/home/fieldjoshua/LightBox",
                str(current_path)
            )
            
            # Write updated service file
            self.service_file.write_text(service_content)
            print(f"✅ Updated service paths to: {current_path}")
    
    def install_service(self):
        """Install the systemd service"""
        if not self.check_sudo():
            return False
            
        print("🔧 Installing LightBox systemd service...")
        
        # Update service file paths
        self.update_service_paths()
        
        # Copy service file to systemd directory
        try:
            shutil.copy2(self.service_file, self.system_service_path)
            print(f"✅ Copied service file to {self.system_service_path}")
            
            # Reload systemd
            subprocess.run(["systemctl", "daemon-reload"], check=True)
            print("✅ Reloaded systemd daemon")
            
            # Enable service
            subprocess.run(["systemctl", "enable", "lightbox"], check=True)
            print("✅ Enabled lightbox service")
            
            return True
            
        except subprocess.CalledProcessError as e:
            print(f"❌ Failed to install service: {e}")
            return False
        except Exception as e:
            print(f"❌ Error installing service: {e}")
            return False
    
    def start_service(self):
        """Start the lightbox service"""
        if not self.check_sudo():
            return False
            
        try:
            subprocess.run(["systemctl", "start", "lightbox"], check=True)
            print("✅ Started lightbox service")
            return True
        except subprocess.CalledProcessError as e:
            print(f"❌ Failed to start service: {e}")
            return False
    
    def stop_service(self):
        """Stop the lightbox service"""
        if not self.check_sudo():
            return False
            
        try:
            subprocess.run(["systemctl", "stop", "lightbox"], check=True)
            print("✅ Stopped lightbox service")
            return True
        except subprocess.CalledProcessError as e:
            print(f"❌ Failed to stop service: {e}")
            return False
    
    def restart_service(self):
        """Restart the lightbox service"""
        if not self.check_sudo():
            return False
            
        try:
            subprocess.run(["systemctl", "restart", "lightbox"], check=True)
            print("✅ Restarted lightbox service")
            return True
        except subprocess.CalledProcessError as e:
            print(f"❌ Failed to restart service: {e}")
            return False
    
    def status_service(self):
        """Show service status (doesn't require sudo)"""
        try:
            result = subprocess.run(
                ["systemctl", "status", "lightbox"],
                capture_output=True,
                text=True
            )
            print("📊 LightBox Service Status:")
            print(result.stdout)
            
            if result.returncode == 0:
                print("✅ Service is running")
            else:
                print("⚠️  Service is not running")
                
            return result.returncode == 0
            
        except subprocess.CalledProcessError as e:
            print(f"❌ Failed to check service status: {e}")
            return False
    
    def logs_service(self, lines=50):
        """Show service logs"""
        try:
            result = subprocess.run(
                ["journalctl", "-u", "lightbox", "-n", str(lines), "--no-pager"],
                capture_output=True,
                text=True
            )
            print(f"📄 LightBox Service Logs (last {lines} lines):")
            print(result.stdout)
            return True
            
        except subprocess.CalledProcessError as e:
            print(f"❌ Failed to get service logs: {e}")
            return False
    
    def uninstall_service(self):
        """Uninstall the systemd service"""
        if not self.check_sudo():
            return False
            
        print("🗑️  Uninstalling LightBox systemd service...")
        
        try:
            # Stop service if running
            subprocess.run(["systemctl", "stop", "lightbox"], check=False)
            
            # Disable service
            subprocess.run(["systemctl", "disable", "lightbox"], check=False)
            
            # Remove service file
            if self.system_service_path.exists():
                self.system_service_path.unlink()
                print(f"✅ Removed service file from {self.system_service_path}")
            
            # Reload systemd
            subprocess.run(["systemctl", "daemon-reload"], check=True)
            print("✅ Reloaded systemd daemon")
            
            return True
            
        except subprocess.CalledProcessError as e:
            print(f"❌ Failed to uninstall service: {e}")
            return False

def main():
    """Main CLI interface"""
    manager = ServiceManager()
    
    if len(sys.argv) < 2:
        print("🔧 LightBox Service Manager")
        print("=" * 30)
        print("Usage: python3 service_manager.py <command>")
        print()
        print("Commands:")
        print("  install    - Install and enable the systemd service")
        print("  start      - Start the service")
        print("  stop       - Stop the service")
        print("  restart    - Restart the service")
        print("  status     - Show service status")
        print("  logs       - Show service logs")
        print("  uninstall  - Remove the service")
        print()
        print("Note: install, start, stop, restart, and uninstall require sudo")
        return
    
    command = sys.argv[1].lower()
    
    if command == "install":
        manager.install_service()
    elif command == "start":
        manager.start_service()
    elif command == "stop":
        manager.stop_service()
    elif command == "restart":
        manager.restart_service()
    elif command == "status":
        manager.status_service()
    elif command == "logs":
        lines = int(sys.argv[2]) if len(sys.argv) > 2 else 50
        manager.logs_service(lines)
    elif command == "uninstall":
        manager.uninstall_service()
    else:
        print(f"❌ Unknown command: {command}")
        print("Run without arguments to see available commands")

if __name__ == "__main__":
    main()