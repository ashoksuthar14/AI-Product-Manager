import json
import uuid
from typing import Dict, List, Any
import google.generativeai as genai

class AutomationAnalyzer:
    def __init__(self, api_key: str = "AIzaSyCPDzArIXcwNwlQcmwsz8BOBaTKLNgS3lg"):
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel("gemini-2.0-flash")
    
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
            You are an experienced automation architect.
            Carefully read the Product-Manager workflow for the project "{project_title}" below and design automation **opportunities that are highly specific to THIS project** (do NOT re-use boiler-plate ideas).

            🔹 Generate **6 – 10 unique tasks**, each one different in scope (e.g. data-sync, QA notifications, release gates, etc.).
            🔹 Prefer tasks that require multi-step orchestration or external APIs – avoid trivial single-node automations.
            🔹 For each task include:
                • task_name – short but descriptive (lower snake case)
                • task_description – 2-3 sentences on what happens
                • automation_benefits – why this saves time / reduces risk for THIS project
                • integration_tools – concrete SaaS / tools you would wire (array)

            Return **ONLY** a JSON array – no markdown, no comments.
            
            Examples of good task names: "sync_app_store_reviews", "auto_regression_test_pipeline".
            Examples of bad task names: "Daily Report", "Send Email".
            
            Product Manager Workflow:
            {pm_workflow}
            """
            
            response = self.model.generate_content(prompt, generation_config={"temperature":0.8})
            
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
        tools = [t.lower() for t in task.get('integration_tools', [])]
        tries = 0
        while tries < 3:
            tries += 1
            try:
                prompt = f"""
You are an expert n8n architect. Create a detailed n8n workflow JSON for the task "{task['task_name']}" (Project: {project_title}).

Requirements:
• Include a trigger node (e.g., cron, webhook, or manual) to start the workflow.
• Use at least 8 nodes, including data processing, integrations, and error handling.
• Ensure every tool listed below is represented by a node in the workflow:
  {', '.join(task.get('integration_tools', []))}
• Provide realistic parameters and credentials placeholders.
• Return only valid JSON (no markdown fences).

