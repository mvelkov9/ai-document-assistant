from sqlalchemy import delete as sa_delete
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.question_answer import QuestionAnswer


class QuestionAnswerRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def create(
        self,
        document_id: str,
        question_text: str,
        answer_text: str,
        source_mode: str,
    ) -> QuestionAnswer:
        record = QuestionAnswer(
            document_id=document_id,
            question_text=question_text,
            answer_text=answer_text,
            source_mode=source_mode,
        )
        self.db.add(record)
        self.db.commit()
        self.db.refresh(record)
        return record

    def list_for_document(self, document_id: str) -> list[QuestionAnswer]:
        statement = (
            select(QuestionAnswer)
            .where(QuestionAnswer.document_id == document_id)
            .order_by(QuestionAnswer.created_at.desc())
        )
        return list(self.db.scalars(statement).all())

    def get_by_id(self, answer_id: str) -> QuestionAnswer | None:
        return self.db.get(QuestionAnswer, answer_id)

    def delete_by_id(self, answer_id: str) -> bool:
        record = self.get_by_id(answer_id)
        if not record:
            return False
        self.db.delete(record)
        self.db.commit()
        return True

    def delete_for_document(self, document_id: str, *, auto_commit: bool = True) -> None:
        statement = sa_delete(QuestionAnswer).where(QuestionAnswer.document_id == document_id)
        self.db.execute(statement)
        if auto_commit:
            self.db.commit()
