"""Resolution calculation utilities"""

from backend.video.constants.video_parameters import ResolutionClass, AspectRatio


_STANDARD_WIDTHS: dict[ResolutionClass, dict[AspectRatio, int]] = {
    ResolutionClass.PREVIEW_256P: {
        AspectRatio.LANDSCAPE_16_9: 456,
        AspectRatio.LANDSCAPE_3_2:  384,
        AspectRatio.SQUARE_1_1:     256,
        AspectRatio.PORTRAIT_2_3:   170,
        AspectRatio.PORTRAIT_9_16:  144,
    },
    ResolutionClass.LOW_512P: {
        AspectRatio.LANDSCAPE_16_9: 910,
        AspectRatio.LANDSCAPE_3_2:  768,
        AspectRatio.SQUARE_1_1:     512,
        AspectRatio.PORTRAIT_2_3:   342,
        AspectRatio.PORTRAIT_9_16:  288,
    },
    ResolutionClass.SD_480P: {
        AspectRatio.LANDSCAPE_16_9: 854,
        AspectRatio.LANDSCAPE_3_2:  720,
        AspectRatio.SQUARE_1_1:     480,
        AspectRatio.PORTRAIT_2_3:   320,
        AspectRatio.PORTRAIT_9_16:  270,
    },
    ResolutionClass.HD_720P: {
        AspectRatio.LANDSCAPE_16_9: 1280,
        AspectRatio.LANDSCAPE_3_2:  1080,
        AspectRatio.SQUARE_1_1:      720,
        AspectRatio.PORTRAIT_2_3:    480,
        AspectRatio.PORTRAIT_9_16:   406,  # rounded to even
    },
}


def get_dimensions(aspect_ratio: AspectRatio, resolution_class: ResolutionClass) -> tuple[int, int]:
    """
    Get width and height for given aspect ratio and resolution class.

    Args:
        aspect_ratio: AspectRatio enum value
        resolution_class: ResolutionClass enum value
    
    Returns:
        Tuple of (width, height)
    """
    width = _STANDARD_WIDTHS[resolution_class][aspect_ratio]
    height = resolution_class.height

    return width, height
