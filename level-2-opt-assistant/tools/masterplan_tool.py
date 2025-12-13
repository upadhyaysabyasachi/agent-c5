"""OPT Masterplan Tool - Creates comprehensive automation roadmap."""

from typing import Dict, List, Any
from datetime import datetime


class MasterplanTool:
    """Tool for generating master automation plans."""
    
    @staticmethod
    def generate_masterplan(opt_data: Dict[str, Any], selected_task: str) -> Dict[str, Any]:
        """
        Generate a comprehensive masterplan for the selected automation.
        
        Args:
            opt_data: Complete OPT data structure
            selected_task: The task selected for automation
            
        Returns:
            Masterplan dictionary with phases and steps
        """
        masterplan = {
            "task": selected_task,
            "created_at": datetime.now().isoformat(),
            "phases": [
                {
                    "phase": "Planning",
                    "steps": [
                        "Define automation scope and requirements",
                        "Identify required APIs, tools, and libraries",
                        "Design data flow and error handling",
                        "Set up development environment"
                    ],
                    "estimated_time": "1-2 hours"
                },
                {
                    "phase": "Development",
                    "steps": [
                        "Set up project structure",
                        "Implement core functionality",
                        "Add error handling and logging",
                        "Write unit tests"
                    ],
                    "estimated_time": "2-4 hours"
                },
                {
                    "phase": "Testing",
                    "steps": [
                        "Test with sample data",
                        "Validate edge cases",
                        "Test error scenarios",
                        "Performance testing"
                    ],
                    "estimated_time": "1-2 hours"
                },
                {
                    "phase": "Deployment",
                    "steps": [
                        "Document usage instructions",
                        "Set up scheduling (if needed)",
                        "Configure environment variables",
                        "Deploy to production environment"
                    ],
                    "estimated_time": "1 hour"
                }
            ],
            "total_estimated_time": "5-9 hours",
            "dependencies": MasterplanTool._identify_dependencies(selected_task),
            "risks": MasterplanTool._identify_risks(selected_task)
        }
        
        return masterplan
    
    @staticmethod
    def _identify_dependencies(task: str) -> List[str]:
        """
        Identify dependencies for the automation task.
        
        Args:
            task: Task description
            
        Returns:
            List of dependencies
        """
        dependencies = []
        task_lower = task.lower()
        
        if "email" in task_lower:
            dependencies.append("Email API credentials (SMTP or service API key)")
        if "api" in task_lower or "webhook" in task_lower:
            dependencies.append("API credentials and documentation")
        if "data" in task_lower or "spreadsheet" in task_lower:
            dependencies.append("Data source access and format specifications")
        if "file" in task_lower:
            dependencies.append("File system access and permissions")
        
        # Always need Python environment
        dependencies.append("Python 3.8+ with required libraries")
        
        return dependencies
    
    @staticmethod
    def _identify_risks(task: str) -> List[str]:
        """
        Identify potential risks for the automation.
        
        Args:
            task: Task description
            
        Returns:
            List of risks
        """
        risks = []
        task_lower = task.lower()
        
        if "api" in task_lower:
            risks.append("API rate limits or changes")
        if "data" in task_lower:
            risks.append("Data format changes")
        if "email" in task_lower:
            risks.append("Email service provider limitations")
        
        risks.append("Error handling for edge cases")
        risks.append("Maintenance requirements as systems evolve")
        
        return risks
    
    @staticmethod
    def format_masterplan(masterplan: Dict[str, Any]) -> str:
        """
        Format masterplan for display.
        
        Args:
            masterplan: Masterplan dictionary
            
        Returns:
            Formatted string
        """
        formatted = f"# 📋 Masterplan: {masterplan['task']}\n\n"
        formatted += f"**Created**: {masterplan['created_at']}\n\n"
        
        formatted += "## Phases\n\n"
        for phase in masterplan['phases']:
            formatted += f"### {phase['phase']} ({phase['estimated_time']})\n\n"
            for i, step in enumerate(phase['steps'], 1):
                formatted += f"{i}. {step}\n"
            formatted += "\n"
        
        formatted += f"**Total Estimated Time**: {masterplan['total_estimated_time']}\n\n"
        
        if masterplan.get('dependencies'):
            formatted += "## Dependencies\n\n"
            for dep in masterplan['dependencies']:
                formatted += f"- {dep}\n"
            formatted += "\n"
        
        if masterplan.get('risks'):
            formatted += "## Potential Risks\n\n"
            for risk in masterplan['risks']:
                formatted += f"- ⚠️ {risk}\n"
            formatted += "\n"
        
        return formatted

