import re
import PyPDF2

def extract_text_from_pdf(pdf_path):
    with open(pdf_path, 'rb') as file:
        reader = PyPDF2.PdfReader(file)
        text = ''
        for page in reader.pages:
            page_text = page.extract_text()
            if page_text:
                text += page_text + '\n'
    return text

def extract_email(text):
    match = re.search(r'[\w\.-]+@[\w\.-]+\.\w+', text)
    return match.group(0) if match else None

def extract_phone(text):
    # More robust phone number pattern
    match = re.search(r'(\+?\d{1,3}[\s\-\.]?)?\(?\d{2,4}\)?[\s\-\.]?\d{3,4}[\s\-\.]?\d{3,4}', text)
    return match.group(0) if match else None

def extract_name(text):
    # Improved logic: look for short capitalized name-like lines at the top
    lines = text.strip().split('\n')
    for line in lines:
        words = line.strip().split()
        if 1 <= len(words) <= 4 and all(w[0].isupper() for w in words if w.isalpha()):
            return line.strip()
    return None

def extract_skills(text):
    # You can expand this list as needed
    skill_keywords = [
        'Python', 'Java', 'C++', 'C#', 'JavaScript', 'HTML', 'CSS',
        'Machine Learning', 'Deep Learning', 'Data Analysis',
        'SQL', 'MongoDB', 'Django', 'Flask', 'Pandas', 'NumPy',
        'AWS', 'Azure', 'Git', 'Docker', 'Kubernetes', 'React', 'Node.js'
    ]
    found_skills = [skill for skill in skill_keywords if re.search(r'\b' + re.escape(skill) + r'\b', text, re.I)]
    return found_skills

def extract_experience(text):
    # Naive extraction of lines mentioning experience or work
    experience_lines = []
    for line in text.split('\n'):
        if re.search(r'\b(experience|worked|at|company|intern)\b', line, re.I):
            experience_lines.append(line.strip())
    return experience_lines

def extract_education(text):
    edu_keywords = ['Bachelor', 'Master', 'B.Tech', 'M.Tech', 'BSc', 'MSc', 'BE', 'ME', 'Degree', 'University', 'College']
    education_lines = []
    for line in text.split('\n'):
        if any(keyword in line for keyword in edu_keywords):
            education_lines.append(line.strip())
    return education_lines

if __name__ == '__main__':
    pdf_path = 'resume.pdf'  # 🔁 Change this to your actual file path

    # Extract full text
    text = extract_text_from_pdf(pdf_path)

    # Display parsed info
    print("\n--- 📄 Resume Summary ---")
    print("👤 Name:", extract_name(text))
    print("📧 Email:", extract_email(text))
    print("📱 Phone:", extract_phone(text))
    print("🛠️ Skills:", ', '.join(extract_skills(text)))
    
    print("\n💼 Experience:")
    experience = extract_experience(text)
    if experience:
        for exp in experience:
            print("•", exp)
    else:
        print("• No specific experience found.")

    print("\n🎓 Education:")
    education = extract_education(text)
    if education:
        for edu in education:
            print("•", edu)
    else:
        print("• No specific education info found.")
