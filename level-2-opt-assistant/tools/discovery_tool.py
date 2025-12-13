"""OPT Discovery Tool - Gathers business context using structured questions."""

from typing import Dict, List, Any
import json


class DiscoveryTool:
    """Tool for conducting OPT discovery phase."""
    
    DISCOVERY_QUESTIONS = [
        {
            "category": "Operating Model",
            "questions": [
                "What is your primary business or role?",
                "How do you currently make money or deliver value?",
                "What is your typical workday/week structure?",
                "Who are your main customers or stakeholders?",
            ]
        },
        {
            "category": "Processes",
            "questions": [
                "What are your main workflows or processes?",
                "Which processes take up most of your time?",
                "What processes do you find repetitive or tedious?",
                "Are there any processes that require multiple tools or manual steps?",
            ]
        },
        {
            "category": "Tasks",
            "questions": [
                "What specific tasks do you do daily/weekly?",
                "Which tasks are most time-consuming?",
                "What tasks involve copying data between systems?",
                "What tasks require you to check multiple sources?",
            ]
        }
    ]
    
    @staticmethod
    def get_next_question(context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Determine the next discovery question based on current context.
        
        Args:
            context: Current OPT data context
            
        Returns:
            Dictionary with question category and question text
        """
        # Check what's missing in context
        if not context.get("operating_model"):
            return {
                "category": "Operating Model",
                "question": DiscoveryTool.DISCOVERY_QUESTIONS[0]["questions"][0],
                "priority": "high"
            }
        
        if not context.get("processes") or len(context.get("processes", [])) < 2:
            return {
                "category": "Processes",
                "question": DiscoveryTool.DISCOVERY_QUESTIONS[1]["questions"][0],
                "priority": "high"
            }
        
        if not context.get("tasks") or len(context.get("tasks", [])) < 3:
            return {
                "category": "Tasks",
                "question": DiscoveryTool.DISCOVERY_QUESTIONS[2]["questions"][0],
                "priority": "high"
            }
        
        # If we have basic info, dig deeper
        return {
            "category": "Deep Dive",
            "question": "Can you tell me more about any pain points or bottlenecks in your current workflow?",
            "priority": "medium"
        }
    
    @staticmethod
    def extract_opt_data(user_response: str, current_context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Extract OPT data from user response.
        
        Args:
            user_response: User's response to discovery question
            current_context: Current OPT context
            
        Returns:
            Updated OPT data dictionary
        """
        updated = current_context.copy()
        
        # Simple extraction logic (in production, use LLM for better extraction)
        response_lower = user_response.lower()
        
        # Extract operating model keywords
        if not updated.get("operating_model"):
            if any(word in response_lower for word in ["business", "company", "work", "role", "job"]):
                # Store a summary
                updated["operating_model"] = user_response[:200]
        
        # Extract processes (look for workflow indicators)
        if "process" in response_lower or "workflow" in response_lower:
            if "processes" not in updated:
                updated["processes"] = []
            # Simple extraction - in production, use NLP
            updated["processes"].append(user_response[:100])
        
        # Extract tasks (look for action verbs)
        action_verbs = ["create", "send", "update", "check", "download", "upload", "process"]
        if any(verb in response_lower for verb in action_verbs):
            if "tasks" not in updated:
                updated["tasks"] = []
            updated["tasks"].append(user_response[:100])
        
        return updated
    
    @staticmethod
    def is_discovery_complete(context: Dict[str, Any]) -> bool:
        """
        Check if discovery phase has gathered sufficient information.
        
        Args:
            context: Current OPT context
            
        Returns:
            True if discovery is complete
        """
        has_operating_model = bool(context.get("operating_model"))
        has_processes = len(context.get("processes", [])) >= 2
        has_tasks = len(context.get("tasks", [])) >= 3
        
        return has_operating_model and has_processes and has_tasks

