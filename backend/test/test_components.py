#!/usr/bin/env python3
"""
Test script for individual pipeline components (without Ray Serve).

This script tests components directly for faster debugging:
- VideoPreprocessor
- VideoGenerator
- FrameInterpolator
- FrameUpscaler
- VideoPostprocessor

Usage:
    python backend/test/test_components.py [config_name]

Available configurations:
    quick       - Quick test: 256x256, 2s, 8fps (no upscaling, no interpolation)
    interpolate - Test interpolation: 512x512, 2s, 16fps (2x interpolation)
    upscale     - Test upscaling: 1024x1024, 2s, 8fps (2x upscaling)
    full        - Full test: 1024x1024, 2s, 16fps (2x upscaling + 2x interpolation)
    default     - Default test: 512x512, 2s, 16fps (same as interpolate)
"""

import sys
import os
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))
os.chdir(project_root)


# Test configurations
TEST_CONFIGS = {
    "quick": {
        "name": "Quick Test",
        "description": "Fast test without upscaling or interpolation",
        "width": 256,
        "height": 256,
        "length": 2,
        "fps": 8,
        "seed": 42,
        "prompt": "A beautiful sunset over the ocean"
    },
    "interpolate": {
        "name": "Interpolation Test",
        "description": "Tests frame interpolation (2x FPS)",
        "width": 512,
        "height": 512,
        "length": 2,
        "fps": 16,
        "seed": 42,
        "prompt": "A beautiful sunset over the ocean"
    },
    "upscale": {
        "name": "Upscaling Test",
        "description": "Tests frame upscaling (2x resolution)",
        "width": 1024,
        "height": 1024,
        "length": 2,
        "fps": 8,
        "seed": 42,
        "prompt": "A beautiful sunset over the ocean"
    },
    "full": {
        "name": "Full Pipeline Test",
        "description": "Tests both upscaling and interpolation",
        "width": 1024,
        "height": 1024,
        "length": 2,
        "fps": 16,
        "seed": 42,
        "prompt": "A beautiful sunset over the ocean"
    },
    "default": {
        "name": "Default Test",
        "description": "Standard test configuration",
        "width": 512,
        "height": 512,
        "length": 2,
        "fps": 16,
        "seed": 42,
        "prompt": "A beautiful sunset over the ocean"
    }
}


