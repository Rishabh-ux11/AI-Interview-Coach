import json

def load_templates(json_path, job_role, round_type):
    """
    Loads interview question templates from a JSON file based on job role and round type.

    Args:
        json_path (str): Path to the JSON file containing templates.
        job_role (str): Job role to filter templates (e.g., "Software Engineer").
        round_type (str): Round type to filter templates (e.g., "Technical", "HR", "System Design").

    Returns:
        list: List of question templates matching the criteria, or an empty list if none found.
    """
    with open(json_path, 'r', encoding='utf-8') as f:
        templates = json.load(f)
    return [
        q for q in templates
        if q.get("job_role", "").lower() == job_role.lower()
        and q.get("round_type", "").lower() == round_type.lower()
    ]

if __name__ == "__main__":
    # Example usage
    path = "interview_questions.json"
    role = input("Enter job role (e.g., Software Engineer): ")
    round_type = input("Enter round type (e.g., Technical, HR, System Design): ")
    questions = load_templates(path, role, round_type)
    if questions:
        print(f"\nQuestions for {role} - {round_type}:")
        for q in questions:
            print("-", q["question"])
    else:
        print("No questions found for this role and round type.")