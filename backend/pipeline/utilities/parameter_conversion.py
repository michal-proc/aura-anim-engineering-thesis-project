from PIL import Image
from typing import List

from backend.pipeline.schemas import (
    VideoParameters,
    VideoGeneratorParams,
    VideoPreprocessorInput,
    VideoPreprocessorOutput,
    FrameInterpolatorInput,
    FrameUpscalerInput,
    VideoPostprocessorParams,
)


def to_preprocessor_input(params: VideoParameters) -> VideoPreprocessorInput:
    """
    Convert VideoParameters to VideoPreprocessorInput.

    Args:
        params: Main video generation parameters

    Returns:
        VideoPreprocessorInput with dimensions and FPS settings
    """
    return VideoPreprocessorInput(
        video_width=params.video_width,
        video_height=params.video_height,
        video_length=params.video_length,
        target_fps=params.fps,
    )


def to_generator_params(
    params: VideoParameters,
    preprocessor_output: VideoPreprocessorOutput
) -> VideoGeneratorParams:
    """
    Convert VideoParameters and preprocessor output to VideoGeneratorParams.

    Args:
        params: Main video generation parameters
        preprocessor_output: Output from preprocessor with adjusted dimensions

    Returns:
        VideoGeneratorParams for the video generator component
    """
    return VideoGeneratorParams(
        prompt=params.prompt,
        negative_prompt=params.negative_prompt,
        video_width=preprocessor_output.adjusted_width,
        video_height=preprocessor_output.adjusted_height,
        video_length=preprocessor_output.adjusted_length,
        fps=8,
        inference_steps=params.inference_steps,
        guidance_scale=params.guidance_scale,
        seed=params.seed,
        base_model=params.base_model,
        motion_adapter=params.motion_adapter,
        loras=params.loras or {}
    )


def to_interpolator_input(
    frames: List[Image.Image],
    fps_factor: int
) -> FrameInterpolatorInput:
    """
    Convert frames and fps_factor to FrameInterpolatorInput.

    Args:
        frames: List of frames to interpolate
        fps_factor: FPS multiplication factor

    Returns:
        FrameInterpolatorInput for the frame interpolator component
    """
    return FrameInterpolatorInput(
        frames=frames,
        fps_factor=fps_factor
    )


def to_upscaler_input(
    frames: List[Image.Image],
    scale_factor: int
) -> FrameUpscalerInput:
    """
    Convert frames and scale_factor to FrameUpscalerInput.

    Args:
        frames: List of frames to upscale
        scale_factor: Upscaling factor

    Returns:
        FrameUpscalerInput for the frame upscaler component
    """
    return FrameUpscalerInput(
        frames=frames,
        scale_factor=scale_factor
    )


def to_postprocessor_params(
    frames: List[Image.Image],
    params: VideoParameters,
    fps: int,
    output_dir: str = "outputs"
) -> VideoPostprocessorParams:
    """
    Convert frames and VideoParameters to VideoPostprocessorParams.

    Args:
        frames: List of frames to post-process
        params: Main video generation parameters
        fps: Final frames per second
        output_dir: Output directory path

    Returns:
        VideoPostprocessorParams for the video postprocessor component
    """
    return VideoPostprocessorParams(
        frames=frames,
        target_duration=params.video_length,
        fps=fps,
        target_width=params.video_width,
        target_height=params.video_height,
        prompt=params.prompt,
        seed=params.seed,
        video_length=params.video_length,
        output_format=params.output_format,
        output_dir=output_dir
    )