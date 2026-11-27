from app.services.llm import _fallback_answer


def test_fallback_answer_uses_context_keywords():
    answer = _fallback_answer(
        "What does the document say about invoices?",
        "Invoices are stored for audit review. Weather is unrelated.",
    )

    assert "Invoices are stored" in answer


def test_fallback_answer_returns_structured_bullets_with_citations():
    answer = _fallback_answer(
        "What does the document say about invoices?",
        "Source 1 (page 2, file: report.pdf):\nInvoices are stored for audit review.",
    )

    assert answer.splitlines()[0] == "Here is the most relevant information from the document:"
    assert "- Invoices are stored for audit review. [1]" in answer
