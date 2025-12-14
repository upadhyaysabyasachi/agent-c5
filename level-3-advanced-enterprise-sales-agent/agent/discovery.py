import os
import json
import time
from typing import List, Dict, Any
from groq import Groq
from dotenv import load_dotenv
from tools.search_tool import SearchTool

load_dotenv()

class DiscoveryEngine:
    """
    Phase 2: Lead Discovery Engine.
    Finds companies matching the Ideal Customer Profile (ICP) using web search.
    """
    
    def __init__(self):
        # Initialize Groq for reasoning and extraction
        self.groq_client = Groq(api_key=os.getenv("GROQ_API_KEY"))
        self.model = "llama-3.3-70b-versatile"
        
        # Initialize search tool (Tavily integration)
        try:
            self.search_tool = SearchTool()
        except (ValueError, ImportError) as e:
            print(f"⚠️  Warning: Search tool initialization failed: {e}")
            self.search_tool = None

    def find_leads(self, icp_profile: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Main entry point: Finds leads matching the ICP.
        
        Args:
            icp_profile: Dictionary containing industry, size, role, pain_points, etc.
            
        Returns:
            List of structured lead dictionaries.
        """
        if not icp_profile:
            print("❌ Error: No ICP profile provided.")
            return []

        print(f"🔎 Analyzing ICP for {icp_profile.get('industry', 'target')} industry...")
        
        # Step 1: Generate Search Queries
        queries = self._generate_search_queries(icp_profile)
        if not queries:
            print("⚠️  Failed to generate search queries.")
            return []
            
        print(f"   Generated {len(queries)} search strategies: {queries}")
        
        all_raw_results = []
        
        # Step 2: Execute Searches (Limit to top 3 queries to save rate limits)
        for query in queries[:3]:
            print(f"   🌐 Searching Web: '{query}'...")
            results = self._execute_search(query)
            if results:
                all_raw_results.extend(results)
            # Brief pause to be polite to APIs
            time.sleep(1)
            
        if not all_raw_results:
            print("❌ No search results found.")
            return []

        # Step 3: Extract & Structure Leads
        print(f"   📊 Processing {len(all_raw_results)} raw results to extract companies...")
        leads = self._extract_leads_from_results(all_raw_results, icp_profile)
        
        # Step 4: Deduplicate (by company name)
        unique_leads = self._deduplicate_leads(leads)
        
        return unique_leads

    def _generate_search_queries(self, icp: Dict[str, Any]) -> List[str]:
        """Uses LLM to create targeted search queries based on ICP."""
        prompt = f"""
        You are a Lead Generation Researcher. Generate 3-5 specific Google search queries to find companies matching this Ideal Customer Profile (ICP).
        
        ICP Profile:
        {json.dumps(icp, indent=2)}
        
        Strategy:
        1. Look for "top companies" lists in the specific vertical.
        2. Look for directories or market maps.
        3. Look for specific technology stacks if mentioned.
        
        Return ONLY a JSON array of strings. Example: ["top fintech startups london", "companies using shopify plus"]
        """
        
        try:
            response = self.groq_client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You output valid JSON arrays only."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3
            )
            return self._parse_json(response.choices[0].message.content)
        except Exception as e:
            print(f"   ⚠️  Query generation failed: {e}")
            return [f"Top {icp.get('industry', 'business')} companies"]

    def _execute_search(self, query: str) -> List[Dict[str, Any]]:
        """Executes search using SearchTool (Tavily integration)."""
        if not self.search_tool:
            return []
            
        try:
            # Use search tool with advanced depth for better lead gen results
            results = self.search_tool.search(
                query=query,
                search_depth="advanced",
                max_results=5
            )
            return results
        except Exception as e:
            print(f"   ❌ Search failed: {str(e)}")
            return []

    def _extract_leads_from_results(self, search_results: List[Dict[str, Any]], icp: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Uses LLM to structure unstructured search results into Lead objects."""
        
        # Prepare context chunks to avoid context window limits
        # We process results in batches if there are many
        
        formatted_results = ""
        for i, res in enumerate(search_results):
            content_snippet = res.get('content', '')[:500] # Truncate long content
            formatted_results += f"--- Source {i+1} ---\nTitle: {res.get('title')}\nURL: {res.get('url')}\nContent: {content_snippet}\n\n"
            
        prompt = f"""
        You are a Lead Data Extractor. Analyze the search results below and extract a list of distinct companies that match the target ICP.
        
        Target ICP: {json.dumps(icp)}
        
        Search Results:
        {formatted_results}
        
        Task:
        1. Identify companies mentioned in the results.
        2. Ignore directories (like Capterra, G2) unless they list specific companies.
        3. Extract key details.
        
        Return a JSON list of objects with this schema:
        {{
            "company_name": "Name",
            "website": "URL (if found or inferable)",
            "industry": "Specific Industry",
            "description": "One sentence description",
            "fit_reason": "Why they match the ICP",
            "source_url": "The Source URL number or link"
        }}
        
        Return ONLY valid JSON.
        """
        
        try:
            response = self.groq_client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "Output valid JSON list of objects only."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.1 # Low temperature for factual extraction
            )
            
            leads = self._parse_json(response.choices[0].message.content)
            
            # Post-processing: Add status field
            for lead in leads:
                lead['status'] = 'new'
                # Ensure employee_count key exists even if empty
                if 'employee_count' not in lead:
                    lead['employee_count'] = "Unknown"
                    
            return leads
            
        except Exception as e:
            print(f"   ⚠️  Lead extraction failed: {e}")
            return []

    def _deduplicate_leads(self, leads: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Removes duplicate companies based on name."""
        unique = {}
        for lead in leads:
            name_key = lead.get('company_name', '').lower().strip()
            if name_key and name_key not in unique:
                unique[name_key] = lead
        return list(unique.values())

    def _parse_json(self, text: str) -> Any:
        """Robust JSON parsing helper."""
        try:
            if not text:
                return []
            
            # Remove markdown code blocks
            if "```json" in text:
                text = text.split("```json")[1].split("```")[0]
            elif "```" in text:
                text = text.split("```")[1].split("```")[0]
                
            return json.loads(text.strip())
        except json.JSONDecodeError:
            print(f"   ⚠️  JSON parse error. Raw text: {text[:50]}...")
            return []
        except Exception as e:
            print(f"   ⚠️  Parse error: {e}")
            return []