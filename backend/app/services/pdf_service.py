from io import BytesIO

import fitz  # PyMuPDF — much better text extraction than pypdf
from pypdf import PdfReader


class PdfService:
    def extract_text(self, content: bytes) -> str:
        # Primary: PyMuPDF (handles complex fonts, tables, encodings)
        result = self._extract_with_pymupdf(content)

        # Fallback: pypdf if PyMuPDF yields very little
        if len(result) < 50:
            pypdf_result = self._extract_with_pypdf(content)
            if len(pypdf_result) > len(result):
                result = pypdf_result

        return result

    @staticmethod
    def _extract_with_pymupdf(content: bytes) -> str:
        doc = fitz.open(stream=content, filetype="pdf")
        parts: list[str] = []
        for page in doc:
            text = page.get_text().strip()
            if text:
                parts.append(text)
        doc.close()
        return "\n\n".join(parts)

    @staticmethod
    def _extract_with_pypdf(content: bytes) -> str:
        reader = PdfReader(BytesIO(content))
        parts: list[str] = []
        for page in reader.pages:
            text = page.extract_text() or ""
            cleaned = text.strip()
            if cleaned:
                parts.append(cleaned)

        result = "\n\n".join(parts)

        # If standard extraction yields very little text, retry with layout mode
        if len(result) < 50:
            layout_parts: list[str] = []
            for page in reader.pages:
                text = page.extract_text(extraction_mode="layout") or ""
                cleaned = text.strip()
                if cleaned:
                    layout_parts.append(cleaned)
            layout_result = "\n\n".join(layout_parts)
            if len(layout_result) > len(result):
                result = layout_result

        return result
