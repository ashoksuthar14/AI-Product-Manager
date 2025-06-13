from app import db
from datetime import datetime
import json

class Project(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    status = db.Column(db.String(20), default='pending')  # pending, analyzing, completed
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    
    # Project requirements and constraints
    requirements = db.Column(db.Text)
    constraints = db.Column(db.Text)
    timeline = db.Column(db.String(100))
    budget = db.Column(db.String(100))
    
    # Complete analysis results (JSON)
    analysis = db.Column(db.Text)  # Stores complete collaborative analysis as JSON
    conversation_log = db.Column(db.Text)  # Stores agent conversation log
    
    # Legacy agent analysis results (kept for compatibility)
    product_manager_analysis = db.Column(db.Text)
    developer_analysis = db.Column(db.Text)
    qa_analysis = db.Column(db.Text)
    ai_engineer_analysis = db.Column(db.Text)
    devops_analysis = db.Column(db.Text)
    ux_designer_analysis = db.Column(db.Text)
    business_analyst_analysis = db.Column(db.Text)
    
    # Final recommendations
    final_recommendations = db.Column(db.Text)
    risk_assessment = db.Column(db.Text)
    implementation_plan = db.Column(db.Text)

    def __repr__(self):
        return f'<Project {self.title}>'

    def get_analysis(self):
        """Get parsed analysis results."""
        if self.analysis:
            try:
                return json.loads(self.analysis)
            except:
                return None
        return None

    def set_analysis(self, analysis_data):
        """Set analysis results as JSON."""
        if analysis_data:
            self.analysis = json.dumps(analysis_data, default=str)
        else:
            self.analysis = None

    def has_analysis(self):
        """Check if project has been analyzed."""
        return self.analysis is not None and self.status == 'completed'

    def get_analysis_summary(self):
        """Get a summary of the analysis for display."""
        analysis_data = self.get_analysis()
        if not analysis_data:
            return None
        
        return {
            'pm_overview': analysis_data.get('pm_overview', 'No overview available'),
            'product_management': analysis_data.get('product_management', {}),
            'technical_development': analysis_data.get('technical_development', {}),
            'quality_assurance': analysis_data.get('quality_assurance', {}),
            'ai_engineering': analysis_data.get('ai_engineering', {}),
            'conversation_log': analysis_data.get('conversation_log', [])
        }

    def to_dict(self):
        return {
            'id': self.id,
            'title': self.title,
            'description': self.description,
            'status': self.status,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat(),
            'requirements': self.requirements,
            'constraints': self.constraints,
            'timeline': self.timeline,
            'budget': self.budget,
            'has_analysis': self.has_analysis()
        } 