Example structure:
{
  "name": "Project Update Management Workflow",
  "nodes": [
    {
      "parameters": {
        "rule": {
          "interval": [
            {
              "field": "cronExpression",
              "expression": "0 9 * * 1"
            }
          ]
        }
      },
      "id": "cron-trigger",
      "name": "Weekly Schedule Trigger",
      "type": "n8n-nodes-base.cron",
      "typeVersion": 1,
      "position": [240, 300]
    },
    {
      "parameters": {
        "authentication": "oAuth2",
        "resource": "database",
        "operation": "getAll",
        "databaseId": "={{ $env.NOTION_WORKERS_DB_ID }}",
        "options": {
          "filter": {
            "filters": [
              {
                "property": "Status",
                "select": {
                  "equals": "Active"
                }
              }
            ]
          }
        }
      },
      "id": "get-workers",
      "name": "Get Active Workers from Notion",
      "type": "n8n-nodes-base.notion",
      "typeVersion": 2,
      "position": [460, 300]
    },
    {
      "parameters": {
        "authentication": "oAuth2",
        "resource": "database",
        "operation": "getAll",
        "databaseId": "={{ $env.NOTION_PROJECTS_DB_ID }}",
        "options": {
          "filter": {
            "filters": [
              {
                "property": "Status",
                "select": {
                  "does_not_equal": "Completed"
                }
              }
            ]
          }
        }
      },
      "id": "get-projects",
      "name": "Get Active Projects",
      "type": "n8n-nodes-base.notion",
      "typeVersion": 2,
      "position": [680, 300]
    },
    {
      "parameters": {
        "jsCode": "// Combine workers with their assigned projects\nconst workers = $input.first().json;\nconst projects = $input.all()[1].json;\n\nconst emailRequests = [];\n\nfor (const worker of workers.results) {\n  const workerProjects = projects.results.filter(project => {\n    const assignedTo = project.properties['Assigned To']?.people || [];\n    return assignedTo.some(person => person.id === worker.id);\n  });\n  \n  if (workerProjects.length > 0) {\n    emailRequests.push({\n      workerId: worker.id,\n      workerName: worker.properties.Name?.title[0]?.text?.content || 'Unknown',\n      workerEmail: worker.properties.Email?.email || '',\n      projects: workerProjects.map(p => ({\n        id: p.id,\n        name: p.properties.Name?.title[0]?.text?.content || 'Untitled Project',\n        deadline: p.properties.Deadline?.date?.start || 'No deadline',\n        status: p.properties.Status?.select?.name || 'Unknown'\n      }))\n    });\n  }\n}\n\nreturn emailRequests.map(req => ({ json: req }));"
      },
      "id": "process-data",
      "name": "Process Worker-Project Data",
      "type": "n8n-nodes-base.code",
      "typeVersion": 2,
      "position": [900, 300]
    },
    {
      "parameters": {
        "authentication": "oAuth2",
        "sendTo": "={{ $json.workerEmail }}",
        "subject": "Weekly Project Update Request - {{ new Date().toLocaleDateString() }}",
        "emailType": "html",
        "message": "<!DOCTYPE html>\n<html>\n<head>\n    <style>\n        body { font-family: Arial, sans-serif; line-height: 1.6; color: #333; }\n        .header { background-color: #4CAF50; color: white; padding: 20px; text-align: center; }\n        .content { padding: 20px; }\n        .project { background-color: #f9f9f9; margin: 10px 0; padding: 15px; border-left: 4px solid #4CAF50; }\n        .footer { background-color: #f1f1f1; padding: 15px; text-align: center; font-size: 12px; }\n        .update-format { background-color: #e8f4fd; padding: 15px; margin: 15px 0; border-radius: 5px; }\n    </style>\n</head>\n<body>\n    <div class=\"header\">\n        <h2>Weekly Project Update Request</h2>\n    </div>\n    \n    <div class=\"content\">\n        <p>Hi {{ $json.workerName }},</p>\n        \n        <p>I hope you're doing well! It's time for our weekly project update. Please provide status updates for your assigned projects:</p>\n        \n        <h3>Your Current Projects:</h3>\n        \n        {{#each $json.projects}}\n        <div class=\"project\">\n            <h4>📋 {{ this.name }}</h4>\n            <p><strong>Current Status:</strong> {{ this.status }}</p>\n            <p><strong>Deadline:</strong> {{ this.deadline }}</p>\n        </div>\n        {{/each}}\n        \n        <div class=\"update-format\">\n            <h3>📝 Please Reply with Updates in This Format:</h3>\n            <p><strong>For each project, please include:</strong></p>\n            <ul>\n                <li><strong>Project Name:</strong> [Project Name]</li>\n                <li><strong>Progress:</strong> [What you've completed this week]</li>\n                <li><strong>Current Status:</strong> [On Track/Delayed/Blocked/Completed]</li>\n                <li><strong>Next Steps:</strong> [What you plan to work on next]</li>\n                <li><strong>Blockers:</strong> [Any issues or help needed]</li>\n                <li><strong>Completion %:</strong> [0-100%]</li>\n            </ul>\n        </div>\n        \n        <p>Please reply to this email with your updates by end of day. If you have any questions or need clarification, don't hesitate to reach out!</p>\n        \n        <p>Thank you for your continued hard work!</p>\n        \n        <p>Best regards,<br>Project Management Team</p>\n    </div>\n    \n    <div class=\"footer\">\n        <p>This is an automated message from the Project Management System</p>\n        <p>Request ID: UPDATE-{{ $json.workerId }}-{{ new Date().toISOString().split('T')[0] }}</p>\n    </div>\n</body>\n</html>",
        "options": {}
      },
      "id": "send-update-request",
      "name": "Send Update Request Email",
      "type": "n8n-nodes-base.gmail",
      "typeVersion": 1,
      "position": [1120, 300]
    },
    {
      "parameters": {
        "authentication": "oAuth2",
        "resource": "database",
        "operation": "create",
        "databaseId": "={{ $env.NOTION_UPDATE_REQUESTS_DB_ID }}",
        "title": "Update Request - {{ $json.workerName }} - {{ new Date().toLocaleDateString() }}",
        "propertiesUi": {
          "propertyValues": [
            {
              "key": "Worker",
              "peopleValue": [
                "={{ $json.workerId }}"
              ]
            },
            {
              "key": "Request Date",
              "dateValue": "={{ new Date().toISOString().split('T')[0] }}"
            },
            {
              "key": "Status",
              "selectValue": "Sent"
            },
            {
              "key": "Projects Count",
              "numberValue": "={{ $json.projects.length }}"
            }
          ]
        }
      },
      "id": "log-request",
      "name": "Log Update Request in Notion",
      "type": "n8n-nodes-base.notion",
      "typeVersion": 2,
      "position": [1340, 300]
    },
    {
      "parameters": {
        "authentication": "oAuth2",
        "pollTimes": {
          "item": [
            {
              "mode": "everyMinute",
              "minute": 5
            }
          ]
        },
        "filters": {
          "subject": "Re: Weekly Project Update Request"
        },
        "format": "resolved",
        "options": {
          "allowUnauthorizedCerts": false,
          "includeAttachments": false
        }
      },
      "id": "email-trigger",
      "name": "Monitor Email Responses",
      "type": "n8n-nodes-base.gmailTrigger",
      "typeVersion": 1,
      "position": [240, 600]
    },
    {
      "parameters": {
        "jsCode": "// Parse email content and extract project updates\nconst emailBody = $json.textPlain || $json.textHtml || '';\nconst senderEmail = $json.from.address;\nconst subject = $json.subject;\n\n// Extract request ID from original email if available\nconst requestIdMatch = emailBody.match(/Request ID: UPDATE-([^-]+)-([0-9-]+)/);\nconst workerId = requestIdMatch ? requestIdMatch[1] : null;\n\n// Parse project updates using regex patterns\nconst projectUpdates = [];\nconst projectBlocks = emailBody.split(/(?=Project Name:|📋)/i).slice(1);\n\nfor (const block of projectBlocks) {\n  const update = {};\n  \n  // Extract project information\n  const nameMatch = block.match(/Project Name:\\s*(.+?)(?=\\n|Progress:|$)/i);\n  const progressMatch = block.match(/Progress:\\s*(.+?)(?=\\n|Current Status:|$)/i);\n  const statusMatch = block.match(/Current Status:\\s*(.+?)(?=\\n|Next Steps:|$)/i);\n  const nextStepsMatch = block.match(/Next Steps:\\s*(.+?)(?=\\n|Blockers:|$)/i);\n  const blockersMatch = block.match(/Blockers:\\s*(.+?)(?=\\n|Completion|$)/i);\n  const completionMatch = block.match(/Completion.*?([0-9]+)%/i);\n  \n  if (nameMatch) {\n    update.projectName = nameMatch[1].trim();\n    update.progress = progressMatch ? progressMatch[1].trim() : '';\n    update.status = statusMatch ? statusMatch[1].trim() : 'Unknown';\n    update.nextSteps = nextStepsMatch ? nextStepsMatch[1].trim() : '';\n    update.blockers = blockersMatch ? blockersMatch[1].trim() : 'None';\n    update.completionPercentage = completionMatch ? parseInt(completionMatch[1]) : 0;\n    \n    projectUpdates.push(update);\n  }\n}\n\nreturn [{\n  json: {\n    senderEmail,\n    workerId,\n    receivedAt: new Date().toISOString(),\n    originalSubject: subject,\n    projectUpdates,\n    rawContent: emailBody.substring(0, 1000) // Keep first 1000 chars for reference\n  }\n}];"
      },
      "id": "parse-email",
      "name": "Parse Email Response",
      "type": "n8n-nodes-base.code",
      "typeVersion": 2,
      "position": [460, 600]
    },
    {
      "parameters": {
        "authentication": "oAuth2",
        "resource": "database",
        "operation": "getAll",
        "databaseId": "={{ $env.NOTION_PROJECTS_DB_ID }}",
        "options": {
          "filter": {
            "filters": [
              {
                "property": "Name",
                "rich_text": {
                  "contains": "={{ $json.projectUpdates[0].projectName }}"
                }
              }
            ]
          }
        }
      },
      "id": "find-project",
      "name": "Find Project in Notion",
      "type": "n8n-nodes-base.notion",
      "typeVersion": 2,
      "position": [680, 600]
    },
    {
      "parameters": {
        "jsCode": "// Process each project update\nconst emailData = $input.first().json;\nconst projectResults = $input.all().slice(1);\n\nconst updates = [];\n\nfor (let i = 0; i < emailData.projectUpdates.length; i++) {\n  const update = emailData.projectUpdates[i];\n  const projectResult = projectResults[i]?.json?.results?.[0];\n  \n  if (projectResult) {\n    updates.push({\n      projectId: projectResult.id,\n      projectName: update.projectName,\n      progress: update.progress,\n      status: update.status,\n      nextSteps: update.nextSteps,\n      blockers: update.blockers,\n      completionPercentage: update.completionPercentage,\n      updatedBy: emailData.senderEmail,\n      updatedAt: emailData.receivedAt\n    });\n  }\n}\n\nreturn updates.map(update => ({ json: update }));"
      },
      "id": "prepare-updates",
      "name": "Prepare Project Updates",
      "type": "n8n-nodes-base.code",
      "typeVersion": 2,
      "position": [900, 600]
    },
    {
      "parameters": {
        "authentication": "oAuth2",
        "resource": "page",
        "operation": "update",
        "pageId": "={{ $json.projectId }}",
        "propertiesUi": {
          "propertyValues": [
            {
              "key": "Status",
              "selectValue": "={{ $json.status }}"
            },
            {
              "key": "Progress %",
              "numberValue": "={{ $json.completionPercentage }}"
            },
            {
              "key": "Last Updated",
              "dateValue": "={{ $json.updatedAt.split('T')[0] }}"
            },
            {
              "key": "Current Blockers",
              "richTextValue": "={{ $json.blockers }}"
            },
            {
              "key": "Next Steps",
              "richTextValue": "={{ $json.nextSteps }}"
            }
          ]
        }
      },
      "id": "update-project",
      "name": "Update Project in Notion",
      "type": "n8n-nodes-base.notion",
      "typeVersion": 2,
      "position": [1120, 600]
    },
    {
      "parameters": {
        "authentication": "oAuth2",
        "resource": "database",
        "operation": "create",
        "databaseId": "={{ $env.NOTION_UPDATE_LOGS_DB_ID }}",
        "title": "Update: {{ $json.projectName }} - {{ new Date($json.updatedAt).toLocaleDateString() }}",
        "propertiesUi": {
          "propertyValues": [
            {
              "key": "Project",
              "relationValue": [
                "={{ $json.projectId }}"
              ]
            },
            {
              "key": "Update Date",
              "dateValue": "={{ $json.updatedAt.split('T')[0] }}"
            },
            {
              "key": "Progress Description",
              "richTextValue": "={{ $json.progress }}"
            },
            {
              "key": "Status",
              "selectValue": "={{ $json.status }}"
            },
            {
              "key": "Completion %",
              "numberValue": "={{ $json.completionPercentage }}"
            },
            {
              "key": "Blockers",
              "richTextValue": "={{ $json.blockers }}"
            },
            {
              "key": "Next Steps",
              "richTextValue": "={{ $json.nextSteps }}"
            },
            {
              "key": "Updated By Email",
              "emailValue": "={{ $json.updatedBy }}"
            }
          ]
        }
      },
      "id": "create-update-log",
      "name": "Create Update Log Entry",
      "type": "n8n-nodes-base.notion",
      "typeVersion": 2,
      "position": [1340, 600]
    },
    {
      "parameters": {
        "authentication": "oAuth2",
        "sendTo": "={{ $json.updatedBy }}",
        "subject": "✅ Project Update Received - Thank You!",
        "emailType": "html",
        "message": "<!DOCTYPE html>\n<html>\n<head>\n    <style>\n        body { font-family: Arial, sans-serif; line-height: 1.6; color: #333; }\n        .header { background-color: #4CAF50; color: white; padding: 20px; text-align: center; }\n        .content { padding: 20px; }\n        .success { background-color: #d4edda; padding: 15px; border-radius: 5px; margin: 15px 0; }\n    </style>\n</head>\n<body>\n    <div class=\"header\">\n        <h2>✅ Update Received Successfully</h2>\n    </div>\n    \n    <div class=\"content\">\n        <div class=\"success\">\n            <p><strong>Thank you for your project update!</strong></p>\n            <p>We've successfully received and processed your update for: <strong>{{ $json.projectName }}</strong></p>\n        </div>\n        \n        <p>Your update has been automatically synced to our project management system. The team leads will review your progress and reach out if any follow-up is needed.</p>\n        \n        <p>Keep up the great work! 🚀</p>\n        \n        <p>Best regards,<br>Project Management Team</p>\n    </div>\n</body>\n</html>"
      },
      "id": "send-confirmation",
      "name": "Send Confirmation Email",
      "type": "n8n-nodes-base.gmail",
      "typeVersion": 1,
      "position": [1560, 600]
    }
  ],
  "connections": {
    "Weekly Schedule Trigger": {
      "main": [
        [
          {
            "node": "Get Active Workers from Notion",
            "type": "main",
            "index": 0
          }
        ]
      ]
    },
    "Get Active Workers from Notion": {
      "main": [
        [
          {
            "node": "Get Active Projects",
            "type": "main",
            "index": 0
          }
        ]
      ]
    },
    "Get Active Projects": {
      "main": [
        [
          {
            "node": "Process Worker-Project Data",
            "type": "main",
            "index": 0
          }
        ]
      ]
    },
    "Process Worker-Project Data": {
      "main": [
        [
          {
            "node": "Send Update Request Email",
            "type": "main",
            "index": 0
          }
        ]
      ]
    },
    "Send Update Request Email": {
      "main": [
        [
          {
            "node": "Log Update Request in Notion",
            "type": "main",
            "index": 0
          }
        ]
      ]
    },
    "Monitor Email Responses": {
      "main": [
        [
          {
            "node": "Parse Email Response",
            "type": "main",
            "index": 0
          }
        ]
      ]
    },
    "Parse Email Response": {
      "main": [
        [
          {
            "node": "Find Project in Notion",
            "type": "main",
            "index": 0
          }
        ]
      ]
    },
    "Find Project in Notion": {
      "main": [
        [
          {
            "node": "Prepare Project Updates",
            "type": "main",
            "index": 0
          }
        ]
      ]
    },
    "Prepare Project Updates": {
      "main": [
        [
          {
            "node": "Update Project in Notion",
            "type": "main",
            "index": 0
          }
        ]
      ]
    },
    "Update Project in Notion": {
      "main": [
        [
          {
            "node": "Create Update Log Entry",
            "type": "main",
            "index": 0
          }
        ]
      ]
    },
    "Create Update Log Entry": {
      "main": [
        [
          {
            "node": "Send Confirmation Email",
            "type": "main",
            "index": 0
          }
        ]
      ]
    }
  },
  "settings": {
    "executionOrder": "v1"
  }
}

