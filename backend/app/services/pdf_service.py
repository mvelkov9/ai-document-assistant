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
