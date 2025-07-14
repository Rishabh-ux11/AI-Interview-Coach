def score_feedback(feedback):
    """
    Assigns a score out of 10 for content, clarity, confidence, and relevance
    based on descriptive strings. Uses keyword-based heuristics.

    Args:
        feedback (dict): {
            "content_depth": "...",
            "clarity": "...",
            "relevance": "...",
            "confidence": "..."
        }

    Returns:
        dict: Individual scores and overall average.
    """
    def score_from_text(text):
        text = text.lower()

        score = 5  # Default neutral score

        strong_pos = ["excellent", "outstanding", "exceptional", "perfect", "impressive"]
        moderate_pos = ["good", "clear", "strong", "well", "confident", "relevant", "detailed"]
        average = ["adequate", "average", "satisfactory", "acceptable", "reasonable"]
        weak = ["basic", "somewhat", "fair", "limited", "partially", "needs improvement"]
        negative = ["poor", "lacking", "unclear", "weak", "insufficient", "incomplete", "confusing"]

        # Priority from strongest to weakest
        if any(word in text for word in strong_pos):
            score = 10
        elif any(word in text for word in moderate_pos):
            score = 8
        elif any(word in text for word in average):
            score = 6
        elif any(word in text for word in weak):
            score = 4
        elif any(word in text for word in negative):
            score = 2

        return score

    content = score_from_text(feedback.get("content_depth", ""))
    clarity = score_from_text(feedback.get("clarity", ""))
    relevance = score_from_text(feedback.get("relevance", ""))
    confidence = score_from_text(feedback.get("confidence", ""))

    return {
        "content_score": content,
        "clarity_score": clarity,
        "relevance_score": relevance,
        "confidence_score": confidence,
        "average_score": round((content + clarity + relevance + confidence) / 4, 2)
    }

# 🔍 Example usage
if __name__ == "__main__":
    sample_feedback = {
        "content_depth": "The answer was strong and showed deep understanding.",
        "clarity": "Very clear explanation with well-structured sentences.",
        "relevance": "Highly relevant to the question asked.",
        "confidence": "The response was given with noticeable confidence."
    }

    scores = score_feedback(sample_feedback)
    print("\n🎯 Scored Feedback:")
    for k, v in scores.items():
        print(f"{k.replace('_', ' ').title()}: {v}/10")
