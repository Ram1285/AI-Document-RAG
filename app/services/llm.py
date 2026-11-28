import re
import logging

import httpx

from app.core.config import get_settings

_SOURCE_HEADER = re.compile(r"Source\s+(\d+)\s*(?:\([^)]*\))?\s*:\s*", re.IGNORECASE)
_SENTENCE_BREAK = re.compile(r"(?<=[.!?])\s+")
logger = logging.getLogger(__name__)

_SYSTEM_PROMPT = (
    "You are a careful document assistant. Answer only using the provided document context. "
    "If the answer is not in the context, say you do not know. Cite supporting source numbers "
    "in square brackets, for example [1]. Keep the answer clear and concise."
)


async def generate_answer(question: str, context: str) -> str:
    settings = get_settings()
    messages = [
        {"role": "system", "content": _SYSTEM_PROMPT},
        {"role": "user", "content": f"Context:\n{context}\n\nQuestion: {question}"},
    ]

    # Ollama is the primary provider and runs on the user's machine.
    try:
        response = await _post_chat(
            f"{settings.ollama_base_url.rstrip('/')}/api/chat",
            timeout=120,
            json={
                "model": settings.ollama_model,
                "messages": messages,
                "stream": False,
                "keep_alive": "30m",
                "options": {"num_predict": 192},
            },
        )
        response.raise_for_status()
        answer = response.json()["message"]["content"].strip()
        if answer:
            return answer
        raise ValueError("Ollama returned an empty answer")
    except (httpx.HTTPError, KeyError, TypeError, ValueError) as exc:
        logger.warning("Ollama answer generation failed; trying configured fallback: %s", exc)

    # GPT-4o is optional and only called when an API key is explicitly configured.
    if settings.openai_api_key:
        try:
            response = await _post_chat(
                f"{settings.openai_api_base_url.rstrip('/')}/chat/completions",
                timeout=60,
                headers={"Authorization": f"Bearer {settings.openai_api_key}"},
                json={"model": settings.openai_model, "messages": messages, "temperature": 0.2},
            )
            response.raise_for_status()
            answer = response.json()["choices"][0]["message"]["content"].strip()
            if answer:
                return answer
            raise ValueError("GPT-4o returned an empty answer")
        except (httpx.HTTPError, KeyError, IndexError, TypeError, ValueError) as exc:
            logger.warning("GPT-4o answer generation failed; using local extractive fallback: %s", exc)

    return _fallback_answer(question, context)


async def _post_chat(
    url: str,
    timeout: float,
    json: dict,
    headers: dict | None = None,
) -> httpx.Response:
    async with httpx.AsyncClient(timeout=timeout) as client:
        return await client.post(url, json=json, headers=headers)


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
