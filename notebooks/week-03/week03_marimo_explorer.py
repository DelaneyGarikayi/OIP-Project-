import marimo

__generated_with = "0.15.0"
app = marimo.App(width="medium")

@app.cell
def _():
    import marimo as mo
    import numpy as np
    import matplotlib.pyplot as plt
    from scipy import ndimage
    from skimage import data, util
    return data, ndimage, np, plt, mo, util

@app.cell
def _(mo):
    mo.md("""
    # Week 3 — Interactive linear-filter explorer

    Use this only **after making a prediction**. Change one parameter at a time and explain the observed change to a partner.
    """)
    return

@app.cell
def _(mo):
    filter_kind = mo.ui.dropdown(
        options=["box", "gaussian", "horizontal derivative", "laplacian"],
        value="gaussian", label="filter"
    )
    sigma = mo.ui.slider(0.5, 6.0, step=0.5, value=2.0, label="sigma")
    size = mo.ui.slider(3, 15, step=2, value=3, label="box size")
    border = mo.ui.dropdown(
        options=["reflect", "nearest", "constant", "wrap"], value="reflect", label="border mode"
    )
    mo.hstack([filter_kind, sigma, size, border])
    return border, filter_kind, sigma, size

@app.cell
def _(border, data, filter_kind, ndimage, np, sigma, size, util):
    image = util.img_as_float(data.camera())
    if filter_kind.value == "box":
        n = int(size.value)
        kernel = np.ones((n, n), dtype=float) / (n * n)
        output = ndimage.correlate(image, kernel, mode=border.value)
    elif filter_kind.value == "gaussian":
        s = float(sigma.value)
        r = int(np.ceil(3*s))
        x = np.arange(-r, r+1)
        g = np.exp(-(x*x)/(2*s*s)); g /= g.sum()
        kernel = np.outer(g, g)
        output = ndimage.correlate(image, kernel, mode=border.value)
    elif filter_kind.value == "horizontal derivative":
        kernel = np.array([[0,0,0],[-1,0,1],[0,0,0]], dtype=float)
        output = ndimage.correlate(image, kernel, mode=border.value)
    else:
        kernel = np.array([[0,1,0],[1,-4,1],[0,1,0]], dtype=float)
        output = ndimage.correlate(image, kernel, mode=border.value)
    return image, kernel, output

@app.cell
def _(image, kernel, mo, np, output, plt):
    fig, axes = plt.subplots(1, 3, figsize=(12, 4))
    axes[0].imshow(image, cmap="gray"); axes[0].set_title("original")
    axes[1].imshow(kernel, cmap="gray"); axes[1].set_title(f"kernel, sum={kernel.sum():.3g}")
    axes[2].imshow(output, cmap="gray"); axes[2].set_title("filtered")
    for ax in axes: ax.axis("off")
    mo.vstack([
        fig,
        mo.md(f"Kernel shape: **{kernel.shape}**  |  max |output|: **{np.max(np.abs(output)):.3g}**")
    ])
    return

@app.cell
def _(mo):
    mo.md("""
    ## Prompts

    1. Which controls alter the *kernel* and which alter only the treatment of the image boundary?
    2. For which filters should a constant image be preserved? For which should it be rejected?
    3. Which kernels are unchanged by a 180° rotation?
    4. Which Gaussian parameter most directly determines the spatial scale of smoothing?
    5. Choose one surprising result and explain it from the kernel coefficients rather than from the displayed image alone.
    """)
    return

if __name__ == "__main__":
    app.run()
