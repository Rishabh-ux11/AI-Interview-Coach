import requests

def generate_interview_question(resume_content, model="gemma3:1b"):
    prompt = f"""
You are an AI interview coach. Given the following resume content, generate one thoughtful interview question for a Software Engineer candidate, directly related to their experience or skills. 
Provide a follow-up prompt structure to probe deeper if needed.

Resume:
\"\"\"
{resume_content}
\"\"\"

Respond in JSON format:
{{
  "question": "...",
  "follow_up_prompt": "..."
}}
"""
    try:
        response = requests.post(
            "http://localhost:11434/api/generate",
            json={"model": model, "prompt": prompt, "stream": False}
        )
        response.raise_for_status()
        data = response.json()
        return data["response"]
    except Exception as e:
        return f"Error: {e}"

# Example usage
if __name__ == "__main__":
    resume = """
    Experienced Software Engineer with a background in Python, cloud computing, and scalable backend systems. Led a team that migrated legacy services to AWS, improving system reliability and reducing costs. Skilled in Django, REST APIs, and CI/CD pipelines.
    """
    print(generate_interview_question(resume))
