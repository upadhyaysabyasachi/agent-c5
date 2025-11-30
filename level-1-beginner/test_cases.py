import time
import shutil
from agent import SmartLookupAgent

# Ensure we have the knowledge base file in the current directory
try:
    # Attempt to use the uploaded file path logic if running in specific envs, 
    # but for local execution, ensure the user has the file.
    pass 
except:
    print("⚠️  Make sure sample_knowledge_base.json is in this folder!")

def run_tests():
    agent = SmartLookupAgent()
    
    print("\n🔹 TEST 1: First time asking (Should use Tool)")
    q1 = "What is an AI Agent?"
    ans1 = agent.run(q1)
    print(f"Agent Answer: {ans1}\n")
    
    print("Waiting for DB to index...\n")
    time.sleep(2) 
    
    print("\n🔹 TEST 2: Asking again (Should use Memory)")
    # We ask slightly differently to test Semantic Search
    q2 = "Explain what an AI agent is"
    ans2 = agent.run(q2)
    print(f"Agent Answer: {ans2}\n")
    
    print("\n🔹 TEST 3: New Topic")
    q3 = "What is RAG?"
    ans3 = agent.run(q3)
    print(f"Agent Answer: {ans3}\n")

if __name__ == "__main__":
    run_tests()