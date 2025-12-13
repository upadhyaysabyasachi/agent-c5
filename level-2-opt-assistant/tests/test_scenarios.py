"""Integration tests for complete OPT scenarios."""

import unittest
from memory.conversation_memory import ConversationMemory
from tools.discovery_tool import DiscoveryTool
from tools.analysis_tool import AnalysisTool
from tools.masterplan_tool import MasterplanTool


class TestOPTScenarios(unittest.TestCase):
    """Test complete OPT workflow scenarios."""
    
    def test_complete_discovery_workflow(self):
        """Test complete discovery phase workflow."""
        memory = ConversationMemory()
        
        # Simulate discovery conversation
        responses = [
            "I run a newsletter for dog owners",
            "I create content, send emails, and manage subscribers",
            "I write articles daily, send weekly newsletters, update subscriber lists"
        ]
        
        for response in responses:
            memory.opt_data = DiscoveryTool.extract_opt_data(response, memory.opt_data)
            memory.add_message("user", response)
        
        # Check if discovery is complete
        is_complete = DiscoveryTool.is_discovery_complete(memory.opt_data)
        
        # Should have enough info after these responses
        self.assertTrue(is_complete or len(memory.opt_data.get("tasks", [])) > 0)
    
    def test_analysis_workflow(self):
        """Test analysis phase workflow."""
        opt_data = {
            "operating_model": "Newsletter business",
            "processes": ["Content creation", "Email marketing"],
            "tasks": [
                "Write articles daily",
                "Send weekly newsletters",
                "Update subscriber lists manually",
                "Format email content"
            ]
        }
        
        suggestions = AnalysisTool.analyze_tasks(opt_data)
        
        self.assertIsInstance(suggestions, list)
        # Should find some automation opportunities
        self.assertGreater(len(suggestions), 0)
    
    def test_masterplan_generation_workflow(self):
        """Test masterplan generation for selected task."""
        opt_data = {
            "operating_model": "Content creator",
            "processes": ["Email marketing"],
            "tasks": ["Send weekly newsletters"]
        }
        
        selected_task = "Automate weekly newsletter sending"
        masterplan = MasterplanTool.generate_masterplan(opt_data, selected_task)
        
        self.assertEqual(masterplan["task"], selected_task)
        self.assertIn("phases", masterplan)
        self.assertIn("dependencies", masterplan)
    
    def test_end_to_end_workflow(self):
        """Test complete end-to-end OPT workflow."""
        # Step 1: Discovery
        memory = ConversationMemory()
        memory.opt_data = {
            "operating_model": "E-commerce store owner",
            "processes": ["Order processing", "Inventory management"],
            "tasks": [
                "Process orders manually",
                "Update inventory spreadsheets",
                "Send order confirmations"
            ]
        }
        
        # Step 2: Analysis
        suggestions = AnalysisTool.analyze_tasks(memory.opt_data)
        self.assertGreater(len(suggestions), 0)
        
        # Step 3: Masterplan
        if suggestions:
            selected_task = suggestions[0]["task"]
            masterplan = MasterplanTool.generate_masterplan(memory.opt_data, selected_task)
            self.assertIsNotNone(masterplan)
    
    def test_phase_transitions(self):
        """Test phase transition logic."""
        memory = ConversationMemory()
        
        # Start in DISCOVERY
        self.assertEqual(memory.current_phase, "DISCOVERY")
        
        # Complete discovery
        memory.opt_data = {
            "operating_model": "Business owner",
            "processes": ["Process 1", "Process 2"],
            "tasks": ["Task 1", "Task 2", "Task 3"]
        }
        
        # Transition to ANALYSIS
        memory.update_phase("ANALYSIS")
        self.assertEqual(memory.current_phase, "ANALYSIS")
        
        # Transition to CODE
        memory.update_phase("CODE")
        self.assertEqual(memory.current_phase, "CODE")


if __name__ == "__main__":
    unittest.main()

