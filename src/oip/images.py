"""Image loading and data-type conversion utilities for OIP.

These helpers provide the common infrastructure used throughout the
Optimisation and Image Processing course. Images themselves remain ordinary
NumPy arrays so that all numerical operations stay explicit.

Copyright (c) 2026 Till Leissner
SPDX-License-Identifier: MIT
"""

import warnings
from collections.abc import Sequence
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
from matplotlib.axes import Axes
from matplotlib.figure import Figure
from numpy.typing import ArrayLike
from skimage import color, data, io, util

_COURSE_IMAGE_DIRS = [
    Path("../../../data-external/shared/img"),
    Path("../../data-external/shared/img"),
    Path("../../img"),
    Path("../img"),
    Path("img"),
]


ImageDType = (
    type[np.uint8] | type[np.uint16] | type[np.float32] | type[np.float64] | type[float] | np.dtype
)


# Introduced in Week 1: image representation and data types.
def ensure_uint8(image):
    """Return *image* as uint8 with an appropriately scaled intensity range."""
    return util.img_as_ubyte(image)


# Introduced in Week 1: image representation and data types.
def ensure_uint16(image):
    """Return *image* as uint16 with an appropriately scaled intensity range."""
    return util.img_as_uint(image)


# Introduced in Week 1: image representation and data types.
def ensure_float(image, dtype: ImageDType = np.float64):
    """Return floating-point image data in the conventional [0, 1] range."""
    dtype = np.dtype(dtype)
    if dtype not in (np.dtype(np.float32), np.dtype(np.float64)):
        raise TypeError("ensure_float supports float32 and float64")
    return util.img_as_float(image).astype(dtype, copy=False)


# Introduced in Week 1: image representation and data types.
def ensure_dtype(image, dtype: ImageDType = np.uint8):
    """Convert an image to one of the data types used in the course."""
    if dtype is float:
        dtype = np.float64

    dtype = np.dtype(dtype)
    if dtype == np.dtype(np.uint8):
        return ensure_uint8(image)
    if dtype == np.dtype(np.uint16):
        return ensure_uint16(image)
    if dtype == np.dtype(np.float32):
        return ensure_float(image, np.float32)
    if dtype == np.dtype(np.float64):
        return ensure_float(image, np.float64)

    raise TypeError(
        f"Unsupported image dtype {dtype}. Use uint8, uint16, float32, float64, or float."
    )


_STANDARD_IMAGES = {
    "camera": data.camera,
    "coins": data.coins,
    "moon": data.moon,
    "page": data.page,
    "text": data.text,
    "astronaut": data.astronaut,
    "coffee": data.coffee,
    "chelsea": data.chelsea,
    "rocket": data.rocket,
}


# Introduced in Week 1: course image infrastructure.
def find_course_image(relative_path):
    """Find an image in common OIP repository layouts."""
    candidates = [
        Path("../../../data-external/shared/img") / relative_path,
        Path("../../data-external/shared/img") / relative_path,
        Path("../../img") / relative_path,
        Path("../img") / relative_path,
        Path("img") / relative_path,
        Path(relative_path),
    ]
    for path in candidates:
        if path.exists():
            return path
    return None


def _find_image(name_or_path):
    """Return a path for an explicit path or course-image name, else ``None``."""
    requested = Path(name_or_path).expanduser()
    if requested.is_file():
        return requested

    direct = find_course_image(requested)
    if direct is not None and direct.is_file():
        return direct

    image_dirs = [d for d in _COURSE_IMAGE_DIRS if d.exists()]
    matches = []
    for image_dir in image_dirs:
        if requested.suffix:
            matches.extend(p for p in image_dir.rglob(requested.name) if p.is_file())
        else:
            matches.extend(p for p in image_dir.rglob(f"{requested.name}.*") if p.is_file())

    if matches:

        def sort_key(path):
            for priority, root in enumerate(_COURSE_IMAGE_DIRS):
                try:
                    rel = path.relative_to(root)
                    return priority, len(rel.parts), str(rel)
                except ValueError:
                    pass
            return len(_COURSE_IMAGE_DIRS), len(path.parts), str(path)

        return sorted(matches, key=sort_key)[0]
    return None


def _standard_image(name, fallback):
    key = str(name).lower()
    if key in _STANDARD_IMAGES:
        return _STANDARD_IMAGES[key]()
    warnings.warn(
        f"Image {name!r} not found; using skimage.data.{fallback}() instead.",
        stacklevel=2,
    )
    return _STANDARD_IMAGES[fallback]()


