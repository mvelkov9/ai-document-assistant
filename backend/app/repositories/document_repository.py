from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.document import Document


class DocumentRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def create(
        self,
        owner_id: str,
        original_filename: str,
        storage_key: str,
        content_type: str,
        size_bytes: int,
    ) -> Document:
        document = Document(
            owner_id=owner_id,
            original_filename=original_filename,
            storage_key=storage_key,
            content_type=content_type,
            size_bytes=size_bytes,
        )
        self.db.add(document)
        self.db.commit()
        self.db.refresh(document)
        return document

    def list_for_owner(
        self, owner_id: str, *, skip: int = 0, limit: int = 20
    ) -> list[Document]:
        statement = (
            select(Document)
            .where(Document.owner_id == owner_id)
            .order_by(Document.created_at.desc())
            .offset(skip)
            .limit(limit)
        )
        return list(self.db.scalars(statement).all())

    def count_for_owner(self, owner_id: str) -> int:
        from sqlalchemy import func

        statement = select(func.count()).select_from(Document).where(
            Document.owner_id == owner_id
        )
        return self.db.scalar(statement) or 0

    def get_for_owner(self, document_id: str, owner_id: str) -> Document | None:
        statement = select(Document).where(
            Document.id == document_id,
            Document.owner_id == owner_id,
        )
        return self.db.scalar(statement)

    def update_processing(self, document: Document, processing_status: str) -> Document:
        document.processing_status = processing_status
        self.db.add(document)
        self.db.commit()
        self.db.refresh(document)
        return document

    def update_summary(self, document: Document, summary_text: str, processing_status: str) -> Document:
        document.summary_text = summary_text
        document.processing_status = processing_status
        self.db.add(document)
        self.db.commit()
        self.db.refresh(document)
        return document

    def delete(self, document: Document, *, auto_commit: bool = True) -> None:
        self.db.delete(document)
        if auto_commit:
            self.db.commit()
