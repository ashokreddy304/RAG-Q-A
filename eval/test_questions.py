"""
Test questions for evaluating the RAG system.
These are generic questions that work with any PDF document.
"""

TEST_QUESTIONS = [
    {
        "id": 1,
        "question": "What is the main topic or title of this document?",
        "expected_answer_contains": ["document", "topic", "title"],
        "difficulty": "easy",
    },
    {
        "id": 2,
        "question": "Who is the author or creator of this document?",
        "expected_answer_contains": ["author", "created", "produced"],
        "difficulty": "medium",
    },
    {
        "id": 3,
        "question": "What are the key points or main sections discussed in this document?",
        "expected_answer_contains": ["sections", "topics", "points"],
        "difficulty": "medium",
    },
    {
        "id": 4,
        "question": "What data or statistics are mentioned in this document?",
        "expected_answer_contains": ["data", "statistics", "numbers"],
        "difficulty": "medium",
    },
    {
        "id": 5,
        "question": "What is the conclusion or main takeaway from this document?",
        "expected_answer_contains": ["conclusion", "summary", "takeaway"],
        "difficulty": "hard",
    },
    {
        "id": 6,
        "question": "Are there any tables or structured data in this document? If so, describe them.",
        "expected_answer_contains": ["table", "data", "structure"],
        "difficulty": "medium",
    },
    {
        "id": 7,
        "question": "What are the references or sources cited in this document?",
        "expected_answer_contains": ["reference", "source", "cited"],
        "difficulty": "hard",
    },
    {
        "id": 8,
        "question": "Can you summarize the document in 2-3 sentences?",
        "expected_answer_contains": ["summary", "brief", "overall"],
        "difficulty": "hard",
    },
]


def get_test_questions(difficulty: str = None) -> list:
    """
    Get test questions, optionally filtered by difficulty.

    Args:
        difficulty: Filter by 'easy', 'medium', or 'hard' (None for all)

    Returns:
        List of test question dictionaries
    """
    if difficulty is None:
        return TEST_QUESTIONS

    return [q for q in TEST_QUESTIONS if q['difficulty'] == difficulty]
