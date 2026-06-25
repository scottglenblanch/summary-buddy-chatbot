"""
Storage service for handling PDF and vector database storage
Supports both local (Docker volumes) and cloud (S3) storage
"""

import os
from pathlib import Path
from typing import Optional, List
import logging

logger = logging.getLogger(__name__)


class StorageService:
    """Handle file storage operations (local or S3)"""
    
    def __init__(self, use_s3: Optional[bool] = None):
        """
        Initialize storage service.

        The storage backend is selected as follows:
        - ``STORAGE_BACKEND=s3``  -> use S3-compatible storage (S3 in AWS, a
          separate MinIO container locally)
        - ``STORAGE_BACKEND=local`` -> use local filesystem / Docker volume
        - unset -> use S3 when an ``AWS_S3_BUCKET`` is configured, otherwise local

        Args:
            use_s3: Force the backend on/off, overriding the environment.
        """
        backend = os.environ.get("STORAGE_BACKEND", "").strip().lower()
        if use_s3 is None:
            if backend == "s3":
                use_s3 = True
            elif backend == "local":
                use_s3 = False
            else:
                use_s3 = bool(os.environ.get("AWS_S3_BUCKET"))

        self.use_s3 = bool(use_s3) and bool(os.environ.get("AWS_S3_BUCKET"))

        # S3 key prefixes
        self.uploads_prefix = "uploads/"
        self.texts_prefix = "summary_buddy_texts/"

        if self.use_s3:
            try:
                import boto3
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
            except ImportError:
                logger.warning("boto3 not available, falling back to local storage")
                self.use_s3 = False
            except Exception as e:
                logger.warning(f"Failed to initialize S3 storage, falling back to local: {e}")
                self.use_s3 = False
        
        # Local storage paths (also used as a fallback when S3 init fails)
        self.pdf_dir = Path(os.environ.get("PDF_DIR", "resources"))
        self.uploads_dir = Path(os.environ.get("UPLOADS_DIR", "resources/uploads"))
        self.texts_dir = Path(os.environ.get("EXTRACTED_TEXTS_DIR", "resources/summary_buddy_texts"))
        
        # Create local directories if they don't exist
        self.pdf_dir.mkdir(parents=True, exist_ok=True)
        self.uploads_dir.mkdir(parents=True, exist_ok=True)
        self.texts_dir.mkdir(parents=True, exist_ok=True)

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
            if self.use_s3:
                key = f"{self.uploads_prefix}{filename}"
                self.s3_client.put_object(Bucket=self.bucket, Key=key, Body=data)
                return f"s3://{self.bucket}/{key}"
            else:
                file_path = self.uploads_dir / filename
                file_path.write_bytes(data)
                return str(file_path)
        except Exception as e:
            logger.error(f"Failed to save upload {filename}: {e}")
            return None

    def read_upload_bytes(self, filename: str) -> Optional[bytes]:
        """Read an original uploaded file's bytes from storage."""
        try:
            if self.use_s3:
                response = self.s3_client.get_object(
                    Bucket=self.bucket, Key=f"{self.uploads_prefix}{filename}"
                )
                return response["Body"].read()
            else:
                file_path = self.uploads_dir / filename
                if file_path.exists():
                    return file_path.read_bytes()
                # Fall back to legacy resources directory
                legacy = self.pdf_dir / filename
                return legacy.read_bytes() if legacy.exists() else None
        except Exception as e:
            logger.error(f"Failed to read upload {filename}: {e}")
            return None

    def list_uploads(self) -> List[str]:
        """List original uploaded files."""
        try:
            if self.use_s3:
                response = self.s3_client.list_objects_v2(
                    Bucket=self.bucket, Prefix=self.uploads_prefix
                )
                return [
                    obj["Key"].replace(self.uploads_prefix, "")
                    for obj in response.get("Contents", [])
                    if obj["Key"] != self.uploads_prefix
                ]
            else:
                return [f.name for f in self.uploads_dir.glob("*") if f.is_file()]
        except Exception as e:
            logger.error(f"Failed to list uploads: {e}")
            return []
    
    def get_pdf_path(self, filename: str = "document.pdf") -> Optional[str]:
        """
        Get path to PDF file
        
        Args:
            filename: Name of the PDF file
        
        Returns:
            Path to PDF file or None if not found
        """
        if self.use_s3:
            key = f"{self.uploads_prefix}{filename}"
            try:
                self.s3_client.head_object(Bucket=self.bucket, Key=key)
                return f"s3://{self.bucket}/{key}"
            except Exception:
                return None
        else:
            for candidate in (self.uploads_dir / filename, self.pdf_dir / filename):
                if candidate.exists():
                    return str(candidate)
            return None
    
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
            if self.use_s3:
                self.s3_client.put_object(
                    Bucket=self.bucket,
                    Key=f"{self.texts_prefix}{filename}",
                    Body=content.encode("utf-8"),
                    ContentType="text/plain"
                )
            else:
                file_path = self.texts_dir / filename
                file_path.write_text(content, encoding="utf-8")
            
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
            if self.use_s3:
                response = self.s3_client.get_object(
                    Bucket=self.bucket,
                    Key=f"{self.texts_prefix}{filename}"
                )
                return response["Body"].read().decode("utf-8")
            else:
                file_path = self.texts_dir / filename
                if file_path.exists():
                    return file_path.read_text(encoding="utf-8")
                return None
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
            if self.use_s3:
                response = self.s3_client.list_objects_v2(
                    Bucket=self.bucket,
                    Prefix=self.texts_prefix
                )
                if "Contents" in response:
                    return [obj["Key"].replace(self.texts_prefix, "") for obj in response["Contents"]]
                return []
            else:
                return [f.name for f in self.texts_dir.glob("*.txt")]
        except Exception as e:
            logger.error(f"Failed to list text files: {e}")
            return []
    
    def delete_text_file(self, filename: str) -> bool:
        """Delete a text file"""
        try:
            if self.use_s3:
                self.s3_client.delete_object(
                    Bucket=self.bucket,
                    Key=f"{self.texts_prefix}{filename}"
                )
            else:
                file_path = self.texts_dir / filename
                if file_path.exists():
                    file_path.unlink()
            return True
        except Exception as e:
            logger.error(f"Failed to delete text file {filename}: {e}")
            return False
    
    def clear_text_files(self) -> bool:
        """Clear all text files"""
        try:
            if self.use_s3:
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
            else:
                for file_path in self.texts_dir.glob("*.txt"):
                    file_path.unlink()
            return True
        except Exception as e:
            logger.error(f"Failed to clear text files: {e}")
            return False
