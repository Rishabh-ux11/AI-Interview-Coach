import requests

def get_answer_feedback(candidate_answer, model="gemma3:1b"):
    prompt = f"""
You are an AI interview coach. Given the following candidate's answer to an interview question, provide detailed feedback in the following four aspects: content depth, clarity, relevance, and confidence. For each aspect, write 1-2 sentences.

Candidate's answer:
\"\"\"
{candidate_answer}
\"\"\"

Respond in JSON format:
{{
  "content_depth": "...",
  "clarity": "...",
  "relevance": "...",
  "confidence": "..."
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
    answer = """
    I migrated our backend services to AWS using Docker and Kubernetes. This reduced downtime by 70% and improved deployment speed. I trained two junior engineers in the process.
    """
    print(get_answer_feedback(answer))
