import os
import json
from groq import Groq
from rich.prompt import Prompt

class ICPBuilder:
    def __init__(self):
        self.client = Groq(api_key=os.getenv("GROQ_API_KEY"))
        self.model = "llama-3.3-70b-versatile"

    def run_interview(self):
        """Conducts a conversation to build the Ideal Customer Profile."""
        print("🤖 I need to understand your target market. Let's build your ICP.")
        
        questions = [
            "What is the primary industry you target?",
            "What is the typical employee count of your ideal customer?",
            "Who is the specific decision maker (Job Title)?",
            "What is the main pain point your product solves?"
        ]
        
        answers = {}
        for q in questions:
            answers[q] = Prompt.ask(f"[cyan]{q}[/cyan]")
            
        # Synthesize into structured JSON using LLM
        return self._synthesize_profile(answers)

    def _synthesize_profile(self, answers):
        prompt = f"""
        Convert these interview answers into a structured JSON Ideal Customer Profile.
        
        Answers: {json.dumps(answers)}
        
        Output JSON with keys: industry, size_range, decision_maker, pain_points, keywords.
        
        Return ONLY valid JSON, no markdown, no explanations.
        """
        
        try:
            completion = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are a JSON generator. Output ONLY valid JSON, no markdown code blocks, no explanations."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0
            )
            
            response_text = completion.choices[0].message.content
            profile = self._parse_json(response_text)
            
            # If parsing failed, create a fallback profile from answers
            if not profile or not isinstance(profile, dict):
                print("⚠️  JSON parsing failed, creating profile from answers...")
                profile = self._create_fallback_profile(answers)
            
            return profile
            
        except Exception as e:
            print(f"⚠️  Error synthesizing profile: {e}")
            print("   Creating fallback profile from answers...")
            return self._create_fallback_profile(answers)
    
    def _parse_json(self, text: str) -> dict:
        """Robust JSON parsing helper."""
        try:
            if not text:
                return {}
            
            # Remove markdown code blocks
            if "```json" in text:
                text = text.split("```json")[1].split("```")[0]
            elif "```" in text:
                text = text.split("```")[1].split("```")[0]
            
            # Try to find JSON object in the text
            text = text.strip()
            
            # Find first { and last }
            start_idx = text.find('{')
            end_idx = text.rfind('}')
            
            if start_idx != -1 and end_idx != -1 and end_idx > start_idx:
                json_text = text[start_idx:end_idx + 1]
                return json.loads(json_text)
            else:
                # Try parsing the whole text
                return json.loads(text)
                
        except json.JSONDecodeError as e:
            print(f"   ⚠️  JSON parse error: {e}")
            print(f"   Raw text preview: {text[:100]}...")
            return {}
        except Exception as e:
            print(f"   ⚠️  Parse error: {e}")
            return {}
    
    def _create_fallback_profile(self, answers: dict) -> dict:
        """Create a basic ICP profile from interview answers as fallback."""
        # Extract information from answers
        industry = ""
        size_range = ""
        decision_maker = ""
        pain_points = ""
        
        for question, answer in answers.items():
            question_lower = question.lower()
            if "industry" in question_lower:
                industry = answer
            elif "employee" in question_lower or "size" in question_lower:
                size_range = answer
            elif "decision maker" in question_lower or "job title" in question_lower:
                decision_maker = answer
            elif "pain point" in question_lower:
                pain_points = answer
        
        # Create structured profile
        profile = {
            "industry": industry or "Unknown",
            "size_range": size_range or "Unknown",
            "decision_maker": decision_maker or "Unknown",
            "pain_points": pain_points or "Unknown",
            "keywords": [industry, decision_maker, pain_points] if any([industry, decision_maker, pain_points]) else []
        }
        
        # Clean up keywords
        profile["keywords"] = [k for k in profile["keywords"] if k and k != "Unknown"]
        
        return profile