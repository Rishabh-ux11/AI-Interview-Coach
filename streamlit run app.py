import streamlit as st
import requests
import PyPDF2
import io
import json
from fpdf import FPDF

OLLAMA_API_URL = "http://localhost:11434/api/generate"
OLLAMA_MODEL = "gemma3:1b"

# ------------------- PDF Resume Parsing -------------------
def extract_text_from_pdf(pdf_file):
    reader = PyPDF2.PdfReader(pdf_file)
    text = ''
    for page in reader.pages:
        page_text = page.extract_text()
        if page_text:
            text += page_text + '\n'
    return text

# ------------------- Question Generation -------------------
def generate_interview_question(resume_text, role):
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
        json={"model": OLLAMA_MODEL, "prompt": prompt, "stream": False}
    )
    return response.json()["response"]

# ------------------- Feedback Generation -------------------
def generate_feedback(candidate_answer):
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
        json={"model": OLLAMA_MODEL, "prompt": prompt, "stream": False}
    )
    return response.json()["response"]

# ------------------- Score Calculator -------------------
def score_feedback(feedback):
    def score_from_text(text):
        text = text.lower()
        strong_pos = ["excellent", "outstanding", "exceptional", "perfect", "impressive"]
        moderate_pos = ["good", "clear", "strong", "well", "confident", "relevant", "detailed"]
        average = ["adequate", "average", "satisfactory", "acceptable", "reasonable"]
        weak = ["basic", "somewhat", "fair", "limited", "partially", "needs improvement"]
        negative = ["poor", "lacking", "unclear", "weak", "insufficient", "incomplete", "confusing"]

        if any(word in text for word in strong_pos):
            return 10
        elif any(word in text for word in moderate_pos):
            return 8
        elif any(word in text for word in average):
            return 6
        elif any(word in text for word in weak):
            return 4
        elif any(word in text for word in negative):
            return 2
        else:
            return 5

    return {
        "content_score": score_from_text(feedback.get("content_depth", "")),
        "clarity_score": score_from_text(feedback.get("clarity", "")),
        "relevance_score": score_from_text(feedback.get("relevance", "")),
        "confidence_score": score_from_text(feedback.get("confidence", "")),
    }

# ------------------- Export Utilities -------------------
def build_session_history_text(messages):
    lines = []
    for msg in messages:
        if msg["role"] == "ai":
            lines.append(f"AI Interviewer: {msg['content']}")
        else:
            lines.append(f"You: {msg['content']}")
            if "feedback" in msg:
                lines.append(f"Feedback:\n{msg['feedback']}")
            if "scores" in msg:
                scores = msg["scores"]
                lines.append(f"Scores: Content={scores['content_score']}/10, Clarity={scores['clarity_score']}/10, Relevance={scores['relevance_score']}/10, Confidence={scores['confidence_score']}/10")
        lines.append("")
    return "\n".join(lines)

def build_session_history_pdf(messages):
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
            if "feedback" in msg:
                pdf.set_text_color(128, 0, 0)
                pdf.multi_cell(0, 10, f"Feedback:\n{msg['feedback']}")
            if "scores" in msg:
                scores = msg["scores"]
                pdf.set_text_color(0, 128, 0)
                pdf.multi_cell(0, 10, f"Scores: Content={scores['content_score']}/10, Clarity={scores['clarity_score']}/10, Relevance={scores['relevance_score']}/10, Confidence={scores['confidence_score']}/10")
        pdf.ln(3)
    return pdf.output(dest='S').encode('latin-1')

# ------------------- Streamlit UI -------------------
st.set_page_config(page_title="AI Interview Coach", page_icon=":robot_face:")
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
        question_json = generate_interview_question(st.session_state.resume_text, st.session_state.role)
        try:
            question_data = json.loads(question_json)
            question = question_data.get("question", "")
            follow_up = question_data.get("follow_up_prompt", "")
        except Exception:
            question = question_json
            follow_up = ""
        st.session_state.messages.append({"role": "ai", "content": question, "follow_up": follow_up})

    for msg in st.session_state.messages:
        if msg["role"] == "ai":
            st.markdown(f"**AI Interviewer:** {msg['content']}")
        else:
            st.markdown(f"**You:** {msg['content']}")
            if "feedback" in msg:
                st.markdown(f"> **Feedback:**\n{msg['feedback']}")
            if "scores" in msg:
                st.markdown(f"📊 **Scores:**")
                st.markdown(
                    f"- Content: {msg['scores']['content_score']}/10\n"
                    f"- Clarity: {msg['scores']['clarity_score']}/10\n"
                    f"- Relevance: {msg['scores']['relevance_score']}/10\n"
                    f"- Confidence: {msg['scores']['confidence_score']}/10"
                )

    with st.form(key="user_input_form", clear_on_submit=True):
        user_input = st.text_area("Your answer:", key="user_input")
        submitted = st.form_submit_button("Submit")
        if submitted and user_input.strip():
            st.session_state.messages.append({"role": "user", "content": user_input})

            feedback_json = generate_feedback(user_input)
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
            scores = score_feedback(feedback)

            st.session_state.messages[-1]["feedback"] = feedback_str
            st.session_state.messages[-1]["scores"] = scores

            question_json = generate_interview_question(st.session_state.resume_text, st.session_state.role)
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
    st.markdown("---")
    st.markdown("### Download your interview session")
    text_data = build_session_history_text(st.session_state.messages)
    st.download_button("📄 Download as Text", text_data, file_name="interview_session.txt", mime="text/plain")
    try:
        pdf_data = build_session_history_pdf(st.session_state.messages)
        st.download_button("🧾 Download as PDF", pdf_data, file_name="interview_session.pdf", mime="application/pdf")
    except:
        st.info("Install fpdf with `pip install fpdf` to enable PDF export.")
else:
    st.info("Please upload a PDF resume and select a job role to begin.")
