"""Unit tests for SummaryService: chunking, BM25 ranking, fallback, and provider dispatch."""

import asyncio

import pytest

from app.services.summary_service import SummaryService, _CHUNK_OVERLAP, _CHUNK_SIZE, _TOP_K_CHUNKS


def _run(coro):
    """Run an async coroutine synchronously."""
    return asyncio.run(coro)


@pytest.fixture
def svc(monkeypatch):
    monkeypatch.setenv("GROQ_API_KEY", "")
    monkeypatch.setenv("GEMINI_API_KEY", "")
    monkeypatch.setenv("OPENAI_API_KEY", "")
    from app.core.config import get_settings

    get_settings.cache_clear()
    s = SummaryService()
    yield s
    get_settings.cache_clear()


# ── _chunk_text ──────────────────────────────────────────────────


def test_chunk_text_short_text():
    text = "This is a short text."
    chunks = SummaryService._chunk_text(text)
    assert chunks == [text]


def test_chunk_text_exact_chunk_size():
    words = ["word"] * _CHUNK_SIZE
    text = " ".join(words)
    chunks = SummaryService._chunk_text(text)
    assert chunks == [text]


def test_chunk_text_overlapping():
    word_count = _CHUNK_SIZE + 200
    words = [f"w{i}" for i in range(word_count)]
    text = " ".join(words)
    chunks = SummaryService._chunk_text(text)
    assert len(chunks) >= 2
    assert len(chunks[0].split()) == _CHUNK_SIZE
    first_words = set(chunks[0].split())
    second_words = set(chunks[1].split())
    overlap = first_words & second_words
    assert len(overlap) >= _CHUNK_OVERLAP


def test_chunk_text_empty_string():
    chunks = SummaryService._chunk_text("")
    assert chunks == [""]


# ── _tokenize ────────────────────────────────────────────────────


def test_tokenize_lowercase():
    tokens = SummaryService._tokenize("Hello WORLD Test123")
    assert "hello" in tokens
    assert "world" in tokens
    assert "test123" in tokens


def test_tokenize_strips_punctuation():
    tokens = SummaryService._tokenize("hello, world! how's it?")
    assert "hello" in tokens
    assert "world" in tokens
    assert "how" in tokens


def test_tokenize_empty():
    assert SummaryService._tokenize("") == []


# ── _rank_chunks ─────────────────────────────────────────────────


def test_rank_chunks_fewer_than_top_k():
    svc = SummaryService.__new__(SummaryService)
    chunks = ["chunk one", "chunk two"]
    result = svc._rank_chunks(chunks, "one")
    assert result == chunks


def test_rank_chunks_returns_top_k():
    svc = SummaryService.__new__(SummaryService)
    chunks = [f"chunk about topic{i} with various words" for i in range(20)]
    result = svc._rank_chunks(chunks, "topic0")
    assert len(result) == _TOP_K_CHUNKS


def test_rank_chunks_relevance_order():
    svc = SummaryService.__new__(SummaryService)
    chunks = [
        "The cat sleeps on the bed quietly at night",
        "Dogs love to play fetch in the park",
        "The weather forecast predicts sunny days ahead",
        "Football match results from yesterday evening game",
        "Cooking pasta recipes for Italian dinner tonight",
        "Python programming language for web development projects",
    ]
    result = svc._rank_chunks(chunks, "cat bed night")
    assert result[0] == chunks[0]


def test_rank_chunks_empty_query():
    svc = SummaryService.__new__(SummaryService)
    chunks = [f"chunk {i}" for i in range(10)]
    result = svc._rank_chunks(chunks, "")
    assert len(result) == _TOP_K_CHUNKS
    assert result == chunks[:_TOP_K_CHUNKS]


# ── _fallback_summary / _fallback_answer ─────────────────────────


def test_fallback_summary(svc):
    text = "This is a test document with some content about machine learning."
    result = svc._fallback_summary(text)
    assert "Fallback summary mode" in result
    assert "machine learning" in result


def test_fallback_summary_truncates_long_text(svc):
    text = "word " * 500
    result = svc._fallback_summary(text)
    assert "..." in result
    assert len(result) < len(text) + 200


def test_fallback_answer(svc):
    text = "AI systems can process documents."
    question = "What can AI do?"
    result = svc._fallback_answer(text, question)
    assert "Fallback Q&A mode" in result
    assert question in result


# ── _provider detection ──────────────────────────────────────────


def test_provider_none_when_no_keys(svc):
    assert svc._provider is None


