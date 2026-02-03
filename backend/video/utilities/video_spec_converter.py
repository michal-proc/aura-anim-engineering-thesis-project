"""Converts video API requests to domain specifications"""

import logging
import random
from typing import Any

from backend.video.schemas import VideoGenerationRequest
from backend.video.schemas import VideoGenerationSpec
from backend.video.utilities.resolutions import get_dimensions
from backend.video.constants import BaseGenerationModel


logger = logging.getLogger(__name__)


class VideoSpecConverter:
    """Converts user video generation requests to technical specifications
    for video generation."""

    _MODEL_DEFAULTS: dict[BaseGenerationModel, dict[str, Any]] = {
        BaseGenerationModel.SD15: {
            "inference_steps": 26,
            "guidance_scale": 7.5,
        },
        BaseGenerationModel.SD21: {
            "inference_steps": 26,
            "guidance_scale": 7.5,
        },
        BaseGenerationModel.EPICREALISM: {
            "inference_steps": 26,
            "guidance_scale": 7.5,
        },
        BaseGenerationModel.REALISTIC_VISION: {
            "inference_steps": 26,
            "guidance_scale": 7.5,
        },
        BaseGenerationModel.DREAMSHAPER: {
            "inference_steps": 26,
            "guidance_scale": 7.5,
        },
        BaseGenerationModel.JUGGERNAUT: {
            "inference_steps": 26,
            "guidance_scale": 7.5,
        },
        BaseGenerationModel.REV_ANIMATED: {
            "inference_steps": 26,
            "guidance_scale": 7.5,
        },
    }

    _MAX_SEED_VALUE = 1_000_000_000

    def convert_to_spec(self, request: VideoGenerationRequest) -> VideoGenerationSpec:
        logger.debug(f"Converting request for prompt: '{request.prompt[:50]}...'")

        width, height = get_dimensions(request.aspect_ratio, request.resolution)
        logger.debug(f"Resolved dimension: {width}x{height} from {request.aspect_ratio.ratio_string} at {request.resolution.name_string}")

        model_defaults = self._get_model_defaults(request.base_model)
        logger.debug(f"Using model defaults for {request.base_model.value}: {model_defaults}")

        seed = self._generate_seed()
        logger.debug(f"Generated seed: {seed}")

        spec = VideoGenerationSpec(
            # Text parameters
            prompt=request.prompt,
            negative_prompt=request.negative_prompt,

            # Resolved dimensions
            width=width,
            height=height,
            video_length=request.video_length,
            fps=request.fps,
            output_format=request.output_format,

            # Model configuration
            base_model=request.base_model,
            motion_adapter=request.motion_adapter,

            # Filled in parameters
            inference_steps=request.inference_steps,
            guidance_scale=model_defaults["guidance_scale"],
            seed=seed,

            # Optional parameters
            loras=None,
            additional_params=None,
        )

        return spec

    def _get_model_defaults(self, model: BaseGenerationModel) -> dict[str, Any]:
        """Get default parameters for a specific model"""
        unknown_model_defaults = {
            "inference_steps": 26,
            "guidance_scale": 5,
        }
        return self._MODEL_DEFAULTS.get(model, unknown_model_defaults)

    def _generate_seed(self) -> int:
        return random.randint(0, 2**32 - 1) % self._MAX_SEED_VALUE
