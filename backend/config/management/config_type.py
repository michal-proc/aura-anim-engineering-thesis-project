from enum import Enum


class ConfigType(Enum):
    """Available configuration types with their corresponding YAML file names."""
    
    PIPELINE = "pipeline"
    VIDEO_GENERATOR = "video_generator"
    VIDEO_PREPROCESSOR = "video_preprocessor"
    VIDEO_POSTPROCESSOR = "video_postprocessor"
    FRAME_INTERPOLATOR = "frame_interpolator"
    FRAME_UPSCALER = "frame_upscaler"
    VIDEO_EXPLORE = "video_explore"
    
    @property
    def filename(self) -> str:
        """Get the YAML filename for this configuration type."""
        return f"{self.value}.yaml"