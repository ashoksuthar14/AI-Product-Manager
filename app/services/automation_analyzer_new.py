import json
import uuid
from typing import Dict, List, Any
import google.generativeai as genai

class AutomationAnalyzer:
    def __init__(self, api_key: str = "AIzaSyCPDzArIXcwNwlQcmwsz8BOBaTKLNgS3lg"):
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel("gemini-1.5-flash")
    
    def analyze_workflow_for_automation(self, pm_workflow: str, project_title: str) -> List[Dict[str, Any]]:
        """
        Analyze Product Manager workflow and identify tasks that can be automated with n8n.
        
        Args:
            pm_workflow: The Product Manager workflow text
            project_title: The project title for context
            
        Returns:
            List of automation opportunities with n8n workflows
        """
        try:
            prompt = f"""
            Analyze the following Product Manager workflow for the project "{project_title}" and identify specific tasks that can be automated using n8n workflows. Focus on tasks that involve:
            
            1. Data collection and monitoring
            2. Communication and notifications
            3. Report generation
            4. API integrations
            5. File management and processing
            6. Scheduling and reminders
            7. Data validation and processing
            8. Social media management
            9. Email campaigns
            10. Database operations
            
            Product Manager Workflow:
            {pm_workflow}
            
            For each automatable task you identify, provide:
            1. Task name (clear and descriptive)
            2. Task description (what it does)
            3. Automation benefits (why automate it)
            4. Tools/services it could integrate with
            
            Return your response as a JSON array where each object has:
            {{
                "task_name": "string",
                "task_description": "string", 
                "automation_benefits": "string",
                "integration_tools": ["tool1", "tool2"]
            }}
            
            Only return the JSON array, no additional text.
            """
            
            response = self.model.generate_content(prompt)
            
            # Parse the JSON response
            response_text = response.text.strip()
            # Remove any markdown formatting
            if response_text.startswith('```json'):
                response_text = response_text[7:]
            if response_text.endswith('```'):
                response_text = response_text[:-3]
            response_text = response_text.strip()
            
            automation_tasks = json.loads(response_text)
            
            # Generate n8n workflows for each task
            n8n_workflows = []
            for task in automation_tasks:
                n8n_workflow = self._generate_n8n_workflow(task, project_title)
                if n8n_workflow:
                    n8n_workflows.append({
                        **task,
                        "n8n_workflow": n8n_workflow
                    })
            
            return n8n_workflows
            
        except Exception as e:
            print(f"Error analyzing workflow: {e}")
            # Return some default automations if analysis fails
            return self._get_default_automations(project_title)
    
    def _generate_n8n_workflow(self, task: Dict[str, Any], project_title: str) -> Dict[str, Any]:
        """
        Generate an n8n workflow JSON for a specific automation task.
        
        Args:
            task: Task details from automation analysis
            project_title: Project title for context
            
        Returns:
            n8n workflow JSON
        """
        try:
            prompt = f"""
            Create an n8n workflow to perform this task: {task['task_name']}
            
            Task Description: {task['task_description']}
            Project Context: {project_title}
            Integration Tools: {', '.join(task.get('integration_tools', []))}
            
            Create a complete n8n workflow JSON that includes:
            1. Appropriate trigger nodes (schedule, webhook, manual, etc.)
            2. Processing nodes (HTTP request, data transformation, etc.)
            3. Integration nodes (Gmail, Slack, databases, APIs, etc.)
            4. Output/action nodes
            5. Proper node connections
            6. Realistic node IDs and positions
            7. Appropriate parameters for each node
            
            The workflow should be production-ready and include proper error handling where possible.
            Use realistic node types from the n8n ecosystem.
            
            Return only the JSON workflow object, no additional text.
            Format should match this structure:
            {{
              "name": "Workflow Name",
              "nodes": [...],
              "connections": {{...}},
              "active": false,
              "settings": {{...}},
              "versionId": "1",
              "meta": {{...}},
              "id": "unique_workflow_id",
              "tags": []
            }}
            """
            
            response = self.model.generate_content(prompt)
            
            # Parse and validate the JSON response
            workflow_text = response.text.strip()
            # Remove any markdown formatting
            if workflow_text.startswith('```json'):
                workflow_text = workflow_text[7:]
            if workflow_text.endswith('```'):
                workflow_text = workflow_text[:-3]
            workflow_text = workflow_text.strip()
            
            workflow = json.loads(workflow_text)
            
            # Ensure required fields are present
            if not workflow.get('id'):
                workflow['id'] = str(uuid.uuid4())
            
            if not workflow.get('name'):
                workflow['name'] = task['task_name']
            
            return workflow
            
        except Exception as e:
            print(f"Error generating n8n workflow for task {task['task_name']}: {e}")
            # Return a basic workflow template
            return self._get_basic_workflow_template(task)
    
    def get_automation_suggestions(self, project_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Get automation suggestions based on project data without existing workflow.
        
        Args:
            project_data: Project information
            
        Returns:
            List of automation suggestions with n8n workflows
        """
        try:
            prompt = f"""
            Based on this project information, suggest 5-7 specific automation tasks that would be valuable for project management and development:
            
            Project: {project_data.get('title', 'Untitled Project')}
            Description: {project_data.get('description', 'No description')}
            Requirements: {project_data.get('requirements', 'No requirements specified')}
            Timeline: {project_data.get('timeline', 'No timeline specified')}
            Budget: {project_data.get('budget', 'No budget specified')}
            
            Focus on practical automation opportunities like:
            - Progress tracking and reporting
            - Team communication and updates
            - Code quality monitoring
            - Deployment processes
            - User feedback collection
            - Performance monitoring
            - Resource management
            - Testing automation
            - Documentation generation
            
            Return your response as a JSON array where each object has:
            {{
                "task_name": "string",
                "task_description": "string", 
                "automation_benefits": "string",
                "integration_tools": ["tool1", "tool2"]
            }}
            
            Only return the JSON array, no additional text.
            """
            
            response = self.model.generate_content(prompt)
            
            # Parse the JSON response
            response_text = response.text.strip()
            # Remove any markdown formatting
            if response_text.startswith('```json'):
                response_text = response_text[7:]
            if response_text.endswith('```'):
                response_text = response_text[:-3]
            response_text = response_text.strip()
            
            automation_tasks = json.loads(response_text)
            
            # Generate n8n workflows for each task
            n8n_workflows = []
            for task in automation_tasks:
                n8n_workflow = self._generate_n8n_workflow(task, project_data.get('title', 'Project'))
                if n8n_workflow:
                    n8n_workflows.append({
                        **task,
                        "n8n_workflow": n8n_workflow
                    })
            
            return n8n_workflows
            
        except Exception as e:
            print(f"Error getting automation suggestions: {e}")
            # Return default suggestions if analysis fails
            return self._get_default_automations(project_data.get('title', 'Project'))
    
    def _get_default_automations(self, project_title: str) -> List[Dict[str, Any]]:
        """Return some default automation suggestions."""
        default_tasks = [
            {
                "task_name": "Daily Progress Report",
                "task_description": "Automatically generate and send daily progress reports to stakeholders",
                "automation_benefits": "Saves time on manual reporting and ensures consistent communication",
                "integration_tools": ["Email", "Slack", "Google Sheets"],
                "n8n_workflow": self._get_basic_workflow_template({
                    "task_name": "Daily Progress Report",
                    "task_description": "Automated daily reporting"
                })
            },
            {
                "task_name": "Task Assignment Notification",
                "task_description": "Send notifications when new tasks are assigned to team members",
                "automation_benefits": "Ensures team members are immediately aware of new assignments",
                "integration_tools": ["Slack", "Email", "Microsoft Teams"],
                "n8n_workflow": self._get_basic_workflow_template({
                    "task_name": "Task Assignment Notification",
                    "task_description": "Automated task notifications"
                })
            },
            {
                "task_name": "Code Quality Monitor",
                "task_description": "Monitor code quality metrics and alert on issues",
                "automation_benefits": "Maintains code standards and catches issues early",
                "integration_tools": ["GitHub", "SonarQube", "Slack"],
                "n8n_workflow": self._get_basic_workflow_template({
                    "task_name": "Code Quality Monitor",
                    "task_description": "Automated code quality monitoring"
                })
            }
        ]
        return default_tasks
    
    def _get_basic_workflow_template(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """Return a basic n8n workflow template."""
        workflow_id = str(uuid.uuid4())
        trigger_id = str(uuid.uuid4())
        action_id = str(uuid.uuid4())
        
        return {
            "name": task.get('task_name', 'Automation Workflow'),
            "nodes": [
                {
                    "parameters": {
                        "interval": 3600000
                    },
                    "id": trigger_id,
                    "name": "Schedule Trigger",
                    "type": "n8n-nodes-base.scheduleTrigger",
                    "typeVersion": 1.1,
                    "position": [240, 300]
                },
                {
                    "parameters": {
                        "operation": "send",
                        "resource": "message",
                        "subject": f"Automation: {task.get('task_name', 'Task')}",
                        "message": f"Automated workflow for: {task.get('task_description', 'Task execution')}",
                        "toList": "admin@example.com"
                    },
                    "id": action_id,
                    "name": "Send Notification",
                    "type": "n8n-nodes-base.gmail",
                    "typeVersion": 2,
                    "position": [640, 300],
                    "credentials": {
                        "gmailOAuth2": {
                            "id": "gmail_credentials",
                            "name": "Gmail OAuth2 Credentials"
                        }
                    }
                }
            ],
            "connections": {
                "Schedule Trigger": {
                    "main": [
                        [
                            {
                                "node": "Send Notification",
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
                "callerPolicy": "workflowsFromSameOwner",
                "errorWorkflow": {
                    "id": "",
                    "name": ""
                }
            },
            "versionId": "1",
            "meta": {
                "templateCredsSetupCompleted": False
            },
            "id": workflow_id,
            "tags": []
        } 