import os
import sys
from dotenv import load_dotenv
from agent.orchestrator import SalesOrchestrator

# Load environment variables
load_dotenv()

def check_env():
    required = ["GROQ_API_KEY", "TAVILY_API_KEY", "SUPABASE_URL", "SUPABASE_KEY"]
    optional = ["ELEVENLABS_API_KEY"]
    
    missing = [key for key in required if not os.getenv(key)]
    if missing:
        print(f"❌ Missing Required Environment Variables: {', '.join(missing)}")
        sys.exit(1)
    
    # Warn about optional but recommended keys
    missing_optional = [key for key in optional if not os.getenv(key)]
    if missing_optional:
        print(f"⚠️  Optional Environment Variables (features will be limited): {', '.join(missing_optional)}")
        print("   Note: ELEVENLABS_API_KEY is needed for voice call features")

if __name__ == "__main__":
    check_env()
    
    print("\n🚀 Enterprise Sales Agent (Level 3) Initializing...")
    
    # Initialize the main brain
    orchestrator = SalesOrchestrator()
    
    # Start the CLI Loop
    orchestrator.run_cli()