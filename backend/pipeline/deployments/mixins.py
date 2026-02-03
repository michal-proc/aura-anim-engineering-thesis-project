import ray
import logging
from abc import ABC

from backend.pipeline.deployments.exceptions import CancellationException


class CancellableDeploymentMixin(ABC):
    """
    Mixin class providing cancellation functionality for Ray Serve deployments.
    """
    
    def __init__(self):
        self.current_job_id: str | None = None
        self._replica_id = ray.get_runtime_context().get_actor_id()
        
    def _check_job_cancelled(self, job_id: str) -> bool:
        """
        Check if job is cancelled.
        
        Args:
            job_id: Job UUID
            
        Returns:
            True if job is cancelled, False otherwise
        """
        from backend.video.factories.services import create_video_job_service
        video_job_service = create_video_job_service()

        try:
            is_cancelled = video_job_service.is_job_cancelled(job_id)
            
            if is_cancelled:
                logging.info(f"Job {job_id} detected as cancelled on replica {self._replica_id}")
            
            return is_cancelled 
        except Exception as e:
            logging.warning(f"Error checking job cancellation status for {job_id} on replica {self._replica_id}: {e}")
            return False
    
    def _start_job_tracking(self, job_id: str, operation: str):
        """
        Start tracking a job on this replica.
        
        Args:
            job_id: Job UUID
            operation: Description of the operation being performed
        """
        self.current_job_id = job_id
        logging.info(f"Starting {operation} for job {job_id} on replica {self._replica_id}")
    
    def _finish_job_tracking(self, job_id: str, operation: str, success: bool = True):
        """
        Finish tracking a job on this replica.

        Args:
            job_id: Job UUID
            operation: Description of the operation that was performed
            success: Whether the operation completed successfully
        """
        if success:
            status = "completed"
            logging.info(f"{operation.capitalize()} {status} for job {job_id} on replica {self._replica_id}")
        self.current_job_id = None
    
    def _check_cancellation_and_raise(self, job_id: str, stage: str):
        """
        Check if job is cancelled and raise CancellationException if so.
        
        Args:
            job_id: Job UUID
            stage: Description of current processing stage
            
        Raises:
            CancellationException: If job is cancelled
        """
        if self._check_job_cancelled(job_id):
            raise CancellationException(f"Job {job_id} was cancelled {stage}")
    
    def get_current_job(self) -> str | None:
        """Get currently processing job ID"""
        return self.current_job_id
    
    def get_replica_id(self) -> str:
        """Get replica identifier"""
        return self._replica_id


class GPUDeploymentMixin(CancellableDeploymentMixin):
    """
    Mixin for deployments that use GPU resources.
    
    Extends CancellableDeploymentMixin with GPU-specific functionality.
    """
    
    def _handle_gpu_operation_with_cancellation(self, job_id: str, operation_name: str, operation_func, *args, **kwargs):
        """
        Execute a GPU operation with cancellation checks before and after.
        
        Args:
            job_id: Job identifier
            operation_name: Name of the operation for logging
            operation_func: Function to execute
            *args: Arguments for the operation function
            **kwargs: Keyword arguments for the operation function
            
        Returns:
            Result of the operation function
            
        Raises:
            CancellationException: If job is cancelled
        """
        self._start_job_tracking(job_id, operation_name)
        
        success = False
        try:
            # Check cancellation before expensive GPU operation
            self._check_cancellation_and_raise(job_id, f"before {operation_name}")

            # Execute the operation
            result = operation_func(*args, **kwargs)
            
            # Check cancellation after operation
            self._check_cancellation_and_raise(job_id, f"after {operation_name}")
            
            logging.info(f"{operation_name.capitalize()} completed for job {job_id} on replica {self._replica_id}")
            success = True
            return result
        
        except CancellationException:
            logging.info(f"{operation_name.capitalize()} cancelled for job {job_id} on replica {self._replica_id}")
            return None
        except Exception as e:
            logging.error(f"{operation_name.capitalize()} failed for job {job_id} on replica {self._replica_id}: {e}")
            raise
        finally:
            self._finish_job_tracking(job_id, operation_name, success=success)


class CPUDeploymentMixin(CancellableDeploymentMixin):
    """
    Mixin for deployments that use only CPU resources.
    
    Extends CancellableDeploymentMixin with CPU-specific functionality.
    """
    
    def _handle_cpu_operation_with_cancellation(self, job_id: str, operation_name: str, operation_func, *args, **kwargs):
        """
        Execute a CPU operation with cancellation checks.
        
        Args:
            job_id: Job identifier
            operation_name: Name of the operation for logging
            operation_func: Function to execute
            *args: Arguments for the operation function
            **kwargs: Keyword arguments for the operation function
            
        Returns:
            Result of the operation function
            
        Raises:
            CancellationException: If job is cancelled
        """
        self._start_job_tracking(job_id, operation_name)
        
        success = False
        try:
            # Check cancellation before operation
            self._check_cancellation_and_raise(job_id, f"before {operation_name}")
            
            # Execute the operation
            result = operation_func(*args, **kwargs)
            
            # Check cancellation after operation
            self._check_cancellation_and_raise(job_id, f"after {operation_name}")
            
            logging.info(f"{operation_name.capitalize()} completed for job {job_id} on replica {self._replica_id}")
            success = True
            return result
            
        except CancellationException:
            logging.info(f"{operation_name.capitalize()} cancelled for job {job_id} on replica {self._replica_id}")
            return None
        except Exception as e:
            logging.error(f"{operation_name.capitalize()} failed for job {job_id} on replica {self._replica_id}: {e}")
            raise
        finally:
            self._finish_job_tracking(job_id, operation_name, success=success)