def test_provider_groq_when_groq_set(monkeypatch):
    monkeypatch.setenv("GROQ_API_KEY", "test-key")
    monkeypatch.setenv("GEMINI_API_KEY", "")
    monkeypatch.setenv("OPENAI_API_KEY", "")
    from app.core.config import get_settings

    get_settings.cache_clear()
    svc = SummaryService()
    assert svc._provider == "groq"
    get_settings.cache_clear()


def test_provider_gemini_when_gemini_set(monkeypatch):
    monkeypatch.setenv("GROQ_API_KEY", "")
    monkeypatch.setenv("GEMINI_API_KEY", "test-key")
    monkeypatch.setenv("OPENAI_API_KEY", "")
    from app.core.config import get_settings

    get_settings.cache_clear()
    svc = SummaryService()
    assert svc._provider == "gemini"
    get_settings.cache_clear()


def test_provider_openai_when_openai_set(monkeypatch):
    monkeypatch.setenv("GROQ_API_KEY", "")
    monkeypatch.setenv("GEMINI_API_KEY", "")
    monkeypatch.setenv("OPENAI_API_KEY", "test-key")
    from app.core.config import get_settings

    get_settings.cache_clear()
    svc = SummaryService()
    assert svc._provider == "openai"
    get_settings.cache_clear()


def test_provider_groq_takes_priority(monkeypatch):
    """When multiple keys are set, groq should be preferred."""
    monkeypatch.setenv("GROQ_API_KEY", "gk")
    monkeypatch.setenv("GEMINI_API_KEY", "gemk")
    monkeypatch.setenv("OPENAI_API_KEY", "oaik")
    from app.core.config import get_settings

    get_settings.cache_clear()
    svc = SummaryService()
    assert svc._provider == "groq"
    get_settings.cache_clear()


# ── summarize() and answer_question() with fallback ──────────────


def test_summarize_fallback_when_no_provider(svc):
    result = _run(svc.summarize("This is a test document about science."))
    assert "Fallback summary mode" in result


def test_summarize_empty_text(svc):
    result = _run(svc.summarize(""))
    assert "does not contain enough" in result


def test_summarize_whitespace_only(svc):
    result = _run(svc.summarize("   \n\t  "))
    assert "does not contain enough" in result


def test_answer_question_fallback(svc):
    answer, mode = _run(svc.answer_question("Document about animals.", "What animals?"))
    assert "Fallback Q&A mode" in answer
    assert mode == "fallback"


def test_answer_question_empty_text(svc):
    answer, mode = _run(svc.answer_question("", "What is this?"))
    assert "does not contain enough" in answer
    assert mode == "fallback"


# ── Helpers for mocking httpx ────────────────────────────────────


class _FakeOK200:
    status_code = 200

    def __init__(self, data):
        self._data = data

    def json(self):
        return self._data

    def raise_for_status(self):
        pass


class _FakeError:
    def __init__(self, code):
        self.status_code = code


def _make_fake_client(responses):
    """Return a fake async httpx client class that cycles through responses."""
    call_idx = {"i": 0}

    class _Client:
        def __init__(self, **kw):
            pass

        async def __aenter__(self):
            return self

        async def __aexit__(self, *a):
            pass

        async def post(self, url, **kw):
            idx = call_idx["i"]
            call_idx["i"] += 1
            return responses[min(idx, len(responses) - 1)]

    return _Client


def _noop_sleep(s):
    """Replacement for asyncio.sleep — returns immediately."""

    async def _inner():
        pass

    return _inner()


# ── _call_groq / _call_gemini / _call_openai with mocked httpx ─


def test_call_groq_success(monkeypatch):
    monkeypatch.setenv("GROQ_API_KEY", "test-groq-key")
    monkeypatch.setenv("GROQ_MODEL", "llama3-8b-8192")
    from app.core.config import get_settings

    get_settings.cache_clear()
    svc = SummaryService()

    import httpx

    resp = _FakeOK200({"choices": [{"message": {"content": "  Groq summary result  "}}]})
    monkeypatch.setattr(httpx, "AsyncClient", _make_fake_client([resp]))
    result = _run(svc._call_groq("system prompt", "user text"))
    assert result == "Groq summary result"
    get_settings.cache_clear()


