"""Supabase storage operations for candidate evaluator."""

import os
import tempfile
from pathlib import Path
from typing import Optional, BinaryIO
from uuid import uuid4

from supabase import Client

from candidate_evaluator.database import get_supabase_client


BUCKET_NAME = "candidate-materials"


class Storage:
    """File storage operations using Supabase Storage."""
    
    def __init__(self, client: Optional[Client] = None):
        self.client = client or get_supabase_client()
        self.bucket = BUCKET_NAME
    
    def _get_user_path(self, user_id: str, filename: str) -> str:
        """Generate storage path for a user's file."""
        unique_id = uuid4().hex[:8]
        safe_filename = "".join(c for c in filename if c.isalnum() or c in "._-")
        return f"{user_id}/{unique_id}_{safe_filename}"
    
    def upload_file(
        self,
        user_id: str,
        file_data: bytes,
        filename: str,
        content_type: Optional[str] = None
    ) -> str:
        """
        Upload a file to Supabase Storage.
        
        Returns the storage path.
        """
        storage_path = self._get_user_path(user_id, filename)
        
        options = {}
        if content_type:
            options["content-type"] = content_type
        
        self.client.storage.from_(self.bucket).upload(
            path=storage_path,
            file=file_data,
            file_options=options
        )
        
        return storage_path
    
    def upload_file_object(
        self,
        user_id: str,
        file_obj: BinaryIO,
        filename: str,
        content_type: Optional[str] = None
    ) -> str:
        """
        Upload a file object to Supabase Storage.
        
        Returns the storage path.
        """
        file_data = file_obj.read()
        return self.upload_file(user_id, file_data, filename, content_type)
    
    def download_file(self, storage_path: str) -> bytes:
        """Download a file from Supabase Storage."""
        response = self.client.storage.from_(self.bucket).download(storage_path)
        return response
    
    def download_to_temp(self, storage_path: str) -> str:
        """
        Download a file to a temporary location.
        
        Returns the path to the temporary file.
        """
        file_data = self.download_file(storage_path)
        
        filename = storage_path.split("/")[-1]
        if "_" in filename:
            filename = "_".join(filename.split("_")[1:])
        
        suffix = Path(filename).suffix or ""
        
        with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
            tmp.write(file_data)
            return tmp.name
    
    def download_multiple_to_temp(self, storage_paths: list[str]) -> list[str]:
        """
        Download multiple files to temporary locations.
        
        Returns list of paths to temporary files.
        """
        temp_paths = []
        for path in storage_paths:
            try:
                temp_path = self.download_to_temp(path)
                temp_paths.append(temp_path)
            except Exception as e:
                print(f"Error downloading {path}: {e}")
        return temp_paths
    
    def delete_file(self, storage_path: str) -> bool:
        """Delete a file from Supabase Storage."""
        try:
            self.client.storage.from_(self.bucket).remove([storage_path])
            return True
        except Exception:
            return False
    
    def delete_user_files(self, user_id: str) -> int:
        """Delete all files for a user. Returns count of deleted files."""
        try:
            files = self.client.storage.from_(self.bucket).list(user_id)
            if not files:
                return 0
            
            paths = [f"{user_id}/{f['name']}" for f in files]
            self.client.storage.from_(self.bucket).remove(paths)
            return len(paths)
        except Exception:
            return 0
    
    def get_file_url(self, storage_path: str, expires_in: int = 3600) -> str:
        """Get a signed URL for a file (valid for expires_in seconds)."""
        response = self.client.storage.from_(self.bucket).create_signed_url(
            storage_path, expires_in
        )
        return response.get("signedURL", "")
    
    def list_user_files(self, user_id: str) -> list[dict]:
        """List all files for a user in storage."""
        try:
            files = self.client.storage.from_(self.bucket).list(user_id)
            return files or []
        except Exception:
            return []


def cleanup_temp_files(temp_paths: list[str]) -> None:
    """Clean up temporary files."""
    for path in temp_paths:
        try:
            os.unlink(path)
        except Exception:
            pass
