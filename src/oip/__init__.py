"""Teaching utilities for the Optimisation and Image Processing (OIP) course."""

from .images import (
    ensure_dtype,
    ensure_float,
    ensure_uint8,
    ensure_uint16,
    find_course_image,
    load_gray,
    load_grey,
    load_rgb,
    plot_rgb_histograms,
    show_rgb_histograms,
)
from .plotting import (
    plot_histogram,
    show_histogram,
    show_image,
    show_images,
)

from .week05 import (
    branching_ring,
    square_image,
    harris_image,
    window_changes,
    load_mask,  
    show_votes,
    show_hough,
    show_corners,
    zhang_suen_steps,
    morphology_mask,
    branching_ring,
)

__all__ = [
    # Week 1
    "ensure_uint8",
    "ensure_uint16",
    "ensure_float",
    "ensure_dtype",
    "find_course_image",
    "load_rgb",
    "load_grey",
    "load_gray",
    "show_image",
    # Week 2
    "show_images",
    "show_histogram",
    "plot_histogram",
    "plot_rgb_histograms",
    "show_rgb_histograms",
]
