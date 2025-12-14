"""
Search Tool - Tavily Integration
Provides web search capabilities for lead discovery and research.
"""

import os
from typing import List, Dict, Any, Optional
from dotenv import load_dotenv

try:
    from tavily import TavilyClient
    TAVILY_AVAILABLE = True
except ImportError:
    TAVILY_AVAILABLE = False
    print("⚠️  Warning: tavily-python package not installed. Search features will be disabled.")

load_dotenv()


class SearchTool:
    """
    Web search tool using Tavily API.
    Provides various search strategies for lead discovery and research.
    """
    
    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize the search tool.
        
        Args:
            api_key: Optional Tavily API key. If not provided, reads from TAVILY_API_KEY env var.
        """
        if not TAVILY_AVAILABLE:
            raise ImportError("tavily-python package is required. Install with: pip install tavily-python")
        
        self.api_key = api_key or os.getenv("TAVILY_API_KEY")
        if not self.api_key:
            raise ValueError("TAVILY_API_KEY not found in environment variables")
        
        self.client = TavilyClient(api_key=self.api_key)
    
    def search(
        self,
        query: str,
        search_depth: str = "advanced",
        max_results: int = 5,
        include_domains: Optional[List[str]] = None,
        exclude_domains: Optional[List[str]] = None
    ) -> List[Dict[str, Any]]:
        """
        Execute a web search using Tavily.
        
        Args:
            query: Search query string
            search_depth: "basic" or "advanced" (advanced provides better results)
            max_results: Maximum number of results to return
            include_domains: Optional list of domains to include
            exclude_domains: Optional list of domains to exclude
            
        Returns:
            List of search result dictionaries with title, url, content, etc.
        """
        try:
            search_params = {
                "query": query,
                "search_depth": search_depth,
                "max_results": max_results
            }
            
            if include_domains:
                search_params["include_domains"] = include_domains
            
            if exclude_domains:
                search_params["exclude_domains"] = exclude_domains
            
            response = self.client.search(**search_params)
            return response.get("results", [])
            
        except Exception as e:
            print(f"❌ Search failed for query '{query}': {str(e)}")
            return []
    
    def search_companies(
        self,
        industry: str,
        location: Optional[str] = None,
        company_size: Optional[str] = None,
        max_results: int = 10
    ) -> List[Dict[str, Any]]:
        """
        Search for companies in a specific industry.
        
        Args:
            industry: Industry or sector to search
            location: Optional location/city/country
            company_size: Optional company size (e.g., "startup", "enterprise")
            max_results: Maximum number of results
            
        Returns:
            List of search results
        """
        # Build query
        query_parts = [f"{industry} companies"]
        
        if location:
            query_parts.append(f"in {location}")
        
        if company_size:
            query_parts.append(company_size)
        
        query = " ".join(query_parts)
        
        return self.search(
            query=query,
            search_depth="advanced",
            max_results=max_results
        )
    
    def search_decision_makers(
        self,
        company_name: str,
        job_title: Optional[str] = None,
        max_results: int = 5
    ) -> List[Dict[str, Any]]:
        """
        Search for decision makers at a specific company.
        
        Args:
            company_name: Name of the company
            job_title: Optional job title (e.g., "VP of Sales", "CTO")
            max_results: Maximum number of results
            
        Returns:
            List of search results
        """
        query_parts = [company_name]
        
        if job_title:
            query_parts.append(job_title)
        else:
            query_parts.append("executives decision makers")
        
        query = " ".join(query_parts)
        
        return self.search(
            query=query,
            search_depth="advanced",
            max_results=max_results
        )
    
    def search_industry_trends(
        self,
        industry: str,
        topic: Optional[str] = None,
        max_results: int = 5
    ) -> List[Dict[str, Any]]:
        """
        Search for industry trends and news.
        
        Args:
            industry: Industry to research
            topic: Optional specific topic (e.g., "AI adoption", "market growth")
            max_results: Maximum number of results
            
        Returns:
            List of search results
        """
        query_parts = [industry]
        
        if topic:
            query_parts.append(topic)
        else:
            query_parts.append("trends news 2024")
        
        query = " ".join(query_parts)
        
        return self.search(
            query=query,
            search_depth="basic",  # Basic is sufficient for news/trends
            max_results=max_results
        )
    
    def search_company_info(
        self,
        company_name: str,
        info_type: str = "about",
        max_results: int = 5
    ) -> List[Dict[str, Any]]:
        """
        Search for specific information about a company.
        
        Args:
            company_name: Name of the company
            info_type: Type of info ("about", "products", "funding", "team", etc.)
            max_results: Maximum number of results
            
        Returns:
            List of search results
        """
        query = f"{company_name} {info_type}"
        
        return self.search(
            query=query,
            search_depth="advanced",
            max_results=max_results
        )
    
    def search_technology_stack(
        self,
        company_name: str,
        max_results: int = 5
    ) -> List[Dict[str, Any]]:
        """
        Search for technology stack used by a company.
        
        Args:
            company_name: Name of the company
            max_results: Maximum number of results
            
        Returns:
            List of search results
        """
        query = f"{company_name} technology stack tools software"
        
        return self.search(
            query=query,
            search_depth="advanced",
            max_results=max_results
        )
    
    def search_competitors(
        self,
        company_name: str,
        industry: Optional[str] = None,
        max_results: int = 10
    ) -> List[Dict[str, Any]]:
        """
        Search for competitors of a company.
        
        Args:
            company_name: Name of the company
            industry: Optional industry filter
            max_results: Maximum number of results
            
        Returns:
            List of search results
        """
        query_parts = [f"{company_name} competitors"]
        
        if industry:
            query_parts.append(industry)
        
        query = " ".join(query_parts)
        
        return self.search(
            query=query,
            search_depth="advanced",
            max_results=max_results
        )
    
    def batch_search(
        self,
        queries: List[str],
        search_depth: str = "advanced",
        max_results_per_query: int = 5
    ) -> Dict[str, List[Dict[str, Any]]]:
        """
        Execute multiple searches in batch.
        
        Args:
            queries: List of search queries
            search_depth: Search depth for all queries
            max_results_per_query: Max results per query
            
        Returns:
            Dictionary mapping queries to their results
        """
        results = {}
        
        for query in queries:
            results[query] = self.search(
                query=query,
                search_depth=search_depth,
                max_results=max_results_per_query
            )
        
        return results
    
    def format_results(self, results: List[Dict[str, Any]], format_type: str = "summary") -> str:
        """
        Format search results for display.
        
        Args:
            results: List of search result dictionaries
            format_type: "summary" (brief) or "detailed" (full)
            
        Returns:
            Formatted string
        """
        if not results:
            return "No results found."
        
        formatted_lines = []
        
        for i, result in enumerate(results, 1):
            title = result.get("title", "No title")
            url = result.get("url", "No URL")
            content = result.get("content", "")
            
            if format_type == "summary":
                # Brief summary
                content_preview = content[:150] + "..." if len(content) > 150 else content
                formatted_lines.append(f"{i}. {title}")
                formatted_lines.append(f"   URL: {url}")
                formatted_lines.append(f"   Preview: {content_preview}\n")
            else:
                # Detailed format
                formatted_lines.append(f"{i}. {title}")
                formatted_lines.append(f"   URL: {url}")
                formatted_lines.append(f"   Content: {content}\n")
        
        return "\n".join(formatted_lines)
    
    def extract_urls(self, results: List[Dict[str, Any]]) -> List[str]:
        """
        Extract URLs from search results.
        
        Args:
            results: List of search result dictionaries
            
        Returns:
            List of URLs
        """
        return [result.get("url") for result in results if result.get("url")]


def create_search_tool(api_key: Optional[str] = None) -> SearchTool:
    """
    Factory function to create a SearchTool instance.
    
    Args:
        api_key: Optional API key
        
    Returns:
        SearchTool instance
    """
    return SearchTool(api_key=api_key)

