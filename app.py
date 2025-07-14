from flask import Flask, request, jsonify
import requests
import json

# Ollama API config
OLLAMA_API_URL = "http://localhost:11434/api/generate"
OLLAMA_MODEL = "gemma3:1b"  # ✅ Use the model you have downloaded

app = Flask(__name__)

# Function to generate a question from resume and role
def generate_question(resume_text, role):
    prompt = f"""
You are an AI interview coach. Given the following resume, generate one thoughtful interview question for a {role} candidate, directly related to their experience or skills. 
Provide a follow-up prompt structure to probe deeper if needed.

Resume:
\"\"\"
{resume_text}
\"\"\"

Respond in JSON format:
{{
  "question": "...",
  "follow_up_prompt": "..."
}}
"""
    response = requests.post(
        OLLAMA_API_URL,
        json={"model": OLLAMA_MODEL, "prompt": prompt, "stream": False}
    )
    data = response.json()
    print("OLLAMA generate_question RESPONSE:", data)

    if "response" not in data:
        return f"Ollama error or malformed response: {data}"
    return data["response"]

# Function to generate feedback on the candidate's answer
def generate_feedback(candidate_answer):
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
    response = requests.post(
        OLLAMA_API_URL,
        json={"model": OLLAMA_MODEL, "prompt": prompt, "stream": False}
    )
    data = response.json()
    print("OLLAMA generate_feedback RESPONSE:", data)

    if "response" not in data:
        return f"Ollama error or malformed response: {data}"
    return data["response"]

# Main endpoint
@app.route('/interview', methods=['POST'])
def interview():
    data = request.get_json()
    resume_text = data.get('resume_text')
    role = data.get('role')
    candidate_answer = data.get('candidate_answer')

    if not resume_text or not role or not candidate_answer:
        return jsonify({"error": "Missing required fields"}), 400

    question_json = generate_question(resume_text, role)
    feedback_json = generate_feedback(candidate_answer)

    try:
        question = json.loads(question_json)
    except Exception:
        question = {"question": question_json, "follow_up_prompt": ""}

    try:
        feedback = json.loads(feedback_json)
    except Exception:
        feedback = {
            "content_depth": feedback_json,
            "clarity": "",
            "relevance": "",
            "confidence": ""
        }

    return jsonify({
        "question": question,
        "feedback": feedback
    })

if __name__ == '__main__':
    app.run(debug=True)
