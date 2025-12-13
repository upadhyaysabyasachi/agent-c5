Project Structure
level-2-opt-assistant/
├── README.md
├── agent/
│   ├── __init__.py
│   ├── core.py              # Main agent
├── tools/
│   ├── __init__.py
│   ├── discovery_tool.py    # OPT discovery questions
│   ├── analysis_tool.py     # Task analysis and suggestion
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
│   └── conversation_memory.py
├── tests/
│   ├── test_discovery.py
│   ├── test_masterplan.py
│   └── test_scenarios.py
├── examples/
│   ├── sample_session_1.json
│   └── sample_session_2.json
└── requirements.txt
