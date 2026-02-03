import logging
import asyncio
from asyncio import sleep
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, status, WebSocket, WebSocketDisconnect
from fastapi.responses import StreamingResponse

from backend.video.factories.services.factories import create_video_explore_service
from backend.video.schemas.api_schemas import (
    VideoGenerationRequest, VideoGenerationResponse,
    JobStatusResponse, JobCancellationResponse,
    VideoDownloadResponse, VideoMetadata,
    WebSocketJobUpdate, WebSocketErrorMessage,
    VideoListResponse, JobListResponse,
    VideoDetailResponse, VideoDeletionResponse, VideoUpdateRequest, GetVideoExploreResponse,
)
from backend.video.schemas.domain_schemas import (
    VideoDownloadInfo,
)
from backend.auth.dependencies.dependencies import CurrentUser
from backend.accounts.models import User

from backend.video.constants import JobStatus
from backend.video.factories.services import (
    create_video_generation_service,
    create_video_job_service,
    create_video_download_service,
)
from backend.video.factories.utilities import (
    create_video_spec_converter
)
from backend.storage.factories.factories import create_video_storage_service
from backend.video.factories.repositories import create_video_download_repository


logger = logging.getLogger(__name__)

router = APIRouter(prefix="/videos", tags=["Videos"])


@router.get("/jobs", response_model=JobListResponse)
async def get_jobs(
    current_user: CurrentUser,
):
    """
    Get list of unread jobs for the authenticated user.

    Returns only jobs with marked_as_read=false, ordered by creation date (newest first).
    Includes metadata with job statistics.
    Requires authentication.
    """
    video_job_service = create_video_job_service()

    try:
        job_details, meta = video_job_service.get_unread_jobs(current_user.id)

        return JobListResponse(
            success=True,
            data=job_details,
            meta=meta,
        )
    except Exception as e:
        logger.error(f"Failed to retrieve job list for user {current_user.id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve job list."
        )


@router.get("", response_model=VideoListResponse)
async def get_videos(
    current_user: CurrentUser,
):
    """
    Get list of all videos for the authenticated user.

    Returns videos ordered by creation date (newest first).
    Requires authentication.
    """
    video_job_service = create_video_job_service()

    try:
        video_list = video_job_service.get_all_videos(current_user.id)

        return VideoListResponse(
            success=True,
            data=video_list,
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve video list."
        )


@router.get("/explore", response_model=GetVideoExploreResponse)
async def get_videos_explore():
    service = create_video_explore_service()

    try:
        videos = service.get_explore_videos()

        return GetVideoExploreResponse(
            success=True,
            data=videos,
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve exploration video list."
        )


