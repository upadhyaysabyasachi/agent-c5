"""OPT Analysis Tool - Analyzes tasks and suggests automation opportunities."""

from typing import Dict, List, Any
from datetime import datetime


class AnalysisTool:
    """Tool for analyzing tasks and suggesting automations."""
    
    @staticmethod
    def analyze_tasks(opt_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Analyze tasks and identify automation opportunities.
        
        Args:
            opt_data: Complete OPT data structure
            
        Returns:
            List of automation suggestions with ROI estimates
        """
        suggestions = []
        tasks = opt_data.get("tasks", [])
        processes = opt_data.get("processes", [])
        
        # Analyze each task for automation potential
        for task in tasks:
            automation_score = AnalysisTool._calculate_automation_score(task)
            
            if automation_score >= 0.6:  # High automation potential
                suggestion = {
                    "task": task,
                    "automation_score": automation_score,
                    "estimated_time_saved": AnalysisTool._estimate_time_saved(task),
                    "complexity": AnalysisTool._estimate_complexity(task),
                    "priority": "high" if automation_score >= 0.8 else "medium",
                    "suggested_approach": AnalysisTool._suggest_approach(task)
                }
                suggestions.append(suggestion)
        
        # Sort by automation score (highest first)
        suggestions.sort(key=lambda x: x["automation_score"], reverse=True)
        
        return suggestions[:3]  # Return top 3 suggestions
    
    @staticmethod
    def _calculate_automation_score(task: str) -> float:
        """
        Calculate automation potential score (0.0 to 1.0).
        
        Args:
            task: Task description
            
        Returns:
            Automation score
        """
        task_lower = task.lower()
        score = 0.0
        
        # Repetitive keywords
        repetitive_keywords = ["daily", "weekly", "every", "repeat", "always", "routine"]
        if any(keyword in task_lower for keyword in repetitive_keywords):
            score += 0.3
        
        # Data manipulation keywords
        data_keywords = ["copy", "transfer", "update", "sync", "extract", "import", "export"]
        if any(keyword in task_lower for keyword in data_keywords):
            score += 0.3
        
        # Manual work keywords
        manual_keywords = ["manually", "by hand", "check", "verify", "format"]
        if any(keyword in task_lower for keyword in manual_keywords):
            score += 0.2
        
        # API/integration keywords (easier to automate)
        api_keywords = ["api", "webhook", "integration", "connect"]
        if any(keyword in task_lower for keyword in api_keywords):
            score += 0.2
        
        return min(score, 1.0)
    
    @staticmethod
    def _estimate_time_saved(task: str) -> str:
        """
        Estimate time saved per automation.
        
        Args:
            task: Task description
            
        Returns:
            Time estimate string
        """
        task_lower = task.lower()
        
        if "daily" in task_lower:
            return "30-60 minutes/day"
        elif "weekly" in task_lower:
            return "2-4 hours/week"
        elif "monthly" in task_lower:
            return "4-8 hours/month"
        else:
            return "1-2 hours per execution"
    
    @staticmethod
    def _estimate_complexity(task: str) -> str:
        """
        Estimate implementation complexity.
        
        Args:
            task: Task description
            
        Returns:
            Complexity level
        """
        task_lower = task.lower()
        
        simple_keywords = ["copy", "move", "format", "send"]
        medium_keywords = ["extract", "transform", "sync", "update"]
        complex_keywords = ["analyze", "integrate", "process", "generate"]
        
        if any(keyword in task_lower for keyword in simple_keywords):
            return "Low"
        elif any(keyword in task_lower for keyword in complex_keywords):
            return "High"
        else:
            return "Medium"
    
    @staticmethod
    def _suggest_approach(task: str) -> str:
        """
        Suggest automation approach.
        
        Args:
            task: Task description
            
        Returns:
            Suggested approach description
        """
        task_lower = task.lower()
        
        if "email" in task_lower:
            return "Python script with SMTP or API integration"
        elif "data" in task_lower or "spreadsheet" in task_lower:
            return "Python script with pandas/openpyxl for data manipulation"
        elif "api" in task_lower or "webhook" in task_lower:
            return "Python script with requests library for API calls"
        elif "file" in task_lower:
            return "Python script with file system operations"
        else:
            return "Python script with appropriate libraries based on requirements"
    
    @staticmethod
    def format_suggestions(suggestions: List[Dict[str, Any]]) -> str:
        """
        Format automation suggestions for display.
        
        Args:
            suggestions: List of automation suggestions
            
        Returns:
            Formatted string for display
        """
        if not suggestions:
            return "No high-value automation opportunities found at this time."
        
        formatted = "## 🎯 Automation Opportunities\n\n"
        
        for i, suggestion in enumerate(suggestions, 1):
            formatted += f"### Option {i}: {suggestion['task'][:60]}...\n\n"
            formatted += f"- **Automation Score**: {suggestion['automation_score']:.0%}\n"
            formatted += f"- **Time Saved**: {suggestion['estimated_time_saved']}\n"
            formatted += f"- **Complexity**: {suggestion['complexity']}\n"
            formatted += f"- **Approach**: {suggestion['suggested_approach']}\n\n"
        
        formatted += "Which automation would you like to build first?"
        
        return formatted

