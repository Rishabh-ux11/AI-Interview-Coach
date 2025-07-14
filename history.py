import streamlit as st
import requests
import PyPDF2
import io
import json

OLLAMA_API_URL = "http://localhost:11434/api/generate"

# Sidebar: Model selection
st.set_page_config(page_title="AI Interview Coach", page_icon=":robot_face:")
st.sidebar.header("⚙️ Model Selection")
question_model = st.sidebar.selectbox("Model for Question Generation", ["gemma", "llama3", "mistral"], index=0)
feedback_model = st.sidebar.selectbox("Model for Feedback Evaluation", ["gemma", "llama3", "mistral"], index=0)

def extract_text_from_pdf(pdf_file):
    reader = PyPDF2.PdfReader(pdf_file)
    text = ''
    for page in reader.pages:
        page_text = page.extract_text()
        if page_text:
            text += page_text + '\n'
    return text

def generate_interview_question(resume_text, role, model):
    prompt = f"""
You are an AI interview coach. Given the following resume, generate one thoughtful interview question for a {role} candidate, directly related to their experience or skills.
Provide a follow-up prompt structure to probe deeper if needed.

Resume:
\"\"\"{resume_text}\"\"\"

Respond in JSON format:
{{
  "question": "...",
  "follow_up_prompt": "..."
}}
"""
    response = requests.post(
        OLLAMA_API_URL,
        json={"model": model, "prompt": prompt, "stream": False}
    )
    return response.json()["response"]

def generate_feedback(candidate_answer, model):
    prompt = f"""
You are an AI interview coach. Given the following candidate's answer to an interview question, provide detailed feedback in the following four aspects: content depth, clarity, relevance, and confidence. For each aspect, write 1-2 sentences.

Candidate's answer:
\"\"\"{candidate_answer}\"\"\"

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
        json={"model": model, "prompt": prompt, "stream": False}
    )
    return response.json()["response"]

def build_session_history_text(messages):
    lines = []
    for msg in messages:
        if msg["role"] == "ai":
            lines.append(f"AI Interviewer: {msg['content']}")
        else:
            lines.append(f"You: {msg['content']}")
            if "feedback" in msg and msg["feedback"]:
                lines.append(f"Feedback:\n{msg['feedback']}")
        lines.append("")
    return "\n".join(lines)

def build_session_history_pdf(messages):
    from fpdf import FPDF
    pdf = FPDF()
    pdf.add_page()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.set_font("Arial", size=12)

    for msg in messages:
        if msg["role"] == "ai":
            pdf.set_text_color(0, 0, 180)
            pdf.multi_cell(0, 10, f"AI Interviewer: {msg['content']}")
        else:
            pdf.set_text_color(0, 0, 0)
            pdf.multi_cell(0, 10, f"You: {msg['content']}")
            if "feedback" in msg and msg["feedback"]:
                pdf.set_text_color(128, 0, 0)
                pdf.multi_cell(0, 10, f"Feedback:\n{msg['feedback']}")
        pdf.ln(3)
    return pdf.output(dest='S').encode('latin-1')

# App main UI
st.title("🤖 AI Interview Coach")
st.write("Upload your resume, select a job role, and chat with your AI interviewer!")

if "messages" not in st.session_state:
    st.session_state.messages = []

resume_file = st.file_uploader("Upload your PDF Resume", type=["pdf"])
role = st.selectbox("Select the job role:", ["Software Engineer", "Data Scientist", "Product Manager", "Designer", "Other"])

if resume_file and role:
    resume_text = extract_text_from_pdf(resume_file)

    if not st.session_state.get("resume_text"):
        st.session_state.resume_text = resume_text
    if not st.session_state.get("role"):
        st.session_state.role = role

    if len(st.session_state.messages) == 0:
        question_json = generate_interview_question(st.session_state.resume_text, st.session_state.role, question_model)
        try:
            question_data = json.loads(question_json)
            question = question_data.get("question", "")
            follow_up = question_data.get("follow_up_prompt", "")
        except Exception:
            question = question_json
            follow_up = ""
        st.session_state.messages.append({"role": "ai", "content": question, "follow_up": follow_up})

    # Chat interface
    for msg in st.session_state.messages:
        if msg["role"] == "ai":
            st.markdown(f"**AI Interviewer:** {msg['content']}")
        else:
            st.markdown(f"**You:** {msg['content']}")
            st.markdown(f"> **Feedback:** {msg['feedback']}")

    with st.form(key="user_input_form", clear_on_submit=True):
        user_input = st.text_area("Your answer:", key="user_input")
        submitted = st.form_submit_button("Submit")
        if submitted and user_input.strip():
            st.session_state.messages.append({"role": "user", "content": user_input})

            feedback_json = generate_feedback(user_input, feedback_model)
            try:
                feedback = json.loads(feedback_json)
            except Exception:
                feedback = {"content_depth": feedback_json, "clarity": "", "relevance": "", "confidence": ""}
            feedback_str = (
                f"Content Depth: {feedback.get('content_depth', '')}\n"
                f"Clarity: {feedback.get('clarity', '')}\n"
                f"Relevance: {feedback.get('relevance', '')}\n"
                f"Confidence: {feedback.get('confidence', '')}"
            )
            st.session_state.messages[-1]["feedback"] = feedback_str

            question_json = generate_interview_question(st.session_state.resume_text, st.session_state.role, question_model)
            try:
                question_data = json.loads(question_json)
                question = question_data.get("question", "")
                follow_up = question_data.get("follow_up_prompt", "")
            except Exception:
                question = question_json
                follow_up = ""
            st.session_state.messages.append({"role": "ai", "content": question, "follow_up": follow_up})
            st.experimental_rerun()

    # Downloads
    st.markdown("### Download your interview session history and feedback")
    session_text = build_session_history_text(st.session_state.messages)
    st.download_button("Download as Text", data=session_text, file_name="interview_session.txt", mime="text/plain")

    try:
        from fpdf import FPDF
        pdf_bytes = build_session_history_pdf(st.session_state.messages)
        st.download_button("Download as PDF", data=pdf_bytes, file_name="interview_session.pdf", mime="application/pdf")
    except ImportError:
        st.info("To enable PDF download, install fpdf: `pip install fpdf`")

else:
    st.info("Please upload a PDF resume and select a job role to begin.")