def _read_image(name_or_path, fallback):
    path = _find_image(name_or_path)
    if path is not None:
        return io.imread(path)
    return _standard_image(name_or_path, fallback=fallback)


# Introduced in Week 1: loading RGB course/sample images.
def load_rgb(name_or_path="astronaut", dtype=np.uint8):
    """Load an RGB image by course-image name, standard-image name, or path."""
    image = _read_image(name_or_path, fallback="astronaut")
    if image.ndim == 2:
        image = color.gray2rgb(image)
    elif image.ndim == 3 and image.shape[-1] == 4:
        image = color.rgba2rgb(image)
    elif image.ndim != 3 or image.shape[-1] != 3:
        raise ValueError(f"Cannot interpret image with shape {image.shape} as RGB")
    return ensure_dtype(image, dtype)


# Introduced in Week 1: loading grayscale course/sample images.
def load_grey(name_or_path="camera", dtype=np.uint8):
    """Load a grayscale image by course-image name, standard-image name, or path."""
    image = _read_image(name_or_path, fallback="camera")
    if image.ndim == 3:
        if image.shape[-1] == 4:
            image = color.rgba2rgb(image)
        image = color.rgb2gray(image)
    elif image.ndim != 2:
        raise ValueError(f"Cannot interpret image with shape {image.shape} as grayscale")
    return ensure_dtype(image, dtype)


# Introduced in Week 1: American-spelling convenience alias.
load_gray = load_grey


# Week 2
def _validate_rgb_image(image: ArrayLike) -> np.ndarray:
    """Return image as ndarray and validate that it is an RGB image."""
    image = np.asarray(image)

    if image.ndim != 3 or image.shape[2] != 3:
        raise ValueError("Expected an RGB image with shape (height, width, 3).")

    return image


def _default_histogram_range(image: np.ndarray) -> tuple[float, float]:
    """Return a reasonable histogram range for the image."""
    if image.dtype == np.uint8:
        return (0, 256)
    return (float(image.min()), float(image.max()))


def _channel_data(
    image: np.ndarray,
) -> dict[str, np.ndarray]:
    """Return R, G, B, and average channels."""
    red = image[..., 0]
    green = image[..., 1]
    blue = image[..., 2]
    average = image.mean(axis=2)

    return {
        "red": red,
        "green": green,
        "blue": blue,
        "average": average,
    }


def plot_rgb_histograms(
    image: ArrayLike,
    *,
    ax: Axes | None = None,
    bins: int = 256,
    value_range: tuple[float, float] | None = None,
    mode: str = "hist",
    percentiles: Sequence[float] | None = None,
) -> Axes:
    """Plot RGB channel statistics for an RGB image.

    Parameters
    ----------
    image
        RGB image with shape (H, W, 3).
    ax
        Matplotlib axis to plot on. If None, a new axis is created.
    bins
        Number of histogram bins.
    value_range
        Histogram range. For uint8 images the default is (0, 256).
    mode
        One of:
        - "hist" : raw histogram (counts)
        - "pdf"  : normalized histogram
        - "cdf"  : cumulative distribution function
    percentiles
        Optional percentiles to indicate with vertical lines,
        e.g. [5, 50, 95].

    Returns
    -------
    Axes
        The Matplotlib axis containing the plot.
    """
    image = _validate_rgb_image(image)

    if ax is None:
        _, ax = plt.subplots()

    if value_range is None:
        value_range = _default_histogram_range(image)

    if mode not in {"hist", "pdf", "cdf"}:
        raise ValueError("mode must be 'hist', 'pdf', or 'cdf'.")

    channels = _channel_data(image)
    colors = {
        "red": "r",
        "green": "g",
        "blue": "b",
        "average": "k",
    }
    labels = {
        "red": "R",
        "green": "G",
        "blue": "B",
        "average": "average",
    }

    if mode == "hist":
        ylabel = "number of pixels"
        title = "RGB histograms"
    elif mode == "pdf":
        ylabel = "probability density"
        title = "RGB PDFs"
    else:  # mode == "cdf"
        ylabel = "cumulative fraction"
        title = "RGB CDFs"

    for name, channel in channels.items():
        hist, edges = np.histogram(channel, bins=bins, range=value_range)
        x = (edges[:-1] + edges[1:]) / 2

        if mode == "hist":
            y = hist
        elif mode == "pdf":
            y = hist.astype(float) / hist.sum()
        else:  # mode == "cdf"
            y = np.cumsum(hist).astype(float)
            y /= y[-1]

        ax.plot(x, y, color=colors[name], label=labels[name])

        if percentiles is not None:
            percentile_values = np.percentile(channel, percentiles)

            for percentile, value in zip(percentiles, percentile_values):
                ax.axvline(
                    value,
                    color=colors[name],
                    linestyle="--",
                    alpha=0.5,
                )

                if mode == "cdf":
                    ax.axhline(
                        percentile / 100,
                        color=colors[name],
                        linestyle=":",
                        linewidth=1,
                        alpha=0.3,
                    )

    ax.set_xlabel("intensity")
    ax.set_ylabel(ylabel)
    ax.set_title(title)
    ax.set_xlim(value_range)

    if mode == "cdf":
        ax.set_ylim(0, 1.02)

    ax.legend()

    return ax