def test_components(config_name="default"):
    """Test pipeline components directly (without Ray Serve)."""

    # Validate config
    if config_name not in TEST_CONFIGS:
        print(f"Error: Unknown configuration '{config_name}'")
        print(f"Available configurations: {', '.join(TEST_CONFIGS.keys())}")
        return False

    config = TEST_CONFIGS[config_name]

    print("=" * 80)
    print("COMPONENT TEST (Direct, No Ray)")
    print("=" * 80)
    print(f"Configuration: {config['name']}")
    print(f"Description: {config['description']}")
    print("=" * 80)

    try:
        print("\nImporting pipeline components...")

        from backend.pipeline.schemas.component_parameters import (
            VideoParameters,
            VideoPreprocessorOutput
        )

        from backend.pipeline.utilities.parameter_conversion import (
            to_preprocessor_input,
            to_generator_params,
            to_interpolator_input,
            to_upscaler_input,
            to_postprocessor_params
        )

        from backend.pipeline.components.video_preprocessor import VideoPreprocessor
        from backend.pipeline.components.video_generator import VideoGenerator
        from backend.pipeline.components.frame_interpolator import FrameInterpolator
        from backend.pipeline.components.frame_upscaler import FrameUpscaler
        from backend.pipeline.components.video_postprocessor import VideoPostprocessor

        print("✓ All components imported successfully")

        print("\nInitializing components...")
        preprocessor = VideoPreprocessor(enable_logging=True)
        generator = VideoGenerator(enable_logging=True)
        interpolator = FrameInterpolator(enable_logging=True)
        upscaler = FrameUpscaler(enable_logging=True)
        postprocessor = VideoPostprocessor(enable_logging=True)

        print("✓ All components initialized successfully")

        test_prompt = config["prompt"]
        test_width = config["width"]
        test_height = config["height"]
        test_length = config["length"]
        test_fps = config["fps"]
        test_seed = config["seed"]

        print("\n" + "=" * 80)
        print("Test Parameters:")
        print(f"  Prompt: {test_prompt}")
        print(f"  Dimensions: {test_width}x{test_height}")
        print(f"  Length: {test_length}s")
        print(f"  FPS: {test_fps}")
        print(f"  Seed: {test_seed}")
        print("=" * 80)

        # Create main VideoParameters object
        params = VideoParameters(
            prompt=test_prompt,
            negative_prompt="blurry, poor quality, bad quality",
            video_width=test_width,
            video_height=test_height,
            video_length=test_length,
            fps=test_fps,
            inference_steps=25,
            guidance_scale=7.5,
            seed=test_seed,
            base_model="sd15",
            motion_adapter="default",
            loras={},
            output_format="mp4"
        )

        print("\n[1/5] Preprocessing parameters...")
        preprocessor_input = to_preprocessor_input(params)

        preprocessor_output = preprocessor.process(preprocessor_input)

        print(f"✓ Preprocessing complete:")
        print(f"  FPS factor: {preprocessor_output.fps_factor}x")
        print(f"  Frame scale factor: {preprocessor_output.frame_scale_factor}x")
        print(f"  Adjusted dimensions: {preprocessor_output.adjusted_width}x{preprocessor_output.adjusted_height}")
        print(f"  Adjusted length: {preprocessor_output.adjusted_length}s")

        print("\n[2/5] Generating base frames...")
        print("  NOTE: This step may take several minutes depending on your hardware")

        generation_params = to_generator_params(params, preprocessor_output)

        base_frames = generator.generate(generation_params)

        print(f"✓ Generated {len(base_frames)} base frames")
        if base_frames:
            print(f"  Frame dimensions: {base_frames[0].width}x{base_frames[0].height}")

        processed_frames = base_frames

        if preprocessor_output.fps_factor > 1:
            print(f"\n[3/5] Interpolating frames ({preprocessor_output.fps_factor}x)...")
            print("  NOTE: This step may take a few minutes")

            interpolator_input = to_interpolator_input(
                processed_frames,
                preprocessor_output.fps_factor
            )

            processed_frames = interpolator.interpolate(interpolator_input)

            print(f"✓ Interpolated to {len(processed_frames)} frames")
        else:
            print("\n[3/5] Skipping frame interpolation (fps_factor = 1)")

        if preprocessor_output.frame_scale_factor > 1:
            print(f"\n[4/5] Upscaling frames ({preprocessor_output.frame_scale_factor}x)...")
            print("  NOTE: This step may take several minutes")

            upscaler_input = to_upscaler_input(
                processed_frames,
                preprocessor_output.frame_scale_factor
            )

            processed_frames = upscaler.upscale(upscaler_input)

            print(f"✓ Upscaled to {processed_frames[0].width}x{processed_frames[0].height}")
        else:
            print("\n[4/5] Skipping frame upscaling (frame_scale_factor = 1)")

        print("\n[5/5] Post-processing and saving video...")

        final_fps = 8 * preprocessor_output.fps_factor
        output_dir = "outputs/test"

        postprocessor_params = to_postprocessor_params(
            processed_frames,
            params,
            final_fps,
            output_dir
        )

        output_path = postprocessor.postprocess(postprocessor_params)

        print(f"✓ Video saved to: {output_path}")

        if os.path.exists(output_path):
            file_size_mb = os.path.getsize(output_path) / (1024 * 1024)
            print(f"  File size: {file_size_mb:.2f} MB")
        else:
            raise RuntimeError(f"Output file not found: {output_path}")

        print("\n" + "=" * 80)
        print("COMPONENT TEST COMPLETED SUCCESSFULLY!")
        print("=" * 80)
        print("Summary:")
        print(f"  Input: {test_width}x{test_height}, {test_length}s @ {test_fps}fps")
        print(f"  Generated: {len(base_frames)} base frames")
        print(f"  Final: {len(processed_frames)} frames @ {final_fps}fps")
        print(f"  Output: {output_path}")
        print("=" * 80)

        return True

    except Exception as e:
        print("\n" + "=" * 80)
        print("COMPONENT TEST FAILED!")
        print("=" * 80)
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
        print("=" * 80)
        return False


def print_usage():
    """Print usage information."""
    print("Component Test Script (Direct, No Ray)")
    print("=" * 80)
    print("\nUsage:")
    print("  python backend/test/test_components.py [config_name]")
    print("\nAvailable configurations:")
    for name, config in TEST_CONFIGS.items():
        print(f"\n  {name:12} - {config['name']}")
        print(f"               {config['description']}")
        print(f"               {config['width']}x{config['height']}, {config['length']}s @ {config['fps']}fps")
    print("\nDefault: default")
    print("=" * 80)


if __name__ == "__main__":
    if len(sys.argv) > 1:
        if sys.argv[1] in ["-h", "--help", "help"]:
            print_usage()
            sys.exit(0)
        config_name = sys.argv[1]
    else:
        config_name = "default"

    print("Component Test Script (Direct, No Ray)")
    print("=" * 80)

    success = test_components(config_name)

    if success:
        print("\n✓ All tests passed!")
        sys.exit(0)
    else:
        print("\n✗ Tests failed!")
        sys.exit(1)
