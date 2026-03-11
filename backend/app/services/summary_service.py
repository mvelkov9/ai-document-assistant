import asyncio
import math
import re
import textwrap
from collections import Counter

import httpx

from app.core.config import get_settings

_MAX_RETRIES = 3
_RETRY_BACKOFF = (2, 5, 10)
_CHUNK_SIZE = 800
_CHUNK_OVERLAP = 100
_TOP_K_CHUNKS = 5


class SummaryService:
    def __init__(self) -> None:
        self.settings = get_settings()

    @property
    def _provider(self) -> str | None:
        """Return which AI provider is configured: 'groq', 'gemini', 'openai', or None."""
        if self.settings.groq_api_key:
            return "groq"
        if self.settings.gemini_api_key:
            return "gemini"
        if self.settings.openai_api_key:
            return "openai"
        return None

    async def summarize(self, text: str) -> str:
        normalized = " ".join(text.split())
        limited = normalized[: self.settings.summary_max_chars]
        if not limited:
            return "Document does not contain enough machine-readable text for summarization."

        if self._provider:
            return await self._provider_summary(limited)
        return self._fallback_summary(limited)

    async def answer_question(self, text: str, question: str) -> tuple[str, str]:
        normalized = " ".join(text.split())
        if not normalized:
            return (
                "The document does not contain enough machine-readable text to answer the question.",
                "fallback",
            )

        # RAG-lite: chunk the text and rank by relevance to the question
        chunks = self._chunk_text(normalized)
        ranked = self._rank_chunks(chunks, question)
        context = "\n\n".join(ranked[:_TOP_K_CHUNKS])
        limited = context[: self.settings.summary_max_chars]

        if self._provider:
            return await self._provider_answer(limited, question), "provider"
        return self._fallback_answer(limited, question), "fallback"

    # ── RAG-lite: chunking and BM25 ranking ────────────────────────

    @staticmethod
    def _chunk_text(text: str) -> list[str]:
        """Split text into overlapping chunks for better context retrieval."""
        words = text.split()
        if len(words) <= _CHUNK_SIZE:
            return [text]
        chunks = []
        step = _CHUNK_SIZE - _CHUNK_OVERLAP
        for i in range(0, len(words), step):
            chunk = " ".join(words[i : i + _CHUNK_SIZE])
            if chunk.strip():
                chunks.append(chunk)
        return chunks

    @staticmethod
    def _tokenize(text: str) -> list[str]:
        return re.findall(r"\w+", text.lower())

    def _rank_chunks(self, chunks: list[str], query: str) -> list[str]:
        """Rank chunks by BM25 relevance to the query."""
        if len(chunks) <= _TOP_K_CHUNKS:
            return chunks

        query_tokens = self._tokenize(query)
        if not query_tokens:
            return chunks[:_TOP_K_CHUNKS]

        # Compute IDF
        n = len(chunks)
        doc_freq: Counter = Counter()
        chunk_token_lists = []
        chunk_lengths = []
        for chunk in chunks:
            tokens = self._tokenize(chunk)
            chunk_token_lists.append(tokens)
            chunk_lengths.append(len(tokens))
            unique_tokens = set(tokens)
            for t in unique_tokens:
                doc_freq[t] += 1

        avg_dl = sum(chunk_lengths) / n if n else 1
        k1 = 1.5
        b = 0.75

        scores = []
        for i, tokens in enumerate(chunk_token_lists):
            tf_map = Counter(tokens)
            dl = chunk_lengths[i]
            score = 0.0
            for qt in query_tokens:
                df = doc_freq.get(qt, 0)
                if df == 0:
                    continue
                idf = math.log((n - df + 0.5) / (df + 0.5) + 1)
                tf = tf_map.get(qt, 0)
                tf_norm = (tf * (k1 + 1)) / (tf + k1 * (1 - b + b * dl / avg_dl))
                score += idf * tf_norm
            scores.append(score)

        ranked_indices = sorted(range(n), key=lambda i: scores[i], reverse=True)
        return [chunks[i] for i in ranked_indices[:_TOP_K_CHUNKS]]

    # ── Gemini REST API ──────────────────────────────────────────────

    async def _call_gemini(self, system: str, user_text: str) -> str:
        """Call Google Gemini generateContent with retry on 429."""
        model = self.settings.gemini_model
        url = (
            f"https://generativelanguage.googleapis.com/v1beta/"
            f"models/{model}:generateContent?key={self.settings.gemini_api_key}"
        )
        payload = {
            "system_instruction": {"parts": [{"text": system}]},
            "contents": [{"parts": [{"text": user_text}]}],
            "generationConfig": {"temperature": 0.2},
        }
        last_exc: Exception | None = None
        for attempt in range(_MAX_RETRIES):
            async with httpx.AsyncClient(timeout=60.0) as client:
                response = await client.post(url, json=payload)
                if response.status_code == 429:
                    wait = _RETRY_BACKOFF[attempt] if attempt < len(_RETRY_BACKOFF) else 10
                    last_exc = RuntimeError("Gemini rate limited")
                    await asyncio.sleep(wait)
                    continue
                if response.status_code in (401, 403):
                    raise RuntimeError(
                        "Gemini API key is invalid or lacks permissions. "
                        "Check GEMINI_API_KEY in your .env file."
                    )
                response.raise_for_status()
                data = response.json()
                return data["candidates"][0]["content"]["parts"][0]["text"].strip()
        raise RuntimeError(
            "Gemini API rate limit (429) after retries. "
            "Check https://aistudio.google.com/usage"
        ) from last_exc

    # ── OpenAI REST API (optional fallback) ─────────────────────────

    async def _call_openai(self, system: str, user_text: str) -> str:
        """Call OpenAI chat completions with retry on 429."""
        headers = {
            "Authorization": f"Bearer {self.settings.openai_api_key}",
            "Content-Type": "application/json",
        }
        payload = {
            "model": self.settings.openai_model,
            "messages": [
                {"role": "system", "content": system},
                {"role": "user", "content": user_text},
            ],
            "temperature": 0.2,
        }
        last_exc: Exception | None = None
        for attempt in range(_MAX_RETRIES):
            async with httpx.AsyncClient(timeout=60.0) as client:
                response = await client.post(
                    "https://api.openai.com/v1/chat/completions",
                    headers=headers,
                    json=payload,
                )
                if response.status_code == 429:
                    wait = _RETRY_BACKOFF[attempt] if attempt < len(_RETRY_BACKOFF) else 10
                    last_exc = RuntimeError("OpenAI rate limited")
                    await asyncio.sleep(wait)
                    continue
                if response.status_code in (401, 403):
                    raise RuntimeError(
                        "OpenAI API key is invalid or expired. "
                        "Check OPENAI_API_KEY in your .env file."
                    )
                response.raise_for_status()
                data = response.json()
                return data["choices"][0]["message"]["content"].strip()
        raise RuntimeError(
            "OpenAI API rate limit (429) after retries. "
            "Check https://platform.openai.com/usage"
        ) from last_exc

    # ── Groq REST API (free, OpenAI-compatible) ─────────────────────

    async def _call_groq(self, system: str, user_text: str) -> str:
        """Call Groq chat completions (OpenAI-compatible) with retry on 429."""
        headers = {
            "Authorization": f"Bearer {self.settings.groq_api_key}",
            "Content-Type": "application/json",
        }
        payload = {
            "model": self.settings.groq_model,
            "messages": [
                {"role": "system", "content": system},
                {"role": "user", "content": user_text},
            ],
            "temperature": 0.2,
        }
        last_exc: Exception | None = None
        for attempt in range(_MAX_RETRIES):
            async with httpx.AsyncClient(timeout=60.0) as client:
                response = await client.post(
                    "https://api.groq.com/openai/v1/chat/completions",
                    headers=headers,
                    json=payload,
                )
                if response.status_code == 429:
                    wait = _RETRY_BACKOFF[attempt] if attempt < len(_RETRY_BACKOFF) else 10
                    last_exc = RuntimeError("Groq rate limited")
                    await asyncio.sleep(wait)
                    continue
                if response.status_code in (401, 403):
                    raise RuntimeError(
                        "Groq API key is invalid or lacks permissions. "
                        "Check GROQ_API_KEY in your .env file."
                    )
                response.raise_for_status()
                data = response.json()
                return data["choices"][0]["message"]["content"].strip()
        raise RuntimeError(
            "Groq API rate limit (429) after retries. "
            "Check https://console.groq.com/settings/limits"
        ) from last_exc

    # ── Unified dispatch ─────────────────────────────────────────────

    async def _call_ai(self, system: str, user_text: str) -> str:
        provider = self._provider
        if provider == "groq":
            return await self._call_groq(system, user_text)
        if provider == "gemini":
            return await self._call_gemini(system, user_text)
        return await self._call_openai(system, user_text)

    async def _provider_summary(self, text: str) -> str:
        return await self._call_ai(
            "Summarize the provided document text into a concise academic and business-oriented summary. "
            "IMPORTANT: Respond in the SAME language as the document text. "
            "Do NOT use markdown formatting — no bold (**), no bullet points (*), no numbered lists (1.), no headings (#). "
            "Write the summary as clean, flowing plain-text paragraphs.",
            text,
        )

    async def _provider_answer(self, text: str, question: str) -> str:
        return await self._call_ai(
            "Answer the user's question using only the provided document context. "
            "If the answer is not supported by the context, say so explicitly. "
            "IMPORTANT: Respond in the SAME language as the question. "
            "Do NOT use markdown formatting — write clean plain-text only.",
            f"Document context: {text}\n\nQuestion: {question}",
        )

    def _fallback_summary(self, text: str) -> str:
        excerpt = textwrap.shorten(text, width=700, placeholder="...")
        return (
            "Fallback summary mode is active because no external AI API key is configured. "
            f"Key document excerpt: {excerpt}"
        )

    def _fallback_answer(self, text: str, question: str) -> str:
        excerpt = textwrap.shorten(text, width=900, placeholder="...")
        return (
            "Fallback Q&A mode is active because no external AI API key is configured. "
            f"Question received: {question}. Relevant excerpt: {excerpt}"
        )
