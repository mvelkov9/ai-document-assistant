from io import BytesIO

from minio import Minio
from minio.error import S3Error

from app.core.config import get_settings


class StorageService:
    def __init__(self) -> None:
        settings = get_settings()
        self.bucket_name = settings.minio_bucket
        self.client = Minio(
            endpoint=settings.minio_endpoint,
            access_key=settings.minio_access_key,
            secret_key=settings.minio_secret_key,
            secure=settings.minio_secure,
        )

    def upload_bytes(self, object_name: str, content: bytes, content_type: str) -> None:
        self._ensure_bucket()
        data_stream = BytesIO(content)
        self.client.put_object(
            bucket_name=self.bucket_name,
            object_name=object_name,
            data=data_stream,
            length=len(content),
            content_type=content_type,
        )

    def download_bytes(self, object_name: str) -> bytes:
        self._ensure_bucket()
        try:
            response = self.client.get_object(self.bucket_name, object_name)
            return response.read()
        except S3Error as exc:
            raise RuntimeError(f"Storage download failed: {exc}") from exc
        finally:
            try:
                response.close()
                response.release_conn()
            except UnboundLocalError:
                pass

    def delete_object(self, object_name: str) -> None:
        self._ensure_bucket()
        try:
            self.client.remove_object(self.bucket_name, object_name)
        except S3Error as exc:
            raise RuntimeError(f"Storage delete failed: {exc}") from exc

    def check_connection(self) -> bool:
        self._ensure_bucket()
        return True

    def _ensure_bucket(self) -> None:
        try:
            exists = self.client.bucket_exists(self.bucket_name)
            if not exists:
                self.client.make_bucket(self.bucket_name)
        except S3Error as exc:
            raise RuntimeError(f"Storage initialization failed: {exc}") from exc
