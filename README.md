# AI Agent Development: Student Guide

A comprehensive hands-on guide to building AI agents from scratch.

---

## Table of Contents

1. [Introduction](#introduction)
2. [Prerequisites](#prerequisites)
3. [Quick Start](#quick-start)
4. [Core Concepts](#core-concepts)
5. [Code Walkthrough](#code-walkthrough)
6. [Learning Tasks](#learning-tasks)
7. [Extension Ideas](#extension-ideas)
8. [Troubleshooting](#troubleshooting)
9. [Resources](#resources)

---

## Introduction

### What You'll Learn

This boilerplate teaches you how to build **autonomous AI agents** - systems that can:

- Understand natural language goals
- Reason about what actions to take
- Use tools to interact with the world
- Maintain memory across interactions
- Reflect on their progress and adapt

### The Big Picture

```
┌─────────────────────────────────────────────────────────────┐
│                      USER GOAL                               │
│            "What is an AI agent?"                           │
└─────────────────────────────────────┬───────────────────────┘
                                      │
                                      ▼
┌─────────────────────────────────────────────────────────────┐
│                    AGENT LOOP                                │
│  ┌─────────┐  ┌─────────┐  ┌─────────┐  ┌─────────┐        │
│  │  SENSE  │→ │  PLAN   │→ │   ACT   │→ │ OBSERVE │→       │
│  └─────────┘  └─────────┘  └─────────┘  └─────────┘        │
│       │                                       │              │
│       │            ┌──────────┐               │              │
│       └────────────│ REFLECT  │←──────────────┘              │
│                    └──────────┘                              │
│                         │                                    │
│                    Loop or Complete                          │
└─────────────────────────────────────────────────────────────┘
                                      │
                                      ▼
┌─────────────────────────────────────────────────────────────┐
│                      FINAL ANSWER                            │
│   "An AI agent is a system that can perceive..."            │
└─────────────────────────────────────────────────────────────┘
```

---

## Prerequisites

### Required Knowledge

- **Python basics**: Functions, classes, dictionaries, async/await
- **API concepts**: HTTP requests, JSON, API keys
- **Command line**: Running Python scripts, environment variables

### Required Software

1. **Python 3.9+**
   ```bash
   python --version  # Should be 3.9 or higher
   ```

2. **pip** (Python package manager)
   ```bash
   pip --version
   ```

### Required API Keys

You need an **OpenAI API key** to run this agent:

1. Go to [platform.openai.com/api-keys](https://platform.openai.com/api-keys)
2. Create a new API key
3. Copy the key (it starts with `sk-`)

---

## Quick Start

### Step 1: Setup Environment

```bash
# Clone or navigate to the project
cd agentic-tutor

# Create a virtual environment (recommended)
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install openai python-dotenv
```

### Step 2: Configure API Key

```bash
# Copy the example environment file
cp env.example .env

# Edit .env and add your OpenAI API key
# OPENAI_API_KEY=sk-your-actual-key-here
```

### Step 3: Run the Agent

```bash
python simple_agent.py
```

### Expected Output

```
============================================================
🤖 SIMPLE AI AGENT DEMO
============================================================

📝 Running agent with goal: 'What is an AI agent and how does the agent loop work?'

============================================================
🚀 AGENT SESSION STARTED
📎 Goal: What is an AI agent and how does the agent loop work?
============================================================

👁️  [SENSE] Iteration 1
----------------------------------------
  gathered_context: user preferences, conversation history
  user_level: intermediate

🧠 [PLAN] Iteration 1
----------------------------------------
  action_type: TOOL_CALL
  tool: search_knowledge
  reasoning: Need to find information about AI agents...

⚡ [ACT] Iteration 1
----------------------------------------
  tool: search_knowledge
  args: {'query': 'AI agent loop'}
  success: True

... (more iterations)

✅ AGENT SESSION COMPLETED
⏱️  Total time: 3.45 seconds
📝 Iterations: 2
```

---

## Core Concepts

### 1. The Agent Loop

The heart of any AI agent is its **reasoning loop**. Our agent follows the **SENSE-PLAN-ACT-OBSERVE-REFLECT** pattern:

| Phase | Purpose | Implementation |
|-------|---------|----------------|
| **SENSE** | Gather context about the current state | Get user info, recent conversation |
| **PLAN** | Decide what action to take | LLM chooses tool and arguments |
| **ACT** | Execute the chosen action | Call the selected tool function |
| **OBSERVE** | Record what happened | Log results, update context |
| **REFLECT** | Evaluate progress | LLM assesses if goal is achieved |

### 2. Tools

Tools are **functions the agent can call** to interact with the world. Think of them as the agent's "hands."

```python
# Example tool definition
{
    "name": "search_knowledge",
    "description": "Search the knowledge base for information",
    "parameters": {
        "query": {"type": "string", "description": "Search query"}
    },
    "function": self._search_knowledge  # Actual Python function
}
```

The LLM sees the tool descriptions and decides:
1. **Which tool** to use
2. **What arguments** to pass
3. **Why** this tool helps achieve the goal

### 3. Memory

Agents need memory to maintain context:

| Type | Purpose | Example |
|------|---------|---------|
| **Short-term** | Current session context | Conversation history, current goal |
| **Long-term** | Persistent knowledge | Stored facts, user preferences |

```python
# Storing a fact
memory.store_fact("The user prefers visual explanations")

# Recalling relevant facts
results = memory.search_facts("user preferences")
```

### 4. Retrieval (RAG)

RAG = **Retrieval Augmented Generation**

Instead of relying only on the LLM's training data, we:
1. **Retrieve** relevant documents from a knowledge base
2. **Provide** them as context to the LLM
3. **Generate** a grounded response

Our boilerplate uses simple keyword search. Production systems use:
- Vector embeddings for semantic search
- Vector databases (Pinecone, Weaviate, pgvector)

### 5. LLM as the Brain

The LLM (GPT-4o-mini in our case) serves as the **reasoning engine**:

- Understands natural language goals
- Decides which tools to use
- Synthesizes information into answers
- Reflects on progress

We communicate with the LLM through **structured prompts** that specify:
- Available tools and their schemas
- Expected output format (JSON)
- Context and constraints

---

## Code Walkthrough

### File Structure

```
simple_agent.py          # Main boilerplate (all-in-one)
sample_knowledge_base.json  # Mock data for retrieval
env.example              # Environment variables template
STUDENT_GUIDE.md         # This guide
```

### Section-by-Section Breakdown

#### Section 1: Configuration

```python
@dataclass
class AgentConfig:
    model: str = "gpt-4o-mini"      # LLM model to use
    max_iterations: int = 5         # Safety limit
    temperature: float = 0.3        # Creativity (0=focused, 1=creative)
    verbose: bool = True            # Print detailed logs
```

**Key concept**: Configuration should be separate from logic for easy tuning.

#### Section 2: Memory Store

```python
class MemoryStore:
    def __init__(self):
        self.context: Dict[str, Any] = {}           # Current session
        self.facts: List[Dict[str, Any]] = []       # Stored knowledge
        self.conversation_history: List[...] = []   # Chat history
        self.user_preferences: Dict[str, Any] = {}  # User info
```

**Key concept**: Memory enables continuity across interactions.

#### Section 3: Tools Registry

```python
class ToolRegistry:
    def register_tool(self, name, description, parameters, function):
        """Register a new tool the agent can use."""
        
    def execute(self, tool_name, args):
        """Execute a tool and return results."""
        
    def get_tools_for_prompt(self):
        """Format tools for LLM to understand."""
```

**Key concept**: Tools are defined declaratively and executed dynamically.

#### Section 4: Agent Core

```python
class SimpleAgent:
    def run(self, goal: str) -> Dict[str, Any]:
        """Main entry - runs the full agent loop."""
        
        while iteration < max_iterations:
            context = self._sense(...)    # Gather context
            plan = self._plan(...)        # LLM decides action
            
            if plan["action_type"] == "COMPLETE":
                return result             # Goal achieved!
            
            result = self._act(plan)      # Execute tool
            self._observe(plan, result)   # Log results
            self._reflect(...)            # Evaluate progress
```

**Key concept**: The loop continues until goal is achieved or limit reached.

#### Section 5: LLM Integration

```python
# Planning prompt structure
planning_prompt = f"""
## Current Goal
{goal}

## Available Tools
{tools_description}

## Your Task
Decide the NEXT action. Respond with JSON:
{{"action_type": "TOOL_CALL", "tool": "...", "args": {...}}}
"""

# Call OpenAI
response = self.llm.chat.completions.create(
    model=self.config.model,
    messages=[
        {"role": "system", "content": self.system_prompt},
        {"role": "user", "content": planning_prompt},
    ],
)
```

**Key concept**: Structured prompts guide LLM behavior reliably.

---

## Learning Tasks

Complete these three tasks to master AI agent development:

### Task 1: Foundation - Understanding the Agent Core

**Goal**: Understand how the agent loop works by running, observing, and modifying it.

#### Exercise 1.1: Trace the Execution

1. Run the agent and carefully read all log output
2. Identify each phase: SENSE, PLAN, ACT, OBSERVE, REFLECT
3. Answer these questions:
   - How many iterations did it take?
   - What tool was called and why?
   - What was the LLM's reasoning?

#### Exercise 1.2: Modify the System Prompt

The system prompt defines the agent's personality. Find this in `simple_agent.py`:

```python
self.system_prompt = """You are an intelligent AI assistant agent..."""
```

**Your task**: Create three different personalities:
1. A friendly tutor that encourages learning
2. A concise expert that gives brief, precise answers
3. A Socratic teacher that answers questions with questions

Test each with the same goal and compare outputs.

#### Exercise 1.3: Add a New Tool

Add a `get_current_time` tool that returns the current date and time.

**Steps**:

1. Find the `_register_default_tools` method in `ToolRegistry`

2. Add a new tool registration:
```python
self.register_tool(
    name="get_current_time",
    description="Get the current date and time. Use when user asks about time.",
    parameters={},
    function=self._get_current_time,
)
```

3. Add the implementation:
```python
def _get_current_time(self) -> Dict[str, Any]:
    """Get current date and time."""
    from datetime import datetime
    now = datetime.now()
    return {
        "success": True,
        "datetime": now.isoformat(),
        "human_readable": now.strftime("%A, %B %d, %Y at %I:%M %p"),
    }
```

4. Test with: `"What time is it right now?"`

**Reflection questions**:
- How did the LLM know to use your new tool?
- What happens if you give a vague description?

---

### Task 2: Reasoning Loop - Enhance Decision Making

**Goal**: Make the agent smarter by improving its reasoning capabilities.

#### Exercise 2.1: Implement Retry on Failure

Currently, if a tool fails, the agent just records the error. Make it retry!

**Steps**:

1. Find the `_act` method in `SimpleAgent`

2. Add retry logic:
```python
def _act(self, plan: Dict[str, Any], iteration: int, max_retries: int = 2) -> Dict[str, Any]:
    """Execute with retry on failure."""
    
    for attempt in range(max_retries + 1):
        result = self.tools.execute(tool_name, args)
        
        if result.get("success", False):
            return result
        
        if attempt < max_retries:
            self.logger.log_phase("RETRY", {
                "attempt": attempt + 1,
                "error": result.get("error", "Unknown"),
            }, iteration)
            time.sleep(1)  # Brief delay before retry
    
    return result  # Return last result even if failed
```

**Test**: Make a tool that fails randomly, see if retry helps.

#### Exercise 2.2: Add Chain of Thought Prompting

Make the agent show its reasoning more explicitly.

**Steps**:

1. Modify the planning prompt to require thinking:
```python
planning_prompt = f"""
## Current Goal
{goal}

## Your Task
First, think step by step about what information you need.
Then decide what action to take.

Respond with JSON:
{{
    "thinking": "Your step-by-step reasoning...",
    "action_type": "TOOL_CALL" | "COMPLETE",
    "tool": "tool_name",
    "args": {{}},
    "reasoning": "Why this action"
}}
"""
```

2. Log the thinking in `_plan`:
```python
self.logger.log_phase("PLAN", {
    "thinking": plan.get("thinking", ""),
    "action_type": plan.get("action_type"),
    ...
}, iteration)
```

**Observe**: Does the agent make better decisions with explicit thinking?

#### Exercise 2.3: Implement CLARIFY Action Type

Sometimes goals are ambiguous. Let the agent ask for clarification!

**Steps**:

1. Update the system prompt to allow CLARIFY:
```python
Action Types:
- TOOL_CALL: Use a tool
- COMPLETE: Goal achieved
- CLARIFY: Need more information from user

For CLARIFY, include a "question" field.
```

2. Handle CLARIFY in the `run` method:
```python
if plan.get("action_type") == "CLARIFY":
    question = plan.get("question", "Could you clarify?")
    return {
        "status": "needs_clarification",
        "question": question,
        "iterations": iteration,
    }
```

3. Test with ambiguous goals like: `"Help me learn something"`

---

### Task 3: Evaluation and Logging

**Goal**: Add observability to understand and improve agent behavior.

#### Exercise 3.1: Structured JSON Logging

Replace print-based logging with structured JSON logs.

**Steps**:

1. Create a file logger in `AgentLogger`:
```python
def __init__(self, verbose: bool = True, log_file: str = "agent_logs.jsonl"):
    self.verbose = verbose
    self.log_file = log_file
    self.logs = []
    
def _log(self, phase: str, data: Dict[str, Any], iteration: int = 0):
    log_entry = {
        "timestamp": datetime.now().isoformat(),
        "phase": phase,
        "iteration": iteration,
        "data": data,
    }
    self.logs.append(log_entry)
    
    # Write to file
    with open(self.log_file, "a") as f:
        f.write(json.dumps(log_entry) + "\n")
```

2. After running, analyze the logs:
```python
# Read and analyze logs
import json
with open("agent_logs.jsonl") as f:
    logs = [json.loads(line) for line in f]

# Count phases
from collections import Counter
phases = Counter(log["phase"] for log in logs)
print(phases)
```

#### Exercise 3.2: Add Execution Time Tracking

Measure how long each phase takes.

**Steps**:

1. Add timing to each phase:
```python
def _plan(self, ...):
    start_time = time.time()
    
    # ... existing planning code ...
    
    elapsed = time.time() - start_time
    self.logger.log_phase("PLAN", {
        "action_type": plan.get("action_type"),
        "elapsed_ms": round(elapsed * 1000, 2),
        ...
    }, iteration)
```

2. Add to the summary report:
```python
def get_summary(self) -> Dict[str, Any]:
    plan_times = [
        log["data"].get("elapsed_ms", 0) 
        for log in self.logs 
        if log["phase"] == "PLAN"
    ]
    return {
        "total_time": self.elapsed,
        "avg_plan_time_ms": sum(plan_times) / len(plan_times) if plan_times else 0,
        ...
    }
```

#### Exercise 3.3: Create a Summary Report

Generate a human-readable report after each run.

**Steps**:

1. Add a `generate_report` method to `AgentLogger`:
```python
def generate_report(self) -> str:
    """Generate a human-readable session report."""
    
    lines = [
        "=" * 60,
        "AGENT SESSION REPORT",
        "=" * 60,
        "",
        f"Goal: {self.logs[0]['data'].get('goal', 'Unknown')}",
        f"Status: {self.logs[-1]['data'].get('status', 'Unknown')}",
        f"Total Time: {self.elapsed:.2f}s",
        f"Iterations: {self.get_iteration_count()}",
        "",
        "PHASE BREAKDOWN:",
        "-" * 40,
    ]
    
    for log in self.logs:
        if log["phase"] not in ["START", "COMPLETE"]:
            lines.append(f"  [{log['phase']}] Iter {log['iteration']}")
    
    lines.extend(["", "=" * 60])
    return "\n".join(lines)
```

2. Print the report at session end:
```python
def complete(self, result):
    ...
    if self.verbose:
        print(self.generate_report())
```

---

## Extension Ideas

Once you've completed the tasks, try these advanced extensions:

### 1. Add Vector Search

Replace keyword search with semantic search:
- Use OpenAI embeddings: `text-embedding-3-small`
- Store embeddings in a simple JSON file or use a vector DB
- Calculate cosine similarity for retrieval

### 2. Implement Conversation Memory

Make the agent remember across sessions:
- Save conversation history to a file
- Load previous context on startup
- Implement "remember" and "forget" commands

### 3. Add Web Search Tool

Integrate real web search:
- Use Tavily API (free tier available)
- Or use SerpAPI for Google results
- Parse and summarize results

### 4. Build a Streamlit UI

Create a visual interface:
- Text input for goals
- Real-time log display
- History of conversations

### 5. Multi-Agent System

Create specialized agents that work together:
- Researcher agent: finds information
- Analyzer agent: processes data
- Writer agent: generates responses

---

## Troubleshooting

### Common Issues

**"OPENAI_API_KEY not found"**
```bash
# Make sure .env file exists and has the key
cat .env
# Should show: OPENAI_API_KEY=sk-...
```

**"Rate limit exceeded"**
- Wait a few seconds between runs
- Use `gpt-4o-mini` instead of `gpt-4o` (cheaper, faster)
- Add retry with exponential backoff

**"JSON parse error"**
- The LLM sometimes outputs invalid JSON
- Check the `_parse_json_response` method for error handling
- Lower temperature for more consistent outputs

**"Tool not found"**
- Check tool name spelling in your prompt
- Ensure tool is registered in `_register_default_tools`

### Debugging Tips

1. **Enable verbose mode**: `AgentConfig(verbose=True)`
2. **Print LLM responses**: Add `print(response_text)` in `_plan`
3. **Check tool results**: Log full tool outputs before summarizing
4. **Use smaller goals**: Test with simple queries first

---

## Resources

### Documentation

- [OpenAI API Docs](https://platform.openai.com/docs)
- [OpenAI Function Calling](https://platform.openai.com/docs/guides/function-calling)
- [LangChain Agents](https://python.langchain.com/docs/modules/agents/)

### Articles

- [Building LLM Agents](https://www.anthropic.com/research/building-effective-agents)
- [RAG Explained](https://www.pinecone.io/learn/retrieval-augmented-generation/)
- [Agent Design Patterns](https://lilianweng.github.io/posts/2023-06-23-agent/)

### Videos

- [Andrej Karpathy - Intro to LLMs](https://www.youtube.com/watch?v=zjkBMFhNj_g)
- [AI Agents Course - DeepLearning.AI](https://www.deeplearning.ai/short-courses/)

### Tools & Frameworks

- [LangChain](https://langchain.com/) - Popular agent framework
- [AutoGen](https://microsoft.github.io/autogen/) - Multi-agent framework
- [CrewAI](https://crewai.com/) - Multi-agent orchestration

---

## Summary

You've learned:

1. **Agent Architecture**: SENSE → PLAN → ACT → OBSERVE → REFLECT loop
2. **Tools**: How agents extend their capabilities with functions
3. **Memory**: Short-term and long-term context management
4. **RAG**: Grounding LLM responses in retrieved knowledge
5. **Logging**: Observability for debugging and improvement

The key insight: **AI agents are just loops that use LLMs to decide what to do next**.

Everything else - tools, memory, RAG - are ways to give the LLM more context and capabilities. Start simple, add complexity as needed, and always maintain visibility into what your agent is doing.

Happy building! 🚀

