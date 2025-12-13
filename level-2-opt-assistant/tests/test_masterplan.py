"""Tests for Masterplan Tool."""

import unittest
from tools.masterplan_tool import MasterplanTool


class TestMasterplanTool(unittest.TestCase):
    """Test cases for MasterplanTool."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.opt_data = {
            "operating_model": "Content creator",
            "processes": ["Video editing", "Social media"],
            "tasks": ["Download footage", "Edit video", "Upload to YouTube"]
        }
        
        self.test_task = "Automate video upload to YouTube"
    
    def test_generate_masterplan(self):
        """Test masterplan generation."""
        masterplan = MasterplanTool.generate_masterplan(self.opt_data, self.test_task)
        
        self.assertIn("phases", masterplan)
        self.assertIn("task", masterplan)
        self.assertIn("dependencies", masterplan)
        self.assertIn("risks", masterplan)
        self.assertEqual(masterplan["task"], self.test_task)
    
    def test_masterplan_has_phases(self):
        """Test that masterplan includes all required phases."""
        masterplan = MasterplanTool.generate_masterplan(self.opt_data, self.test_task)
        
        phase_names = [phase["phase"] for phase in masterplan["phases"]]
        self.assertIn("Planning", phase_names)
        self.assertIn("Development", phase_names)
        self.assertIn("Testing", phase_names)
        self.assertIn("Deployment", phase_names)
    
    def test_masterplan_phases_have_steps(self):
        """Test that each phase has steps."""
        masterplan = MasterplanTool.generate_masterplan(self.opt_data, self.test_task)
        
        for phase in masterplan["phases"]:
            self.assertIn("steps", phase)
            self.assertGreater(len(phase["steps"]), 0)
    
    def test_identify_dependencies(self):
        """Test dependency identification."""
        task_with_api = "Automate API data sync"
        deps = MasterplanTool._identify_dependencies(task_with_api)
        
        self.assertIsInstance(deps, list)
        self.assertGreater(len(deps), 0)
    
    def test_identify_risks(self):
        """Test risk identification."""
        task = "Automate email sending"
        risks = MasterplanTool._identify_risks(task)
        
        self.assertIsInstance(risks, list)
        self.assertGreater(len(risks), 0)
    
    def test_format_masterplan(self):
        """Test masterplan formatting."""
        masterplan = MasterplanTool.generate_masterplan(self.opt_data, self.test_task)
        formatted = MasterplanTool.format_masterplan(masterplan)
        
        self.assertIsInstance(formatted, str)
        self.assertIn(self.test_task, formatted)
        self.assertIn("Phases", formatted)


if __name__ == "__main__":
    unittest.main()

