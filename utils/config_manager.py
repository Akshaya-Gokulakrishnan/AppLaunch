import json
import os
import logging
from typing import Dict, List, Optional

logger = logging.getLogger(__name__)

class ConfigManager:
    """Manages application configuration and persistence"""
    
    def __init__(self, config_file: str = 'config/applications.json'):
        self.config_file = config_file
        self.config_dir = os.path.dirname(config_file)
        self._ensure_config_directory()
        self._load_config()
    
    def _ensure_config_directory(self):
        """Ensure the config directory exists"""
        if self.config_dir and not os.path.exists(self.config_dir):
            os.makedirs(self.config_dir, exist_ok=True)
            logger.info(f"Created config directory: {self.config_dir}")
    
    def _load_config(self):
        """Load configuration from JSON file"""
        try:
            if os.path.exists(self.config_file):
                with open(self.config_file, 'r') as f:
                    self.config = json.load(f)
                logger.info(f"Loaded configuration from {self.config_file}")
            else:
                # Create default configuration
                self.config = {"applications": []}
                self._save_config()
                logger.info(f"Created default configuration at {self.config_file}")
        except json.JSONDecodeError as e:
            logger.error(f"Error parsing config file {self.config_file}: {e}")
            self.config = {"applications": []}
        except Exception as e:
            logger.error(f"Error loading config file {self.config_file}: {e}")
            self.config = {"applications": []}
    
    def _save_config(self):
        """Save configuration to JSON file"""
        try:
            with open(self.config_file, 'w') as f:
                json.dump(self.config, f, indent=2)
            logger.info(f"Saved configuration to {self.config_file}")
            return True
        except Exception as e:
            logger.error(f"Error saving config file {self.config_file}: {e}")
            return False
    
    def get_applications(self) -> List[Dict]:
        """
        Get all configured applications
        
        Returns:
            List[Dict]: List of application configurations
        """
        return self.config.get('applications', [])
    
    def get_application(self, app_id: str) -> Optional[Dict]:
        """
        Get a specific application configuration
        
        Args:
            app_id: Unique identifier for the application
            
        Returns:
            Optional[Dict]: Application configuration or None if not found
        """
        applications = self.get_applications()
        for app in applications:
            if app.get('id') == app_id:
                return app
        return None
    
    def add_application(self, app_config: Dict) -> bool:
        """
        Add a new application configuration
        
        Args:
            app_config: Application configuration dictionary
            
        Returns:
            bool: True if added successfully, False otherwise
        """
        try:
            # Validate required fields
            required_fields = ['id', 'name', 'command']
            for field in required_fields:
                if not app_config.get(field):
                    logger.error(f"Missing required field '{field}' in application config")
                    return False
            
            # Check if application ID already exists
            if self.get_application(app_config['id']):
                logger.error(f"Application with ID '{app_config['id']}' already exists")
                return False
            
            # Set default values
            app_config.setdefault('description', '')
            app_config.setdefault('working_dir', '')
            app_config.setdefault('icon', 'play-circle')
            app_config.setdefault('category', 'General')
            
            # Add to configuration
            self.config['applications'].append(app_config)
            
            # Save to file
            if self._save_config():
                logger.info(f"Added application: {app_config['id']}")
                return True
            else:
                # Remove from memory if save failed
                self.config['applications'].remove(app_config)
                return False
                
        except Exception as e:
            logger.error(f"Error adding application: {e}")
            return False
    
    def remove_application(self, app_id: str) -> bool:
        """
        Remove an application configuration
        
        Args:
            app_id: Unique identifier for the application
            
        Returns:
            bool: True if removed successfully, False otherwise
        """
        try:
            applications = self.config.get('applications', [])
            
            # Find and remove the application
            for i, app in enumerate(applications):
                if app.get('id') == app_id:
                    removed_app = applications.pop(i)
                    
                    # Save to file
                    if self._save_config():
                        logger.info(f"Removed application: {app_id}")
                        return True
                    else:
                        # Restore if save failed
                        applications.insert(i, removed_app)
                        return False
            
            logger.warning(f"Application with ID '{app_id}' not found")
            return False
            
        except Exception as e:
            logger.error(f"Error removing application {app_id}: {e}")
            return False
    
    def update_application(self, app_id: str, updates: Dict) -> bool:
        """
        Update an existing application configuration
        
        Args:
            app_id: Unique identifier for the application
            updates: Dictionary of fields to update
            
        Returns:
            bool: True if updated successfully, False otherwise
        """
        try:
            applications = self.config.get('applications', [])
            
            # Find and update the application
            for app in applications:
                if app.get('id') == app_id:
                    # Store original values in case we need to rollback
                    original_values = {}
                    for key, value in updates.items():
                        if key in app:
                            original_values[key] = app[key]
                        app[key] = value
                    
                    # Save to file
                    if self._save_config():
                        logger.info(f"Updated application: {app_id}")
                        return True
                    else:
                        # Rollback changes if save failed
                        for key, value in original_values.items():
                            app[key] = value
                        for key in updates:
                            if key not in original_values:
                                app.pop(key, None)
                        return False
            
            logger.warning(f"Application with ID '{app_id}' not found")
            return False
            
        except Exception as e:
            logger.error(f"Error updating application {app_id}: {e}")
            return False
    
    def get_applications_by_category(self, category: str) -> List[Dict]:
        """
        Get applications filtered by category
        
        Args:
            category: Category to filter by
            
        Returns:
            List[Dict]: List of applications in the specified category
        """
        applications = self.get_applications()
        return [app for app in applications if app.get('category') == category]
    
    def get_categories(self) -> List[str]:
        """
        Get all unique categories
        
        Returns:
            List[str]: List of unique categories
        """
        applications = self.get_applications()
        categories = set()
        for app in applications:
            categories.add(app.get('category', 'General'))
        return sorted(list(categories))
    
    def validate_application(self, app_config: Dict) -> List[str]:
        """
        Validate an application configuration
        
        Args:
            app_config: Application configuration dictionary
            
        Returns:
            List[str]: List of validation errors (empty if valid)
        """
        errors = []
        
        # Required fields
        required_fields = ['id', 'name', 'command']
        for field in required_fields:
            if not app_config.get(field):
                errors.append(f"Missing required field: {field}")
        
        # ID format validation
        app_id = app_config.get('id', '')
        if app_id:
            if not isinstance(app_id, str):
                errors.append("Application ID must be a string")
            elif not app_id.replace('-', '').replace('_', '').isalnum():
                errors.append("Application ID must contain only letters, numbers, hyphens, and underscores")
        
        # Command validation
        command = app_config.get('command', '')
        if command and not isinstance(command, str):
            errors.append("Command must be a string")
        
        return errors
    
    def reload_config(self):
        """Reload configuration from file"""
        self._load_config()
        logger.info("Configuration reloaded")
