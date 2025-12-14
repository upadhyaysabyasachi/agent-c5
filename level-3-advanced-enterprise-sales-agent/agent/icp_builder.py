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
        """
        
        completion = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": "Output valid JSON only."},
                {"role": "user", "content": prompt}
            ],
            temperature=0
        )
        # Parse JSON helper from Level 1 would go here
        return json.loads(completion.choices[0].message.content)