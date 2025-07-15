# How LaunchPad Works

## Application Launch Process

The LaunchPad portal uses Python's `subprocess` module to launch and manage applications. Here's how it works:

### 1. Application Configuration
Applications are defined in `config/applications.json` with these fields:
- **id**: Unique identifier for the application
- **name**: Display name shown in the UI
- **description**: Brief description of what the app does
- **command**: The actual command to execute
- **working_dir**: Directory to run the command from (optional)
- **icon**: Feather icon name for the UI
- **category**: Category for filtering and organization

### 2. Launch Process
When you click "Launch Application":
1. The Flask app receives the request
2. `ProcessManager` creates a new subprocess using `subprocess.Popen()`
3. The process runs in the background
4. Process information is stored for tracking

### 3. Process Management
- **Status Tracking**: Uses process PID to check if still running
- **Stop Process**: Sends SIGTERM, then SIGKILL if needed
- **Auto-cleanup**: Removes dead processes from tracking

### 4. UI Updates
- **Real-time Status**: JavaScript polls `/api/status` every 30 seconds
- **Status Badges**: Show "Running" or "Stopped" with visual indicators
- **Action Buttons**: Dynamically show "Launch" or "Stop" based on status

## Example Applications

### Web Server
```json
{
  "id": "python-server",
  "name": "Python HTTP Server",
  "description": "Simple HTTP server on port 8000",
  "command": "python3 -m http.server 8000",
  "working_dir": "",
  "icon": "server",
  "category": "Development"
}
```

### Long-running Script
```json
{
  "id": "monitor-logs",
  "name": "Log Monitor",
  "description": "Monitor system logs in real-time",
  "command": "tail -f /var/log/syslog",
  "working_dir": "",
  "icon": "monitor",
  "category": "System"
}
```

### Interactive Application
```json
{
  "id": "python-repl",
  "name": "Python REPL",
  "description": "Interactive Python interpreter",
  "command": "python3 -i",
  "working_dir": "",
  "icon": "terminal",
  "category": "Development"
}
```

## Important Notes

1. **Process Isolation**: Each application runs as a separate process
2. **No Terminal UI**: Applications requiring terminal interaction won't work well
3. **Background Processes**: Best suited for servers, monitors, and background tasks
4. **Resource Management**: Processes continue running until explicitly stopped
5. **Error Handling**: Failed launches are logged and reported to the user

## Security Considerations

- Applications run with the same privileges as the Flask app
- No sandboxing or containerization
- Commands are executed directly via shell
- Consider security implications before adding untrusted applications