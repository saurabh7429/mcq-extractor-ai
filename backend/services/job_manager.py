"""
Job Manager Service - handles background job tracking with file-based storage.
"""
import json
import logging
import os
import threading
import uuid
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, Optional, List
from backend.config import Config

# Create logger
logger = logging.getLogger(__name__)

# Job status constants
JOB_STATUS_PENDING = 'pending'
JOB_STATUS_PROCESSING = 'processing'
JOB_STATUS_COMPLETED = 'completed'
JOB_STATUS_FAILED = 'failed'

# Job stages
STAGE_READING_PDF = 'reading_pdf'
STAGE_EXTRACTING_TEXT = 'extracting_text'
STAGE_AI_PROCESSING = 'ai_processing'
STAGE_FORMATTING = 'formatting'
STAGE_SAVING = 'saving'
STAGE_COMPLETED = 'completed'


class JobManager:
    """
    Manages background jobs with file-based storage.
    Each job is stored as a JSON file to survive server restarts.
    """
    
    _instance = None
    _lock = threading.Lock()
    
    def __new__(cls):
        """Singleton pattern for thread safety."""
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
                    cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        """Initialize the job manager."""
        if self._initialized:
            return
        
        from backend.config import Config
        self.jobs_folder = Config.BASE_DIR / 'storage' / 'jobs'
        self.jobs_folder.mkdir(parents=True, exist_ok=True)
        self._jobs_lock = threading.Lock()
        
        # Cleanup old job files on startup
        self._cleanup_old_jobs()
        
        logger.info(f"JobManager initialized. Jobs folder: {self.jobs_folder}")
        self._initialized = True
    
    def _get_job_file_path(self, job_id: str) -> Path:
        """Get the file path for a job."""
        return self.jobs_folder / f'{job_id}.json'
    
    def _cleanup_old_jobs(self, max_age_hours: int = 24):
        """Remove old job files to save storage space."""
        try:
            if not self.jobs_folder.exists():
                return
            
            now = datetime.now()
            removed_count = 0
            
            for job_file in self.jobs_folder.glob('*.json'):
                try:
                    # Get file modification time
                    mtime = datetime.fromtimestamp(job_file.stat().st_mtime)
                    age_hours = (now - mtime).total_seconds() / 3600
                    
                    if age_hours > max_age_hours:
                        job_file.unlink()
                        removed_count += 1
                except Exception as e:
                    logger.warning(f"Could not remove old job file {job_file}: {e}")
            
            if removed_count > 0:
                logger.info(f"Cleaned up {removed_count} old job files")
                
        except Exception as e:
            logger.warning(f"Error during job cleanup: {e}")
    
    def _read_job_file(self, job_id: str) -> Optional[Dict[str, Any]]:
        """Read job data from JSON file."""
        job_file = self._get_job_file_path(job_id)
        
        if not job_file.exists():
            return None
        
        try:
            with open(job_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"Error reading job file {job_id}: {e}")
            return None
    
    def _write_job_file(self, job_id: str, job_data: Dict[str, Any]) -> bool:
        """Write job data to JSON file."""
        job_file = self._get_job_file_path(job_id)
        
        try:
            with open(job_file, 'w', encoding='utf-8') as f:
                json.dump(job_data, f, indent=2, ensure_ascii=False)
            return True
        except Exception as e:
            logger.error(f"Error writing job file {job_id}: {e}")
            return False
    
    def create_job(self, file_id: str, metadata: Optional[Dict[str, Any]] = None) -> str:
        """
        Create a new job and return job_id.
        
        Args:
            file_id: The file_id being processed
            metadata: Optional additional metadata
            
        Returns:
            job_id: Unique job identifier
        """
        job_id = str(uuid.uuid4())[:12]  # Short UUID for readability
        
        job_data = {
            'job_id': job_id,
            'file_id': file_id,
            'status': JOB_STATUS_PENDING,
            'stage': STAGE_READING_PDF,
            'progress': 0,
            'message': 'Job created, waiting to start...',
            'created_at': datetime.now().isoformat(),
            'updated_at': datetime.now().isoformat(),
            'total_pages': 0,
            'pages_processed': 0,
            'mcqs_found': 0,
            'error': None,
            'result': None,
            'metadata': metadata or {}
        }
        
        with self._jobs_lock:
            self._write_job_file(job_id, job_data)
        
        logger.info(f"Created job {job_id} for file {file_id}")
        return job_id
    
    def get_job(self, job_id: str) -> Optional[Dict[str, Any]]:
        """
        Get job status by job_id.
        
        Args:
            job_id: The job identifier
            
        Returns:
            Job data dict or None if not found
        """
        with self._jobs_lock:
            return self._read_job_file(job_id)
    
    def update_job(self, job_id: str, **kwargs) -> bool:
        """
        Update job with new data.
        
        Args:
            job_id: The job identifier
            **kwargs: Fields to update
            
        Returns:
            True if successful
        """
        with self._jobs_lock:
            job_data = self._read_job_file(job_id)
            
            if not job_data:
                logger.warning(f"Job not found: {job_id}")
                return False
            
            # Update fields
            for key, value in kwargs.items():
                if key not in ['job_id', 'created_at']:  # Don't allow changing these
                    job_data[key] = value
            
            job_data['updated_at'] = datetime.now().isoformat()
            
            return self._write_job_file(job_id, job_data)
    
    def set_stage(self, job_id: str, stage: str, progress: int, message: str = None) -> bool:
        """
        Update job stage and progress.
        
        Args:
            job_id: The job identifier
            stage: Current stage
            progress: Progress percentage (0-100)
            message: Optional status message
            
        Returns:
            True if successful
        """
        kwargs = {
            'stage': stage,
            'progress': min(100, max(0, progress))
        }
        
        if message:
            kwargs['message'] = message
        
        return self.update_job(job_id, **kwargs)
    
    def set_processing(self, job_id: str) -> bool:
        """Mark job as processing."""
        return self.update_job(
            job_id,
            status=JOB_STATUS_PROCESSING,
            stage=STAGE_READING_PDF,
            progress=5,
            message='Reading PDF file...'
        )
    
    def set_progress(self, job_id: str, stage: str, progress: int, message: str, 
                     pages_processed: int = None, total_pages: int = None, 
                     mcqs_found: int = None) -> bool:
        """
        Set detailed progress information.
        
        Args:
            job_id: The job identifier
            stage: Current stage name
            progress: Progress percentage (0-100)
            message: Status message
            pages_processed: Number of pages processed
            total_pages: Total pages in PDF
            mcqs_found: Number of MCQs found so far
            
        Returns:
            True if successful
        """
        kwargs = {
            'stage': stage,
            'progress': min(100, max(0, progress)),
            'message': message
        }
        
        if pages_processed is not None:
            kwargs['pages_processed'] = pages_processed
        if total_pages is not None:
            kwargs['total_pages'] = total_pages
        if mcqs_found is not None:
            kwargs['mcqs_found'] = mcqs_found
        
        return self.update_job(job_id, **kwargs)
    
    def set_completed(self, job_id: str, result: Dict[str, Any]) -> bool:
        """
        Mark job as completed with result.
        
        Args:
            job_id: The job identifier
            result: The final result data
            
        Returns:
            True if successful
        """
        return self.update_job(
            job_id,
            status=JOB_STATUS_COMPLETED,
            stage=STAGE_COMPLETED,
            progress=100,
            message='Extraction completed successfully!',
            result=result
        )
    
    def set_failed(self, job_id: str, error: str) -> bool:
        """
        Mark job as failed with error message.
        
        Args:
            job_id: The job identifier
            error: Error message
            
        Returns:
            True if successful
        """
        return self.update_job(
            job_id,
            status=JOB_STATUS_FAILED,
            progress=0,
            message='Job failed',
            error=error
        )
    
    def delete_job(self, job_id: str) -> bool:
        """
        Delete a job file.
        
        Args:
            job_id: The job identifier
            
        Returns:
            True if successful
        """
        with self._jobs_lock:
            job_file = self._get_job_file_path(job_id)
            
            if job_file.exists():
                try:
                    job_file.unlink()
                    logger.info(f"Deleted job file: {job_id}")
                    return True
                except Exception as e:
                    logger.error(f"Error deleting job file {job_id}: {e}")
                    return False
            
            return False
    
    def list_jobs(self, limit: int = 50) -> List[Dict[str, Any]]:
        """
        List recent jobs.
        
        Args:
            limit: Maximum number of jobs to return
            
        Returns:
            List of job data dicts
        """
        jobs = []
        
        try:
            job_files = sorted(
                self.jobs_folder.glob('*.json'),
                key=lambda f: f.stat().st_mtime,
                reverse=True
            )[:limit]
            
            for job_file in job_files:
                job_data = self._read_job_file(job_file.stem)
                if job_data:
                    jobs.append(job_data)
                    
        except Exception as e:
            logger.error(f"Error listing jobs: {e}")
        
        return jobs


# Global instance
_job_manager = None

def get_job_manager() -> JobManager:
    """Get the global JobManager instance."""
    global _job_manager
    if _job_manager is None:
        _job_manager = JobManager()
    return _job_manager

