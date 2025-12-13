import json
from datetime import datetime
from typing import Dict, List, Any

class ConversationMemory:
    def __init__(self):
        # State Tracking
        self.current_phase = "DISCOVERY"  # DISCOVERY, ANALYSIS, PLAN, CODE
        
        # Structured Data (The "Context" we are building)
        self.opt_data = {
            "operating_model": None,  # e.g., "Solo content creator"
            "processes": [],          # e.g., ["Video editing", "Email marketing"]
            "tasks": []               # e.g., ["Download raw footage", "Upload to YT"]
        }
        
        # Conversation History
        self.history: List[Dict[str, str]] = []
        
    def update_phase(self, new_phase: str):
        self.current_phase = new_phase
        print(f"🔄 Phase Transition: -> {new_phase}")

    def save_context(self, key: str, value: Any):
        """Updates specific parts of the OPT data."""
        if key in self.opt_data:
            self.opt_data[key] = value
        
    def add_message(self, role: str, content: str):
        self.history.append({
            "role": role, 
            "content": content,
            "timestamp": datetime.now().isoformat()
        })
    
    def get_history_str(self) -> str:
        return "\n".join([f"{m['role'].upper()}: {m['content']}" for m in self.history[-10:]])