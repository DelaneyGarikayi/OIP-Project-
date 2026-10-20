"""Small plotting helpers for OIP teaching notebooks.

The functions in this module remove repetitive Matplotlib boilerplate. They do
not implement image-processing algorithms.

Copyright (c) 2026 Till Leissner
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from collections.abc import Sequence

import matplotlib.pyplot as plt
import numpy as np
from matplotlib.axes import Axes
from matplotlib.figure import Figure
from numpy.typing import ArrayLike


# Introduced in Week 1: basic image display helper.
def show_image(image, title="", cmap="gray", *, figsize=(5, 4), vmin=None, vmax=None):
    """Display one image without axes and return the Matplotlib figure and axes."""
    fig, ax = plt.subplots(figsize=figsize)
    ax.imshow(
        image,
        cmap=cmap if image.ndim == 2 else None,
        vmin=vmin,
        vmax=vmax,
    )
    ax.set_title(title)
    ax.axis("off")
    plt.show()
    return fig, ax


# Week 2
def show_images(*images, titles=None, cmap="gray", figsize=None, vmin=None, vmax=None):
    """Display several images side by side and return the figure and axes."""
    if not images:
        raise ValueError("Provide at least one image")
    n = len(images)
    if titles is None:
        titles = [""] * n
    if len(titles) != n:
        raise ValueError("titles must have the same length as images")
    if figsize is None:
        figsize = (4 * n, 4)

    fig, axes = plt.subplots(1, n, figsize=figsize, squeeze=False)
    axes = axes[0]
    for ax, image, title in zip(axes, images, titles):
        ax.imshow(
            image,
            cmap=cmap if image.ndim == 2 else None,
            vmin=vmin,
            vmax=vmax,
        )
        ax.set_title(title)
        ax.axis("off")
    fig.tight_layout()
    plt.show()
    return fig, axes


### Week 2
def plot_histogram(
    image: ArrayLike,
    *,
    ax: Axes | None = None,
    bins: int = 256,
    value_range: tuple[float, float] | None = None,
    percentiles: Sequence[float] | None = None,
    cumulative: bool = False,
    normalize: bool = False,
) -> Axes:
    """Plot the histogram of a grayscale image.

    Parameters
    ----------
    image
        Two-dimensional grayscale image.
    ax
        Matplotlib axis to plot on. If None, a new axis is created.
    bins
        Number of histogram bins.
    value_range
        Intensity range used for the histogram. For uint8 images,
        the default is (0, 256).
    percentiles
        Optional percentiles to indicate with vertical lines,
        e.g. [5, 50, 95].
    cumulative
        If True, plot the normalized cumulative histogram.
    normalize
        If True, normalize the ordinary histogram so that the bin
        values sum to one. Ignored when cumulative=True.

    Returns
    -------
    Axes
        The Matplotlib axis containing the plot.
    """
    image = np.asarray(image)

    if image.ndim != 2:
        raise ValueError("plot_histogram() expects a 2-D grayscale image.")

    if ax is None:
        _, ax = plt.subplots()

    if value_range is None:
        if image.dtype == np.uint8:
            value_range = (0, 256)
        else:
            value_range = (float(image.min()), float(image.max()))

    hist, edges = np.histogram(
        image,
        bins=bins,
        range=value_range,
    )

    x = (edges[:-1] + edges[1:]) / 2

    if cumulative:
        values = np.cumsum(hist)
        values = values / values[-1]

        ax.plot(x, values)
        ax.set_ylabel("cumulative fraction")
        ax.set_ylim(0, 1.02)
        ax.set_title("cumulative histogram")

    else:
        values = hist.astype(float)

        if normalize:
            values /= values.sum()
            ylabel = "fraction of pixels"
        else:
            ylabel = "number of pixels"

        ax.plot(x, values)
        ax.set_ylabel(ylabel)
        ax.set_title("histogram")

    ax.set_xlabel("intensity")
    ax.set_xlim(value_range)

    if percentiles is not None:
        percentile_values = np.percentile(image, percentiles)

        for percentile, value in zip(percentiles, percentile_values):
            ax.axvline(
                value,
                linestyle="--",
                label=f"{percentile:g}% = {value:.1f}",
            )

            if cumulative:
                ax.axhline(
                    percentile / 100,
                    linestyle=":",
                    linewidth=1,
                )

        ax.legend()

    return ax


### Week 2
def show_histogram(
    image: ArrayLike,
    *,
    bins: int = 256,
    value_range: tuple[float, float] | None = None,
    percentiles: Sequence[float] | None = None,
    cumulative: bool = False,
    normalize: bool = False,
    title: str | None = None,
    figsize: tuple[float, float] | None = None,
) -> tuple[Figure, np.ndarray]:
    """Show a grayscale image together with its histogram.

    Optionally display percentile markers and a cumulative histogram.

    Parameters
    ----------
    image
        Two-dimensional grayscale image.
    bins
        Number of histogram bins.
    value_range
        Intensity range used for plotting and histogram calculation.
        For uint8 images, the default display range is 0...255 and
        the histogram range is 0...256.
    percentiles
        Optional percentiles to indicate, e.g. [5, 50, 95].

        If True, add a cumulative histogram as a third panel.
    normalize
        If True, normalize the ordinary histogram so that its values
        sum to one.
    title
        Optional title for the image panel.
    figsize
        Optional Matplotlib figure size.

    Returns
    -------
    Figure
        The created Matplotlib figure.
    ndarray
        Array containing the created axes.
    """
    image = np.asarray(image)

    if image.ndim != 2:
        raise ValueError("show_histogram() expects a 2-D grayscale image.")

    if value_range is None:
        if image.dtype == np.uint8:
            histogram_range = (0, 256)
            display_range = (0, 255)
        else:
            display_range = (
                float(image.min()),
                float(image.max()),
            )
            histogram_range = display_range
    else:
        histogram_range = value_range
        display_range = value_range

    ncols = 3 if cumulative else 2

    if figsize is None:
        figsize = (13, 4) if cumulative else (9, 4)

    fig, axes = plt.subplots(
        1,
        ncols,
        figsize=figsize,
    )

    axes[0].imshow(
        image,
        cmap="gray",
        vmin=display_range[0],
        vmax=display_range[1],
    )
    axes[0].set_title(title or "image")
    axes[0].axis("off")

    plot_histogram(
        image,
        ax=axes[1],
        bins=bins,
        value_range=histogram_range,
        percentiles=percentiles,
        cumulative=False,
        normalize=normalize,
    )

    if cumulative:
        plot_histogram(
            image,
            ax=axes[2],
            bins=bins,
            value_range=histogram_range,
            percentiles=percentiles,
            cumulative=True,
        )

    fig.tight_layout()

    return fig, axes
