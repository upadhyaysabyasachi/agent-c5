import json
from datetime import datetime
from rich.console import Console
from agent.icp_builder import ICPBuilder
from agent.discovery import DiscoveryEngine
from agent.qualification import QualificationSystem
from agent.engagement import EngagementEngine
from agent.crm import CRMHandler

console = Console()

class SalesOrchestrator:
    def __init__(self):
        self.state = {
            "icp_profile": None,
            "leads": [],
            "qualified_leads": [],
            "current_phase": "INIT"
        }
        self.icp_builder = ICPBuilder()
        self.discovery = DiscoveryEngine()
        self.qualifier = QualificationSystem()
        self.engagement = EngagementEngine()
        self.crm = CRMHandler()

    def run_cli(self):
        """Main interaction loop."""
        while True:
            if self.state["current_phase"] == "INIT":
                self._handle_init()
            elif self.state["current_phase"] == "DISCOVERY":
                self._handle_discovery()
            elif self.state["current_phase"] == "QUALIFICATION":
                self._handle_qualification()
            elif self.state["current_phase"] == "ENGAGEMENT":
                self._handle_engagement()
            elif self.state["current_phase"] == "CRM":
                self._handle_crm()
            
            # Simple exit condition for demo
            if self.state["current_phase"] == "DONE":
                console.print("[green]✅ Campaign Setup Complete![/green]")
                break

    def _handle_init(self):
        console.print("[bold blue]Phase 1: ICP Definition[/bold blue]")
        choice = console.input("Do you have an existing ICP profile? (y/n): ")
        
        if choice.lower() == 'n':
            self.state["icp_profile"] = self.icp_builder.run_interview()
        else:
            # Load mock profile
            self.state["icp_profile"] = {
                "industry": "B2B SaaS",
                "role": "VP of Sales",
                "size": "50-200"
            }
        
        self.state["current_phase"] = "DISCOVERY"

    def _handle_discovery(self):
        console.print("\n[bold blue]Phase 2: Lead Discovery[/bold blue]")
        console.print(f"🔎 Searching for {self.state['icp_profile']['industry']} companies...")
        
        # Trigger discovery engine
        leads = self.discovery.find_leads(self.state["icp_profile"])
        self.state["leads"] = leads
        
        console.print(f"✅ Found {len(leads)} potential leads.")
        self.state["current_phase"] = "QUALIFICATION"

    def _handle_qualification(self):
        console.print("\n[bold blue]Phase 3: Automated Qualification[/bold blue]")
        
        qualified = []
        for lead in self.state["leads"]:
            score = self.qualifier.score_lead(lead, self.state["icp_profile"])
            lead["score"] = score
            console.print(f"   • {lead['company_name']}: Score {score}/100")
            
            # Only qualify leads with score >= 50
            if score >= 50:
                qualified.append(lead)
        
        self.state["qualified_leads"] = qualified
        console.print(f"\n[green]✅ {len(qualified)} leads qualified for outreach[/green]")
        
        if qualified:
            self.state["current_phase"] = "ENGAGEMENT"
        else:
            # Skip to CRM if no qualified leads
            self.state["current_phase"] = "CRM"
    
    def _handle_engagement(self):
        """Phase 4: Engagement - Email and Voice Outreach"""
        console.print("\n[bold blue]Phase 4: Engagement & Outreach[/bold blue]")
        
        if not self.state["qualified_leads"]:
            console.print("[yellow]No qualified leads to engage[/yellow]")
            self.state["current_phase"] = "DONE"
            return
        
        # Ask user for engagement preference
        console.print("\n[cyan]Engagement Options:[/cyan]")
        console.print("1. Generate emails for all qualified leads")
        console.print("2. Make voice calls (requires ELEVENLABS_API_KEY)")
        console.print("3. Skip engagement")
        
        choice = console.input("\n[bold]Choose option (1/2/3):[/bold] ")
        
        if choice == "1":
            self._handle_email_engagement()
        elif choice == "2":
            self._handle_voice_engagement()
        else:
            console.print("[yellow]Skipping engagement phase[/yellow]")
        
        # Move to CRM phase after engagement
        self.state["current_phase"] = "CRM"
    
    def _handle_email_engagement(self):
        """Generate and send emails to qualified leads."""
        console.print("\n[cyan]📧 Generating personalized emails...[/cyan]")
        
        for lead in self.state["qualified_leads"][:5]:  # Limit to 5 for demo
            email = self.engagement.generate_email(lead, self.state["icp_profile"])
            console.print(f"\n[bold]Email for {lead['company_name']}:[/bold]")
            console.print(f"   Subject: {email.get('subject')}")
            console.print(f"   Preview: {email.get('body', '')[:100]}...")
            
            # Optionally send
            send_choice = console.input(f"   Send this email? (y/n): ")
            if send_choice.lower() == 'y':
                result = self.engagement.send_email(email)
                console.print(f"   Status: {result.get('status')}")
                # Store engagement result for CRM
                if not lead.get("engagement_result"):
                    lead["engagement_result"] = {
                        "type": "email",
                        "data": email
                    }
    
    def _handle_voice_engagement(self):
        """Make voice calls to qualified leads."""
        console.print("\n[cyan]📞 Voice Call Engagement[/cyan]")
        
        if not self.engagement.voice_tool:
            console.print("[red]❌ Voice tool not available. Please set ELEVENLABS_API_KEY[/red]")
            return
        
        # Select lead for call
        console.print("\n[bold]Select a lead to call:[/bold]")
        for i, lead in enumerate(self.state["qualified_leads"][:5], 1):
            console.print(f"   {i}. {lead['company_name']} (Score: {lead.get('score', 0)})")
        
        try:
            selection = int(console.input("\n[bold]Enter number (1-5):[/bold] "))
            if 1 <= selection <= min(5, len(self.state["qualified_leads"])):
                selected_lead = self.state["qualified_leads"][selection - 1]
                
                # Ask for call type
                call_type = console.input("Call type - Interactive (i) or Script-only (s): ")
                interactive = call_type.lower() == 'i'
                
                # Make the call
                result = self.engagement.make_voice_call(
                    selected_lead,
                    self.state["icp_profile"],
                    interactive=interactive
                )
                
                if result.get("status") == "completed":
                    console.print("[green]✅ Call completed successfully[/green]")
                    # Store engagement result for CRM
                    selected_lead["engagement_result"] = {
                        "type": "voice",
                        "data": result
                    }
                else:
                    console.print(f"[red]❌ Call failed: {result.get('error', 'Unknown error')}[/red]")
            else:
                console.print("[yellow]Invalid selection[/yellow]")
        except ValueError:
            console.print("[yellow]Invalid input[/yellow]")
        except KeyboardInterrupt:
            console.print("\n[yellow]Call cancelled by user[/yellow]")
    
    def _handle_crm(self):
        """Phase 5: CRM Handoff - Save data to database and prepare for export."""
        console.print("\n[bold blue]Phase 5: CRM Handoff[/bold blue]")
        
        # Ask user what to do
        console.print("\n[cyan]CRM Options:[/cyan]")
        console.print("1. Save all leads to database")
        console.print("2. Save engagement results (emails/calls)")
        console.print("3. View CRM summary")
        console.print("4. Export CRM data")
        console.print("5. Skip CRM handoff")
        
        choice = console.input("\n[bold]Choose option (1-5):[/bold] ")
        
        if choice == "1":
            self._save_leads_to_crm()
        elif choice == "2":
            self._save_engagement_results()
        elif choice == "3":
            self.crm.display_crm_summary()
        elif choice == "4":
            self._export_crm_data()
        else:
            console.print("[yellow]Skipping CRM handoff[/yellow]")
        
        self.state["current_phase"] = "DONE"
    
    def _save_leads_to_crm(self):
        """Save all discovered leads to CRM database."""
        console.print("\n[cyan]💾 Saving leads to CRM database...[/cyan]")
        
        if not self.state.get("leads"):
            console.print("[yellow]No leads to save[/yellow]")
            return
        
        # Bulk save leads
        result = self.crm.bulk_save_leads(self.state["leads"])
        
        console.print(f"\n[green]✅ Saved {result['saved_count']} leads to database[/green]")
        
        # Update state with saved IDs
        for i, lead in enumerate(self.state["leads"]):
            if i < len(result["saved_ids"]):
                lead["id"] = result["saved_ids"][i]
    
    def _save_engagement_results(self):
        """Save engagement results (emails/calls) to CRM."""
        console.print("\n[cyan]💾 Saving engagement results...[/cyan]")
        
        if not self.state.get("qualified_leads"):
            console.print("[yellow]No qualified leads with engagement data[/yellow]")
            return
        
        saved_count = 0
        for lead in self.state["qualified_leads"]:
            # Check if lead has engagement data
            if lead.get("engagement_result"):
                engagement_type = lead["engagement_result"].get("type")
                engagement_data = lead["engagement_result"].get("data", {})
                
                if self.crm.save_engagement_result(lead, engagement_type, engagement_data):
                    saved_count += 1
        
        console.print(f"[green]✅ Saved {saved_count} engagement results[/green]")
    
    def _export_crm_data(self):
        """Export CRM data for handoff."""
        console.print("\n[cyan]📤 Exporting CRM data...[/cyan]")
        
        # Ask for status filter
        filter_choice = console.input("Filter by status? (qualified/engaged/all): ")
        status_filter = None if filter_choice.lower() == "all" else filter_choice.lower()
        
        export_data = self.crm.export_crm_data(status_filter=status_filter)
        
        if export_data:
            # Save to file
            import json
            filename = f"crm_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            with open(filename, "w") as f:
                json.dump(export_data, f, indent=2)
            
            console.print(f"[green]✅ CRM data exported to: {filename}[/green]")
            console.print(f"   • {export_data['total_leads']} leads")
            console.print(f"   • {export_data['total_contacts']} contacts")
            console.print(f"   • {export_data['total_interactions']} interactions")