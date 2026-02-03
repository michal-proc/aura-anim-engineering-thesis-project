import pytest

from backend.video.utilities.video_spec_converter import VideoSpecConverter  # noqa: F401
from backend.video.schemas import VideoGenerationRequest
from backend.video.constants import (
    AspectRatio,
    ResolutionClass,
    VideoFPS,
    VideoFormat,
    BaseGenerationModel,
    MotionAdapter,
)

def test_convert_to_spec_uses_defaults(monkeypatch):
    converter = VideoSpecConverter()

    aspect_ratio = next(iter(AspectRatio))

    def fake_dimensions(ar, resolution):
        assert ar == aspect_ratio
        assert resolution == ResolutionClass.LOW_512P
        return 640, 360

    monkeypatch.setattr(
        "backend.video.utilities.video_spec_converter.get_dimensions",
        fake_dimensions,
    )
    monkeypatch.setattr(
        "backend.video.utilities.video_spec_converter.random.randint",
        lambda a, b: 1234,
    )

    request = VideoGenerationRequest(
        prompt="A prompt",
        negative_prompt="A negative prompt",
        aspect_ratio=aspect_ratio,
        resolution=ResolutionClass.LOW_512P,
        video_length=4,
        fps=VideoFPS.BASE,
        output_format=VideoFormat.MP4,
        base_model=BaseGenerationModel.SD15,
        motion_adapter=MotionAdapter.DEFAULT,
        inference_steps=30,
    )

    spec = converter.convert_to_spec(request)

    assert spec.width == 640
    assert spec.height == 360
    assert spec.seed == 1234
    assert spec.base_model == request.base_model
    assert spec.motion_adapter == request.motion_adapter
    assert spec.output_format == request.output_format
    assert spec.guidance_scale == converter._MODEL_DEFAULTS[request.base_model]["guidance_scale"]


@pytest.mark.parametrize(
    ("base_model", "expected_guidance"),
    [
        (BaseGenerationModel.SD15, 7.5),
        (BaseGenerationModel.DREAMSHAPER, 7.5),
        (BaseGenerationModel.REV_ANIMATED, 7.5),
    ],
)
def test_convert_to_spec_applies_model_guidance(monkeypatch, base_model, expected_guidance):
    converter = VideoSpecConverter()

    monkeypatch.setattr(
        "backend.video.utilities.video_spec_converter.get_dimensions",
        lambda ar, resolution: (512, 288),
    )
    monkeypatch.setattr(
        "backend.video.utilities.video_spec_converter.random.randint",
        lambda a, b: 999_999,
    )

    request = VideoGenerationRequest(
        prompt="Guidance check",
        negative_prompt=None,
        aspect_ratio=AspectRatio.LANDSCAPE_16_9,
        resolution=ResolutionClass.LOW_512P,
        video_length=6,
        fps=VideoFPS.ANIMATION,
        output_format=VideoFormat.WEBM,
        base_model=base_model,
        motion_adapter=MotionAdapter.DEFAULT,
        inference_steps=42,
    )

    spec = converter.convert_to_spec(request)

    assert spec.guidance_scale == expected_guidance
    assert spec.inference_steps == 42
    assert spec.seed == 999_999 % converter._MAX_SEED_VALUE


def test_convert_to_spec_sets_optional_fields(monkeypatch):
    converter = VideoSpecConverter()

    monkeypatch.setattr(
        "backend.video.utilities.video_spec_converter.get_dimensions",
        lambda ar, resolution: (640, 360),
    )
    monkeypatch.setattr(
        "backend.video.utilities.video_spec_converter.random.randint",
        lambda a, b: 123,
    )

    request = VideoGenerationRequest(
        prompt="Optional fields",
        negative_prompt=None,
        aspect_ratio=AspectRatio.LANDSCAPE_16_9,
        resolution=ResolutionClass.LOW_512P,
        video_length=3,
        fps=VideoFPS.BASE,
        output_format=VideoFormat.MP4,
        base_model=BaseGenerationModel.SD21,
        motion_adapter=MotionAdapter.DEFAULT,
    )

    spec = converter.convert_to_spec(request)

    assert spec.width == 640
    assert spec.height == 360
    assert spec.loras is None
    assert spec.additional_params is None