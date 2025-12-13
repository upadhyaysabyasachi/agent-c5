# OPT Assistant - AI Automation Agent

An intelligent automation consultant that uses the **OPT Framework** (Operating Model → Process → Task) to help businesses identify and build automation solutions.

## 🎯 What is OPT Framework?

The OPT Framework is a structured approach to automation:

- **Operating Model**: Understanding what you do and how you make money
- **Process**: Identifying high-level workflows
- **Task**: Finding specific repetitive tasks that can be automated

## 🚀 Features

- **Discovery Phase**: Asks targeted questions to understand your business
- **Analysis Phase**: Identifies high-ROI automation opportunities
- **Masterplan Generation**: Creates comprehensive implementation plans
- **Code Generation**: Generates production-ready Python automation scripts
- **Deployment Instructions**: Provides setup and deployment guidance

## 📋 Project Structure

```
level-2-opt-assistant/
├── README.md
├── main.py                    # Entry point
├── agent/
│   ├── __init__.py
│   └── core.py               # Main OPT agent
├── tools/
│   ├── __init__.py
│   ├── discovery_tool.py     # OPT discovery questions
│   ├── analysis_tool.py      # Task analysis and suggestions
│   ├── masterplan_tool.py   # Masterplan generation
│   ├── code_gen_tool.py     # Python code generation
│   └── deployment_tool.py   # Deployment instructions
├── prompts/
│   ├── __init__.py
│   ├── opt_coach.py         # OPT coaching prompts
│   ├── task_analysis.py     # Task analysis prompts
│   └── code_generation.py   # Code generation prompts
├── memory/
│   ├── __init__.py
│   └── conversation_memory.py # Conversation state management
├── tests/
│   ├── test_discovery.py
│   ├── test_masterplan.py
│   └── test_scenarios.py
├── examples/
│   ├── sample_session_1.json
│   └── sample_session_2.json
└── requirements.txt
```

## 🛠️ Installation

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Setup Environment Variables

Create a `.env` file in the project root:

```bash
# Required
GROQ_API_KEY=your_groq_api_key_here

# Optional (for advanced features)
OPENAI_API_KEY=your_openai_api_key_here
```

Get your Groq API key from: [console.groq.com/keys](https://console.groq.com/keys)

### 3. Run the Agent

```bash
python main.py
```

## 💡 Usage Example

```
🤖 AI Automation Agent Initialized (OPT Framework)
Tell me about your business! (e.g., 'I run a newsletter for dog owners')

You: I run a YouTube channel about cooking
Agent: That's great! Can you tell me more about your typical workflow?

You: I film, edit, create thumbnails, and upload videos
Agent: Which step takes the most time?

You: Writing video descriptions is really tedious
Agent: Perfect! I've identified automation opportunities...
```

## 🔄 Workflow Phases

### 1. Discovery Phase
- Gathers information about your business
- Identifies operating model, processes, and tasks
- Asks targeted questions to understand pain points

### 2. Analysis Phase
- Analyzes tasks for automation potential
- Calculates ROI and time savings
- Suggests top automation opportunities

### 3. Code Generation Phase
- Generates production-ready Python scripts
- Includes error handling and logging
- Provides deployment instructions

## 🧪 Testing

Run the test suite:

```bash
# Run all tests
python -m pytest tests/

# Run specific test file
python -m pytest tests/test_discovery.py
python -m pytest tests/test_masterplan.py
python -m pytest tests/test_scenarios.py
```

Or use unittest:

```bash
python -m unittest discover tests
```

## 📚 Examples

Check out example sessions in the `examples/` directory:
- `sample_session_1.json`: Content creator automation
- `sample_session_2.json`: E-commerce inventory automation

## 🛠️ Tools Overview

### DiscoveryTool
Conducts structured discovery using OPT framework questions.

```python
from tools.discovery_tool import DiscoveryTool

question = DiscoveryTool.get_next_question(context)
is_complete = DiscoveryTool.is_discovery_complete(context)
```

### AnalysisTool
Analyzes tasks and suggests automation opportunities.

```python
from tools.analysis_tool import AnalysisTool

suggestions = AnalysisTool.analyze_tasks(opt_data)
formatted = AnalysisTool.format_suggestions(suggestions)
```

### MasterplanTool
Generates comprehensive automation masterplans.

```python
from tools.masterplan_tool import MasterplanTool

masterplan = MasterplanTool.generate_masterplan(opt_data, selected_task)
formatted = MasterplanTool.format_masterplan(masterplan)
```

### DeploymentTool
Provides deployment instructions and setup guidance.

```python
from tools.deployment_tool import DeploymentTool

instructions = DeploymentTool.generate_deployment_instructions(
    script_path="automation.py",
    dependencies=["requests", "pandas"]
)
```

## 🎓 How It Works

1. **State Machine**: The agent uses a state machine to track conversation phases
2. **Memory Management**: ConversationMemory maintains context and OPT data
3. **Tool Integration**: Each phase uses specialized tools for its function
4. **LLM Integration**: Uses Groq's LLM for natural language understanding and generation

## 🔧 Customization

### Adding New Tools

1. Create a new tool file in `tools/`
2. Implement tool functions
3. Import in `tools/__init__.py`
4. Integrate into agent workflow in `agent/core.py`

### Modifying Prompts

Edit prompt files in `prompts/`:
- `opt_coach.py`: Main coaching prompts
- `task_analysis.py`: Analysis prompts
- `code_generation.py`: Code generation prompts

## 📝 Generated Files

Automation scripts are saved to:
```
generated_automations/
├── automation_1234567890.py
├── automation_1234567891.py
└── ...
```

## 🐛 Troubleshooting

### "GROQ_API_KEY not found"
- Make sure `.env` file exists in project root
- Verify the key is correctly formatted

### "Module not found" errors
- Run `pip install -r requirements.txt`
- Check Python path and virtual environment

### Code generation issues
- Check that the conversation context is complete
- Verify the selected task is clear and specific

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Add tests for new features
4. Submit a pull request

## 📄 License

This project is part of the agent-c5 learning series.

## 🔗 Resources

- [Groq Cloud API](https://console.groq.com/docs)
- [OPT Framework Documentation](https://example.com/opt-framework)
- [Python Best Practices](https://docs.python.org/3/tutorial/)

---

**Happy Automating!** 🚀

