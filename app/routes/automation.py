from flask import Blueprint, render_template, request, jsonify
from app.models.project import Project
import google.generativeai as genai
import json
import uuid
import json
import os

bp = Blueprint('automation', __name__, url_prefix='/automation')

# Initialize Gemini from environment
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY") or os.getenv("OPENAI_API_KEY")
model = None
if GEMINI_API_KEY:
    try:
        genai.configure(api_key=GEMINI_API_KEY)
        model = genai.GenerativeModel("gemini-1.5-flash")
    except Exception as e:
        print(f"Failed to initialize Gemini model: {e}")

def analyze_workflow_simple(pm_workflow: str, project_title: str):
    """Simple workflow analysis using Gemini."""
    try:
        if model is None:
            return get_default_automations()
        prompt = f"""
        Analyze this Product Manager workflow for "{project_title}" and identify 3-5 tasks that can be automated with n8n:

        {pm_workflow}

        For each task, return JSON format:
        {{
            "task_name": "Task Name",
            "task_description": "What it does",
            "automation_benefits": "Why automate it",
            "integration_tools": ["tool1", "tool2"],
            "n8n_workflow": {{basic workflow JSON}}
        }}

        Return a JSON array only.
        """
        
        response = model.generate_content(prompt)
        response_text = response.text.strip()
        
        # Clean up response
        if response_text.startswith('```json'):
            response_text = response_text[7:]
        if response_text.endswith('```'):
            response_text = response_text[:-3]
        response_text = response_text.strip()
        
        automations = json.loads(response_text)
        
        # Add basic workflows if missing
        for automation in automations:
            if 'n8n_workflow' not in automation:
                automation['n8n_workflow'] = get_basic_workflow(automation['task_name'])
                
        return automations
        
    except Exception as e:
        print(f"Error in workflow analysis: {e}")
        return get_default_automations()

def get_automation_suggestions_simple(project_data):
    """Get automation suggestions for a project."""
    try:
        if model is None:
            return get_default_automations()
        prompt = f"""
        Suggest 5 automation workflows for this project:
        
        Title: {project_data.get('title', 'Project')}
        Description: {project_data.get('description', 'No description')}
        
        Focus on: notifications, reporting, monitoring, data processing, communication
        
        Return JSON array with format:
        {{
            "task_name": "Name",
            "task_description": "Description", 
            "automation_benefits": "Benefits",
            "integration_tools": ["tools"]
        }}
        """
        
        response = model.generate_content(prompt)
        response_text = response.text.strip()
        
        # Clean up response
        if response_text.startswith('```json'):
            response_text = response_text[7:]
        if response_text.endswith('```'):
            response_text = response_text[:-3]
        response_text = response_text.strip()
        
        automations = json.loads(response_text)
        
        # Add n8n workflows
        for automation in automations:
            automation['n8n_workflow'] = get_basic_workflow(automation['task_name'])
                
        return automations
        
    except Exception as e:
        print(f"Error getting suggestions: {e}")
        return get_default_automations()

def get_default_automations():
    """Return default automation examples."""
    return [
        {
            "task_name": "Daily Progress Report",
            "task_description": "Automatically generate and send daily progress reports to stakeholders",
            "automation_benefits": "Saves time on manual reporting and ensures consistent communication",
            "integration_tools": ["Email", "Slack", "Google Sheets"],
            "n8n_workflow": get_basic_workflow("Daily Progress Report")
        },
        {
            "task_name": "Task Assignment Notification",
            "task_description": "Send notifications when new tasks are assigned to team members",
            "automation_benefits": "Ensures team members are immediately aware of new assignments",
            "integration_tools": ["Slack", "Email", "Microsoft Teams"],
            "n8n_workflow": get_basic_workflow("Task Assignment Notification")
        },
        {
            "task_name": "Code Quality Monitor",
            "task_description": "Monitor code quality metrics and alert on issues",
            "automation_benefits": "Maintains code standards and catches issues early",
            "integration_tools": ["GitHub", "SonarQube", "Slack"],
            "n8n_workflow": get_basic_workflow("Code Quality Monitor")
        }
    ]

