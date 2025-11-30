import json
import os

# Load the provided sample knowledge base
try:
    with open("sample_knowledge_base.json", "r") as f:
        KNOWLEDGE_BASE = json.load(f)
except FileNotFoundError:
    # Fallback if file isn't moved yet
    KNOWLEDGE_BASE = []

def search_knowledge_base(query: str) -> str:
    """
    Search the internal company knowledge base for policies and guides.
    Performs flexible keyword matching by splitting query into words.
    """
    query = query.lower()

    # Split query into individual words for better matching
    query_words = [word.strip() for word in query.split() if len(word.strip()) > 2]

    if not query_words:
        return "No relevant documents found in the internal knowledge base."

    results = []

    for item in KNOWLEDGE_BASE:
        title_lower = item["title"].lower()
        content_lower = item["content"].lower()

        # Check if any query word matches title or content
        for word in query_words:
            if word in title_lower or word in content_lower:
                results.append(f"Title: {item['title']}\nContent: {item['content']}")
                break  # Only add each document once

    if not results:
        return f"No relevant documents found for query: '{query}'. Try simpler or different keywords."

    return "\n\n".join(results[:3])

# Tool Definitions for the Agent
TOOLS = {
    "search_knowledge_base": {
        "description": "Search internal company documents (policies, how-to guides). Use this for 'how to', 'what is', or policy questions.",
        "function": search_knowledge_base
    }
}