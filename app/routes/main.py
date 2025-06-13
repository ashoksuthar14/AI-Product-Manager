from flask import Blueprint, render_template, request, jsonify
from app.models.project import Project
from app.agents.agent_coordinator import AgentCoordinator
from flask_socketio import emit
from app import socketio
import asyncio
import threading

bp = Blueprint('main', __name__)

@bp.route('/')
def index():
    """Landing page route."""
    return render_template('index.html')

@bp.route('/analyze')
def analyze_page():
    return render_template('projects/analyze.html')

@bp.route('/analyze', methods=['POST'])
def analyze_project():
    try:
        # Get project data from request
        project_data = request.get_json()
        
        # Start real-time analysis in background
        def run_analysis():
            try:
                # Initialize collaborative agent coordinator with real-time updates
                coordinator = AgentCoordinator(emit_updates=True)
                
                # Run collaborative analysis
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                analysis = loop.run_until_complete(coordinator.collaborative_analysis(project_data))
                loop.close()
                
                # Emit final results
                socketio.emit('analysis_complete', {
                    'success': True,
                    'analysis': analysis,
                    'conversation_log': coordinator.get_conversation_summary(),
                    'message': 'Collaborative analysis completed successfully!'
                })
                
            except Exception as e:
                socketio.emit('analysis_error', {
                    'success': False,
                    'error': str(e)
                })
        
        # Start analysis in background thread
        analysis_thread = threading.Thread(target=run_analysis)
        analysis_thread.daemon = True
        analysis_thread.start()
        
        return jsonify({
            'success': True,
            'message': 'Analysis started! You will receive real-time updates.'
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@bp.route('/dashboard')
def dashboard():
    """Dashboard showing all projects."""
    projects = Project.query.all()
    return render_template('dashboard.html', projects=projects)

# SocketIO event handlers
@socketio.on('connect')
def handle_connect():
    print('Client connected')
    emit('status', {'msg': 'Connected to analysis server'})

@socketio.on('disconnect')
def handle_disconnect():
    print('Client disconnected')

@socketio.on('start_analysis')
def handle_start_analysis(data):
    """Handle real-time analysis request via WebSocket."""
    try:
        project_data = data.get('project_data', {})
        
        def run_analysis():
            try:
                # Initialize collaborative agent coordinator with real-time updates
                coordinator = AgentCoordinator(emit_updates=True)
                
                # Run collaborative analysis
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                analysis = loop.run_until_complete(coordinator.collaborative_analysis(project_data))
                loop.close()
                
                # Emit final results
                socketio.emit('analysis_complete', {
                    'success': True,
                    'analysis': analysis,
                    'conversation_log': coordinator.get_conversation_summary(),
                    'message': 'Collaborative analysis completed successfully!'
                })
                
            except Exception as e:
                socketio.emit('analysis_error', {
                    'success': False,
                    'error': str(e)
                })
        
        # Start analysis in background thread
        analysis_thread = threading.Thread(target=run_analysis)
        analysis_thread.daemon = True
        analysis_thread.start()
        
        emit('analysis_started', {'message': 'Analysis started! You will receive real-time updates.'})
        
    except Exception as e:
        emit('analysis_error', {'success': False, 'error': str(e)}) 