def get_basic_workflow(task_name):
    """Generate a basic n8n workflow template."""
    workflow_id = str(uuid.uuid4())
    trigger_id = str(uuid.uuid4())
    action_id = str(uuid.uuid4())
    transform_id = str(uuid.uuid4())
    
    return {
        "name": f"{task_name} Automation",
        "nodes": [
            {
                "parameters": {
                    "interval": "hour",
                    "intervalSize": 1
                },
                "id": trigger_id,
                "name": "Schedule Trigger",
                "type": "n8n-nodes-base.scheduleTrigger",
                "typeVersion": 1.1,
                "position": [240, 300]
            },
            {
                "parameters": {
                    "jsCode": f"// Process data for {task_name}\nconst data = {{\n  task: '{task_name}',\n  timestamp: new Date().toISOString(),\n  status: 'automated'\n}};\n\nreturn [{{ json: data }}];"
                },
                "id": transform_id,
                "name": "Process Data",
                "type": "n8n-nodes-base.code",
                "typeVersion": 2,
                "position": [440, 300]
            },
            {
                "parameters": {
                    "method": "POST",
                    "url": "https://webhook.site/your-webhook-url",
                    "options": {
                        "headers": {
                            "Content-Type": "application/json"
                        }
                    },
                    "bodyParametersUi": {
                        "parameter": [
                            {
                                "name": "task_name",
                                "value": f"{task_name}"
                            },
                            {
                                "name": "data",
                                "value": "={{ $json }}"
                            }
                        ]
                    }
                },
                "id": action_id,
                "name": "Send Webhook",
                "type": "n8n-nodes-base.httpRequest",
                "typeVersion": 4.1,
                "position": [640, 300]
            }
        ],
        "connections": {
            "Schedule Trigger": {
                "main": [
                    [
                        {
                            "node": "Process Data",
                            "type": "main",
                            "index": 0
                        }
                    ]
                ]
            },
            "Process Data": {
                "main": [
                    [
                        {
                            "node": "Send Webhook",
                            "type": "main",
                            "index": 0
                        }
                    ]
                ]
            }
        },
        "active": False,
        "settings": {
            "saveManualExecutions": True,
            "callerPolicy": "workflowsFromSameOwner"
        },
        "versionId": "1",
        "meta": {
            "templateCredsSetupCompleted": False
        },
        "id": workflow_id,
        "tags": []
    }

@bp.route('/')
def automation_dashboard():
    """Display automation dashboard with all available automations."""
    return render_template('automation/dashboard.html')

@bp.route('/analyze/<int:project_id>')
def analyze_project_automation(project_id):
    """Analyze a specific project for automation opportunities."""
    try:
        project = Project.query.get_or_404(project_id)
        
        # Get the Product Manager workflow from analysis
        analysis_data = project.get_analysis()
        if not analysis_data:
            return jsonify({
                'success': False,
                'error': 'Project has not been analyzed yet. Please run the project analysis first.'
            }), 400
        
        # Extract PM workflow/overview
        pm_workflow = analysis_data.get('pm_overview', '')
        if not pm_workflow:
            # Fallback to other analysis sections
            product_mgmt = analysis_data.get('product_management', {})
            pm_workflow = product_mgmt.get('strategy', '') or product_mgmt.get('market_analysis', '') or str(product_mgmt)
        
        if not pm_workflow:
            return jsonify({
                'success': False,
                'error': 'No Product Manager workflow found in project analysis.'
            }), 400
        
        # Analyze for automation opportunities
        automations = analyze_workflow_simple(pm_workflow, project.title)
        
        return jsonify({
            'success': True,
            'project': project.to_dict(),
            'automations': automations,
            'count': len(automations)
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@bp.route('/suggest')
def suggest_automations():
    """Suggest general automation workflows based on project data."""
    try:
        # Get project data from query parameters
        project_data = {
            'title': request.args.get('title', 'General Project'),
            'description': request.args.get('description', ''),
            'requirements': request.args.get('requirements', ''),
            'timeline': request.args.get('timeline', ''),
            'budget': request.args.get('budget', '')
        }
        
        automations = get_automation_suggestions_simple(project_data)
        
        return jsonify({
            'success': True,
            'project': project_data,
            'automations': automations,
            'count': len(automations)
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@bp.route('/workflow/<workflow_id>')
def get_workflow(workflow_id):
    """Get a specific n8n workflow by ID."""
    try:
        # This would typically fetch from a database
        # For now, return a sample workflow
        return jsonify({
            'success': True,
            'workflow': {
                'id': workflow_id,
                'name': 'Sample Workflow',
                'description': 'Sample n8n workflow'
            }
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@bp.route('/project/<int:project_id>')
def project_automations(project_id):
    """Display automation page for a specific project."""
    try:
        project = Project.query.get_or_404(project_id)
        return render_template('automation/project.html', project=project)
        
    except Exception as e:
        return render_template('automation/error.html', error=str(e)) 