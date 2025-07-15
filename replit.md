# Application Portal

## Overview

This is a Flask-based web application that serves as a portal for launching and managing various command-line applications. The system provides a web interface to start, stop, and monitor different applications through a centralized dashboard.

## User Preferences

```
Preferred communication style: Simple, everyday language.
```

## System Architecture

The application follows a traditional Flask web application architecture with the following key components:

### Frontend Architecture
- **Template Engine**: Jinja2 templates with Bootstrap for responsive UI
- **Static Assets**: CSS and JavaScript files for styling and interactivity
- **UI Framework**: Bootstrap with dark theme and Feather icons
- **Client-side Features**: Search, filtering, and auto-refresh functionality

### Backend Architecture
- **Web Framework**: Flask with standard routing and template rendering
- **Process Management**: Custom ProcessManager class for launching and tracking subprocess
- **Configuration Management**: JSON-based configuration system for application definitions
- **Session Management**: Flask sessions with secret key for flash messaging

### Core Components
- **Main Application** (`app.py`): Flask routes and request handling
- **Process Manager** (`utils/process_manager.py`): Subprocess lifecycle management
- **Config Manager** (`utils/config_manager.py`): JSON configuration persistence
- **Templates**: Base layout with inheritance for consistent UI

## Key Components

### Process Manager
- **Purpose**: Manages launching and tracking of application processes
- **Implementation**: Uses Python's `subprocess` and `psutil` libraries
- **Features**: Process state tracking, launch/stop operations, status monitoring

### Configuration Manager
- **Purpose**: Handles application configuration persistence
- **Storage**: JSON file-based configuration (`config/applications.json`)
- **Features**: CRUD operations for application definitions, default configuration creation

### Web Interface
- **Main Portal**: Grid view of available applications with status indicators
- **Management Interface**: Forms for adding/removing applications
- **Real-time Updates**: JavaScript-based status refresh and filtering

## Data Flow

1. **Application Loading**: ConfigManager loads application definitions from JSON
2. **Status Check**: ProcessManager checks running processes for each application
3. **UI Rendering**: Flask renders templates with application data and status
4. **User Actions**: Launch requests trigger ProcessManager to start applications
5. **Status Updates**: JavaScript polls for status changes and updates UI

## External Dependencies

### Python Libraries
- **Flask**: Web framework and templating
- **psutil**: System and process utilities
- **subprocess**: Process management
- **logging**: Application logging

### Frontend Dependencies
- **Bootstrap**: UI framework (via CDN)
- **Feather Icons**: Icon library (via CDN)
- **Custom CSS/JS**: Portal-specific styling and functionality

### Configuration
- **JSON Configuration**: Application definitions stored in `config/applications.json`
- **Environment Variables**: Session secret key from `SESSION_SECRET`

## Deployment Strategy

### Development Setup
- **Entry Point**: `main.py` runs Flask development server
- **Host/Port**: Configured for `0.0.0.0:5000` with debug mode
- **Static Files**: Served by Flask development server

### Production Considerations
- **WSGI Server**: Would need production WSGI server (not included)
- **Environment Variables**: Session secret should be set in production
- **File Permissions**: Config directory needs write access for application management
- **Process Management**: Subprocess handling may need additional security considerations

### File Structure
```
/
├── app.py                 # Main Flask application
├── main.py               # Development server entry point
├── config/
│   └── applications.json # Application definitions
├── utils/
│   ├── process_manager.py # Process lifecycle management
│   └── config_manager.py  # Configuration persistence
├── templates/            # Jinja2 templates
├── static/
│   ├── css/             # Custom stylesheets
│   └── js/              # Client-side JavaScript
```

### Security Notes
- Applications are launched as subprocess with limited isolation
- No authentication system implemented
- File system access through application commands
- Session management uses basic Flask sessions