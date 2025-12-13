import os

def save_automation_script(filename: str, code_content: str):
    """Saves the generated python code to a file."""
    
    # Ensure a directory exists
    output_dir = "generated_automations"
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
        
    filepath = os.path.join(output_dir, filename)
    
    # Remove markdown code blocks if present
    clean_code = code_content.replace("```python", "").replace("```", "").strip()
    
    with open(filepath, "w") as f:
        f.write(clean_code)
        
    return f"✅ Script saved to {filepath}"