def test_call_groq_rate_limit_retry(monkeypatch):
    monkeypatch.setenv("GROQ_API_KEY", "test-groq-key")
    monkeypatch.setenv("GROQ_MODEL", "llama3-8b-8192")
    from app.core.config import get_settings

    get_settings.cache_clear()
    svc = SummaryService()

    import httpx

    resp_429 = _FakeError(429)
    resp_200 = _FakeOK200({"choices": [{"message": {"content": "After retry"}}]})
    monkeypatch.setattr(httpx, "AsyncClient", _make_fake_client([resp_429, resp_200]))
    monkeypatch.setattr(asyncio, "sleep", _noop_sleep)
    result = _run(svc._call_groq("system", "text"))
    assert result == "After retry"
    get_settings.cache_clear()


def test_call_groq_auth_failure(monkeypatch):
    monkeypatch.setenv("GROQ_API_KEY", "bad-key")
    monkeypatch.setenv("GROQ_MODEL", "llama3-8b-8192")
    from app.core.config import get_settings

    get_settings.cache_clear()
    svc = SummaryService()

    import httpx

    monkeypatch.setattr(httpx, "AsyncClient", _make_fake_client([_FakeError(401)]))
    with pytest.raises(RuntimeError, match="Groq API key is invalid"):
        _run(svc._call_groq("system", "text"))
    get_settings.cache_clear()


def test_call_groq_max_retries_exceeded(monkeypatch):
    monkeypatch.setenv("GROQ_API_KEY", "test-key")
    monkeypatch.setenv("GROQ_MODEL", "llama3-8b-8192")
    from app.core.config import get_settings

    get_settings.cache_clear()
    svc = SummaryService()

    import httpx

    monkeypatch.setattr(httpx, "AsyncClient", _make_fake_client([_FakeError(429)]))
    monkeypatch.setattr(asyncio, "sleep", _noop_sleep)
    with pytest.raises(RuntimeError, match="rate limit.*after retries"):
        _run(svc._call_groq("system", "text"))
    get_settings.cache_clear()


def test_call_gemini_success(monkeypatch):
    monkeypatch.setenv("GEMINI_API_KEY", "test-gemini-key")
    monkeypatch.setenv("GEMINI_MODEL", "gemini-2.0-flash")
    monkeypatch.setenv("GROQ_API_KEY", "")
    from app.core.config import get_settings

    get_settings.cache_clear()
    svc = SummaryService()

    import httpx

    resp = _FakeOK200({"candidates": [{"content": {"parts": [{"text": "  Gemini result  "}]}}]})
    monkeypatch.setattr(httpx, "AsyncClient", _make_fake_client([resp]))
    result = _run(svc._call_gemini("system", "text"))
    assert result == "Gemini result"
    get_settings.cache_clear()


def test_call_gemini_auth_failure(monkeypatch):
    monkeypatch.setenv("GEMINI_API_KEY", "bad-key")
    monkeypatch.setenv("GROQ_API_KEY", "")
    from app.core.config import get_settings

    get_settings.cache_clear()
    svc = SummaryService()

    import httpx

    monkeypatch.setattr(httpx, "AsyncClient", _make_fake_client([_FakeError(403)]))
    with pytest.raises(RuntimeError, match="Gemini API key is invalid"):
        _run(svc._call_gemini("system", "text"))
    get_settings.cache_clear()


def test_call_openai_success(monkeypatch):
    monkeypatch.setenv("OPENAI_API_KEY", "test-openai-key")
    monkeypatch.setenv("OPENAI_MODEL", "gpt-4o-mini")
    monkeypatch.setenv("GROQ_API_KEY", "")
    monkeypatch.setenv("GEMINI_API_KEY", "")
    from app.core.config import get_settings

    get_settings.cache_clear()
    svc = SummaryService()

    import httpx

    resp = _FakeOK200({"choices": [{"message": {"content": "  OpenAI result  "}}]})
    monkeypatch.setattr(httpx, "AsyncClient", _make_fake_client([resp]))
    result = _run(svc._call_openai("system", "text"))
    assert result == "OpenAI result"
    get_settings.cache_clear()


def test_call_openai_auth_failure(monkeypatch):
    monkeypatch.setenv("OPENAI_API_KEY", "bad-key")
    monkeypatch.setenv("GROQ_API_KEY", "")
    monkeypatch.setenv("GEMINI_API_KEY", "")
    from app.core.config import get_settings

    get_settings.cache_clear()
    svc = SummaryService()

    import httpx

    monkeypatch.setattr(httpx, "AsyncClient", _make_fake_client([_FakeError(401)]))
    with pytest.raises(RuntimeError, match="OpenAI API key is invalid"):
        _run(svc._call_openai("system", "text"))
    get_settings.cache_clear()