"""

                response = self.model.generate_content(prompt, generation_config={"temperature":0.9})
                text = response.text.strip()
                if text.startswith('```'):
                    text = text.strip('`\n ')  # remove fences if any
                workflow = json.loads(text)

                # verify each tool present in nodes json
                node_json = json.dumps(workflow.get('nodes', [])).lower()
                if not all(t in node_json for t in tools):
                    raise ValueError('Missing tool nodes')

                sanitized = self._sanitize_workflow(workflow, task)
                return sanitized
            except Exception as e:
                print(f"Attempt {tries} failed for {task['task_name']}: {e}")
                continue

        # fallback
        return self._get_basic_workflow_template(task)

    def _sanitize_workflow(self, workflow: Dict[str, Any], task: Dict[str, Any]) -> Dict[str, Any]:
        """Ensure workflow conforms to n8n schema."""
        # Ensure nodes list exists
        if 'nodes' not in workflow or not isinstance(workflow['nodes'], list):
            workflow['nodes'] = []
        # Add ids and positions
        for idx, node in enumerate(workflow['nodes']):
            node.setdefault('id', str(uuid.uuid4()))
            node.setdefault('position', [240 + 200*idx, 300])
        # Build linear connections if none
        if not workflow.get('connections') and len(workflow['nodes']) >= 2:
            workflow['connections'] = {}
            for i in range(len(workflow['nodes']) - 1):
                from_name = workflow['nodes'][i]['name']
                to_name = workflow['nodes'][i+1]['name']
                workflow['connections'][from_name] = {
                    'main': [[{'node': to_name, 'type': 'main', 'index': 0}]]
                }
        # other required fields
        workflow.setdefault('id', str(uuid.uuid4()))
        workflow.setdefault('name', task.get('task_name', 'Workflow'))
        workflow.setdefault('active', False)
        workflow.setdefault('settings', {'saveManualExecutions': True})
        workflow.setdefault('versionId', '1')
        workflow.setdefault('meta', {'templateCredsSetupCompleted': False})
        workflow.setdefault('tags', [])
        return workflow
    
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
        """Return a basic workflow template if generation fails."""
        if task['task_name'] == 'managing schedules and updates':
            return {
                "id": str(uuid.uuid4()),
                "name": "Project Update Management Workflow",
                "nodes": [
                    {
                        "parameters": {
                            "rule": {
                                "interval": [
                                    {
                                        "field": "cronExpression",
                                        "expression": "0 9 * * 1"
                                    }
                                ]
                            }
                        },
                        "id": "cron-trigger",
                        "name": "Weekly Schedule Trigger",
                        "type": "n8n-nodes-base.cron",
                        "typeVersion": 1,
                        "position": [240, 300]
                    },
                    {
                        "parameters": {
                            "authentication": "oAuth2",
                            "resource": "database",
                            "operation": "getAll",
                            "databaseId": "={{ $env.NOTION_WORKERS_DB_ID }}",
                            "options": {
                                "filter": {
                                    "filters": [
                                        {
                                            "property": "Status",
                                            "select": {
                                                "equals": "Active"
                                            }
                                        }
                                    ]
                                }
                            }
                        },
                        "id": "get-workers",
                        "name": "Get Active Workers from Notion",
                        "type": "n8n-nodes-base.notion",
                        "typeVersion": 2,
                        "position": [460, 300]
                    },
                    {
                        "parameters": {
                            "authentication": "oAuth2",
                            "resource": "database",
                            "operation": "getAll",
                            "databaseId": "={{ $env.NOTION_PROJECTS_DB_ID }}",
                            "options": {
                                "filter": {
                                    "filters": [
                                        {
                                            "property": "Status",
                                            "select": {
                                                "does_not_equal": "Completed"
                                            }
                                        }
                                    ]
                                }
                            }
                        },
                        "id": "get-projects",
                        "name": "Get Active Projects",
                        "type": "n8n-nodes-base.notion",
                        "typeVersion": 2,
                        "position": [680, 300]
                    },
                    {
                        "parameters": {
                            "jsCode": "// Combine workers with their assigned projects\nconst workers = $input.first().json;\nconst projects = $input.all()[1].json;\n\nconst emailRequests = [];\n\nfor (const worker of workers.results) {\n  const workerProjects = projects.results.filter(project => {\n    const assignedTo = project.properties['Assigned To']?.people || [];\n    return assignedTo.some(person => person.id === worker.id);\n  });\n  \n  if (workerProjects.length > 0) {\n    emailRequests.push({\n      workerId: worker.id,\n      workerName: worker.properties.Name?.title[0]?.text?.content || 'Unknown',\n      workerEmail: worker.properties.Email?.email || '',\n      projects: workerProjects.map(p => ({\n        id: p.id,\n        name: p.properties.Name?.title[0]?.text?.content || 'Untitled Project',\n        deadline: p.properties.Deadline?.date?.start || 'No deadline',\n        status: p.properties.Status?.select?.name || 'Unknown'\n      }))\n    });\n  }\n}\n\nreturn emailRequests.map(req => ({ json: req }));"
                        },
                        "id": "process-data",
                        "name": "Process Worker-Project Data",
                        "type": "n8n-nodes-base.code",
                        "typeVersion": 2,
                        "position": [900, 300]
                    },
                    {
                        "parameters": {
                            "authentication": "oAuth2",
                            "sendTo": "={{ $json.workerEmail }}",
                            "subject": "Weekly Project Update Request - {{ new Date().toLocaleDateString() }}",
                            "emailType": "html",
                            "message": "<!DOCTYPE html>\n<html>\n<head>\n    <style>\n        body { font-family: Arial, sans-serif; line-height: 1.6; color: #333; }\n        .header { background-color: #4CAF50; color: white; padding: 20px; text-align: center; }\n        .content { padding: 20px; }\n        .project { background-color: #f9f9f9; margin: 10px 0; padding: 15px; border-left: 4px solid #4CAF50; }\n        .footer { background-color: #f1f1f1; padding: 15px; text-align: center; font-size: 12px; }\n        .update-format { background-color: #e8f4fd; padding: 15px; margin: 15px 0; border-radius: 5px; }\n    </style>\n</head>\n<body>\n    <div class=\"header\">\n        <h2>Weekly Project Update Request</h2>\n    </div>\n    \n    <div class=\"content\">\n        <p>Hi {{ $json.workerName }},</p>\n        \n        <p>I hope you're doing well! It's time for our weekly project update. Please provide status updates for your assigned projects:</p>\n        \n        <h3>Your Current Projects:</h3>\n        \n        {{#each $json.projects}}\n        <div class=\"project\">\n            <h4>📋 {{ this.name }}</h4>\n            <p><strong>Current Status:</strong> {{ this.status }}</p>\n            <p><strong>Deadline:</strong> {{ this.deadline }}</p>\n        </div>\n        {{/each}}\n        \n        <div class=\"update-format\">\n            <h3>📝 Please Reply with Updates in This Format:</h3>\n            <p><strong>For each project, please include:</strong></p>\n            <ul>\n                <li><strong>Project Name:</strong> [Project Name]</li>\n                <li><strong>Progress:</strong> [What you've completed this week]</li>\n                <li><strong>Current Status:</strong> [On Track/Delayed/Blocked/Completed]</li>\n                <li><strong>Next Steps:</strong> [What you plan to work on next]</li>\n                <li><strong>Blockers:</strong> [Any issues or help needed]</li>\n                <li><strong>Completion %:</strong> [0-100%]</li>\n            </ul>\n        </div>\n        \n        <p>Please reply to this email with your updates by end of day. If you have any questions or need clarification, don't hesitate to reach out!</p>\n        \n        <p>Thank you for your continued hard work!</p>\n        \n        <p>Best regards,<br>Project Management Team</p>\n    </div>\n    \n    <div class=\"footer\">\n        <p>This is an automated message from the Project Management System</p>\n        <p>Request ID: UPDATE-{{ $json.workerId }}-{{ new Date().toISOString().split('T')[0] }}</p>\n    </div>\n</body>\n</html>",
                            "options": {}
                        },
                        "id": "send-update-request",
                        "name": "Send Update Request Email",
                        "type": "n8n-nodes-base.gmail",
                        "typeVersion": 1,
                        "position": [1120, 300]
                    },
                    {
                        "parameters": {
                            "authentication": "oAuth2",
                            "resource": "database",
                            "operation": "create",
                            "databaseId": "={{ $env.NOTION_UPDATE_REQUESTS_DB_ID }}",
                            "title": "Update Request - {{ $json.workerName }} - {{ new Date().toLocaleDateString() }}",
                            "propertiesUi": {
                                "propertyValues": [
                                    {
                                        "key": "Worker",
                                        "peopleValue": [
                                            "={{ $json.workerId }}"
                                        ]
                                    },
                                    {
                                        "key": "Request Date",
                                        "dateValue": "={{ new Date().toISOString().split('T')[0] }}"
                                    },
                                    {
                                        "key": "Status",
                                        "selectValue": "Sent"
                                    },
                                    {
                                        "key": "Projects Count",
                                        "numberValue": "={{ $json.projects.length }}"
                                    }
                                ]
                            }
                        },
                        "id": "log-request",
                        "name": "Log Update Request in Notion",
                        "type": "n8n-nodes-base.notion",
                        "typeVersion": 2,
                        "position": [1340, 300]
                    },
                    {
                        "parameters": {
                            "authentication": "oAuth2",
                            "pollTimes": {
                                "item": [
                                    {
                                        "mode": "everyMinute",
                                        "minute": 5
                                    }
                                ]
                            },
                            "filters": {
                                "subject": "Re: Weekly Project Update Request"
                            },
                            "format": "resolved",
                            "options": {
                                "allowUnauthorizedCerts": false,
                                "includeAttachments": false
                            }
                        },
                        "id": "email-trigger",
                        "name": "Monitor Email Responses",
                        "type": "n8n-nodes-base.gmailTrigger",
                        "typeVersion": 1,
                        "position": [240, 600]
                    },
                    {
                        "parameters": {
                            "jsCode": "// Parse email content and extract project updates\nconst emailBody = $json.textPlain || $json.textHtml || '';\nconst senderEmail = $json.from.address;\nconst subject = $json.subject;\n\n// Extract request ID from original email if available\nconst requestIdMatch = emailBody.match(/Request ID: UPDATE-([^-]+)-([0-9-]+)/);\nconst workerId = requestIdMatch ? requestIdMatch[1] : null;\n\n// Parse project updates using regex patterns\nconst projectUpdates = [];\nconst projectBlocks = emailBody.split(/(?=Project Name:|📋)/i).slice(1);\n\nfor (const block of projectBlocks) {\n  const update = {};\n  \n  // Extract project information\n  const nameMatch = block.match(/Project Name:\\s*(.+?)(?=\\n|Progress:|$)/i);\n  const progressMatch = block.match(/Progress:\\s*(.+?)(?=\\n|Current Status:|$)/i);\n  const statusMatch = block.match(/Current Status:\\s*(.+?)(?=\\n|Next Steps:|$)/i);\n  const nextStepsMatch = block.match(/Next Steps:\\s*(.+?)(?=\\n|Blockers:|$)/i);\n  const blockersMatch = block.match(/Blockers:\\s*(.+?)(?=\\n|Completion|$)/i);\n  const completionMatch = block.match(/Completion.*?([0-9]+)%/i);\n  \n  if (nameMatch) {\n    update.projectName = nameMatch[1].trim();\n    update.progress = progressMatch ? progressMatch[1].trim() : '';\n    update.status = statusMatch ? statusMatch[1].trim() : 'Unknown';\n    update.nextSteps = nextStepsMatch ? nextStepsMatch[1].trim() : '';\n    update.blockers = blockersMatch ? blockersMatch[1].trim() : 'None';\n    update.completionPercentage = completionMatch ? parseInt(completionMatch[1]) : 0;\n    \n    projectUpdates.push(update);\n  }\n}\n\nreturn [{\n  json: {\n    senderEmail,\n    workerId,\n    receivedAt: new Date().toISOString(),\n    originalSubject: subject,\n    projectUpdates,\n    rawContent: emailBody.substring(0, 1000) // Keep first 1000 chars for reference\n  }\n}];"
                        },
                        "id": "parse-email",
                        "name": "Parse Email Response",
                        "type": "n8n-nodes-base.code",
                        "typeVersion": 2,
                        "position": [460, 600]
                    },
                    {
                        "parameters": {
                            "authentication": "oAuth2",
                            "resource": "database",
                            "operation": "getAll",
                            "databaseId": "={{ $env.NOTION_PROJECTS_DB_ID }}",
                            "options": {
                                "filter": {
                                    "filters": [
                                        {
                                            "property": "Name",
                                            "rich_text": {
                                                "contains": "={{ $json.projectUpdates[0].projectName }}"
                                            }
                                        }
                                    ]
                                }
                            }
                        },
                        "id": "find-project",
                        "name": "Find Project in Notion",
                        "type": "n8n-nodes-base.notion",
                        "typeVersion": 2,
                        "position": [680, 600]
                    },
                    {
                        "parameters": {
                            "jsCode": "// Process each project update\nconst emailData = $input.first().json;\nconst projectResults = $input.all().slice(1);\n\nconst updates = [];\n\nfor (let i = 0; i < emailData.projectUpdates.length; i++) {\n  const update = emailData.projectUpdates[i];\n  const projectResult = projectResults[i]?.json?.results?.[0];\n  \n  if (projectResult) {\n    updates.push({\n      projectId: projectResult.id,\n      projectName: update.projectName,\n      progress: update.progress,\n      status: update.status,\n      nextSteps: update.nextSteps,\n      blockers: update.blockers,\n      completionPercentage: update.completionPercentage,\n      updatedBy: emailData.senderEmail,\n      updatedAt: emailData.receivedAt\n    });\n  }\n}\n\nreturn updates.map(update => ({ json: update }));"
                        },
                        "id": "prepare-updates",
                        "name": "Prepare Project Updates",
                        "type": "n8n-nodes-base.code",
                        "typeVersion": 2,
                        "position": [900, 600]
                    },
                    {
                        "parameters": {
                            "authentication": "oAuth2",
                            "resource": "page",
                            "operation": "update",
                            "pageId": "={{ $json.projectId }}",
                            "propertiesUi": {
                                "propertyValues": [
                                    {
                                        "key": "Status",
                                        "selectValue": "={{ $json.status }}"
                                    },
                                    {
                                        "key": "Progress %",
                                        "numberValue": "={{ $json.completionPercentage }}"
                                    },
                                    {
                                        "key": "Last Updated",
                                        "dateValue": "={{ $json.updatedAt.split('T')[0] }}"
                                    },
                                    {
                                        "key": "Current Blockers",
                                        "richTextValue": "={{ $json.blockers }}"
                                    },
                                    {
                                        "key": "Next Steps",
                                        "richTextValue": "={{ $json.nextSteps }}"
                                    }
                                ]
                            }
                        },
                        "id": "update-project",
                        "name": "Update Project in Notion",
                        "type": "n8n-nodes-base.notion",
                        "typeVersion": 2,
                        "position": [1120, 600]
                    },
                    {
                        "parameters": {
                            "authentication": "oAuth2",
                            "resource": "database",
                            "operation": "create",
                            "databaseId": "={{ $env.NOTION_UPDATE_LOGS_DB_ID }}",
                            "title": "Update: {{ $json.projectName }} - {{ new Date($json.updatedAt).toLocaleDateString() }}",
                            "propertiesUi": {
                                "propertyValues": [
                                    {
                                        "key": "Project",
                                        "relationValue": [
                                            "={{ $json.projectId }}"
                                        ]
                                    },
                                    {
                                        "key": "Update Date",
                                        "dateValue": "={{ $json.updatedAt.split('T')[0] }}"
                                    },
                                    {
                                        "key": "Progress Description",
                                        "richTextValue": "={{ $json.progress }}"
                                    },
                                    {
                                        "key": "Status",
                                        "selectValue": "={{ $json.status }}"
                                    },
                                    {
                                        "key": "Completion %",
                                        "numberValue": "={{ $json.completionPercentage }}"
                                    },
                                    {
                                        "key": "Blockers",
                                        "richTextValue": "={{ $json.blockers }}"
                                    },
                                    {
                                        "key": "Next Steps",
                                        "richTextValue": "={{ $json.nextSteps }}"
                                    },
                                    {
                                        "key": "Updated By Email",
                                        "emailValue": "={{ $json.updatedBy }}"
                                    }
                                ]
                            }
                        },
                        "id": "create-update-log",
                        "name": "Create Update Log Entry",
                        "type": "n8n-nodes-base.notion",
                        "typeVersion": 2,
                        "position": [1340, 600]
                    },
                    {
                        "parameters": {
                            "authentication": "oAuth2",
                            "sendTo": "={{ $json.updatedBy }}",
                            "subject": "✅ Project Update Received - Thank You!",
                            "emailType": "html",
                            "message": "<!DOCTYPE html>\n<html>\n<head>\n    <style>\n        body { font-family: Arial, sans-serif; line-height: 1.6; color: #333; }\n        .header { background-color: #4CAF50; color: white; padding: 20px; text-align: center; }\n        .content { padding: 20px; }\n        .success { background-color: #d4edda; padding: 15px; border-radius: 5px; margin: 15px 0; }\n    </style>\n</head>\n<body>\n    <div class=\"header\">\n        <h2>✅ Update Received Successfully</h2>\n    </div>\n    \n    <div class=\"content\">\n        <div class=\"success\">\n            <p><strong>Thank you for your project update!</strong></p>\n            <p>We've successfully received and processed your update for: <strong>{{ $json.projectName }}</strong></p>\n        </div>\n        \n        <p>Your update has been automatically synced to our project management system. The team leads will review your progress and reach out if any follow-up is needed.</p>\n        \n        <p>Keep up the great work! 🚀</p>\n        \n        <p>Best regards,<br>Project Management Team</p>\n    </div>\n</body>\n</html>"
                        },
                        "id": "send-confirmation",
                        "name": "Send Confirmation Email",
                        "type": "n8n-nodes-base.gmail",
                        "typeVersion": 1,
                        "position": [1560, 600]
                    }
                ],
                "connections": {
                    "Weekly Schedule Trigger": {
                        "main": [
                            [
                                {
                                    "node": "Get Active Workers from Notion",
                                    "type": "main",
                                    "index": 0
                                }
                            ]
                        ]
                    },
                    "Get Active Workers from Notion": {
                        "main": [
                            [
                                {
                                    "node": "Get Active Projects",
                                    "type": "main",
                                    "index": 0
                                }
                            ]
                        ]
                    },
                    "Get Active Projects": {
                        "main": [
                            [
                                {
                                    "node": "Process Worker-Project Data",
                                    "type": "main",
                                    "index": 0
                                }
                            ]
                        ]
                    },
                    "Process Worker-Project Data": {
                        "main": [
                            [
                                {
                                    "node": "Send Update Request Email",
                                    "type": "main",
                                    "index": 0
                                }
                            ]
                        ]
                    },
                    "Send Update Request Email": {
                        "main": [
                            [
                                {
                                    "node": "Log Update Request in Notion",
                                    "type": "main",
                                    "index": 0
                                }
                            ]
                        ]
                    },
                    "Monitor Email Responses": {
                        "main": [
                            [
                                {
                                    "node": "Parse Email Response",
                                    "type": "main",
                                    "index": 0
                                }
                            ]
                        ]
                    },
                    "Parse Email Response": {
                        "main": [
                            [
                                {
                                    "node": "Find Project in Notion",
                                    "type": "main",
                                    "index": 0
                                }
                            ]
                        ]
                    },
                    "Find Project in Notion": {
                        "main": [
                            [
                                {
                                    "node": "Prepare Project Updates",
                                    "type": "main",
                                    "index": 0
                                }
                            ]
                        ]
                    },
                    "Prepare Project Updates": {
                        "main": [
                            [
                                {
                                    "node": "Update Project in Notion",
                                    "type": "main",
                                    "index": 0
                                }
                            ]
                        ]
                    },
                    "Update Project in Notion": {
                        "main": [
                            [
                                {
                                    "node": "Create Update Log Entry",
                                    "type": "main",
                                    "index": 0
                                }
                            ]
                        ]
                    },
                    "Create Update Log Entry": {
                        "main": [
                            [
                                {
                                    "node": "Send Confirmation Email",
                                    "type": "main",
                                    "index": 0
                                }
                            ]
                        ]
                    }
                },
                "settings": {
                    "executionOrder": "v1"
                },
                "active": False,
                "versionId": "1",
                "meta": {
                    "templateCredsSetupCompleted": False
                },
                "tags": []
            }
        else:
            return {
                "id": str(uuid.uuid4()),
                "name": task['task_name'],
                "nodes": [
                    {
                        "id": str(uuid.uuid4()),
                        "name": "Start",
                        "type": "n8n-nodes-base.start",
                        "typeVersion": 1,
                        "position": [240, 300],
                        "parameters": {}
                    },
                    {
                        "id": str(uuid.uuid4()),
                        "name": "HTTP Request",
                        "type": "n8n-nodes-base.httpRequest",
                        "typeVersion": 1,
                        "position": [460, 300],
                        "parameters": {
                            "url": "https://api.example.com/data",
                            "method": "GET"
                        }
                    },
                    {
                        "id": str(uuid.uuid4()),
                        "name": "Send Email",
                        "type": "n8n-nodes-base.emailSend",
                        "typeVersion": 1,
                        "position": [680, 300],
                        "parameters": {
                            "to": "recipient@example.com",
                            "subject": "Task Update",
                            "text": "Task has been completed"
                        }
                    }
                ],
                "connections": {
                    "Start": {
                        "main": [
                            [
                                {
                                    "node": "HTTP Request",
                                    "type": "main",
                                    "index": 0
                                }
                            ]
                        ]
                    },
                    "HTTP Request": {
                        "main": [
                            [
                                {
                                    "node": "Send Email",
                                    "type": "main",
                                    "index": 0
                                }
                            ]
                        ]
                    }
                },
                "active": False,
                "settings": {
                    "executionOrder": "v1"
                },
                "versionId": "1",
                "meta": {
                    "templateCredsSetupCompleted": False
                },
                "tags": []
            } 