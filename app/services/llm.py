import httpx

from app.core.config import get_settings


async def generate_answer(question: str, context: str) -> str:
    settings = get_settings()
    if not settings.openai_api_key:
        return _fallback_answer(question, context)

    url = f"{settings.openai_api_base_url.rstrip('/')}/chat/completions"
    headers = {"Authorization": f"Bearer {settings.openai_api_key}"}
    payload = {
        "model": settings.llm_model,
        "messages": [
            {
                "role": "system",
                "content": (
                    "Answer using only the provided document context. "
                    "If the answer is not in the context, say you do not know."
                ),
            },
            {"role": "user", "content": f"Context:\n{context}\n\nQuestion: {question}"},
        ],
        "temperature": 0.2,
    }

    async with httpx.AsyncClient(timeout=60) as client:
        response = await client.post(url, headers=headers, json=payload)
        response.raise_for_status()
        data = response.json()
        return data["choices"][0]["message"]["content"].strip()


def _fallback_answer(question: str, context: str) -> str:
    sentences = [part.strip() for part in context.replace("\n", " ").split(".") if part.strip()]
    if not sentences:
        return "I do not know based on the uploaded document."

    keywords = {word.lower().strip(".,:;!?") for word in question.split() if len(word) > 3}
    ranked = sorted(
        sentences,
        key=lambda sentence: sum(1 for word in keywords if word in sentence.lower()),
        reverse=True,
    )
    answer = ". ".join(ranked[:3])
    return f"{answer}." if answer else "I do not know based on the uploaded document."
