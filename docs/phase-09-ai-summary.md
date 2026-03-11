# Phase 09 - AI Summary Integration

## Purpose

Extend the stored-document workflow with the first AI-supported value path: extracting text from uploaded PDFs and generating a summary that can be shown back to the user.

## Implemented changes

- added PDF text extraction service using `pypdf`
- added summarization service with two modes
- added provider mode using Groq (free tier, Llama 3.3 70B), Google Gemini, and OpenAI-compatible HTTP APIs
- added local fallback mode when no API key is configured
- added document repository update methods for processing state and stored summary text
- added authenticated summary endpoint for one document

## Why dual-mode summarization matters

The project should remain demonstrable even without immediate paid AI usage. The fallback mode keeps the workflow functional for local or low-cost demonstrations, while the provider mode preserves a realistic cloud integration architecture.

## Summary flow

1. user uploads a PDF document
2. user calls the summarize endpoint for that document
3. backend loads the file from MinIO
4. backend extracts text from the PDF
5. backend generates a summary through provider mode or fallback mode
6. summary is saved to the database and returned to the client

## Current limitations

- fallback summaries are heuristic, not model-generated
- extraction quality depends on embedded PDF text and not on OCR

## Security and cost notes

- external AI calls remain optional and configuration-driven
- fallback mode reduces mandatory API spend during development and evaluation
- only owner-accessible documents can be summarized through the API
- rate limiting enforced at 10 requests per minute on summarize and summarize-jobs endpoints
- both synchronous and asynchronous summary paths are available

## Verification

- Python source compilation completed after AI summary integration
- editor diagnostics reported no immediate file errors

## Next step

Build document question-answer functionality and then move summary/Q&A execution into background processing.
