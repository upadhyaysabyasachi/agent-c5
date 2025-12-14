"""
CRM Module - Phase 5: CRM Handoff
Handles saving leads, contacts, and interactions to Supabase database.
Prepares data for CRM export and handoff.
"""

import os
import json
from typing import Dict, Any, List, Optional
from datetime import datetime
from dotenv import load_dotenv
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from supabase import create_client, Client

load_dotenv()
console = Console()


class CRMHandler:
    """
    Phase 5: CRM Handler
    Manages database operations and CRM handoff functionality.
    """
    
    def __init__(self):
        """Initialize CRM handler with Supabase connection."""
        supabase_url = os.getenv("SUPABASE_URL")
        supabase_key = os.getenv("SUPABASE_KEY")
        
        if not supabase_url or not supabase_key:
            raise ValueError("SUPABASE_URL and SUPABASE_KEY must be set in environment variables")
        
        self.supabase: Client = create_client(supabase_url, supabase_key)
        console.print("[green]✅ CRM Handler initialized (Supabase connected)[/green]")
    
    def save_lead(self, lead: Dict[str, Any]) -> Optional[int]:
        """
        Save a lead to the database.
        
        Args:
            lead: Lead dictionary with company_name, website, industry, etc.
            
        Returns:
            Lead ID if successful, None otherwise
        """
        try:
            # Prepare lead data
            lead_data = {
                "company_name": lead.get("company_name"),
                "website": lead.get("website"),
                "industry": lead.get("industry"),
                "employee_count": lead.get("employee_count", "Unknown"),
                "icp_score": lead.get("score", lead.get("icp_score", 0.0)),
                "status": lead.get("status", "new")
            }
            
            # Insert into database
            response = self.supabase.table("leads").insert(lead_data).execute()
            
            if response.data and len(response.data) > 0:
                lead_id = response.data[0]["id"]
                console.print(f"[green]✅ Lead saved: {lead_data['company_name']} (ID: {lead_id})[/green]")
                return lead_id
            else:
                console.print(f"[yellow]⚠️  Lead saved but no ID returned[/yellow]")
                return None
                
        except Exception as e:
            console.print(f"[red]❌ Error saving lead: {e}[/red]")
            return None
    
    def save_contacts(self, lead_id: int, contacts: List[Dict[str, Any]]) -> List[int]:
        """
        Save contacts/decision makers for a lead.
        
        Args:
            lead_id: ID of the lead
            contacts: List of contact dictionaries
            
        Returns:
            List of contact IDs
        """
        contact_ids = []
        
        if not contacts:
            return contact_ids
        
        try:
            for contact in contacts:
                contact_data = {
                    "lead_id": lead_id,
                    "name": contact.get("name"),
                    "title": contact.get("title"),
                    "email": contact.get("email"),
                    "phone": contact.get("phone"),
                    "linkedin_url": contact.get("linkedin_url"),
                    "is_decision_maker": contact.get("is_decision_maker", False)
                }
                
                response = self.supabase.table("contacts").insert(contact_data).execute()
                
                if response.data and len(response.data) > 0:
                    contact_id = response.data[0]["id"]
                    contact_ids.append(contact_id)
                    console.print(f"[green]   ✅ Contact saved: {contact_data['name']} (ID: {contact_id})[/green]")
                    
        except Exception as e:
            console.print(f"[red]❌ Error saving contacts: {e}[/red]")
        
        return contact_ids
    
    def save_interaction(
        self,
        lead_id: int,
        interaction_type: str,
        direction: str,
        content: str,
        sentiment_score: Optional[float] = None
    ) -> Optional[int]:
        """
        Save an interaction (email, call, etc.) to the database.
        
        Args:
            lead_id: ID of the lead
            interaction_type: 'email', 'voice', 'linkedin'
            direction: 'inbound' or 'outbound'
            content: Email body, call transcript, etc.
            sentiment_score: Optional sentiment score (0.0-1.0)
            
        Returns:
            Interaction ID if successful, None otherwise
        """
        try:
            interaction_data = {
                "lead_id": lead_id,
                "type": interaction_type,
                "direction": direction,
                "content": content,
                "sentiment_score": sentiment_score
            }
            
            response = self.supabase.table("interactions").insert(interaction_data).execute()
            
            if response.data and len(response.data) > 0:
                interaction_id = response.data[0]["id"]
                console.print(f"[green]✅ Interaction saved: {interaction_type} ({direction})[/green]")
                return interaction_id
            else:
                return None
                
        except Exception as e:
            console.print(f"[red]❌ Error saving interaction: {e}[/red]")
            return None
    
    def update_lead_status(self, lead_id: int, new_status: str) -> bool:
        """
        Update the status of a lead.
        
        Args:
            lead_id: ID of the lead
            new_status: New status ('new', 'enriched', 'qualified', 'engaged', 'converted', 'disqualified')
            
        Returns:
            True if successful, False otherwise
        """
        valid_statuses = ['new', 'enriched', 'qualified', 'engaged', 'converted', 'disqualified']
        
        if new_status not in valid_statuses:
            console.print(f"[red]❌ Invalid status: {new_status}. Must be one of {valid_statuses}[/red]")
            return False
        
        try:
            response = self.supabase.table("leads").update({
                "status": new_status
            }).eq("id", lead_id).execute()
            
            if response.data:
                console.print(f"[green]✅ Lead {lead_id} status updated to: {new_status}[/green]")
                return True
            else:
                console.print(f"[yellow]⚠️  Lead {lead_id} not found or already has status {new_status}[/yellow]")
                return False
                
        except Exception as e:
            console.print(f"[red]❌ Error updating lead status: {e}[/red]")
            return False
    
    def save_engagement_result(
        self,
        lead: Dict[str, Any],
        engagement_type: str,
        engagement_data: Dict[str, Any]
    ) -> bool:
        """
        Save engagement results (email or call) to database.
        
        Args:
            lead: Lead dictionary
            engagement_type: 'email' or 'voice'
            engagement_data: Engagement result data
            
        Returns:
            True if successful, False otherwise
        """
        # First, ensure lead exists in database
        lead_id = lead.get("id")
        
        if not lead_id:
            # Try to find existing lead by company name
            try:
                response = self.supabase.table("leads").select("id").eq(
                    "company_name", lead.get("company_name")
                ).execute()
                
                if response.data and len(response.data) > 0:
                    lead_id = response.data[0]["id"]
                else:
                    # Create new lead
                    lead_id = self.save_lead(lead)
            except Exception as e:
                console.print(f"[red]❌ Error finding/creating lead: {e}[/red]")
                return False
        
        if not lead_id:
            console.print("[red]❌ Could not get lead ID[/red]")
            return False
        
        # Save interaction
        content = ""
        sentiment_score = None
        
        if engagement_type == "email":
            content = engagement_data.get("body", "")
            # Could analyze sentiment here
        elif engagement_type == "voice":
            transcript = engagement_data.get("result", {}).get("transcript", [])
            content = json.dumps(transcript, indent=2)
            # Extract sentiment if available
            sentiment_score = engagement_data.get("sentiment_score")
        
        interaction_id = self.save_interaction(
            lead_id=lead_id,
            interaction_type=engagement_type,
            direction="outbound",
            content=content,
            sentiment_score=sentiment_score
        )
        
        # Update lead status based on engagement
        if interaction_id:
            if engagement_type == "voice":
                self.update_lead_status(lead_id, "engaged")
            elif engagement_type == "email":
                self.update_lead_status(lead_id, "qualified")
            
            return True
        
        return False
    
    def get_lead_summary(self, lead_id: int) -> Optional[Dict[str, Any]]:
        """
        Get a complete summary of a lead including contacts and interactions.
        
        Args:
            lead_id: ID of the lead
            
        Returns:
            Dictionary with lead, contacts, and interactions
        """
        try:
            # Get lead
            lead_response = self.supabase.table("leads").select("*").eq("id", lead_id).execute()
            
            if not lead_response.data:
                return None
            
            lead = lead_response.data[0]
            
            # Get contacts
            contacts_response = self.supabase.table("contacts").select("*").eq("lead_id", lead_id).execute()
            contacts = contacts_response.data if contacts_response.data else []
            
            # Get interactions
            interactions_response = self.supabase.table("interactions").select("*").eq(
                "lead_id", lead_id
            ).order("timestamp", desc=True).execute()
            interactions = interactions_response.data if interactions_response.data else []
            
            return {
                "lead": lead,
                "contacts": contacts,
                "interactions": interactions,
                "interaction_count": len(interactions),
                "contact_count": len(contacts)
            }
            
        except Exception as e:
            console.print(f"[red]❌ Error getting lead summary: {e}[/red]")
            return None
    
    def export_crm_data(self, status_filter: Optional[str] = None) -> Dict[str, Any]:
        """
        Export all CRM data for handoff to external CRM systems.
        
        Args:
            status_filter: Optional status filter ('qualified', 'engaged', etc.)
            
        Returns:
            Dictionary with all leads, contacts, and interactions
        """
        try:
            query = self.supabase.table("leads").select("*")
            
            if status_filter:
                query = query.eq("status", status_filter)
            
            leads_response = query.execute()
            leads = leads_response.data if leads_response.data else []
            
            # Get all contacts
            contacts_response = self.supabase.table("contacts").select("*").execute()
            contacts = contacts_response.data if contacts_response.data else []
            
            # Get all interactions
            interactions_response = self.supabase.table("interactions").select("*").execute()
            interactions = interactions_response.data if interactions_response.data else []
            
            export_data = {
                "export_timestamp": datetime.now().isoformat(),
                "total_leads": len(leads),
                "total_contacts": len(contacts),
                "total_interactions": len(interactions),
                "leads": leads,
                "contacts": contacts,
                "interactions": interactions
            }
            
            console.print(f"[green]✅ Exported {len(leads)} leads, {len(contacts)} contacts, {len(interactions)} interactions[/green]")
            
            return export_data
            
        except Exception as e:
            console.print(f"[red]❌ Error exporting CRM data: {e}[/red]")
            return {}
    
    def display_crm_summary(self):
        """Display a summary of all CRM data."""
        try:
            # Get counts
            leads_response = self.supabase.table("leads").select("id, status").execute()
            leads = leads_response.data if leads_response.data else []
            
            # Count by status
            status_counts = {}
            for lead in leads:
                status = lead.get("status", "unknown")
                status_counts[status] = status_counts.get(status, 0) + 1
            
            # Create summary table
            table = Table(title="CRM Summary", show_header=True, header_style="bold magenta")
            table.add_column("Status", style="cyan")
            table.add_column("Count", justify="right", style="green")
            
            for status, count in sorted(status_counts.items()):
                table.add_row(status, str(count))
            
            table.add_row("TOTAL", str(len(leads)), style="bold")
            
            console.print("\n")
            console.print(table)
            
            # Get recent interactions
            interactions_response = self.supabase.table("interactions").select(
                "id, type, direction, timestamp"
            ).order("timestamp", desc=True).limit(5).execute()
            
            if interactions_response.data:
                console.print("\n[bold]Recent Interactions:[/bold]")
                for interaction in interactions_response.data:
                    console.print(
                        f"  • {interaction['type']} ({interaction['direction']}) - "
                        f"{interaction.get('timestamp', 'N/A')[:10]}"
                    )
            
        except Exception as e:
            console.print(f"[red]❌ Error displaying CRM summary: {e}[/red]")
    
    def bulk_save_leads(self, leads: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Save multiple leads to the database in bulk.
        
        Args:
            leads: List of lead dictionaries
            
        Returns:
            Dictionary with saved_count and failed_count
        """
        saved_count = 0
        failed_count = 0
        saved_ids = []
        
        console.print(f"[cyan]📦 Bulk saving {len(leads)} leads...[/cyan]")
        
        for lead in leads:
            lead_id = self.save_lead(lead)
            if lead_id:
                saved_count += 1
                saved_ids.append(lead_id)
            else:
                failed_count += 1
        
        result = {
            "saved_count": saved_count,
            "failed_count": failed_count,
            "total": len(leads),
            "saved_ids": saved_ids
        }
        
        console.print(f"[green]✅ Bulk save complete: {saved_count} saved, {failed_count} failed[/green]")
        
        return result

