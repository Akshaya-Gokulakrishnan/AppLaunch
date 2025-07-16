import subprocess
import psutil
import logging
import os
from typing import Dict, List, Optional

logger = logging.getLogger(__name__)

class ProcessManager:
    """Manages launching and tracking of application processes"""
    
    def __init__(self):
        self.running_processes: Dict[str, subprocess.Popen] = {}
        self.process_info: Dict[str, Dict] = {}
        self.output_buffers: Dict[str, str] = {}
        self.component_processes: Dict[str, Dict[str, subprocess.Popen]] = {}  # app_id -> {component_name: process}
    
    def launch_application(self, app_id: str, app_config: Dict) -> bool:
        """
        Launch an application process
        
        Args:
            app_id: Unique identifier for the application
            app_config: Application configuration dictionary
            
        Returns:
            bool: True if launch successful, False otherwise
        """
        try:
            # Check if already running
            if self.is_running(app_id):
                logger.warning(f"Application {app_id} is already running")
                return False
            
            # Check if application has components (multi-component) or single command
            if app_config.get('components'):
                return self._launch_multi_component_application(app_id, app_config)
            else:
                return self._launch_single_component_application(app_id, app_config)
                
        except Exception as e:
            logger.error(f"Error launching application {app_id}: {e}")
            return False
    
    def _launch_single_component_application(self, app_id: str, app_config: Dict) -> bool:
        """Launch a single-component application"""
        try:
            command = app_config.get('command', '')
            working_dir = app_config.get('working_dir', '') or None
            
            if not command:
                logger.error(f"No command specified for application {app_id}")
                return False
            
            # Split command into parts for subprocess
            command_parts = command.split()
            
            # Remove log file handling, restore original subprocess.PIPE behavior
            process = subprocess.Popen(
                command_parts,
                cwd=working_dir,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,  # Combine stderr with stdout
                stdin=subprocess.PIPE,
                text=True,
                bufsize=1,  # Line buffered
                universal_newlines=True,
                shell=True  # Use shell=True for Windows compatibility
            )
            
            # Store process information
            self.running_processes[app_id] = process
            self.process_info[app_id] = {
                'pid': process.pid,
                'command': command,
                'working_dir': working_dir,
                'name': app_config.get('name', app_id),
                'type': 'single'
            }
            self.output_buffers[app_id] = ""
            
            logger.info(f"Successfully launched application {app_id} with PID {process.pid}")
            return True
            
        except FileNotFoundError:
            logger.error(f"Command not found for application {app_id}: {command}")
            return False
        except PermissionError:
            logger.error(f"Permission denied launching application {app_id}")
            return False
        except Exception as e:
            logger.error(f"Error launching single component application {app_id}: {e}")
            return False
    
    def _launch_multi_component_application(self, app_id: str, app_config: Dict) -> bool:
        """Launch a multi-component application (frontend + backend)"""
        try:
            components = app_config.get('components', [])
            
            if not components:
                logger.error(f"No components specified for application {app_id}")
                return False
            
            # Sort components by order
            components = sorted(components, key=lambda x: x.get('order', 0))
            
            launched_processes = {}
            combined_output = ""
            
            for component in components:
                component_name = component.get('name', '')
                command = component.get('command', '')
                working_dir = component.get('working_dir', '') or app_config.get('working_dir', '') or None
                
                if not command:
                    logger.error(f"No command specified for component {component_name} in application {app_id}")
                    continue
                
                # Split command into parts for subprocess
                command_parts = command.split()
                
                # Remove log file handling, restore original subprocess.PIPE behavior
                process = subprocess.Popen(
                    command_parts,
                    cwd=working_dir,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.STDOUT,
                    stdin=subprocess.PIPE,
                    text=True,
                    bufsize=1,
                    universal_newlines=True,
                    shell=True  # Use shell=True for Windows compatibility
                )
                
                launched_processes[component_name] = process
                combined_output += f"[{component_name}] Started with PID {process.pid}\n"
                
                logger.info(f"Successfully launched component {component_name} for application {app_id} with PID {process.pid}")
                
                # Small delay between component launches
                import time
                time.sleep(0.5)
            
            if launched_processes:
                # Store component processes
                self.component_processes[app_id] = launched_processes
                
                # Create a combined process info
                main_process = list(launched_processes.values())[0]  # Use first component as main
                self.running_processes[app_id] = main_process
                self.process_info[app_id] = {
                    'pid': main_process.pid,
                    'command': f"Multi-component app ({len(launched_processes)} components)",
                    'working_dir': app_config.get('working_dir', ''),
                    'name': app_config.get('name', app_id),
                    'type': 'multi',
                    'components': {name: proc.pid for name, proc in launched_processes.items()}
                }
                self.output_buffers[app_id] = combined_output
                
                logger.info(f"Successfully launched multi-component application {app_id} with {len(launched_processes)} components")
                return True
            else:
                logger.error(f"Failed to launch any components for application {app_id}")
                return False
                
        except Exception as e:
            # Clean up any launched processes on error
            if 'launched_processes' in locals():
                for proc in launched_processes.values():
                    try:
                        proc.terminate()
                        proc.wait(timeout=5)
                    except:
                        proc.kill()
            
            logger.error(f"Error launching multi-component application {app_id}: {e}")
            return False
    
    def stop_application(self, app_id: str) -> bool:
        """
        Stop a running application
        
        Args:
            app_id: Unique identifier for the application
            
        Returns:
            bool: True if stop successful, False otherwise
        """
        try:
            if app_id not in self.running_processes:
                logger.warning(f"Application {app_id} is not running")
                return False
            
            process_info = self.process_info.get(app_id, {})
            
            # Check if it's a multi-component application
            if app_id in self.component_processes:
                # Stop all components
                for component_name, process in self.component_processes[app_id].items():
                    try:
                        process.terminate()
                        try:
                            process.wait(timeout=5)
                        except subprocess.TimeoutExpired:
                            process.kill()
                            process.wait()
                        logger.info(f"Stopped component {component_name} of application {app_id}")
                    except Exception as e:
                        logger.error(f"Error stopping component {component_name}: {e}")
                
                # Clean up component processes
                del self.component_processes[app_id]
            else:
                # Single component application
                process = self.running_processes[app_id]
                
                # Terminate the process
                process.terminate()
                
                # Wait for process to terminate (with timeout)
                try:
                    process.wait(timeout=5)
                except subprocess.TimeoutExpired:
                    # Force kill if it doesn't terminate gracefully
                    process.kill()
                    process.wait()
            
            # Clean up
            del self.running_processes[app_id]
            del self.process_info[app_id]
            if app_id in self.output_buffers:
                del self.output_buffers[app_id]
            
            logger.info(f"Successfully stopped application {app_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error stopping application {app_id}: {e}")
            return False
    
    def is_running(self, app_id: str) -> bool:
        """
        Check if an application is currently running
        
        Args:
            app_id: Unique identifier for the application
            
        Returns:
            bool: True if running, False otherwise
        """
        if app_id not in self.running_processes:
            return False
        
        process = self.running_processes[app_id]
        
        # Check if process is still alive
        if process.poll() is None:
            return True
        else:
            # Process has terminated, clean up
            if app_id in self.running_processes:
                del self.running_processes[app_id]
            if app_id in self.process_info:
                del self.process_info[app_id]
            if app_id in self.output_buffers:
                del self.output_buffers[app_id]
            return False
    
    def get_running_processes(self) -> List[str]:
        """
        Get list of currently running application IDs
        
        Returns:
            List[str]: List of running application IDs
        """
        running = []
        for app_id in list(self.running_processes.keys()):
            if self.is_running(app_id):
                running.append(app_id)
        return running
    
    def get_process_info(self, app_id: str) -> Optional[Dict]:
        """
        Get information about a running process
        
        Args:
            app_id: Unique identifier for the application
            
        Returns:
            Optional[Dict]: Process information or None if not running
        """
        if not self.is_running(app_id):
            return None
        
        info = self.process_info.get(app_id, {}).copy()
        
        # Add current status information
        try:
            process = self.running_processes[app_id]
            info['status'] = 'running'
            info['return_code'] = process.poll()
            
            # Try to get system information about the process
            try:
                ps_process = psutil.Process(process.pid)
                info['memory_info'] = ps_process.memory_info()._asdict()
                info['cpu_percent'] = ps_process.cpu_percent()
                info['create_time'] = ps_process.create_time()
            except psutil.NoSuchProcess:
                pass
            
        except Exception as e:
            logger.error(f"Error getting process info for {app_id}: {e}")
            info['status'] = 'error'
        
        return info
    
    def cleanup_dead_processes(self):
        """Clean up any dead processes from tracking"""
        dead_processes = []
        for app_id in list(self.running_processes.keys()):
            if not self.is_running(app_id):
                dead_processes.append(app_id)
        
        for app_id in dead_processes:
            logger.info(f"Cleaned up dead process: {app_id}")
    
    def stop_all_applications(self):
        """Stop all running applications"""
        for app_id in list(self.running_processes.keys()):
            self.stop_application(app_id)
    
    def send_input(self, app_id: str, user_input: str) -> bool:
        """
        Send input to a running application
        
        Args:
            app_id: Unique identifier for the application
            user_input: Input text to send
            
        Returns:
            bool: True if input sent successfully, False otherwise
        """
        try:
            if app_id not in self.running_processes:
                logger.warning(f"Application {app_id} is not running")
                return False
            
            process = self.running_processes[app_id]
            
            # Check if process is still alive
            if process.poll() is not None:
                logger.warning(f"Application {app_id} process has terminated")
                self.cleanup_dead_processes()
                return False
            
            # Send input to the process
            process.stdin.write(user_input + '\n')
            process.stdin.flush()
            
            logger.debug(f"Sent input to {app_id}: {user_input}")
            return True
            
        except Exception as e:
            logger.error(f"Error sending input to {app_id}: {e}")
            return False
    
    def get_output(self, app_id: str) -> str:
        """
        Get output from a running application
        
        Args:
            app_id: Unique identifier for the application
            
        Returns:
            str: Output from the application
        """
        try:
            if app_id not in self.running_processes:
                return ""
            
            process = self.running_processes[app_id]
            
            # Check if process is still alive
            if process.poll() is not None:
                logger.warning(f"Application {app_id} process has terminated")
                self.cleanup_dead_processes()
                return ""
            
            # Read available output (non-blocking)
            new_output = ""
            try:
                import select
                import os
                
                if hasattr(select, 'select'):
                    # Unix-like systems
                    ready, _, _ = select.select([process.stdout], [], [], 0.1)
                    if ready:
                        # Read available data
                        data = os.read(process.stdout.fileno(), 1024)
                        if data:
                            new_output = data.decode('utf-8', errors='ignore')
                else:
                    # Fallback - try to read without blocking
                    try:
                        line = process.stdout.readline()
                        if line:
                            new_output = line
                    except:
                        pass
                
                # Add to buffer
                if new_output:
                    self.output_buffers[app_id] = self.output_buffers.get(app_id, "") + new_output
                
                # Return all accumulated output and clear buffer
                output = self.output_buffers.get(app_id, "")
                self.output_buffers[app_id] = ""
                return output
                    
            except Exception as e:
                logger.debug(f"Error reading output from {app_id}: {e}")
                return ""
            
        except Exception as e:
            logger.error(f"Error getting output from {app_id}: {e}")
            return ""
        
        logger.info("All applications stopped")
