import os
import json
import time
import re
from groq import Groq
from dotenv import load_dotenv
from rich.console import Console
from rich.markdown import Markdown

from memory.conversation_memory import ConversationMemory
from prompts.opt_coach import DISCOVERY_SYSTEM_PROMPT, ANALYSIS_SYSTEM_PROMPT, CODE_GEN_SYSTEM_PROMPT
from prompts.code_generation import CODE_GENERATION_PROMPT
from tools.discovery_tool import DiscoveryTool
from tools.analysis_tool import AnalysisTool
from tools.masterplan_tool import MasterplanTool
from tools.code_gen_tool import save_automation_script
from tools.deployment_tool import DeploymentTool

load_dotenv()
console = Console()

class OPTAgent:
    def __init__(self):
        api_key = os.getenv("GROQ_API_KEY")
        if not api_key:
            raise ValueError("GROQ_API_KEY not found in environment variables")
        self.client = Groq(api_key=api_key)
        self.memory = ConversationMemory()
        self.model = "llama-3.3-70b-versatile"
        self.selected_task = None  # Track the task selected for automation
        self.recent_responses = []  # Track recent responses to detect repetition
        self.repetition_threshold = 2  # Exit after 2 consecutive similar responses
        self.previous_phase = None  # Track phase changes to reset repetition tracking

    def _is_exit_command(self, user_input: str) -> bool:
        """Check if user input is an exit command (handles various formats)."""
        if not user_input:
            return False
        
        exit_keywords = ["exit", "quit", "bye", "end", "stop", "close", "done", "finish"]
        user_lower = user_input.lower().strip()
        
        # Check for exact matches
        if user_lower in exit_keywords:
            return True
        
        # Check if any exit keyword appears in the input
        for keyword in exit_keywords:
            if keyword in user_lower:
                # Make sure it's not part of another word
                if re.search(r'\b' + re.escape(keyword) + r'\b', user_lower):
                    return True
        
        return False

    def _are_responses_similar(self, response1: str, response2: str, similarity_threshold: float = 0.85) -> bool:
        """Check if two responses are similar (to detect repetition)."""
        if not response1 or not response2:
            return False
        
        # Normalize responses (lowercase, strip whitespace)
        r1 = response1.lower().strip()
        r2 = response2.lower().strip()
        
        # Exact match
        if r1 == r2:
            return True
        
        # Check if one is a substring of the other (for very similar responses)
        if len(r1) > 50 and len(r2) > 50:  # Only for longer responses
            # Calculate simple similarity based on common words
            words1 = set(r1.split())
            words2 = set(r2.split())
            if len(words1) > 0 and len(words2) > 0:
                common_words = words1.intersection(words2)
                similarity = len(common_words) / max(len(words1), len(words2))
                if similarity >= similarity_threshold:
                    return True
        
        # Check if responses are very similar in length and content
        if abs(len(r1) - len(r2)) < max(len(r1), len(r2)) * 0.2:  # Within 20% length difference
            # Check for significant overlap in key phrases
            # Extract first 100 chars as a signature
            sig1 = r1[:100] if len(r1) > 100 else r1
            sig2 = r2[:100] if len(r2) > 100 else r2
            if sig1 == sig2:
                return True
        
        return False

    def _check_repetition(self, response: str) -> bool:
        """Check if the agent is repeating the same response."""
        if not response:
            return False
        
        # Add current response to recent responses
        self.recent_responses.append(response)
        
        # Keep only last N responses (threshold + 1 to compare)
        max_track = self.repetition_threshold + 1
        if len(self.recent_responses) > max_track:
            self.recent_responses = self.recent_responses[-max_track:]
        
        # Need at least threshold number of responses to check
        if len(self.recent_responses) < self.repetition_threshold:
            return False
        
        # Check if last N responses are all similar
        last_responses = self.recent_responses[-self.repetition_threshold:]
        for i in range(1, len(last_responses)):
            if not self._are_responses_similar(last_responses[0], last_responses[i]):
                return False
        
        # All recent responses are similar - repetition detected
        return True

    def run(self):
        console.print("[bold green]🤖 AI Automation Agent Initialized (OPT Framework)[/bold green]")
        console.print("Tell me about your business! (e.g., 'I run a newsletter for dog owners')")
        
        # Initialize previous phase
        self.previous_phase = self.memory.current_phase

        while True:
            user_input = console.input("[bold cyan]You:[/bold cyan] ")
            
            # Check for exit command before processing
            if self._is_exit_command(user_input):
                console.print("[bold yellow]👋 Goodbye! Thanks for using the OPT Assistant.[/bold yellow]")
                break
            
            self.memory.add_message("user", user_input)
            
            # Reset repetition tracking on phase change
            if self.previous_phase != self.memory.current_phase:
                self.recent_responses = []
                self.previous_phase = self.memory.current_phase
            
            # --- STATE MACHINE LOGIC ---
            response = ""
            
            if self.memory.current_phase == "DISCOVERY":
                response = self._handle_discovery()
                
            elif self.memory.current_phase == "ANALYSIS":
                response = self._handle_analysis()
                
            elif self.memory.current_phase == "CODE":
                response = self._handle_code_generation()

            # Check if response indicates exit (from phase handlers)
            if response == "<EXIT>":
                console.print("[bold yellow]👋 Goodbye! Thanks for using the OPT Assistant.[/bold yellow]")
                break

            # Check for repetition - if agent is giving same response, exit gracefully
            if self._check_repetition(response):
                console.print(f"[bold yellow]Agent:[/bold yellow]")
                console.print(Markdown(response))
                console.print("\n[bold yellow]⚠️  I notice I've been repeating myself. Let me step back.[/bold yellow]")
                console.print("[bold yellow]👋 Thanks for using the OPT Assistant. Feel free to start a new session when you're ready![/bold yellow]")
                break

            # Display Response
            self.memory.add_message("assistant", response)
            console.print(f"[bold green]Agent:[/bold green]")
            console.print(Markdown(response))

    def _handle_discovery(self) -> str:
        """Consultative phase to gather info using DiscoveryTool."""
        # Extract OPT data from latest user message
        if self.memory.history:
            last_user_msg = next(
                (msg for msg in reversed(self.memory.history) if msg['role'] == 'user'),
                None
            )
            if last_user_msg:
                self.memory.opt_data = DiscoveryTool.extract_opt_data(
                    last_user_msg['content'],
                    self.memory.opt_data
                )
        
        # Check if discovery is complete
        if DiscoveryTool.is_discovery_complete(self.memory.opt_data):
            self.memory.update_phase("ANALYSIS")
            return (
                "Great! I have enough information about your business. "
                "Let me analyze your tasks and suggest automation opportunities...\n\n"
                "**Moving to Analysis Phase**"
            )
        
        # Get next discovery question
        next_question = DiscoveryTool.get_next_question(self.memory.opt_data)
        
        # Build context-aware prompt
        context_summary = f"""
Current OPT Context:
- Operating Model: {self.memory.opt_data.get('operating_model', 'Not yet identified')}
- Processes: {len(self.memory.opt_data.get('processes', []))} identified
- Tasks: {len(self.memory.opt_data.get('tasks', []))} identified

Next Question Category: {next_question['category']}
"""
        
        messages = [
            {"role": "system", "content": DISCOVERY_SYSTEM_PROMPT},
            {"role": "user", "content": f"{context_summary}\n\nConversation History:\n{self.memory.get_history_str()}\n\nAsk the next discovery question naturally in conversation."}
        ]
        
        response = self._call_llm(messages)
        
        # Check for manual phase transition trigger
        if "<PHASE_COMPLETE>" in response:
            response = response.replace("<PHASE_COMPLETE>", "")
            self.memory.update_phase("ANALYSIS")
            response += "\n\n**Discovery complete. Moving to Analysis...**"
            
        return response

    def _handle_analysis(self) -> str:
        """Suggesting automations using AnalysisTool."""
        # Check for exit command in user's latest message
        if self.memory.history:
            last_user_msg = self.memory.history[-1]['content'] if self.memory.history[-1]['role'] == 'user' else ""
            if last_user_msg and self._is_exit_command(last_user_msg):
                return "<EXIT>"
        
        # First time in analysis phase - generate suggestions
        if not hasattr(self, '_analysis_suggestions') or not self._analysis_suggestions:
            # Analyze tasks using AnalysisTool
            self._analysis_suggestions = AnalysisTool.analyze_tasks(self.memory.opt_data)
            
            if not self._analysis_suggestions:
                return (
                    "I've analyzed your tasks, but I couldn't find high-value automation opportunities "
                    "at this time. Would you like to explore more specific tasks or processes?"
                )
            
            # Format suggestions
            suggestions_text = AnalysisTool.format_suggestions(self._analysis_suggestions)
            
            # Get LLM to present suggestions naturally
            messages = [
                {"role": "system", "content": ANALYSIS_SYSTEM_PROMPT},
                {"role": "user", "content": f"OPT Data: {json.dumps(self.memory.opt_data, indent=2)}\n\n{suggestions_text}\n\nPresent these suggestions naturally and ask which one they'd like to build."}
            ]
            
            response = self._call_llm(messages)
            return response
        
        # User has responded - check if they selected a task
        last_user_msg = self.memory.history[-1]['content'].lower() if self.memory.history else ""
        
        # Check if user selected a task (look for numbers or task mentions)
        selected_task = None
        for i, suggestion in enumerate(self._analysis_suggestions, 1):
            task_text = suggestion['task'].lower()
            if (
                str(i) in last_user_msg or
                task_text[:30] in last_user_msg or
                "option " + str(i) in last_user_msg or
                "first" in last_user_msg and i == 1 or
                "second" in last_user_msg and i == 2 or
                "third" in last_user_msg and i == 3
            ):
                selected_task = suggestion['task']
                break
        
        # Also check for explicit build/code keywords
        if not selected_task and ("build" in last_user_msg or "code" in last_user_msg or "automate" in last_user_msg):
            # Use first suggestion as default
            if self._analysis_suggestions:
                selected_task = self._analysis_suggestions[0]['task']
        
        if selected_task:
            self.selected_task = selected_task
            self.memory.update_phase("CODE")
            return (
                f"Perfect! I'll help you build automation for: **{selected_task}**\n\n"
                "Let me create a masterplan and then generate the code for you..."
            )
        
        # Still in analysis - continue conversation
        messages = [
            {"role": "system", "content": ANALYSIS_SYSTEM_PROMPT},
            {"role": "user", "content": f"User said: {self.memory.history[-1]['content']}\n\nAvailable options:\n{AnalysisTool.format_suggestions(self._analysis_suggestions)}\n\nHelp them choose or clarify."}
        ]
        
        response = self._call_llm(messages)
        return response

    def _handle_code_generation(self) -> str:
        """Writing the script with masterplan and deployment instructions."""
        # Generate masterplan first (if not already done)
        if not hasattr(self, '_masterplan') or not self._masterplan:
            if not self.selected_task:
                # Try to extract task from conversation
                self.selected_task = self._extract_task_from_conversation()
            
            if self.selected_task:
                self._masterplan = MasterplanTool.generate_masterplan(
                    self.memory.opt_data,
                    self.selected_task
                )
                masterplan_text = MasterplanTool.format_masterplan(self._masterplan)
                
                # Show masterplan first
                console.print("\n[bold yellow]📋 Masterplan Generated:[/bold yellow]")
                console.print(Markdown(masterplan_text))
            else:
                self._masterplan = {}
        
        # Generate code
        task_description = self.selected_task or "the selected automation task"
        opt_context = json.dumps(self.memory.opt_data, indent=2)
        
        code_prompt = f"""
Generate a complete Python automation script for: {task_description}

## Context:
{opt_context}

## Requirements:
1. Complete, executable code (no placeholders)
2. Use environment variables for API keys/secrets (load from .env)
3. Include error handling and logging
4. Add clear comments and docstrings
5. Include all necessary imports

## Conversation History:
{self.memory.get_history_str()}

Return ONLY the Python code block wrapped in markdown code fences.
"""
        
        messages = [
            {"role": "system", "content": CODE_GENERATION_PROMPT},
            {"role": "user", "content": code_prompt}
        ]
        
        code_response = self._call_llm(messages)
        
        # Extract and save code
        timestamp = int(time.time())
        filename = f"automation_{timestamp}.py"
        save_result = save_automation_script(filename, code_response)
        
        # Generate deployment instructions
        # Extract dependencies from code (simple heuristic)
        dependencies = self._extract_dependencies(code_response)
        deployment_instructions = DeploymentTool.generate_deployment_instructions(
            script_path=f"generated_automations/{filename}",
            dependencies=dependencies
        )
        deployment_text = DeploymentTool.format_deployment_instructions(deployment_instructions)
        
        # Create requirements.txt if needed
        if dependencies:
            req_file = DeploymentTool.create_requirements_file(
                dependencies,
                output_path=f"generated_automations/requirements_{timestamp}.txt"
            )
        
        response = f"""## ✅ Code Generated Successfully!

**File saved**: `{save_result}`

### Generated Code:

{code_response}

---

## 🚀 Deployment Instructions

{deployment_text}

---

**Next Steps:**
1. Review the generated code
2. Set up your `.env` file with required API keys
3. Install dependencies: `pip install -r generated_automations/requirements_{timestamp}.txt`
4. Test the script: `python generated_automations/{filename}`
"""
        
        return response
    
    def _extract_task_from_conversation(self) -> str:
        """Extract the selected task from conversation history."""
        # Look for task mentions in recent messages
        for msg in reversed(self.memory.history[-5:]):
            content = msg['content'].lower()
            # Check if it mentions a task from our suggestions
            if hasattr(self, '_analysis_suggestions'):
                for suggestion in self._analysis_suggestions:
                    if suggestion['task'].lower()[:30] in content:
                        return suggestion['task']
        return None
    
    def _extract_dependencies(self, code: str) -> list:
        """Extract Python dependencies from code."""
        dependencies = []
        code_lower = code.lower()
        
        # Common library detection
        common_libs = {
            'requests': 'requests',
            'pandas': 'pandas',
            'numpy': 'numpy',
            'openpyxl': 'openpyxl',
            'xlsxwriter': 'xlsxwriter',
            'beautifulsoup4': 'beautifulsoup4',
            'selenium': 'selenium',
            'pillow': 'pillow',
            'pytz': 'pytz',
            'python-dotenv': 'python-dotenv',
            'groq': 'groq',
            'openai': 'openai',
        }
        
        for lib_name, pip_name in common_libs.items():
            if f'import {lib_name}' in code_lower or f'from {lib_name}' in code_lower:
                dependencies.append(pip_name)
        
        # Always include python-dotenv if .env is mentioned
        if '.env' in code_lower or 'load_dotenv' in code_lower:
            if 'python-dotenv' not in dependencies:
                dependencies.append('python-dotenv')
        
        return dependencies

    def _call_llm(self, messages, temperature=0.7):
        """Call the LLM with error handling."""
        try:
            completion = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=temperature
            )
            return completion.choices[0].message.content
        except Exception as e:
            console.print(f"[bold red]Error calling LLM: {str(e)}[/bold red]")
            return "I encountered an error. Please try again or check your API key."