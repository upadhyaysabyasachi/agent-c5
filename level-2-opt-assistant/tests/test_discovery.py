"""Tests for Discovery Tool."""

import unittest
from tools.discovery_tool import DiscoveryTool


class TestDiscoveryTool(unittest.TestCase):
    """Test cases for DiscoveryTool."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.empty_context = {
            "operating_model": None,
            "processes": [],
            "tasks": []
        }
        
        self.partial_context = {
            "operating_model": "Content creator",
            "processes": ["Video editing"],
            "tasks": ["Download footage", "Edit video"]
        }
        
        self.complete_context = {
            "operating_model": "Content creator",
            "processes": ["Video editing", "Social media"],
            "tasks": ["Download footage", "Edit video", "Upload to YouTube", "Post on social"]
        }
    
    def test_get_next_question_empty_context(self):
        """Test getting next question with empty context."""
        question = DiscoveryTool.get_next_question(self.empty_context)
        
        self.assertIn("question", question)
        self.assertIn("category", question)
        self.assertEqual(question["category"], "Operating Model")
    
    def test_get_next_question_partial_context(self):
        """Test getting next question with partial context."""
        question = DiscoveryTool.get_next_question(self.partial_context)
        
        self.assertIn("question", question)
        # Should ask about tasks since we only have 2
        self.assertIn(question["category"], ["Tasks", "Processes"])
    
    def test_extract_opt_data(self):
        """Test extracting OPT data from user response."""
        response = "I run a newsletter business for dog owners"
        updated = DiscoveryTool.extract_opt_data(response, self.empty_context)
        
        self.assertIsNotNone(updated.get("operating_model"))
    
    def test_is_discovery_complete_empty(self):
        """Test discovery completeness check with empty context."""
        self.assertFalse(DiscoveryTool.is_discovery_complete(self.empty_context))
    
    def test_is_discovery_complete_partial(self):
        """Test discovery completeness check with partial context."""
        self.assertFalse(DiscoveryTool.is_discovery_complete(self.partial_context))
    
    def test_is_discovery_complete_full(self):
        """Test discovery completeness check with complete context."""
        self.assertTrue(DiscoveryTool.is_discovery_complete(self.complete_context))


if __name__ == "__main__":
    unittest.main()

