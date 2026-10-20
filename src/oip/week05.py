"""Lecture 05 images and plotting helpers.

Algorithms remain visible in notebooks; these helpers handle plotting, reproducible
example images, and the optional Zhang-Suen iteration demonstration.
"""

from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
from PIL import Image
from scipy import ndimage as ndi
from skimage import data
# pylint: disable=no-name-in-module
from skimage.draw import ellipse, line
from skimage.measure import euler_number
from skimage.morphology import disk
from skimage.transform import AffineTransform, warp

from oip.plotting import show_images


def load_mask(path, *, dark_foreground=False):
    """Load a course TIFF explicitly as grayscale, then threshold at 128.

    Palette TIFFs must be converted to luminance before thresholding. The old
    lines image and SDU logo have dark foreground; the opening/closing masks do not.
    """
    with Image.open(Path(path)) as image:
        gray = np.asarray(image.convert("L"))
    return gray < 128 if dark_foreground else gray >= 128


def harris_image():
    """Checkerboard, ellipse and touching squares reused from l06.ipynb."""
    transform = AffineTransform(scale=(1.3, 1.1), rotation=1, shear=0.7, translation=(110, 30))
    image = warp(data.checkerboard()[:90, :90], transform.inverse, output_shape=(200, 310))
    rr, cc = ellipse(160, 175, 10, 100, shape=image.shape)
    image[rr, cc] = 1
    image[30:80, 200:250] = 1
    image[80:130, 250:300] = 1
    return image


def square_image():
    """Simple flat, edge and corner example, with image coordinates (row, column)."""
    image = np.zeros((100, 100))
    image[25:75, 25:75] = 1
    return image


def window_changes(image, radius=5):
    """Show SSD under horizontal/vertical one-pixel window shifts at three sites."""
    sites = {"flat": (50, 50), "edge": (25, 50), "corner": (25, 25)}
    _fig, ax = plt.subplots(figsize=(4, 4))
    ax.imshow(image, cmap="gray", vmin=0, vmax=1)
    results = {}
    for name, (row, col) in sites.items():
        source = image[row - radius : row + radius + 1, col - radius : col + radius + 1]
        horizontal = image[row - radius : row + radius + 1, col - radius + 1 : col + radius + 2]
        vertical = image[row - radius + 1 : row + radius + 2, col - radius : col + radius + 1]
        results[name] = (
            float(((source - horizontal) ** 2).sum()),
            float(((source - vertical) ** 2).sum()),
        )
        ax.plot(col, row, "r+")
        ax.text(col + 3, row + 3, name, color="red")
    plt.show()
    for name, (dx, dy) in results.items():
        print(f"{name}: horizontal SSD={dx:.1f}, vertical SSD={dy:.1f}")
    return results


def show_corners(image, response, corners, title="Harris corners"):
    """Display signed response and selected (row, column) coordinates."""
    fig, axes = plt.subplots(1, 3, figsize=(12, 4))
    axes[0].imshow(image, cmap="gray", vmin=0, vmax=1)
    axes[0].set_title("Input")
    limit = max(float(np.abs(response).max()), 1e-12)
    plot = axes[1].imshow(response, cmap="coolwarm", vmin=-limit, vmax=limit)
    fig.colorbar(plot, ax=axes[1], shrink=0.7)
    axes[1].set_title("Signed Harris response")
    axes[2].imshow(image, cmap="gray", vmin=0, vmax=1)
    axes[2].plot(corners[:, 1], corners[:, 0], "r+")
    axes[2].set_title(f"{title}: {len(corners)}")
    for ax in axes:
        ax.axis("off")
    fig.tight_layout()
    plt.show()


def line_image(missing=0.0, noise=0.0):
    """Three l06 lines with deterministic missing edge points/background noise."""
    image = np.zeros((200, 200), dtype=bool)
    idx = np.arange(25, 175)
    image[idx, idx] = True
    image[line(45, 25, 25, 175)] = True
    image[line(25, 135, 175, 155)] = True
    rng = np.random.default_rng(5)
    return (image & (rng.random(image.shape) >= missing)) | (rng.random(image.shape) < noise)


def show_votes():
    """Plot the exact three-point slope/intercept activity from the lecture."""
    points = np.array([[0, 1], [1, 2], [2, 3]])
    slopes = np.linspace(-1, 3, 200)
    fig, axes = plt.subplots(1, 2, figsize=(9, 3))
    axes[0].scatter(points[:, 0], points[:, 1])
    axes[0].set(xlabel="x", ylabel="y", title="Image points")
    for x, y in points:
        axes[1].plot(slopes, -x * slopes + y, label=f"({x}, {y})")
    axes[1].set(xlabel="slope k", ylabel="intercept d", title="Votes")
    axes[1].legend()
    fig.tight_layout()
    plt.show()


