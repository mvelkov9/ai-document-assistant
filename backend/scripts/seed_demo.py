import sys
from pathlib import Path
from uuid import uuid4

from sqlalchemy import select

from app.core.security import hash_password
from app.db.session import SessionLocal, init_db
from app.models.document import Document
from app.repositories.document_repository import DocumentRepository
from app.repositories.user_repository import UserRepository
from app.services.storage_service import StorageService

# Ensure the project root (/app) is on sys.path when running from scripts/
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))


DEMO_EMAIL = "demo.user@example.com"
DEMO_PASSWORD = "VerySecure123"
DEMO_FILENAME = "demo-company-policy.pdf"


def build_demo_pdf() -> bytes:
    content = (
        b"%PDF-1.4\n"
        b"1 0 obj<< /Type /Catalog /Pages 2 0 R >>endobj\n"
        b"2 0 obj<< /Type /Pages /Kids [3 0 R] /Count 1 >>endobj\n"
        b"3 0 obj<< /Type /Page /Parent 2 0 R /MediaBox [0 0 300 200] /Contents 4 0 R /Resources<< /Font<< /F1 5 0 R >> >> >>endobj\n"
        b"4 0 obj<< /Length 116 >>stream\n"
        b"BT /F1 12 Tf 20 160 Td (Demo company policy) Tj 0 -20 Td (Secure PDF handling and AI summaries.) Tj ET\n"
        b"endstream endobj\n"
        b"5 0 obj<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica >>endobj\n"
        b"xref\n0 6\n0000000000 65535 f \n0000000010 00000 n \n0000000063 00000 n \n0000000122 00000 n \n0000000265 00000 n \n0000000431 00000 n \n"
        b"trailer<< /Size 6 /Root 1 0 R >>\nstartxref\n501\n%%EOF\n"
    )
    return content


def main() -> None:
    init_db()
    db = SessionLocal()
    try:
        user_repository = UserRepository(db)
        document_repository = DocumentRepository(db)
        storage = StorageService()

        user = user_repository.get_by_email(DEMO_EMAIL)
        if not user:
            user = user_repository.create(
                email=DEMO_EMAIL,
                full_name="Demo User",
                password_hash=hash_password(DEMO_PASSWORD),
                role="admin",
            )
            print(f"Created demo user: {DEMO_EMAIL}")
        else:
            print(f"Demo user already exists: {DEMO_EMAIL}")

        existing_document = db.scalar(
            select(Document).where(
                Document.owner_id == user.id,
                Document.original_filename == DEMO_FILENAME,
            )
        )

        if existing_document:
            print(f"Demo document already exists: {DEMO_FILENAME}")
            print(f"Login email: {DEMO_EMAIL}")
            print(f"Login password: {DEMO_PASSWORD}")
            return

        pdf_bytes = build_demo_pdf()
        storage_key = f"{user.id}/{uuid4()}-{Path(DEMO_FILENAME).name}"
        storage.upload_bytes(storage_key, pdf_bytes, "application/pdf")

        document = document_repository.create(
            owner_id=user.id,
            original_filename=DEMO_FILENAME,
            storage_key=storage_key,
            content_type="application/pdf",
            size_bytes=len(pdf_bytes),
        )
        document.summary_text = (
            "This demo PDF explains secure handling of internal PDF files and the use of AI-powered summaries."
        )
        document.processing_status = "ready"
        db.add(document)
        db.commit()

        print(f"Created demo document: {DEMO_FILENAME}")
        print(f"Login email: {DEMO_EMAIL}")
        print(f"Login password: {DEMO_PASSWORD}")
    finally:
        db.close()


if __name__ == "__main__":
    main()
