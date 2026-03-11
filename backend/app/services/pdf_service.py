from io import BytesIO

from pypdf import PdfReader


class PdfService:
    def extract_text(self, content: bytes) -> str:
        reader = PdfReader(BytesIO(content))
        parts: list[str] = []
        for page in reader.pages:
            text = page.extract_text() or ""
            cleaned = text.strip()
            if cleaned:
                parts.append(cleaned)
        return "\n\n".join(parts)
