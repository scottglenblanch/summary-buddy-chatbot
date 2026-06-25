"""
Storage service for handling PDF and extracted text storage.

Uses S3-compatible object storage (Amazon S3 in AWS, a MinIO container locally).
"""

import os
from typing import Optional, List
import logging

import boto3

logger = logging.getLogger(__name__)


class StorageService:
    """Handle file storage operations against S3-compatible object storage."""

    def __init__(self):
        """Initialize the S3-compatible storage client."""
        # S3 key prefixes
        self.uploads_prefix = "uploads/"
        self.texts_prefix = "summary_buddy_texts/"

        endpoint_url = os.environ.get("AWS_S3_ENDPOINT_URL") or None
        self.s3_client = boto3.client(
            "s3",
            region_name=os.environ.get("AWS_REGION", "us-east-1"),
            endpoint_url=endpoint_url,
        )
        self.bucket = os.environ.get("AWS_S3_BUCKET")
        self._ensure_bucket()
        logger.info(
            f"Initialized S3 storage (bucket: {self.bucket}, "
            f"endpoint: {endpoint_url or 'aws'})"
        )

    def _ensure_bucket(self) -> None:
        """Create the configured S3 bucket if it does not already exist.

        Useful for local MinIO where the bucket may not be pre-created.
        """
        try:
            self.s3_client.head_bucket(Bucket=self.bucket)
        except Exception:
            try:
                self.s3_client.create_bucket(Bucket=self.bucket)
                logger.info(f"Created storage bucket: {self.bucket}")
            except Exception as e:
                logger.warning(f"Could not ensure bucket '{self.bucket}' exists: {e}")

    def save_upload(self, filename: str, data: bytes) -> Optional[str]:
        """
        Persist an original uploaded file (PDF or TXT) to storage.

        Args:
            filename: Name to store the file under.
            data: Raw file bytes.

        Returns:
            The storage location (S3 URI or local path), or None on failure.
        """
        try:
            key = f"{self.uploads_prefix}{filename}"
            self.s3_client.put_object(Bucket=self.bucket, Key=key, Body=data)
            return f"s3://{self.bucket}/{key}"
        except Exception as e:
            logger.error(f"Failed to save upload {filename}: {e}")
            return None

    def read_upload_bytes(self, filename: str) -> Optional[bytes]:
        """Read an original uploaded file's bytes from storage."""
        try:
            response = self.s3_client.get_object(
                Bucket=self.bucket, Key=f"{self.uploads_prefix}{filename}"
            )
            return response["Body"].read()
        except Exception as e:
            logger.error(f"Failed to read upload {filename}: {e}")
            return None

    def list_uploads(self) -> List[str]:
        """List original uploaded files."""
        try:
            response = self.s3_client.list_objects_v2(
                Bucket=self.bucket, Prefix=self.uploads_prefix
            )
            return [
                obj["Key"].replace(self.uploads_prefix, "")
                for obj in response.get("Contents", [])
                if obj["Key"] != self.uploads_prefix
            ]
        except Exception as e:
            logger.error(f"Failed to list uploads: {e}")
            return []
    
    def save_text_file(self, filename: str, content: str) -> bool:
        """
        Save extracted text file
        
        Args:
            filename: Name of the file
            content: Content to save
        
        Returns:
            True if successful, False otherwise
        """
        try:
            self.s3_client.put_object(
                Bucket=self.bucket,
                Key=f"{self.texts_prefix}{filename}",
                Body=content.encode("utf-8"),
                ContentType="text/plain"
            )
            return True
        except Exception as e:
            logger.error(f"Failed to save text file {filename}: {e}")
            return False
    
    def read_text_file(self, filename: str) -> Optional[str]:
        """
        Read extracted text file
        
        Args:
            filename: Name of the file
        
        Returns:
            File content or None if not found
        """
        try:
            response = self.s3_client.get_object(
                Bucket=self.bucket,
                Key=f"{self.texts_prefix}{filename}"
            )
            return response["Body"].read().decode("utf-8")
        except Exception as e:
            logger.error(f"Failed to read text file {filename}: {e}")
            return None
    
    def list_text_files(self) -> List[str]:
        """
        List all extracted text files
        
        Returns:
            List of filenames
        """
        try:
            response = self.s3_client.list_objects_v2(
                Bucket=self.bucket,
                Prefix=self.texts_prefix
            )
            if "Contents" in response:
                return [obj["Key"].replace(self.texts_prefix, "") for obj in response["Contents"]]
            return []
        except Exception as e:
            logger.error(f"Failed to list text files: {e}")
            return []
    
    def delete_text_file(self, filename: str) -> bool:
        """Delete a text file"""
        try:
            self.s3_client.delete_object(
                Bucket=self.bucket,
                Key=f"{self.texts_prefix}{filename}"
            )
            return True
        except Exception as e:
            logger.error(f"Failed to delete text file {filename}: {e}")
            return False
    
    def clear_text_files(self) -> bool:
        """Clear all text files"""
        try:
            response = self.s3_client.list_objects_v2(
                Bucket=self.bucket,
                Prefix=self.texts_prefix
            )
            if "Contents" in response:
                for obj in response["Contents"]:
                    self.s3_client.delete_object(
                        Bucket=self.bucket,
                        Key=obj["Key"]
                    )
            return True
        except Exception as e:
            logger.error(f"Failed to clear text files: {e}")
            return False
