import os
import logging
from minio import Minio
from minio.error import S3Error
from datetime import timedelta


logger = logging.getLogger(__name__)


class MinIOClient:
    def __init__(self, *, bucket_name: str):
        # Connection details
        self._internal_endpoint = os.getenv("MINIO_ENDPOINT", "localhost:9000")
        self._access_key = os.getenv("MINIO_ACCESS_KEY", "minio_admin")
        self._secret_key = os.getenv("MINIO_SECRET_KEY", "minio_pass123")
        self._use_ssl = os.getenv("MINIO_USE_SSL", "false").lower() == "true"
        self._public_endpoint = os.getenv("MINIO_PUBLIC_ENDPOINT", self._internal_endpoint)
        
        # Client configuration
        self.bucket_name = bucket_name

        self._client = Minio(
            self._internal_endpoint,
            access_key=self._access_key,
            secret_key=self._secret_key,
            secure=self._use_ssl,
        )

        self._ensure_bucket_exists()

    def _ensure_bucket_exists(self):
        """
        Create the video outputs bucket if it doesn't exist.
        """
        try:
            if not self._client.bucket_exists(self.bucket_name):
                self._client.make_bucket(self.bucket_name)
                logger.info(f"Created bucket: {self.bucket_name}")
        except S3Error as e:
            logger.error(f"Error creating bucket: {e}")

    def bucket_exists(self):
        """Check whether the owned bucket exists."""
        return self._client.bucket_exists(self.bucket_name)
    
    def upload_file(self, file_path: str, object_name: str | None = None) -> str:
        """
        Upload a file to MinIO and return the object URL.
        """
        if object_name is None:
            object_name = os.path.basename(file_path)
            
        try:
            self._client.fput_object(self.bucket_name, object_name, file_path)
            return f"http://{self._internal_endpoint}/{self.bucket_name}/{object_name}"
        except S3Error as e:
            logger.error(f"Error uploading file: {e}")
            raise

    def get_presigned_url(self, object_name: str, expires_hours: int) -> str:
        """
        Get a public URL for downloading a file.
        """
        protocol = "https" if self._use_ssl else "http"
        url = f"{protocol}://{self._public_endpoint}/{self.bucket_name}/{object_name}"

        logger.debug(f"Generated public URL for {object_name}: {url}")
        return url

    def list_objects(self, prefix: str = "") -> list[dict]:
        """
        List objects in the bucket.
        """
        try:
            objects = []
            for obj in self._client.list_objects(self.bucket_name, prefix=prefix):
                objects.append({
                    "name": obj.object_name,
                    "size": obj.size,
                    "last_modified": obj.last_modified.isoformat() if obj.last_modified else None
                })
            return objects
        except S3Error as e:
            logger.error(f"Error listing objects: {e}")
            raise
    
    def check_connection(self) -> bool:
        """
        Test if MinIO connection is working.
        """
        try:
            return self._client.bucket_exists(self.bucket_name)
        except Exception as e:
            logger.error(f"MinIO connection check failed: {e}")
            return False

    def get_object(self, object_name: str):
        """
        Get object from MinIO for streaming.

        Args:
            object_name: Object key in the bucket

        Returns:
            HTTPResponse object that can be streamed

        Raises:
            S3Error: If object retrieval fails
        """
        try:
            response = self._client.get_object(self.bucket_name, object_name)
            return response
        except S3Error as e:
            logger.error(f"Error getting object {object_name}: {e}")
            raise
