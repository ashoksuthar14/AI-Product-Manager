from flask import Blueprint, render_template, redirect, url_for, flash, request, jsonify
from app.models import Project
from app import db, socketio
from app.agents.agent_coordinator import AgentCoordinator
import asyncio

bp = Blueprint('projects', __name__)

@bp.route('/projects')
def projects():
    """Display all projects."""
    all_projects = Project.query.all()
    return render_template('projects/projects.html', projects=all_projects)

@bp.route('/projects/new', methods=['GET', 'POST'])
def new_project():
    """Create a new project."""
    if request.method == 'POST':
        title = request.form.get('title')
        description = request.form.get('description')
        requirements = request.form.get('requirements')
        constraints = request.form.get('constraints')
        timeline = request.form.get('timeline')
        budget = request.form.get('budget')
        
        project = Project(
            title=title,
            description=description,
            requirements=requirements,
            constraints=constraints,
            timeline=timeline,
            budget=budget,
            user_id=1  # Default user ID since we removed login
        )
        
        db.session.add(project)
        db.session.commit()
        
        flash('Project created successfully!', 'success')
        return redirect(url_for('projects.projects'))
    
    return render_template('projects/new_project.html')

@bp.route('/projects/<int:project_id>')
def project_detail(project_id):
    """Display project details and analysis results."""
    project = Project.query.get_or_404(project_id)
    return render_template('projects/project_detail.html', project=project)

@bp.route('/projects/<int:project_id>/analyze', methods=['POST'])
def analyze_project(project_id):
    """Analyze a specific project and store results."""
    project = Project.query.get_or_404(project_id)
    
    try:
        # Update project status to analyzing
        project.status = 'analyzing'
        db.session.commit()
        
        # Initialize collaborative agent coordinator
        coordinator = AgentCoordinator()
        
        # Prepare project data for analysis
        project_data = {
            'title': project.title,
            'description': project.description,
            'requirements': project.requirements,
            'constraints': project.constraints,
            'timeline': project.timeline,
            'budget': project.budget
        }
        
        # Run collaborative analysis
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        analysis = loop.run_until_complete(coordinator.collaborative_analysis(project_data))
        loop.close()
        
        # Store analysis results using new model methods
        project.set_analysis(analysis)
        project.conversation_log = coordinator.get_conversation_summary()
        project.status = 'completed'
        db.session.commit()
        
        return jsonify({
            'success': True,
            'analysis': analysis,
            'conversation_log': coordinator.get_conversation_summary(),
            'message': 'Collaborative analysis completed successfully!',
            'redirect_url': url_for('projects.project_detail', project_id=project.id)
        })
        
    except Exception as e:
        # Reset status on error
        project.status = 'pending'
        db.session.commit()
        
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@bp.route('/projects/<int:project_id>/conversation')
def project_conversation(project_id):
    """Display project conversation log."""
    project = Project.query.get_or_404(project_id)
    return render_template('projects/conversation.html', project=project)

@bp.route('/projects/<int:project_id>/status')
def project_status(project_id):
    """Get project analysis status."""
    project = Project.query.get_or_404(project_id)
    return jsonify({
        'status': project.status,
        'updated_at': project.updated_at.isoformat()
    })

@bp.route('/projects/api/list')
def api_list_projects():
    """API endpoint to get all projects for automation dashboard."""
    try:
        projects = Project.query.all()
        projects_data = [project.to_dict() for project in projects]
        
        return jsonify({
            'success': True,
            'projects': projects_data
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@bp.route('/projects/save_analysis', methods=['POST'])
def save_analysis():
    """Save analysis results from the analyze page."""
    try:
        data = request.get_json()
        
        # Create a new project with the analysis data
        project = Project(
            title=data.get('title', 'Untitled Project'),
            description=data.get('description', ''),
            requirements=data.get('requirements', ''),
            constraints=data.get('constraints', ''),
            timeline=data.get('timeline', ''),
            budget=data.get('budget', ''),
            user_id=1,  # Default user ID
            status='completed'
        )
        
        # Store analysis and conversation data
        if 'analysis' in data:
            project.set_analysis(data['analysis'])
        
        if 'conversation_log' in data:
            project.conversation_log = data['conversation_log']
        
        db.session.add(project)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Analysis saved successfully!',
            'project_id': project.id,
            'redirect_url': url_for('projects.project_detail', project_id=project.id)
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500 