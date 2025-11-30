import os
import json
import time
from datetime import datetime
from typing import Dict, Any, List
from groq import Groq
from dotenv import load_dotenv

# Import our new modules
from memory import Memory
from tools import TOOLS

load_dotenv()

class SmartLookupAgent:
    def __init__(self):
        self.llm = Groq(api_key=os.getenv("GROQ_API_KEY"))
        self.model = "llama-3.3-70b-versatile" # Reliable model for agents
        self.memory = Memory()
        self.logs = []
        
        # Ensure logs directory exists
        if not os.path.exists("logs"):
            os.makedirs("logs")

    def run(self, user_query: str):
        """Main SPOAR Loop"""
        print(f"\n{'='*60}")
        print(f"🤖 AGENT START: {user_query}")
        print(f"{'='*60}\n")
        
        context = {
            "goal": user_query,
            "iteration": 0,
            "past_memories": []
        }

        # --- PHASE 1: SENSE (With Memory!) ---
        # Before planning, check if we've answered this before
        print("👁️  SENSING...")
        relevant_memories = self.memory.search_memory(user_query)
        if relevant_memories:
            print(f"   found {len(relevant_memories)} relevant past memories.")
            context["past_memories"] = relevant_memories
        
        # Start Loop
        max_iterations = 5
        for i in range(max_iterations):
            context["iteration"] += 1
            
            # --- PHASE 2: PLAN ---
            plan = self._plan(context)
            
            # Check for completion
            if plan["action"] == "COMPLETE":
                final_answer = plan["answer"]
                
                # --- MEMORY STORAGE ---
                # Save this interaction for the future
                self.memory.add_memory(user_query, final_answer)
                
                self._log_phase("COMPLETE", plan)
                self.save_logs(f"logs/agent_log_{int(time.time())}.json")
                return final_answer

            # --- PHASE 3: ACT ---
            result = self._act(plan)
            
            # --- PHASE 4: OBSERVE ---
            observation = {
                "tool": plan.get("tool", "unknown"),
                "result": result,
                "success": "ERROR" not in str(result)
            }
            self._log_phase("OBSERVE", observation)

            # --- PHASE 5: REFLECT ---
            reflection = self._reflect(context, observation)

            # Update context with what we learned
            context["last_observation"] = observation
            context["last_reflection"] = reflection

        return "❌ Failed to answer within iteration limit."

    def _plan(self, context):
        """Decide next steps using LLM."""
        memories_text = "\n".join(context["past_memories"]) if context["past_memories"] else "None"

        prompt = f"""
        You are a smart internal support agent.

        GOAL: {context['goal']}

        RELEVANT PAST MEMORIES (Use these if they answer the question!):
        {memories_text}

        PREVIOUS TOOL RESULT:
        {context.get('last_observation', {}).get('result', 'None')}

        PREVIOUS REFLECTION:
        {context.get('last_reflection', 'None')}

        AVAILABLE TOOLS:
        - search_knowledge_base: Search internal docs.

        INSTRUCTIONS:
        1. If 'RELEVANT PAST MEMORIES' contains the answer, use action "COMPLETE".
        2. If you need info, use action "USE_TOOL".
        3. If a previous search returned no results, try a DIFFERENT, SIMPLER query (use key terms only).
        4. If you have searched 2+ times with no results, COMPLETE with "I don't have information about that."
        5. Respond in JSON format ONLY.

        JSON SCHEMA:
        {{
          "action": "USE_TOOL" or "COMPLETE",
          "tool": "search_knowledge_base" (if needed),
          "args": {{"query": "simple keywords only"}},
          "answer": "Final answer here (if complete)"
        }}
        """
        
        completion = self.llm.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": "You are a JSON-speaking agent. Output ONLY valid JSON."},
                {"role": "user", "content": prompt}
            ],
            temperature=0
        )
        
        return self._parse_json(completion.choices[0].message.content)

    def _act(self, plan):
        """Execute the tool with error handling."""
        if plan.get("action") != "USE_TOOL":
            return None

        tool_name = plan.get("tool")
        if not tool_name:
            return "ERROR: No tool specified in plan"

        args = plan.get("args", {})

        # Execute tool with error handling
        if tool_name not in TOOLS:
            result = f"ERROR: Tool '{tool_name}' not found"
        else:
            try:
                print(f"⚡ ACT: Calling {tool_name} with {args}")
                tool_func = TOOLS[tool_name]["function"]
                result = tool_func(**args)
            except Exception as e:
                result = f"ERROR: {str(e)}"
                print(f"   ⚠️  Tool execution failed: {str(e)}")

        return result

    def _reflect(self, context, observation):
        """REFLECT: Evaluate progress toward goal using LLM."""
        prompt = f"""Goal: {context['goal']}

Action Taken: {observation['tool']}
Result: {str(observation['result'])[:200]}
Success: {observation['success']}

In 1-2 sentences, reflect on:
1. Did this action help progress toward the goal?
2. What should happen next?

Be brief and actionable."""

        try:
            response = self.llm.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You reflect on agent progress. Be brief."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3,
                max_tokens=100
            )

            reflection = response.choices[0].message.content.strip()
            self._log_phase("REFLECT", {"reflection": reflection})
            return reflection
        except Exception as e:
            error_msg = f"Reflection failed: {str(e)}"
            print(f"   ⚠️  {error_msg}")
            return error_msg

    def _parse_json(self, text):
        """Parse JSON from LLM response with robust error handling."""
        if not text or not text.strip():
            print("⚠️  Warning: Empty response from LLM, using fallback")
            return {
                "action": "COMPLETE",
                "reasoning": "LLM returned empty response",
                "answer": "I encountered an error processing your request. Please try again."
            }

        # Remove markdown code blocks if present
        if "```json" in text:
            text = text.split("```json")[1].split("```")[0]
        elif "```" in text:
            text = text.split("```")[1].split("```")[0]

        text = text.strip()

        # Try to find JSON object in the text if it's not pure JSON
        if not text.startswith("{"):
            start_idx = text.find("{")
            end_idx = text.rfind("}")
            if start_idx != -1 and end_idx != -1 and end_idx > start_idx:
                text = text[start_idx:end_idx + 1]

        try:
            return json.loads(text)
        except json.JSONDecodeError as e:
            print(f"⚠️  JSON Parse Error: {str(e)}")
            print(f"⚠️  Raw response: {text[:200]}...")
            # Return a safe fallback
            return {
                "action": "COMPLETE",
                "reasoning": f"Failed to parse LLM response: {str(e)}",
                "answer": "I encountered an error processing the response. Please try rephrasing your question."
            }

    def _log_phase(self, phase, data):
        entry = {"phase": phase, "data": data, "timestamp": datetime.now().isoformat()}
        self.logs.append(entry)
        print(f"📝 {phase}: {str(data)[:100]}...")

    def save_logs(self, filepath):
        with open(filepath, "w") as f:
            json.dump(self.logs, f, indent=2)