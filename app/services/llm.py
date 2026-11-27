import re

import httpx

from app.core.config import get_settings

_SOURCE_HEADER = re.compile(r"Source\s+(\d+)\s*(?:\([^)]*\))?\s*:\s*", re.IGNORECASE)
_SENTENCE_BREAK = re.compile(r"(?<=[.!?])\s+")


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
                    "You are a careful document assistant. Answer only using the provided "
                    "document context. Cite supporting source numbers in square brackets, "
                    "for example [1]. If the answer is not in the context, say so plainly.\n\n"
                    "Format every answer for easy scanning:\n"
                    "- Start with one clear, direct sentence.\n"
                    "- Follow with 2-5 short bullet points for the key details.\n"
                    "- Use **bold** for important terms and keep sentences concise.\n"
                    "- Do not repeat the question or invent information."
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
    keywords = {
        word.lower().strip(".,:;!?()[]")
        for word in question.split()
        if len(word) > 3
    }
    ranked = []
    seen = set()

    for source_number, block_text in _split_sources(context):
        for sentence in _SENTENCE_BREAK.split(block_text):
            sentence = " ".join(sentence.split()).strip()
            if len(sentence) < 20 or sentence.lower() in seen:
                continue
            seen.add(sentence.lower())
            score = sum(1 for word in keywords if word in sentence.lower())
            if score:
                ranked.append((score, sentence, source_number))

    if not ranked:
        return "I do not know based on the uploaded document."

    ranked.sort(key=lambda item: item[0], reverse=True)
    lines = ["Here is the most relevant information from the document:", ""]
    for _, sentence, source_number in ranked[:4]:
        citation = f" [{source_number}]" if source_number else ""
        lines.append(f"- {sentence}{citation}")

    return "\n".join(lines)


def _split_sources(context: str) -> list[tuple[int | None, str]]:
    matches = list(_SOURCE_HEADER.finditer(context))
    if not matches:
        return [(None, context)]

    blocks = []
    for index, match in enumerate(matches):
        start = match.end()
        end = matches[index + 1].start() if index + 1 < len(matches) else len(context)
        blocks.append((int(match.group(1)), context[start:end]))
    return blocks
