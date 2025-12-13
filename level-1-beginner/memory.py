import os
import json
from typing import List, Dict, Any
from supabase import create_client, Client
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

class Memory:
    def __init__(self):
        # Initialize Supabase
        url = os.environ.get("SUPABASE_URL")
        key = os.environ.get("SUPABASE_KEY")
        if not url or not key:
            raise ValueError("Supabase credentials missing in .env")
        self.supabase: Client = create_client(url, key)

        # Initialize OpenAI for Embeddings
        openai_key = os.environ.get("OPENAI_API_KEY")
        if not openai_key:
            raise ValueError("OPENAI_API_KEY missing in .env")
        self.openai = OpenAI(api_key=openai_key)

    def get_embedding(self, text: str) -> List[float]:
        """Convert text to a vector using OpenAI with error handling."""
        try:
            text = text.replace("\n", " ")
            response = self.openai.embeddings.create(input=[text], model="text-embedding-3-small")
            return response.data[0].embedding
        except Exception as e:
            print(f"⚠️  OpenAI embedding error: {str(e)}")
            raise RuntimeError(f"Failed to generate embedding: {str(e)}")

    def add_memory(self, user_question: str, agent_answer: str):
        """Store a Q&A pair in the database with duplicate detection."""
        try:
            content = f"Question: {user_question}\nAnswer: {agent_answer}"

            # Check for duplicates using high similarity threshold
            existing_memories = self.search_memory(user_question, threshold=0.90)

            if existing_memories:
                # Very similar memory already exists, skip insertion
                print(f"💭 Similar memory exists, skipping: {user_question[:30]}...")
                return

            # No duplicate found, proceed with insertion
            embedding = self.get_embedding(content)

            data = {
                "content": content,
                "metadata": {"type": "conversation", "question": user_question},
                "embedding": embedding
            }

            self.supabase.table("memories").insert(data).execute()
            print(f"💾 Memory stored: {user_question[:30]}...")
        except Exception as e:
            print(f"⚠️  Failed to store memory: {str(e)}")
            # Don't crash the agent, just log the error

    def search_memory(self, query: str, threshold: float = 0.75) -> List[str]:
        """Search for relevant past interactions with error handling."""
        try:
            query_embedding = self.get_embedding(query)

            response = self.supabase.rpc(
                "match_memories",
                {
                    "query_embedding": query_embedding,
                    "match_threshold": threshold,
                    "match_count": 3
                }
            ).execute()

            # Handle empty or None responses
            if not response or not response.data:
                return []

            # Extract just the text content
            return [item['content'] for item in response.data if item and 'content' in item]
        except Exception as e:
            print(f"⚠️  Memory search failed: {str(e)}")
            # Return empty list instead of crashing
            return []