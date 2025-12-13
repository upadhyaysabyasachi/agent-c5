"""OPT Deployment Tool - Provides deployment instructions and setup."""

from typing import Dict, List, Any
import os


class DeploymentTool:
    """Tool for generating deployment instructions."""
    
    @staticmethod
    def generate_deployment_instructions(
        script_path: str,
        dependencies: List[str],
        schedule: str = None
    ) -> Dict[str, Any]:
        """
        Generate deployment instructions for the automation script.
        
        Args:
            script_path: Path to the generated script
            dependencies: List of required dependencies
            schedule: Optional scheduling information (cron format or description)
            
        Returns:
            Deployment instructions dictionary
        """
        instructions = {
            "script_path": script_path,
            "dependencies": dependencies,
            "setup_steps": [
                "1. Install Python 3.8 or higher",
                "2. Install required dependencies",
                "3. Set up environment variables",
                "4. Test the script manually",
                "5. Set up scheduling (if needed)"
            ],
            "environment_setup": DeploymentTool._generate_env_setup(),
            "dependency_installation": DeploymentTool._generate_dependency_commands(dependencies),
            "scheduling": DeploymentTool._generate_scheduling_info(schedule),
            "monitoring": DeploymentTool._generate_monitoring_info()
        }
        
        return instructions
    
    @staticmethod
    def _generate_env_setup() -> str:
        """Generate environment variable setup instructions."""
        return """
# Create a .env file in the script directory
# Add your API keys and credentials:

# Example:
# API_KEY=your_api_key_here
# EMAIL_PASSWORD=your_email_password
# DATABASE_URL=your_database_url
        """
    
    @staticmethod
    def _generate_dependency_commands(dependencies: List[str]) -> str:
        """Generate pip install commands."""
        if not dependencies:
            return "pip install -r requirements.txt"
        
        # Filter out standard library modules
        external_deps = [dep for dep in dependencies if dep not in [
            "os", "sys", "json", "datetime", "typing", "pathlib"
        ]]
        
        if external_deps:
            return f"pip install {' '.join(external_deps)}"
        return "No external dependencies required"
    
    @staticmethod
    def _generate_scheduling_info(schedule: str = None) -> str:
        """Generate scheduling information."""
        if not schedule:
            return """
# Manual Execution:
python script_name.py

# For automated scheduling, use cron (Linux/Mac) or Task Scheduler (Windows):

# Linux/Mac Cron Example (runs daily at 9 AM):
# 0 9 * * * /usr/bin/python3 /path/to/script_name.py

# Windows Task Scheduler:
# Create a new task that runs python.exe with the script path
            """
        
        return f"""
# Scheduled to run: {schedule}

# Add to crontab (Linux/Mac):
# Edit crontab: crontab -e
# Add line with appropriate schedule

# Or use Windows Task Scheduler with the specified schedule
        """
    
    @staticmethod
    def _generate_monitoring_info() -> str:
        """Generate monitoring and logging information."""
        return """
# Monitoring Recommendations:

1. Add logging to track script execution:
   import logging
   logging.basicConfig(filename='automation.log', level=logging.INFO)

2. Set up error notifications (email/Slack) for failures

3. Monitor script execution time and resource usage

4. Set up alerts for critical failures
        """
    
    @staticmethod
    def format_deployment_instructions(instructions: Dict[str, Any]) -> str:
        """
        Format deployment instructions for display.
        
        Args:
            instructions: Deployment instructions dictionary
            
        Returns:
            Formatted string
        """
        formatted = "# 🚀 Deployment Instructions\n\n"
        formatted += f"**Script**: `{instructions['script_path']}`\n\n"
        
        formatted += "## Setup Steps\n\n"
        for step in instructions['setup_steps']:
            formatted += f"{step}\n"
        formatted += "\n"
        
        formatted += "## Environment Setup\n\n"
        formatted += "```bash\n"
        formatted += instructions['environment_setup']
        formatted += "\n```\n\n"
        
        formatted += "## Install Dependencies\n\n"
        formatted += "```bash\n"
        formatted += f"{instructions['dependency_installation']}\n"
        formatted += "```\n\n"
        
        formatted += "## Scheduling\n\n"
        formatted += "```bash\n"
        formatted += instructions['scheduling']
        formatted += "\n```\n\n"
        
        formatted += "## Monitoring\n\n"
        formatted += "```python\n"
        formatted += instructions['monitoring']
        formatted += "\n```\n"
        
        return formatted
    
    @staticmethod
    def create_requirements_file(dependencies: List[str], output_path: str = "requirements.txt"):
        """
        Create a requirements.txt file with dependencies.
        
        Args:
            dependencies: List of dependency names
            output_path: Path to save requirements.txt
        """
        # Filter out standard library modules
        external_deps = [dep for dep in dependencies if dep not in [
            "os", "sys", "json", "datetime", "typing", "pathlib", "logging"
        ]]
        
        with open(output_path, "w") as f:
            for dep in external_deps:
                f.write(f"{dep}\n")
        
        return output_path

