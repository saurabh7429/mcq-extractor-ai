"""
Storage Service - handles file storage operations.
"""
import logging
from pathlib import Path
from typing import List
from werkzeug.datastructures import FileStorage

# Create logger
logger = logging.getLogger(__name__)


class StorageService:
    """Handles file storage operations for uploads and downloads."""
    
    def __init__(self):
        """Initialize storage service."""
        from backend.config import Config
        self.upload_folder = Config.UPLOAD_FOLDER
        self.json_folder = Config.JSON_OUTPUT_FOLDER
        logger.info("Storage Service initialized")
    
    def save_upload(self, file: FileStorage, filename: str) -> Path:
        """
        Save an uploaded file.
        
        Args:
            file: Uploaded file object
            filename: Target filename
        
        Returns:
            Path to saved file
        """
        try:
            # Ensure directory exists
            self.upload_folder.mkdir(parents=True, exist_ok=True)
            
            # Save file
            file_path = self.upload_folder / filename
            file.save(str(file_path))
            
            logger.info(f"File saved: {file_path}")
            return file_path
            
        except Exception as e:
            logger.error(f"Error saving file: {e}")
            raise
    
    def save_json(self, content: str, filename: str) -> Path:
        """
        Save JSON content to file.
        
        Args:
            content: JSON content as string
            filename: Target filename
        
        Returns:
            Path to saved file
        """
        try:
            # Ensure directory exists
            self.json_folder.mkdir(parents=True, exist_ok=True)
            
            # Save file
            file_path = self.json_folder / filename
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            
            logger.info(f"JSON saved: {file_path}")
            return file_path
            
        except Exception as e:
            logger.error(f"Error saving JSON: {e}")
            raise
    
    def save_json_by_uuid(self, content: str, file_id: str) -> Path:
        """
        Save JSON content using UUID as filename.
        
        Args:
            content: JSON content as string
            file_id: UUID for the file (without extension)
        
        Returns:
            Path to saved file
        """
        try:
            # Ensure directory exists
            self.json_folder.mkdir(parents=True, exist_ok=True)
            
            # Create filename with .json extension
            filename = f"{file_id}.json"
            file_path = self.json_folder / filename
            
            # Save file
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            
            logger.info(f"JSON saved with UUID: {file_path}")
            return file_path
            
        except Exception as e:
            logger.error(f"Error saving JSON: {e}")
            raise
    
    def get_json_by_uuid(self, file_id: str) -> Path:
        """
        Get path to JSON file by UUID.
        
        Args:
            file_id: UUID for the file (without extension)
        
        Returns:
            Path to JSON file or None if not found
        """
        filename = f"{file_id}.json"
        file_path = self.json_folder / filename
        
        if file_path.exists():
            return file_path
        return None
    
    def get_pdf_path(self, filename: str) -> Path:
        """Get path to PDF file."""
        return self.upload_folder / filename
    
    def get_json_path(self, filename: str) -> Path:
        """Get path to JSON file."""
        return self.json_folder / filename
    
    def list_pdf_files(self) -> List[str]:
        """List all PDF files in upload folder."""
        try:
            if not self.upload_folder.exists():
                return []
            return [f.name for f in self.upload_folder.iterdir() if f.suffix.lower() == '.pdf']
        except Exception as e:
            logger.error(f"Error listing PDF files: {e}")
            return []
    
    def list_json_files(self) -> List[str]:
        """List all JSON files in output folder."""
        try:
            if not self.json_folder.exists():
                return []
            return [f.name for f in self.json_folder.iterdir() if f.suffix.lower() == '.json']
        except Exception as e:
            logger.error(f"Error listing JSON files: {e}")
            return []
    
    def delete_file(self, file_path: Path) -> bool:
        """
        Delete a file.
        
        Args:
            file_path: Path to file to delete
        
        Returns:
            True if successful
        """
        try:
            if file_path.exists():
                file_path.unlink()
                logger.info(f"File deleted: {file_path}")
                return True
            return False
        except Exception as e:
            logger.error(f"Error deleting file: {e}")
            return False
