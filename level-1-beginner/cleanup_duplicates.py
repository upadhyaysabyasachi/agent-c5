#!/usr/bin/env python3
"""
Cleanup script to remove duplicate memories from Supabase.

This script:
1. Fetches all memories from the database
2. Identifies duplicates using semantic similarity
3. Keeps the most recent version of each duplicate group
4. Deletes older duplicates
"""

import os
import sys
import json
from typing import List, Dict, Any, Set
from dotenv import load_dotenv
from supabase import create_client
from openai import OpenAI
import numpy as np

load_dotenv()

def normalize_embedding(embedding) -> List[float]:
    """Normalize embedding to a list of floats, handling different storage formats."""
    if embedding is None:
        raise ValueError("Embedding is None")
    
    # If it's already a list of numbers, return as is
    if isinstance(embedding, list):
        # Check if all elements are already floats/ints
        if all(isinstance(x, (int, float)) for x in embedding):
            return [float(x) for x in embedding]
        # If it's a list of strings, try to parse them
        if all(isinstance(x, str) for x in embedding):
            try:
                return [float(x) for x in embedding]
            except (ValueError, TypeError):
                pass
    
    # If it's a string, try to parse as JSON
    if isinstance(embedding, str):
        try:
            parsed = json.loads(embedding)
            if isinstance(parsed, list):
                return [float(x) for x in parsed]
        except (json.JSONDecodeError, ValueError, TypeError):
            pass
    
    # If it's a numpy array, convert to list
    if isinstance(embedding, np.ndarray):
        return embedding.tolist()
    
    # Last resort: try to convert directly
    try:
        return [float(x) for x in embedding]
    except (TypeError, ValueError) as e:
        raise ValueError(f"Unable to normalize embedding: {type(embedding)} - {str(e)}")

def cosine_similarity(a, b) -> float:
    """Calculate cosine similarity between two vectors."""
    # Normalize embeddings to ensure they're lists of floats
    a_normalized = normalize_embedding(a)
    b_normalized = normalize_embedding(b)
    
    # Convert to numpy arrays with explicit float dtype
    a_np = np.array(a_normalized, dtype=np.float32)
    b_np = np.array(b_normalized, dtype=np.float32)
    
    # Calculate cosine similarity
    dot_product = np.dot(a_np, b_np)
    norm_a = np.linalg.norm(a_np)
    norm_b = np.linalg.norm(b_np)
    
    # Avoid division by zero
    if norm_a == 0 or norm_b == 0:
        return 0.0
    
    return float(dot_product / (norm_a * norm_b))

