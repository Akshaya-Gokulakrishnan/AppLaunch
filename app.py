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
        app_data = {
            'id': request.form.get('id'),
            'name': request.form.get('name'),
            'description': request.form.get('description'),
            'command': request.form.get('command'),
            'working_dir': request.form.get('working_dir', ''),
            'icon': request.form.get('icon', 'play-circle'),
            'category': request.form.get('category', 'General')
        }
        
        # Validate required fields
        if not all([app_data['id'], app_data['name'], app_data['command']]):
            flash("ID, Name, and Command are required fields", 'error')
            return redirect(url_for('manage'))
        
        # Check if ID already exists
        if config_manager.get_application(app_data['id']):
            flash(f"Application with ID '{app_data['id']}' already exists", 'error')
            return redirect(url_for('manage'))
        
        # Add the application
        success = config_manager.add_application(app_data)
        
        if success:
            flash(f"Application '{app_data['name']}' added successfully", 'success')
            logger.info(f"Added new application: {app_data['id']}")
        else:
            flash("Failed to add application", 'error')
            
    except Exception as e:
        logger.error(f"Error adding application: {e}")
        flash(f"Error adding application: {str(e)}", 'error')
    
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
