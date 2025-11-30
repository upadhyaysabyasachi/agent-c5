#!/usr/bin/env python3
"""
Verification script to check Supabase setup for the agent.
Tests:
1. Connection to Supabase
2. Memories table exists with correct schema
3. match_memories RPC function exists
4. Basic memory operations work
"""

import os
import sys
from dotenv import load_dotenv
from supabase import create_client

load_dotenv()

def test_connection():
    """Test basic connection to Supabase."""
    print("\n" + "="*60)
    print("🔍 SUPABASE SETUP VERIFICATION")
    print("="*60)

    url = os.getenv("SUPABASE_URL")
    key = os.getenv("SUPABASE_KEY")

    print("\n1️⃣  Checking credentials...")
    if not url or not key:
        print("   ❌ FAIL: SUPABASE_URL or SUPABASE_KEY not found in .env")
        return None

    print(f"   ✅ Found SUPABASE_URL: {url}")
    print(f"   ✅ Found SUPABASE_KEY: {key[:20]}...")

    print("\n2️⃣  Testing connection...")
    try:
        supabase = create_client(url, key)
        print("   ✅ Connection established")
        return supabase
    except Exception as e:
        print(f"   ❌ FAIL: {str(e)}")
        return None

def test_memories_table(supabase):
    """Check if memories table exists and has correct structure."""
    print("\n3️⃣  Checking 'memories' table...")

    try:
        # Try to query the table (will fail if table doesn't exist)
        response = supabase.table("memories").select("*").limit(1).execute()
        print("   ✅ Table 'memories' exists")

        # Check if we can see the structure
        if response.data:
            print(f"   ✅ Table has data ({len(response.data)} sample row)")
            sample = response.data[0]
            print(f"   📊 Sample columns: {', '.join(sample.keys())}")

            # Verify required columns
            required_cols = ["content", "metadata", "embedding"]
            missing = [col for col in required_cols if col not in sample.keys()]
            if missing:
                print(f"   ⚠️  WARNING: Missing columns: {', '.join(missing)}")
            else:
                print(f"   ✅ All required columns present: {', '.join(required_cols)}")
        else:
            print("   ℹ️  Table is empty (no data yet)")
            print("   ⚠️  Cannot verify column structure without data")

        return True
    except Exception as e:
        print(f"   ❌ FAIL: {str(e)}")
        return False

def test_match_memories_function(supabase):
    """Check if match_memories RPC function exists."""
    print("\n4️⃣  Checking 'match_memories' RPC function...")

    try:
        # Create a dummy embedding (1536 dimensions for text-embedding-3-small)
        dummy_embedding = [0.0] * 1536

        # Try calling the RPC function
        response = supabase.rpc(
            "match_memories",
            {
                "query_embedding": dummy_embedding,
                "match_threshold": 0.75,
                "match_count": 1
            }
        ).execute()

        print("   ✅ RPC function 'match_memories' exists and is callable")
        print(f"   📊 Returned {len(response.data)} results")
        return True
    except Exception as e:
        error_msg = str(e)
        if "function match_memories" in error_msg.lower() or "does not exist" in error_msg.lower():
            print(f"   ❌ FAIL: RPC function 'match_memories' does not exist")
            print(f"   ℹ️  Error: {error_msg}")
        else:
            print(f"   ⚠️  Function exists but error occurred: {error_msg}")
        return False

def test_memory_operations():
    """Test the actual Memory class operations."""
    print("\n5️⃣  Testing Memory class operations...")

    try:
        from memory import Memory
        print("   ✅ Memory class imported successfully")

        # Test initialization
        try:
            memory = Memory()
            print("   ✅ Memory initialized successfully")
        except ValueError as e:
            print(f"   ❌ FAIL: {str(e)}")
            return False
        except Exception as e:
            print(f"   ❌ FAIL: OpenAI initialization error: {str(e)}")
            return False

        # Test embedding generation
        print("\n   Testing embedding generation...")
        try:
            test_text = "This is a test"
            embedding = memory.get_embedding(test_text)
            print(f"   ✅ Generated embedding (dimension: {len(embedding)})")

            if len(embedding) != 1536:
                print(f"   ⚠️  WARNING: Expected 1536 dimensions, got {len(embedding)}")
        except Exception as e:
            print(f"   ❌ FAIL: {str(e)}")
            return False

        # Test search (should work even if no memories exist)
        print("\n   Testing memory search...")
        try:
            results = memory.search_memory("test query")
            print(f"   ✅ Search executed (found {len(results)} results)")
        except Exception as e:
            print(f"   ❌ FAIL: {str(e)}")
            return False

        return True
    except ImportError as e:
        print(f"   ❌ FAIL: Cannot import Memory class: {str(e)}")
        return False
    except Exception as e:
        print(f"   ❌ FAIL: Unexpected error: {str(e)}")
        return False

def main():
    # Test connection
    supabase = test_connection()
    if not supabase:
        print("\n" + "="*60)
        print("❌ VERIFICATION FAILED: Cannot connect to Supabase")
        print("="*60)
        sys.exit(1)

    # Test table
    table_ok = test_memories_table(supabase)

    # Test RPC function
    rpc_ok = test_match_memories_function(supabase)

    # Test memory operations
    memory_ok = test_memory_operations()

    # Summary
    print("\n" + "="*60)
    print("📋 VERIFICATION SUMMARY")
    print("="*60)
    print(f"Connection:         {'✅ PASS' if supabase else '❌ FAIL'}")
    print(f"memories table:     {'✅ PASS' if table_ok else '❌ FAIL'}")
    print(f"match_memories RPC: {'✅ PASS' if rpc_ok else '❌ FAIL'}")
    print(f"Memory operations:  {'✅ PASS' if memory_ok else '❌ FAIL'}")
    print("="*60)

    if supabase and table_ok and rpc_ok and memory_ok:
        print("\n✅ ALL CHECKS PASSED - Supabase is configured correctly!")
        print("   You can run the agent with: python test_cases.py")
    else:
        print("\n❌ SOME CHECKS FAILED - Please fix the issues above")
        if not table_ok:
            print("\n📝 To create the memories table, run this SQL in Supabase:")
            print("""
CREATE TABLE memories (
    id BIGSERIAL PRIMARY KEY,
    content TEXT NOT NULL,
    metadata JSONB,
    embedding VECTOR(1536),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX ON memories USING ivfflat (embedding vector_cosine_ops);
""")
        if not rpc_ok:
            print("\n📝 To create the match_memories function, run this SQL in Supabase:")
            print("""
CREATE OR REPLACE FUNCTION match_memories(
    query_embedding VECTOR(1536),
    match_threshold FLOAT,
    match_count INT
)
RETURNS TABLE (
    id BIGINT,
    content TEXT,
    metadata JSONB,
    similarity FLOAT
)
LANGUAGE SQL
AS $$
    SELECT
        id,
        content,
        metadata,
        1 - (embedding <=> query_embedding) AS similarity
    FROM memories
    WHERE 1 - (embedding <=> query_embedding) > match_threshold
    ORDER BY embedding <=> query_embedding
    LIMIT match_count;
$$;
""")
    print()

if __name__ == "__main__":
    main()
