import pytest
from pydantic import ValidationError

from backend.video.schemas import VideoGenerationRequest
from backend.video.constants import (
    AspectRatio,
    ResolutionClass,
    VideoFPS,
    VideoFormat,
    BaseGenerationModel,
    MotionAdapter,
)

def test_video_generation_request_accepts_list_aspect_ratio():
    target_ratio = next(iter(AspectRatio))

    request = VideoGenerationRequest(
        prompt="Prompt",
        negative_prompt="None",
        aspect_ratio=list(target_ratio.value),  # type: ignore[arg-type]
        resolution=ResolutionClass.LOW_512P,
        video_length=4,
        fps=VideoFPS.BASE,
        output_format=VideoFormat.MP4,
        base_model=BaseGenerationModel.SD15,
        motion_adapter=MotionAdapter.DEFAULT,
        inference_steps=30,
    )

    assert request.aspect_ratio is target_ratio


def test_video_generation_request_uses_default_inference_steps():
    target_ratio = next(iter(AspectRatio))

    request = VideoGenerationRequest(
        prompt="Prompt",
        negative_prompt="None",
        aspect_ratio=target_ratio,
        resolution=ResolutionClass.LOW_512P,
        video_length=4,
        fps=VideoFPS.BASE,
        output_format=VideoFormat.MP4,
        base_model=BaseGenerationModel.SD15,
        motion_adapter=MotionAdapter.DEFAULT,
    )

    assert request.inference_steps == 25


def test_video_generation_request_rejects_invalid_inference_steps():
    target_ratio = next(iter(AspectRatio))

    with pytest.raises(ValidationError):
        VideoGenerationRequest(
            prompt="Prompt",
            negative_prompt="None",
            aspect_ratio=target_ratio,
            resolution=ResolutionClass.LOW_512P,
            video_length=4,
            fps=VideoFPS.BASE,
            output_format=VideoFormat.MP4,
            base_model=BaseGenerationModel.SD15,
            motion_adapter=MotionAdapter.DEFAULT,
            inference_steps=0,
        )
