level-3-enterprise-sales-agent/
├── .env                    # API Keys (Groq, Tavily, Supabase, ElevenLabs)
├── main.py                 # Entry point
├── database_schema.sql     # Supabase SQL setup
├── agent/
│   ├── __init__.py
│   ├── orchestrator.py     # Main State Machine
│   ├── icp_builder.py      # Phase 1: ICP Definition
│   ├── discovery.py        # Phase 2: Lead Finding
│   ├── qualification.py    # Phase 3: Frameworks (BANT/MEDDIC)
│   ├── engagement.py       # Phase 4: Email/Voice Logic
│   └── crm.py              # Phase 5: Handoff
├── tools/
│   ├── search_tool.py      # Tavily integration
│   └── voice_tool.py       # ElevenLabs Stub
└── config/
    └── frameworks.json     # BANT, MEDDIC definitions