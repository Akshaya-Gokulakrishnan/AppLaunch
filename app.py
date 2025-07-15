import os
import logging
from flask import Flask, render_template, request, jsonify, redirect, url_for, flash
from utils.process_manager import ProcessManager
from utils.config_manager import ConfigManager

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Create the app
app = Flask(__name__)
app.secret_key = os.environ.get("SESSION_SECRET", "dev-secret-key")

# Initialize managers
process_manager = ProcessManager()
config_manager = ConfigManager()

@app.route('/')
def index():
    """Main portal page showing all available applications"""
    try:
        applications = config_manager.get_applications()
        running_apps = process_manager.get_running_processes()
        
        # Add status to each application
        for app_config in applications:
            app_config['status'] = 'running' if app_config['id'] in running_apps else 'stopped'
        
        return render_template('index.html', applications=applications)
    except Exception as e:
        logger.error(f"Error loading applications: {e}")
        flash(f"Error loading applications: {str(e)}", 'error')
        return render_template('index.html', applications=[])

@app.route('/launch/<app_id>')
def launch_application(app_id):
    """Launch a specific application"""
    try:
        application = config_manager.get_application(app_id)
        if not application:
            flash(f"Application '{app_id}' not found", 'error')
            return redirect(url_for('index'))
        
        # Check if already running
        if process_manager.is_running(app_id):
            flash(f"Application '{application['name']}' is already running", 'warning')
            return redirect(url_for('index'))
        
        # Launch the application
        success = process_manager.launch_application(app_id, application)
        
        if success:
            flash(f"Application '{application['name']}' launched successfully", 'success')
            logger.info(f"Successfully launched application: {app_id}")
        else:
            flash(f"Failed to launch application '{application['name']}'", 'error')
            logger.error(f"Failed to launch application: {app_id}")
            
    except Exception as e:
        logger.error(f"Error launching application {app_id}: {e}")
        flash(f"Error launching application: {str(e)}", 'error')
    
    return redirect(url_for('index'))

@app.route('/stop/<app_id>')
def stop_application(app_id):
    """Stop a running application"""
    try:
        application = config_manager.get_application(app_id)
        if not application:
            flash(f"Application '{app_id}' not found", 'error')
            return redirect(url_for('index'))
        
        # Check if running
        if not process_manager.is_running(app_id):
            flash(f"Application '{application['name']}' is not running", 'warning')
            return redirect(url_for('index'))
        
        # Stop the application
        success = process_manager.stop_application(app_id)
        
        if success:
            flash(f"Application '{application['name']}' stopped successfully", 'success')
            logger.info(f"Successfully stopped application: {app_id}")
        else:
            flash(f"Failed to stop application '{application['name']}'", 'error')
            logger.error(f"Failed to stop application: {app_id}")
            
    except Exception as e:
        logger.error(f"Error stopping application {app_id}: {e}")
        flash(f"Error stopping application: {str(e)}", 'error')
    
    return redirect(url_for('index'))

@app.route('/manage')
def manage():
    """Application management page"""
    try:
        applications = config_manager.get_applications()
        return render_template('manage.html', applications=applications)
    except Exception as e:
        logger.error(f"Error loading applications for management: {e}")
        flash(f"Error loading applications: {str(e)}", 'error')
        return render_template('manage.html', applications=[])

