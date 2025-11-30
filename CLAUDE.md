# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Agent Core (agent-c5) is a minimal, extensible AI agent implementation using the SENSE-PLAN-ACT-OBSERVE-REFLECT (SPOAR) pattern. The repository contains two progressively advanced agent implementations demonstrating different architectural patterns and capabilities.

## Code Architecture

### Two-Tier Implementation Structure

**1. Simple Agent (`simple_agent.py`)**
- Self-contained, single-file implementation (~350 lines)
- Uses Groq Cloud's `openai/gpt-oss-120b` model
- Demonstrates core SPOAR loop without external dependencies beyond LLM
- Tools defined inline as dictionary of functions
- No persistent memory between sessions
- Includes Tavily web search integration

**2. Level-1 Beginner Agent (`level-1-beginner/`)**
- Modular, production-ready architecture split across:
  - `agent.py`: Main agent class implementing SPOAR loop
  - `memory.py`: RAG-based memory system using Supabase vector DB
  - `tools.py`: Tool definitions and knowledge base search
  - `test_cases.py`: Test harness demonstrating memory persistence
- Uses Groq Cloud's `llama-3.3-70b-versatile` model
- Implements semantic memory search with OpenAI embeddings
- Demonstrates memory reuse across sessions (RAG pattern)
- Searches `sample_knowledge_base.json` for internal documentation

### The SPOAR Loop Pattern

All agents follow the five-phase reasoning loop:

1. **SENSE**: Gather current context (goal, available tools, past actions, relevant memories)
2. **PLAN**: LLM decides next action (USE_TOOL or COMPLETE) in structured JSON format
3. **ACT**: Execute the planned tool with specified arguments
4. **OBSERVE**: Record action results and success/failure status
5. **REFLECT**: LLM evaluates progress and determines next steps

This pattern is implemented in both agents but with different levels of sophistication.

### Memory Architecture (Level-1)

The memory system uses a RAG (Retrieval Augmented Generation) pattern:

- **Storage**: Supabase PostgreSQL with pgvector extension
- **Embeddings**: OpenAI `text-embedding-3-small` model (1536 dimensions)
- **Search**: Semantic similarity search via Supabase RPC function `match_memories`
- **Format**: Stores "Question: {user_query}\nAnswer: {agent_response}" as single content field
- **Threshold**: Default similarity threshold of 0.75 for relevance filtering
- **Retrieval**: Top 3 most relevant past interactions included in SENSE phase

Memory is checked BEFORE planning, allowing the agent to reuse previous answers for similar questions.

### Tool System

Tools are defined as dictionaries with:
- `description`: What the tool does (shown to LLM for selection)
- `function`: Python callable with named parameters

The LLM outputs tool calls as JSON with `tool` name and `args` dictionary. The agent framework handles execution and error handling.

## Development Commands

### Environment Setup

```bash
# Copy environment template
cp env.example .env

# Edit .env and add required keys:
# - GROQ_API_KEY (required for both agents)
# - TAVILY_API_KEY (optional, for web search in simple agent)
# - SUPABASE_URL, SUPABASE_KEY (required for level-1 agent)
# - OPENAI_API_KEY (required for level-1 agent embeddings)
```

### Install Dependencies

```bash
# For simple agent
pip install groq python-dotenv tavily-python

# For level-1 agent (includes simple agent deps)
pip install -r level-1-beginner/requirements.txt
```

### Running Agents

```bash
# Run simple agent (edit goal in file first)
python simple_agent.py

# Run level-1 agent with test cases
cd level-1-beginner
python test_cases.py

# Run level-1 agent directly
cd level-1-beginner
python agent.py  # modify file to add agent instantiation and run call
```

### Testing Memory System

The level-1 agent's test suite demonstrates memory persistence:
- Test 1: First query searches knowledge base (no memory yet)
- Test 2: Similar query reuses stored memory (semantic match)
- Test 3: New topic triggers fresh search

## Key Implementation Details

### JSON Parsing from LLM

Both agents implement robust JSON extraction in `_parse_json()`:
- Strips markdown code blocks (`\`\`\`json`)
- Extracts JSON objects from text by finding first `{` and last `}`
- Falls back to safe error response on parse failure
- Never crashes on malformed LLM output

### Error Handling Pattern

Tools return error strings prefixed with "ERROR:" rather than raising exceptions. The OBSERVE phase checks for this prefix to determine success/failure.

### Iteration Limits

- Simple agent: 10 iterations (configurable in `run()`)
- Level-1 agent: 5 iterations (hardcoded in loop)

Prevents infinite loops while allowing multi-step reasoning.

### Logging

- Simple agent: Console output with emoji phase markers (👁️ SENSE, 🧠 PLAN, ⚡ ACT, 📊 OBSERVE, 💭 REFLECT)
- Level-1 agent: JSON logs saved to `logs/agent_log_{timestamp}.json` on completion

## External Services

### Groq Cloud
- API endpoint for fast LLM inference
- Models used: `openai/gpt-oss-120b` (simple), `llama-3.3-70b-versatile` (level-1)
- Get keys at: https://console.groq.com/keys

### Tavily (Optional)
- Web search API for real-time information
- Only used in simple agent's `tavily_search` tool
- Get keys at: https://tavily.com

### Supabase (Level-1 Only)
- PostgreSQL database with pgvector extension
- Requires pre-configured `memories` table with embedding column
- RPC function `match_memories` must exist for similarity search

### OpenAI (Level-1 Only)
- Used exclusively for text embeddings (not chat)
- Model: `text-embedding-3-small`
- Alternative: Could swap for local embeddings (e.g., sentence-transformers)

## Knowledge Base Structure

`sample_knowledge_base.json` contains internal documentation as array of objects:
```json
{
  "id": 1,
  "title": "Document Title",
  "content": "Full text content...",
  "tags": ["topic1", "topic2"],
  "difficulty": "beginner|intermediate|advanced",
  "source": "Source name"
}
```

Search in `tools.py` performs simple lowercase keyword matching on title and content fields.

## Extending the Agents

### Adding New Tools

In simple agent:
```python
TOOLS["new_tool"] = {
    "description": "What it does (shown to LLM)",
    "function": lambda arg1, arg2: "result"
}
```

In level-1 agent (`tools.py`):
```python
def new_tool_function(param: str) -> str:
    # implementation
    return "result"

TOOLS["new_tool"] = {
    "description": "What it does",
    "function": new_tool_function
}
```

Update the PLAN phase prompt to include the new tool in the "AVAILABLE TOOLS" section.

### Swapping LLM Providers

Both agents use Groq's OpenAI-compatible API. To use a different provider:
1. Change the client initialization in `__init__`
2. Update the `model` string to the new model name
3. Ensure API compatibility with `chat.completions.create()` interface

### Enhancing Memory Search

Current implementation uses simple similarity threshold. Consider:
- Hybrid search (semantic + keyword)
- Re-ranking retrieved results
- Metadata filtering (e.g., by date, topic)
- Adjusting `match_count` and `match_threshold` in `memory.py`
