from enum import Enum


class AspectRatio(Enum):
    """Supported aspect ratios"""
    LANDSCAPE_16_9 = (16, 9)
    LANDSCAPE_3_2 = (3, 2)
    SQUARE_1_1 = (1, 1)
    PORTRAIT_2_3 = (2, 3)
    PORTRAIT_9_16 = (9, 16)

    @property
    def ratio_string(self) -> str:
        """Get the aspect ratio as a string"""
        w, h = self.value
        return f"{w}:{h}"
    
    @property
    def width_ratio(self) -> int:
        """Get the width component of the ratio"""
        return self.value[0]
    
    @property
    def height_ratio(self) -> int:
        """Get the height component of the ratio"""
        return self.value[1]


class ResolutionClass(int, Enum):
    """Supported resolution classes"""
    PREVIEW_256P = 256
    LOW_512P = 512
    SD_480P = 480
    HD_720P = 720
    
    @property
    def height(self) -> int:
        """Get the base height for this resolution class"""
        return self.value

    @property
    def name_string(self) -> str:
        """Get the resolution class as a string"""
        return f"{self.value}p"


class VideoFPS(int, Enum):
    """Supported video frame rates"""
    BASE = 8
    SMOOTH = 16
    CINEMATIC = 24
    HIGH = 32


class VideoFormat(str, Enum):
    """Supported output formats"""
    MP4 = "mp4"
    WEBM = "webm"
    GIF = "gif"


class BaseGenerationModel(str, Enum):
    """Supported base models"""
    SD15 = "sd15"
    SD21 = "sd21"
    EPICREALISM = "epicrealism"
    REALISTIC_VISION = "realistic_vision"
    DREAMSHAPER = "dreamshaper"
    JUGGERNAUT = "juggernaut"
    REV_ANIMATED = "rev_animated"


class MotionAdapter(str, Enum):
    """Supported motion adapters"""
    DEFAULT = "default"