@router.get("/{video_id}", response_model=VideoDetailResponse)
async def get_video(
    video_id: str,
    current_user: CurrentUser,
):
    """
    Get detailed information about a specific video.

    Returns video details if it exists and belongs to the authenticated user.
    """
    video_job_service = create_video_job_service()

    try:
        video = video_job_service.get_video_detail(video_id, current_user.id)

        if not video:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Video {video_id} not found."
            )

        return VideoDetailResponse(
            success=True,
            data=video,
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to retrieve video {video_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve video."
        )


@router.get("/shared/{video_id}", response_model=VideoDetailResponse)
async def get_shared_video(
    video_id: str
):
    """
    Get detailed information about a specific video.

    Returns video details if it exists and belongs to the authenticated user.
    """
    video_job_service = create_video_job_service()

    try:
        video = video_job_service.get_shared_video_detail(video_id)

        if not video:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Video {video_id} not found."
            )

        return VideoDetailResponse(
            success=True,
            data=video,
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to retrieve video {video_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve video."
        )


@router.put("/{job_id}", response_model=VideoDetailResponse)
async def update_video(
    job_id: str,
    request: VideoUpdateRequest,
    current_user: CurrentUser,
):
    """
    Update video metadata.

    Allows updating `name` and `shared` flag for a given video.
    Both fields are nullable – if a field is null/omitted, it is not modified.
    """
    video_job_service = create_video_job_service()

    try:
        updated_video = video_job_service.update_video(
            job_id=job_id,
            user_id=current_user.id,
            name=request.name,
            shared=request.shared,
        )

        if not updated_video:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Video {job_id} not found.",
            )

        return VideoDetailResponse(
            success=True,
            data=updated_video,
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to update video {job_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update video."
        )


@router.delete("/{video_id}", response_model=VideoDeletionResponse)
async def delete_video(
    video_id: str,
    current_user: CurrentUser,
):
    """
    Delete a video.

    Deletes the video if it exists and belongs to the authenticated user.
    """
    video_job_service = create_video_job_service()

    try:
        success = video_job_service.delete_video(video_id, current_user.id)

        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Video {video_id} not found."
            )

        return VideoDeletionResponse(
            success=True,
            video_id=video_id,
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to delete video {video_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete video."
        )


@router.get("/{video_id}/file")
async def stream_video_file(
    video_id: str,
    current_user: CurrentUser,
):
    """
    Stream video file.

    Streams the video file if it exists and belongs to the authenticated user.
    """
    video_job_service = create_video_job_service()
    video_storage_service = create_video_storage_service()

    try:
        video = video_job_service.get_video_detail(video_id, current_user.id)
        if not video:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Video {video_id} not found."
            )

        if not video_job_service.is_job_completed(video_id):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Video generation is not completed yet."
            )

        with create_video_download_repository() as video_download_repository:
            video_info = video_download_repository.get_video_file_info(video_id)

            if not video_info:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Video file not found."
                )

            object_key = video_info["object_key"]
            file_format = video_info["format"]

        response = video_storage_service.stream_video(object_key)

        media_type_map = {
            "mp4": "video/mp4",
            "webm": "video/webm",
            "gif": "image/gif",
        }
        media_type = media_type_map.get(file_format.lower(), "application/octet-stream")

        return StreamingResponse(
            response.stream(amt=8192),
            media_type=media_type,
            headers={
                "Content-Disposition": f'inline; filename="{video_id}.{file_format}"'
            }
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to stream video {video_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to stream video."
        )


@router.post("/generate", response_model=VideoGenerationResponse)
async def generate_video(
    request: VideoGenerationRequest,
    current_user: CurrentUser,
):
    """
    Start a new video generation job.

    Creates a new video generation job with the provided parameters
    and returns the job ID for tracking progress.
    """
    video_generation_service = create_video_generation_service()
    video_job_service = create_video_job_service()
    video_spec_converter = create_video_spec_converter()

    user_id = current_user.id

    try:
        spec = video_spec_converter.convert_to_spec(request)
        job_id = video_job_service.create_job(spec, user_id)
        await video_generation_service.schedule_generation(job_id)

        return VideoGenerationResponse(
            job_id=job_id,
            status=JobStatus.PENDING,
        )

    except Exception as e:
        logger.error(f"Failed to create video generation job: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create video generation job."
        )

@router.get("/jobs/{job_id}", response_model=JobStatusResponse)
async def get_job_status(
    job_id: str,
):
    """
    Get the status of the given video generation job.
    """
    video_job_service = create_video_job_service()

    try:
        status_info = video_job_service.get_job_status(job_id)

        if status_info is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Job {job_id} not found.",
            )

        job_name, job_status, progress_percentage = status_info

        return JobStatusResponse(
            job_id=job_id,
            status=job_status,
            progress_percentage=progress_percentage,
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get job status for {job_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get job status."
        )


@router.post("/jobs/{job_id}/cancel", response_model=JobCancellationResponse)
async def cancel_job(
    job_id: str,
):
    """
    Cancel a pending or processing video generation job.
    
    Jobs that are already completed, failed, or cancelled cannot be cancelled.
    """
    video_job_service = create_video_job_service()

    try:
        success = video_job_service.cancel_job(job_id)

        return JobCancellationResponse(
            job_id=job_id,
            is_successful=success,
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to cancel job {job_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to cancel job."
        )


@router.get("/jobs/{job_id}/download", response_model=VideoDownloadResponse)
async def get_video_download(
    job_id: str,
):
    video_download_service = create_video_download_service()

    try:
        download_info = video_download_service.get_download_info(job_id)

        if download_info is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Video generation result not found."
            )

        return _construct_video_download_response(download_info)
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to retrieve download info for job {job_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve download info."
        )


@router.websocket("/jobs/{job_id}/ws")
async def websocket_job_status(
    websocket: WebSocket,
    job_id: str,
):
    """
    WebSocket endpoint for real-time job status updates.

    Sends periodic updates about job status and progress.
    """
    await websocket.accept()

    video_job_service = create_video_job_service()

    initial_status = video_job_service.get_job_status(job_id)
    if initial_status is None:
        error_message = WebSocketErrorMessage(
            job_id=job_id,
            error=f"Job {job_id} not found.",
        )
        await websocket.send_json(error_message.model_dump())
        await websocket.close()
        return

    try:
        last_status = None
        last_progress = None

        while True:

            status_info = video_job_service.get_job_status(job_id)

            if status_info is None:
                error_message = WebSocketErrorMessage(
                    job_id=job_id,
                    error="Job no longer exists"
                )
                await websocket.send_json(error_message.model_dump())
                break

            job_name, job_status, progress_percentage = status_info

            is_final = job_status in [JobStatus.COMPLETED, JobStatus.CANCELLED, JobStatus.FAILED]


            if job_status != last_status or progress_percentage != last_progress:
                update_message = WebSocketJobUpdate(
                    job_id=job_id,
                    name=job_name,
                    status=job_status,
                    progress_percentage=progress_percentage,
                    final=is_final,
                    timestamp=datetime.now(),
                )

                await websocket.send_json(update_message.model_dump(mode='json'))

                last_status = job_status
                last_progress = progress_percentage

            if is_final:
                break

            await asyncio.sleep(2)

    except WebSocketDisconnect:
        logger.info(f"Client disconnected from job {job_id} status updates")
    except Exception as e:
        logger.error(f"WebSocket error for job {job_id}: {e}")
        try:
            error_message=WebSocketErrorMessage(
                job_id=job_id,
                error="Internal server error",
            )
            await websocket.send_json(error_message.model_dump())
        except:
            # WebSocket connection might be closed, errors are ignored
            pass
    finally:
        try:
            await websocket.close()
        except:
            # Connection might already be closed
            pass

def _construct_video_download_response(download_info: VideoDownloadInfo) -> VideoDownloadResponse:
    video_file = download_info.video_file
    metadata = VideoMetadata(
        duration_seconds=video_file.duration_seconds,
        width=video_file.width,
        height=video_file.height,
        fps=video_file.fps,
        format=video_file.format,
        file_size_bytes=video_file.file_size_bytes,
    )

    return VideoDownloadResponse(
        job_id=download_info.job_id,
        download_url=download_info.download_url,
        expires_at=download_info.expires_at,
        video_metadata=metadata,
    )