class DuplicateCleaner:
    def __init__(self, dry_run: bool = True):
        """
        Initialize the duplicate cleaner.

        Args:
            dry_run: If True, only show what would be deleted without actually deleting
        """
        self.dry_run = dry_run

        # Initialize Supabase
        url = os.getenv("SUPABASE_URL")
        key = os.getenv("SUPABASE_KEY")
        if not url or not key:
            raise ValueError("Supabase credentials missing in .env")
        self.supabase = create_client(url, key)

        # Initialize OpenAI (for backup embedding generation if needed)
        openai_key = os.getenv("OPENAI_API_KEY")
        if openai_key:
            self.openai = OpenAI(api_key=openai_key)
        else:
            self.openai = None

    def fetch_all_memories(self) -> List[Dict[str, Any]]:
        """Fetch all memories from the database."""
        print("\n📥 Fetching all memories from database...")
        try:
            response = self.supabase.table("memories").select("*").execute()
            memories = response.data
            print(f"   ✅ Found {len(memories)} total memories")
            return memories
        except Exception as e:
            print(f"   ❌ Error fetching memories: {str(e)}")
            return []

    def find_duplicate_groups(self, memories: List[Dict[str, Any]],
                             threshold: float = 0.90) -> List[List[Dict[str, Any]]]:
        """
        Find groups of duplicate memories based on embedding similarity.

        Args:
            memories: List of memory records
            threshold: Similarity threshold (0.90 = 90% similar)

        Returns:
            List of duplicate groups, each group contains similar memories
        """
        print(f"\n🔍 Analyzing memories for duplicates (threshold: {threshold})...")

        duplicate_groups = []
        processed_ids: Set[int] = set()

        for i, memory_a in enumerate(memories):
            if memory_a['id'] in processed_ids:
                continue

            # Start a new group with this memory
            group = [memory_a]

            # Compare with all other memories
            for j, memory_b in enumerate(memories):
                if i == j or memory_b['id'] in processed_ids:
                    continue

                # Calculate similarity
                try:
                    embedding_a = memory_a.get('embedding')
                    embedding_b = memory_b.get('embedding')
                    
                    # Skip if embeddings are missing
                    if embedding_a is None or embedding_b is None:
                        continue

                    similarity = cosine_similarity(embedding_a, embedding_b)

                    if similarity >= threshold:
                        group.append(memory_b)
                        processed_ids.add(memory_b['id'])

                except ValueError as e:
                    # More detailed error for debugging
                    print(f"   ⚠️  Error comparing memories {memory_a.get('id')} and {memory_b.get('id')}: {str(e)}")
                    continue
                except Exception as e:
                    print(f"   ⚠️  Unexpected error comparing memories {memory_a.get('id')} and {memory_b.get('id')}: {str(e)}")
                    continue

            # If group has more than 1 memory, it's a duplicate group
            if len(group) > 1:
                duplicate_groups.append(group)
                processed_ids.add(memory_a['id'])

        print(f"   ✅ Found {len(duplicate_groups)} duplicate groups")
        return duplicate_groups

    def select_memories_to_delete(self, duplicate_groups: List[List[Dict[str, Any]]]) -> List[int]:
        """
        Select which memories to delete from each duplicate group.
        Keeps the most recent one, deletes older ones.

        Args:
            duplicate_groups: List of duplicate groups

        Returns:
            List of memory IDs to delete
        """
        print("\n📋 Selecting memories to delete...")

        to_delete = []

        for group in duplicate_groups:
            # Sort by created_at timestamp (most recent first)
            sorted_group = sorted(group, key=lambda x: x.get('created_at', ''), reverse=True)

            # Keep the first (most recent), delete the rest
            keep = sorted_group[0]
            delete = sorted_group[1:]

            print(f"\n   Group of {len(group)} duplicates:")
            print(f"   📌 KEEP:   ID {keep['id']} - {keep['content'][:60]}...")
            print(f"            Created: {keep.get('created_at', 'unknown')}")

            for mem in delete:
                print(f"   🗑️  DELETE: ID {mem['id']} - {mem['content'][:60]}...")
                print(f"            Created: {mem.get('created_at', 'unknown')}")
                to_delete.append(mem['id'])

        return to_delete

    def delete_memories(self, memory_ids: List[int]) -> int:
        """
        Delete memories by ID.

        Args:
            memory_ids: List of memory IDs to delete

        Returns:
            Number of successfully deleted memories
        """
        if not memory_ids:
            print("\n✅ No memories to delete!")
            return 0

        print(f"\n🗑️  Deleting {len(memory_ids)} duplicate memories...")

        if self.dry_run:
            print("   ⚠️  DRY RUN MODE - No actual deletions performed")
            print(f"   Would delete IDs: {memory_ids}")
            return len(memory_ids)

        deleted_count = 0
        failed_count = 0

        for mem_id in memory_ids:
            try:
                self.supabase.table("memories").delete().eq("id", mem_id).execute()
                deleted_count += 1
                print(f"   ✅ Deleted memory ID {mem_id}")
            except Exception as e:
                failed_count += 1
                print(f"   ❌ Failed to delete memory ID {mem_id}: {str(e)}")

        print(f"\n   ✅ Successfully deleted: {deleted_count}")
        if failed_count > 0:
            print(f"   ❌ Failed to delete: {failed_count}")

        return deleted_count

    def run(self, threshold: float = 0.90):
        """
        Run the complete cleanup process.

        Args:
            threshold: Similarity threshold for detecting duplicates (default 0.90)
        """
        print("="*60)
        print("🧹 DUPLICATE MEMORY CLEANUP")
        print("="*60)

        if self.dry_run:
            print("\n⚠️  RUNNING IN DRY RUN MODE")
            print("   No changes will be made to the database")
        else:
            print("\n⚠️  RUNNING IN LIVE MODE")
            print("   Duplicates WILL BE DELETED from the database")

            response = input("\n   Are you sure you want to continue? (yes/no): ")
            if response.lower() != "yes":
                print("\n   ❌ Cleanup cancelled")
                return

        # Step 1: Fetch all memories
        memories = self.fetch_all_memories()
        if not memories:
            print("\n   No memories found in database")
            return

        # Step 2: Find duplicate groups
        duplicate_groups = self.find_duplicate_groups(memories, threshold)
        if not duplicate_groups:
            print("\n✅ No duplicates found! Database is clean.")
            return

        # Step 3: Select memories to delete
        to_delete = self.select_memories_to_delete(duplicate_groups)

        # Step 4: Delete duplicates
        deleted_count = self.delete_memories(to_delete)

        # Summary
        print("\n" + "="*60)
        print("📊 CLEANUP SUMMARY")
        print("="*60)
        print(f"Total memories:        {len(memories)}")
        print(f"Duplicate groups:      {len(duplicate_groups)}")
        print(f"Duplicates to remove:  {len(to_delete)}")
        print(f"Memories after cleanup: {len(memories) - deleted_count}")
        print("="*60)

        if self.dry_run:
            print("\n💡 To perform actual cleanup, run with --live flag:")
            print("   python cleanup_duplicates.py --live")

def main():
    import argparse

    parser = argparse.ArgumentParser(
        description="Clean up duplicate memories from Supabase database"
    )
    parser.add_argument(
        "--live",
        action="store_true",
        help="Actually delete duplicates (default is dry-run mode)"
    )
    parser.add_argument(
        "--threshold",
        type=float,
        default=0.90,
        help="Similarity threshold for duplicate detection (0.0-1.0, default: 0.90)"
    )

    args = parser.parse_args()

    # Create cleaner
    cleaner = DuplicateCleaner(dry_run=not args.live)

    # Run cleanup
    try:
        cleaner.run(threshold=args.threshold)
    except KeyboardInterrupt:
        print("\n\n⚠️  Cleanup interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n❌ Cleanup failed: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()
