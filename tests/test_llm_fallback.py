from app.services.llm import _fallback_answer


def test_fallback_answer_uses_context_keywords():
    answer = _fallback_answer(
        "What does the document say about invoices?",
        "Invoices are stored for audit review. Weather is unrelated.",
    )

    assert "Invoices are stored" in answer