def show_hough(edges, accumulator, angles, distances, peaks):
    """Display edge map, log accumulator, and infinite supporting lines.

    Angles must be uniformly spaced. Coordinates are x=column, y=row.
    """
    votes, peak_angles, peak_distances = peaks
    step = np.rad2deg(angles[1] - angles[0])
    bounds = [
        np.rad2deg(angles[0]) - step / 2,
        np.rad2deg(angles[-1]) + step / 2,
        distances[-1] + 0.5,
        distances[0] - 0.5,
    ]
    fig, axes = plt.subplots(1, 3, figsize=(12, 4))
    axes[0].imshow(edges, cmap="gray", vmin=0, vmax=1)
    axes[0].set_title("Edge pixels")
    axes[1].imshow(np.log1p(accumulator), extent=bounds, aspect="auto", cmap="magma")
    axes[1].plot(np.rad2deg(peak_angles), peak_distances, "c+")
    axes[1].set(xlabel="Normal angle (degrees)", ylabel="Signed distance", title="log(1+votes)")
    axes[2].imshow(edges, cmap="gray", vmin=0, vmax=1)
    for angle, distance in zip(peak_angles, peak_distances, strict=True):
        origin = distance * np.array([np.cos(angle), np.sin(angle)])
        tangent = np.array([-np.sin(angle), np.cos(angle)])
        ends = origin[:, None] + tangent[:, None] * np.array([-1000, 1000])
        axes[2].plot(ends[0], ends[1], linewidth=1)
    axes[2].set(
        xlim=(0, edges.shape[1] - 1),
        ylim=(edges.shape[0] - 1, 0),
        title=f"{len(votes)} supporting lines",
    )
    fig.tight_layout()
    plt.show()


def morphology_mask():
    """Blocks, thin bridge, specks and holes matching the slide prediction task."""
    image = np.zeros((120, 180), dtype=bool)
    image[20:65, 15:60] = True
    image[20:65, 80:125] = True
    image[41:44, 60:80] = True
    image[32:35, 30:33] = False
    image[35:42, 95:102] = False
    image[85:88, 15:85] = True
    image[78:108, 110:113] = True
    image[85:87, 140:142] = True
    image[98, 155] = True
    return image


def branching_ring():
    """Thick connected object with a branch and one hole."""
    seed = np.zeros((100, 140), dtype=bool)
    segments = [
        ((75, 35), (30, 35)),
        ((30, 35), (15, 15)),
        ((30, 35), (15, 55)),
        ((60, 35), (60, 80)),
    ]
    for start, end in segments:
        seed[line(*start, *end)] = True
    rr, cc = np.indices(seed.shape)
    seed |= np.abs(np.sqrt((rr - 60) ** 2 + (cc - 100) ** 2) - 20) <= 0.7
    return ndi.binary_dilation(seed, structure=disk(5))


def topology(binary):
    """Return (8-connected foreground components, holes), for demonstration only."""
    components = ndi.label(binary, structure=np.ones((3, 3)))[1]
    return int(components), int(components - euler_number(binary, connectivity=2))


def show_iteration(history, iteration=1):
    """Display one full Zhang-Suen iteration (two subiterations)."""
    show_images(
        history[0],
        history[iteration],
        history[-1],
        titles=["Input", f"Iteration {iteration}", "Converged"],
        vmin=0,
        vmax=1,
    )


def zhang_suen_steps(binary):
    """Return snapshots after full two-subiteration Zhang-Suen passes.

    Uses a zero-padded border, simultaneous deletion, and 8-connected foreground.
    Does not modify the input. The first snapshot is the original binary image.
    """
    image = np.pad(np.asarray(binary, dtype=bool), 1)
    history = [image[1:-1, 1:-1].copy()]
    while True:
        changed = False
        for phase in (0, 1):
            p2 = image[:-2, 1:-1]
            p3 = image[:-2, 2:]
            p4 = image[1:-1, 2:]
            p5 = image[2:, 2:]
            p6 = image[2:, 1:-1]
            p7 = image[2:, :-2]
            p8 = image[1:-1, :-2]
            p9 = image[:-2, :-2]
            neighbours = [p2, p3, p4, p5, p6, p7, p8, p9]
            count = np.stack(neighbours).sum(axis=0)
            transitions = np.stack(
                [(~a) & b for a, b in zip(neighbours, neighbours[1:] + neighbours[:1], strict=True)]
            ).sum(axis=0)
            if phase == 0:
                preserve = ~(p2 & p4 & p6) & ~(p4 & p6 & p8)
            else:
                preserve = ~(p2 & p4 & p8) & ~(p2 & p6 & p8)
            delete = image[1:-1, 1:-1] & (count >= 2) & (count <= 6) & (transitions == 1) & preserve
            if delete.any():
                image[1:-1, 1:-1][delete] = False
                changed = True
        if not changed:
            return history
        history.append(image[1:-1, 1:-1].copy())
