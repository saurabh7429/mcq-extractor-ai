"""
Status API route - handles job status checking.
"""
import logging
from flask import Blueprint, jsonify
from backend.utils.error_handler import NotFoundError, ValidationError

# Create logger
logger = logging.getLogger(__name__)

# Create blueprint
bp = Blueprint('status', __name__)


@bp.route('/<job_id>', methods=['GET'])
def get_job_status(job_id: str):
    """
    Get the status of a background job.
    
    Args:
        job_id: The job identifier
        
    Returns:
        JSON response with job status
    """
    logger.info(f"Checking status for job: {job_id}")
    
    # Validate job_id
    if not job_id or len(job_id) < 4:
        raise ValidationError("Invalid job ID")
    
    # Get job from JobManager
    from backend.services.job_manager import get_job_manager
    
    job_manager = get_job_manager()
    job = job_manager.get_job(job_id)
    
    if not job:
        logger.warning(f"Job not found: {job_id}")
        raise NotFoundError(f"Job not found: {job_id}")
    
    # Build response based on status
    response = {
        'job_id': job.get('job_id'),
        'status': job.get('status'),
        'stage': job.get('stage'),
        'progress': job.get('progress', 0),
        'message': job.get('message', ''),
        'created_at': job.get('created_at'),
        'updated_at': job.get('updated_at'),
    }
    
    # Add optional fields if available
    if job.get('total_pages'):
        response['total_pages'] = job['total_pages']
    if job.get('pages_processed'):
        response['pages_processed'] = job['pages_processed']
    if job.get('mcqs_found'):
        response['mcqs_found'] = job['mcqs_found']
    
    # Add result if completed
    if job.get('status') == 'completed' and job.get('result'):
        response['mcqs'] = job['result'].get('mcqs', [])
        response['count'] = job['result'].get('count', 0)
        response['file_id'] = job.get('file_id')
    
    # Add error if failed
    if job.get('status') == 'failed' and job.get('error'):
        response['error'] = job['error']
    
    logger.info(f"Job status: {job_id} - {job.get('status')} ({job.get('progress')}%)")
    
    return jsonify({
        'success': True,
        **response
    }), 200


@bp.route('/', methods=['GET'])
def list_jobs():
    """
    List recent jobs (for debugging/management).
    
    Returns:
        JSON response with list of recent jobs
    """
    from backend.services.job_manager import get_job_manager
    
    job_manager = get_job_manager()
    jobs = job_manager.list_jobs(limit=20)
    
    # Simplify job data for list view
    simplified_jobs = []
    for job in jobs:
        simplified_jobs.append({
            'job_id': job.get('job_id'),
            'file_id': job.get('file_id'),
            'status': job.get('status'),
            'stage': job.get('stage'),
            'progress': job.get('progress', 0),
            'created_at': job.get('created_at'),
            'updated_at': job.get('updated_at')
        })
    
    return jsonify({
        'success': True,
        'jobs': simplified_jobs,
        'count': len(simplified_jobs)
    }), 200

