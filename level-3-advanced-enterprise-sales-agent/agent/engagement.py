"""
Engagement Module - Phase 4: Email and Voice Outreach
Handles outbound communication with leads via email and voice calls.
"""

import os
import json
from typing import Dict, Any, List, Optional
from groq import Groq
from dotenv import load_dotenv
from rich.console import Console
from rich.panel import Panel

# Import voice tool
from tools.voice_tool import VoiceTool

load_dotenv()
console = Console()


class EngagementEngine:
    """
    Phase 4: Engagement Engine
    Handles outbound communication via email and voice calls.
    """
    
    def __init__(self):
        # Initialize Groq for email/script generation
        self.groq_client = Groq(api_key=os.getenv("GROQ_API_KEY"))
        self.model = "llama-3.3-70b-versatile"
        
        # Initialize voice tool (optional - only if API key is available)
        self.voice_tool = None
        try:
            if os.getenv("ELEVENLABS_API_KEY"):
                self.voice_tool = VoiceTool()
                console.print("[green]✅ Voice capabilities enabled[/green]")
            else:
                console.print("[yellow]⚠️  ELEVENLABS_API_KEY not found - voice features disabled[/yellow]")
        except Exception as e:
            console.print(f"[yellow]⚠️  Voice tool initialization failed: {e}[/yellow]")
    
    def generate_email(self, lead: Dict[str, Any], icp_profile: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate a personalized email for a lead.
        
        Args:
            lead: Lead information
            icp_profile: ICP profile for personalization
            
        Returns:
            Dictionary with email subject, body, and metadata
        """
        prompt = f"""
        You are a professional B2B sales email writer. Write a personalized, concise email to engage a potential lead.
        
        Lead Information:
        - Company: {lead.get('company_name', 'Unknown')}
        - Industry: {lead.get('industry', 'Unknown')}
        - Website: {lead.get('website', 'N/A')}
        - Description: {lead.get('description', 'N/A')}
        
        Target ICP:
        - Industry: {icp_profile.get('industry', 'N/A')}
        - Pain Points: {icp_profile.get('pain_points', 'N/A')}
        
        Requirements:
        1. Subject line: Clear, value-driven, under 50 characters
        2. Body: 3-4 short paragraphs, personalized, no generic templates
        3. Include a clear call-to-action
        4. Professional but friendly tone
        5. Reference specific company details if available
        
        Return JSON with keys: subject, body, tone, cta
        """
        
        try:
            response = self.groq_client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are an expert sales email writer. Output valid JSON only."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7
            )
            
            email_data = self._parse_json(response.choices[0].message.content)
            
            return {
                "type": "email",
                "lead_id": lead.get('id'),
                "subject": email_data.get('subject', 'Follow-up'),
                "body": email_data.get('body', ''),
                "tone": email_data.get('tone', 'professional'),
                "cta": email_data.get('cta', 'Schedule a call'),
                "status": "draft"
            }
        except Exception as e:
            console.print(f"[red]❌ Email generation failed: {e}[/red]")
            return {
                "type": "email",
                "lead_id": lead.get('id'),
                "subject": "Follow-up",
                "body": "Hello, I'd like to discuss how we can help...",
                "status": "error"
            }
    
    def generate_call_script(self, lead: Dict[str, Any], icp_profile: Dict[str, Any]) -> str:
        """
        Generate a call script for voice outreach.
        
        Args:
            lead: Lead information
            icp_profile: ICP profile
            
        Returns:
            Call script as string
        """
        prompt = f"""
        You are a professional sales call script writer. Create a concise, natural call script for an outbound sales call.
        
        Lead Information:
        - Company: {lead.get('company_name', 'Unknown')}
        - Industry: {lead.get('industry', 'Unknown')}
        - Contact: {lead.get('contact_name', 'Decision Maker')}
        
        Target ICP:
        - Industry: {icp_profile.get('industry', 'N/A')}
        - Pain Points: {icp_profile.get('pain_points', 'N/A')}
        
        Requirements:
        1. Opening: Brief, warm introduction (15-20 seconds)
        2. Value proposition: Clear, personalized benefit (30 seconds)
        3. Question: One open-ended question to engage
        4. Natural, conversational tone
        5. Total script should be 60-90 seconds when spoken
        
        Return ONLY the script text, no JSON, no markdown.
        """
        
        try:
            response = self.groq_client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are an expert sales call script writer. Return only the script text."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7
            )
            
            return response.choices[0].message.content.strip()
        except Exception as e:
            console.print(f"[red]❌ Script generation failed: {e}[/red]")
            return f"Hello, this is [Your Name] calling from [Company]. I wanted to reach out because we help companies like {lead.get('company_name', 'yours')}..."
    
    def make_voice_call(
        self,
        lead: Dict[str, Any],
        icp_profile: Dict[str, Any],
        interactive: bool = False
    ) -> Dict[str, Any]:
        """
        Make a voice call to a lead using ElevenLabs.
        
        Args:
            lead: Lead information
            icp_profile: ICP profile
            interactive: If True, allows real-time conversation (requires STT integration)
            
        Returns:
            Call result dictionary with transcript and metadata
        """
        if not self.voice_tool:
            console.print("[red]❌ Voice tool not available. Cannot make call.[/red]")
            return {"status": "error", "message": "Voice tool not initialized"}
        
        console.print(f"\n[bold blue]📞 Initiating voice call to {lead.get('company_name', 'Lead')}[/bold blue]")
        
        # Generate call script
        script = self.generate_call_script(lead, icp_profile)
        console.print(Panel(script, title="Call Script", border_style="cyan"))
        
        # Define conversation handler
        conversation_history = [{"role": "system", "content": f"Lead: {lead.get('company_name')}, Industry: {lead.get('industry')}"}]
        
        def handle_user_speech(user_text: str) -> str:
            """Handle user speech and generate agent response."""
            if not user_text:
                return script  # Initial greeting
            
            # Add user message to history
            conversation_history.append({"role": "user", "content": user_text})
            
            # Generate response using LLM
            prompt = f"""
            You are a professional sales representative on a call with a potential client.
            
            Lead: {lead.get('company_name')}
            Industry: {lead.get('industry')}
            
            Conversation so far:
            {json.dumps(conversation_history[-5:], indent=2)}
            
            Generate a natural, helpful response (2-3 sentences max). Be conversational, not scripted.
            """
            
            try:
                response = self.groq_client.chat.completions.create(
                    model=self.model,
                    messages=[
                        {"role": "system", "content": "You are a professional sales rep. Be natural and helpful."},
                        {"role": "user", "content": prompt}
                    ],
                    temperature=0.8
                )
                
                agent_response = response.choices[0].message.content.strip()
                conversation_history.append({"role": "assistant", "content": agent_response})
                return agent_response
            except Exception as e:
                return "I apologize, could you repeat that?"
        
        # Conduct the call
        try:
            if interactive:
                # Interactive mode (requires STT - currently uses text input as fallback)
                console.print("[yellow]⚠️  Interactive mode: Using text input (STT integration needed for full voice)[/yellow]")
                call_result = self.voice_tool.voice_call(
                    script=script,
                    on_user_speech=handle_user_speech,
                    max_turns=10
                )
            else:
                # Non-interactive: Just play the script
                console.print("[cyan]Playing call script...[/cyan]")
                audio_data = self.voice_tool.speak(script, play_audio=True)
                call_result = {
                    "status": "completed",
                    "turns": 1,
                    "transcript": [{"role": "agent", "text": script}],
                    "audio_length": len(audio_data)
                }
            
            # Save call recording if needed
            if call_result.get('transcript'):
                console.print(f"[green]✅ Call completed: {len(call_result['transcript'])} exchanges[/green]")
            
            return {
                "lead_id": lead.get('id'),
                "type": "voice",
                "direction": "outbound",
                "result": call_result,
                "status": "completed"
            }
            
        except Exception as e:
            console.print(f"[red]❌ Call failed: {e}[/red]")
            return {
                "lead_id": lead.get('id'),
                "type": "voice",
                "status": "error",
                "error": str(e)
            }
        finally:
            # Cleanup voice tool resources
            if self.voice_tool:
                self.voice_tool.cleanup()
    
    def send_email(self, email_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Send an email (placeholder - integrate with email service).
        
        Args:
            email_data: Email dictionary from generate_email()
            
        Returns:
            Send result
        """
        # Placeholder - in production, integrate with SendGrid, Mailgun, etc.
        console.print(f"[cyan]📧 Email prepared for {email_data.get('lead_id')}[/cyan]")
        console.print(f"   Subject: {email_data.get('subject')}")
        console.print(f"   Status: {email_data.get('status')}")
        
        return {
            "status": "sent" if email_data.get('status') != 'error' else "failed",
            "email_id": email_data.get('lead_id'),
            "message": "Email sent (mock - integrate with email service)"
        }
    
    def _parse_json(self, text: str) -> Dict[str, Any]:
        """Parse JSON from LLM response."""
        try:
            if not text:
                return {}
            
            # Remove markdown code blocks
            if "```json" in text:
                text = text.split("```json")[1].split("```")[0]
            elif "```" in text:
                text = text.split("```")[1].split("```")[0]
            
            return json.loads(text.strip())
        except json.JSONDecodeError:
            console.print(f"[yellow]⚠️  JSON parse error. Using fallback.[/yellow]")
            return {}
        except Exception as e:
            console.print(f"[red]❌ Parse error: {e}[/red]")
            return {}