def rgb_to_gray_average(image: ArrayLike) -> np.ndarray:
    """Convert an RGB image to grayscale using the average method.

    Gray = (R + G + B) / 3

    Parameters
    ----------
    image
        RGB image with shape (H, W, 3).

    Returns
    -------
    ndarray
        Grayscale image as floating-point array.
    """
    image = _validate_rgb_image(image).astype(float)

    return image.mean(axis=2)


def rgb_to_gray_luminosity(image: ArrayLike) -> np.ndarray:
    """Convert an RGB image to grayscale using the luminosity method.

    Gray = 0.21 R + 0.72 G + 0.07 B

    Parameters
    ----------
    image
        RGB image with shape (H, W, 3).

    Returns
    -------
    ndarray
        Grayscale image as floating-point array.
    """
    image = _validate_rgb_image(image).astype(float)

    red = image[..., 0]
    green = image[..., 1]
    blue = image[..., 2]

    return 0.21 * red + 0.72 * green + 0.07 * blue


def rgb_to_gray_lightness(image: ArrayLike) -> np.ndarray:
    """Convert an RGB image to grayscale using the lightness method.

    Gray = (max(R, G, B) + min(R, G, B)) / 2

    Parameters
    ----------
    image
        RGB image with shape (H, W, 3).

    Returns
    -------
    ndarray
        Grayscale image as floating-point array.
    """
    image = _validate_rgb_image(image).astype(float)

    maximum = image.max(axis=2)
    minimum = image.min(axis=2)

    return (maximum + minimum) / 2


def show_rgb_histograms(
    image: ArrayLike,
    *,
    bins: int = 256,
    value_range: tuple[float, float] | None = None,
    show_hist: bool = True,
    show_pdf: bool = True,
    show_cdf: bool = True,
    percentiles: Sequence[float] | None = None,
    title: str | None = None,
    figsize: tuple[float, float] | None = None,
) -> tuple[Figure, np.ndarray]:
    """Show an RGB image together with histogram/PDF/CDF plots.

    Parameters
    ----------
    image
        RGB image with shape (H, W, 3).
    bins
        Number of histogram bins.
    value_range
        Histogram range. For uint8 images the default is (0, 256).
    show_hist
        If True, show the raw histogram.
    show_pdf
        If True, show the normalized histogram (PDF).
    show_cdf
        If True, show the cumulative distribution function (CDF).
    percentiles
        Optional percentiles to indicate with vertical lines.
    title
        Optional title for the image panel.
    figsize
        Optional figure size.

    Returns
    -------
    Figure
        The created Matplotlib figure.
    ndarray
        Array of axes.
    """
    image = _validate_rgb_image(image)

    if value_range is None:
        hist_range = _default_histogram_range(image)
    else:
        hist_range = value_range

    display_range = (0, 255) if image.dtype == np.uint8 else hist_range

    plot_modes = []
    if show_hist:
        plot_modes.append("hist")
    if show_pdf:
        plot_modes.append("pdf")
    if show_cdf:
        plot_modes.append("cdf")

    ncols = 1 + len(plot_modes)

    if ncols == 1:
        raise ValueError("At least one of show_hist, show_pdf, or show_cdf must be True.")

    if figsize is None:
        figsize = (4.5 * ncols, 4.0)

    fig, axes = plt.subplots(1, ncols, figsize=figsize)

    if ncols == 2:
        axes = np.array(axes, dtype=object)

    axes[0].imshow(
        image,
        vmin=display_range[0],
        vmax=display_range[1],
    )
    axes[0].set_title(title or "RGB image")
    axes[0].axis("off")

    for i, mode in enumerate(plot_modes, start=1):
        plot_rgb_histograms(
            image,
            ax=axes[i],
            bins=bins,
            value_range=hist_range,
            mode=mode,
            percentiles=percentiles,
        )

    fig.tight_layout()

    return fig, axes