@app.route('/add_application', methods=['POST'])
def add_application():
    """Add a new application to the portal"""
    try:
        # Get basic form data
        app_config = {
            'id': request.form.get('id', '').strip(),
            'name': request.form.get('name', '').strip(),
            'description': request.form.get('description', '').strip(),
            'icon': request.form.get('icon', 'play-circle'),
            'category': request.form.get('category', 'General')
        }
        
        # Check application type
        app_type = request.form.get('app_type', 'single')
        
        if app_type == 'single':
            # Single component application
            app_config['command'] = request.form.get('command', '').strip()
            app_config['working_dir'] = request.form.get('working_dir', '').strip()
        else:
            # Multi-component application
            app_config['working_dir'] = request.form.get('app_working_dir', '').strip()
            
            # Get component data
            component_names = request.form.getlist('component_name[]')
            component_commands = request.form.getlist('component_command[]')
            component_orders = request.form.getlist('component_order[]')
            
            components = []
            for i, name in enumerate(component_names):
                if name.strip() and i < len(component_commands) and component_commands[i].strip():
                    components.append({
                        'name': name.strip(),
                        'command': component_commands[i].strip(),
                        'order': int(component_orders[i]) if i < len(component_orders) else 1
                    })
            
            if components:
                app_config['components'] = components
            else:
                flash('At least one component is required for multi-component applications.', 'error')
                return redirect(url_for('manage'))
        
        # Add application using config manager
        if config_manager.add_application(app_config):
            flash('Application added successfully!', 'success')
        else:
            flash('Failed to add application. Please check the logs.', 'error')
            
    except Exception as e:
        logger.error(f"Error adding application: {e}")
        flash('An error occurred while adding the application.', 'error')
    
    return redirect(url_for('manage'))

@app.route('/remove_application/<app_id>')
def remove_application(app_id):
    """Remove an application from the portal"""
    try:
        application = config_manager.get_application(app_id)
        if not application:
            flash(f"Application '{app_id}' not found", 'error')
            return redirect(url_for('manage'))
        
        # Stop the application if it's running
        if process_manager.is_running(app_id):
            process_manager.stop_application(app_id)
        
        # Remove the application
        success = config_manager.remove_application(app_id)
        
        if success:
            flash(f"Application '{application['name']}' removed successfully", 'success')
            logger.info(f"Removed application: {app_id}")
        else:
            flash("Failed to remove application", 'error')
            
    except Exception as e:
        logger.error(f"Error removing application {app_id}: {e}")
        flash(f"Error removing application: {str(e)}", 'error')
    
    return redirect(url_for('manage'))

@app.route('/view/<app_id>')
def view_application(app_id):
    """View a running application in a terminal-like interface"""
    try:
        application = config_manager.get_application(app_id)
        if not application:
            flash(f"Application '{app_id}' not found", 'error')
            return redirect(url_for('index'))
        
        # Check if running
        if not process_manager.is_running(app_id):
            flash(f"Application '{application['name']}' is not running", 'warning')
            return redirect(url_for('index'))
        
        return render_template('terminal.html', application=application, app_id=app_id)
        
    except Exception as e:
        logger.error(f"Error viewing application {app_id}: {e}")
        flash(f"Error viewing application: {str(e)}", 'error')
        return redirect(url_for('index'))

@app.route('/send_input/<app_id>', methods=['POST'])
def send_input(app_id):
    """Send input to a running application"""
    try:
        data = request.get_json()
        if not data or 'input' not in data:
            return jsonify({'success': False, 'error': 'No input provided'})
        
        user_input = data['input']
        success = process_manager.send_input(app_id, user_input)
        
        if success:
            return jsonify({'success': True})
        else:
            return jsonify({'success': False, 'error': 'Failed to send input'})
            
    except Exception as e:
        logger.error(f"Error sending input to {app_id}: {e}")
        return jsonify({'success': False, 'error': str(e)})

@app.route('/get_output/<app_id>')
def get_output(app_id):
    """Get output from a running application"""
    try:
        output = process_manager.get_output(app_id)
        return jsonify({
            'success': True,
            'output': output
        })
    except Exception as e:
        logger.error(f"Error getting output from {app_id}: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        })

@app.route('/api/status')
def api_status():
    """API endpoint to get application status"""
    try:
        applications = config_manager.get_applications()
        running_apps = process_manager.get_running_processes()
        
        status_data = []
        for app_config in applications:
            status_data.append({
                'id': app_config['id'],
                'name': app_config['name'],
                'status': 'running' if app_config['id'] in running_apps else 'stopped'
            })
        
        return jsonify({
            'success': True,
            'applications': status_data
        })
    except Exception as e:
        logger.error(f"Error getting status: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        })

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
