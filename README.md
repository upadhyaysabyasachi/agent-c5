# Ultra-Simple Agent Core with SPOAR Loop

A minimal, extensible AI agent implementation using the SENSE-PLAN-ACT-OBSERVE-REFLECT pattern.

---

## Quick Start

### 1. Install Dependencies

```bash
pip install groq python-dotenv
```

### 2. Setup API Key

```bash
# Copy the example environment file
cp env.example .env

# Edit .env and add your Groq Cloud API key
# GROQ_API_KEY=gsk-your-actual-key-here
```

Get your API key at: [console.groq.com/keys](https://console.groq.com/keys)

### 3. Run the Agent

```bash
python simple_agent.py
```

---

## The Complete Code (200 Lines)

The agent is implemented in a single file: `simple_agent.py`

**Model:** Uses `openai/gpt-oss-120b` via Groq Cloud - a 120B parameter model optimized for agentic tasks.

### Core Structure

```python
# Tools: Simple dictionary of functions
TOOLS = {
    "search": {
        "description": "Search for information about a topic",
        "function": lambda topic: f"Information about {topic}: [Mock result]"
    },
    "calculate": {
        "description": "Calculate a math expression",
        "function": lambda expr: str(eval(expr))
    }
}

# Agent: Single class with SPOAR methods
class SimpleAgent:
    def run(self, goal: str) -> str:
        # Main loop: SENSE → PLAN → ACT → OBSERVE → REFLECT
        ...
    
    def _sense(self, context): ...
    def _plan(self, context): ...
    def _act(self, plan): ...
    def _observe(self, plan, result): ...
    def _reflect(self, context, observation): ...
```

---

## Example Output

```
============================================================
🎯 GOAL: What is 25 * 4 + 100?
============================================================

--- ITERATION 1 ---

👁️  SENSE
  iteration: 1
  goal: What is 25 * 4 + 100?
  previous_actions: None

🧠 PLAN
  action: USE_TOOL
  tool: calculate
  reasoning: Need to calculate the mathematical expression 25 * 4 + 100...

⚡ ACT
  tool: calculate
  args: {'expr': '25 * 4 + 100'}
  result: 200

📊 OBSERVE
  action: calculate
  success: True

💭 REFLECT
  reflection: The calculation successfully returned 200. This directly answers the goal, so we can now provide the complete answer.

--- ITERATION 2 ---

🧠 PLAN
  action: COMPLETE
  tool: N/A
  reasoning: I have the calculation result and can now answer the question...

✅ COMPLETE
  answer: The answer to 25 * 4 + 100 is 200.

============================================================
FINAL ANSWER: The answer to 25 * 4 + 100 is 200.
============================================================
```

---

## Core Concepts

### The SPOAR Loop

| Phase | Purpose | What Happens |
|------|---------|---------------|
| **SENSE** | Gather context | Collect current state, available tools, previous actions |
| **PLAN** | Decide action | LLM (`openai/gpt-oss-120b`) chooses which tool to use or if goal is complete |
| **ACT** | Execute action | Run the selected tool function |
| **OBSERVE** | Record results | Log what happened, check for errors |
| **REFLECT** | Evaluate progress | LLM (`openai/gpt-oss-120b`) assesses if we're closer to the goal |

### Tools

Tools are simple functions the agent can call:

```python
TOOLS = {
    "search": {
        "description": "Search for information about a topic",
        "function": lambda topic: f"Information about {topic}: [Mock result]"
    },
    "calculate": {
        "description": "Calculate a math expression",
        "function": lambda expr: str(eval(expr))
    }
}
```

The LLM sees tool descriptions and decides:
1. **Which tool** to use
2. **What arguments** to pass
3. **When** to complete instead of using a tool

---

## How to Extend This Agent

### 1. Add More Tools

```python
TOOLS = {
    "search": {...},
    "calculate": {...},
    "get_weather": {
        "description": "Get weather for a city",
        "function": lambda city: f"Weather in {city}: 72°F, sunny"
    },
    "get_time": {
        "description": "Get current time",
        "function": lambda: __import__('datetime').datetime.now().strftime("%H:%M:%S")
    }
}
```

### 2. Add Memory Persistence

```python
class SimpleAgent:
    def __init__(self):
        # ... existing code ...
        self.long_term_memory = []  # Facts to remember
    
    def _sense(self, context: Dict[str, Any]) -> Dict[str, Any]:
        # Add memory to context
        context["memories"] = self.long_term_memory[-5:]  # Last 5 facts
        return context
    
    def store_fact(self, fact: str):
        """Store something in long-term memory."""
        self.long_term_memory.append({
            "fact": fact,
            "timestamp": datetime.now().isoformat()
        })
```

### 3. Add Error Recovery

```python
def _act(self, plan: Dict[str, Any]) -> Any:
    """ACT: Execute with retry on failure."""
    
    if plan["action"] != "USE_TOOL":
        return None
    
    max_retries = 2
    for attempt in range(max_retries + 1):
        try:
            tool_func = TOOLS[plan["tool"]]["function"]
            result = tool_func(**plan.get("args", {}))
            return result
        except Exception as e:
        if attempt < max_retries:
                print(f"  ⚠️  Retry {attempt + 1}/{max_retries}")
                continue
            return f"ERROR after {max_retries} retries: {str(e)}"
```

### 4. Add Structured Logging

```python
import json
from datetime import datetime

class SimpleAgent:
    def __init__(self):
        # ... existing code ...
    self.logs = []
    
    def _log_phase(self, phase: str, data: Dict[str, Any]):
        """Log with structure."""
    log_entry = {
        "timestamp": datetime.now().isoformat(),
        "phase": phase,
            "data": data
    }
    self.logs.append(log_entry)
    
        # Print for visibility
        print(f"{phase}")
        for key, value in data.items():
            print(f"  {key}: {value}")
        print()
    
    def save_logs(self, filename: str = "agent_logs.jsonl"):
        """Save logs to file."""
        with open(filename, "a") as f:
            for log in self.logs:
                f.write(json.dumps(log) + "\n")
```

### 5. Add Multi-Step Planning

```python
def _plan(self, context: Dict[str, Any]) -> Dict[str, Any]:
    """Enhanced planning with multi-step thinking."""
    
    prompt = f"""Goal: {context['goal']}

Think step-by-step:
1. What information do I have?
2. What information do I need?
3. What's the next logical action?

Then respond with JSON:
{{
  "thinking": "your step-by-step reasoning",
  "action": "USE_TOOL" or "COMPLETE",
  "tool": "tool_name",
  "args": {{}},
  "reasoning": "why this action",
  "answer": "final answer if COMPLETE"
}}"""
    
    # ... rest of planning code ...
```

### 6. Add Real Web Search

```python
import requests

TOOLS = {
    "web_search": {
        "description": "Search the web for current information",
        "function": lambda query: web_search(query)
    }
}

def web_search(query: str) -> str:
    """Real web search using Tavily API."""
    api_key = os.getenv("TAVILY_API_KEY")
    
    response = requests.post(
        "https://api.tavily.com/search",
        json={
            "api_key": api_key,
            "query": query,
            "max_results": 3
        }
    )
    
    results = response.json()
    return json.dumps(results["results"], indent=2)
```

---

## Testing Different Goals

```python
if __name__ == "__main__":
    agent = SimpleAgent()
    
    # Test 1: Math
    print("\n=== TEST 1: MATH ===")
    agent.run("What is 15 * 8 + 42?")
    
    # Test 2: Information
    print("\n=== TEST 2: SEARCH ===")
    agent.run("Search for information about Python programming")
    
    # Test 3: Multiple steps
    print("\n=== TEST 3: COMPLEX ===")
    agent.run("Calculate 100 / 4, then search for information about that number")
```

---

## Troubleshooting

### "GROQ_API_KEY not found"

```bash
# Make sure .env file exists and has the key
cat .env
# Should show: GROQ_API_KEY=gsk_...
```

### "Rate limit exceeded"

- Wait a few seconds between runs
- Groq Cloud offers fast inference with generous rate limits
- Add retry with exponential backoff

### "JSON parse error"

- The LLM sometimes outputs invalid JSON
- Check the `_parse_json` method for error handling
- Lower temperature for more consistent outputs

### "Tool not found"

- Check tool name spelling in your prompt
- Ensure tool is registered in `TOOLS` dictionary

---

## Key Takeaways

1. **SPOAR Loop is Just 5 Functions**
   - SENSE → Gather context
   - PLAN → Decide action
   - ACT → Execute
   - OBSERVE → Record results
   - REFLECT → Evaluate

2. **Tools = Simple Functions**
   - Dictionary of name → function
   - LLM sees descriptions, picks tools

3. **Context Flows Through Loop**
   - Each phase enriches context
   - Next iteration has full history

4. **Easy to Extend**
   - Add new tools → 3 lines
   - Add memory → Few lines in SENSE
   - Add logging → Modify _log_phase

This is your **foundation**. Everything else (RAG, multi-agent, planning, etc.) builds on this core loop!

---

## Resources

- [Groq Cloud API Docs](https://console.groq.com/docs)
- [Groq Cloud Models](https://console.groq.com/docs/models)
- [GPT OSS 120B Model Documentation](https://console.groq.com/docs/model/openai/gpt-oss-120b)
- [LangChain Agents](https://python.langchain.com/docs/modules/agents/)

---

Happy building! 🚀
