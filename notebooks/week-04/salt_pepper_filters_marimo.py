# /// script
# requires-python = ">=3.11"
# dependencies = [
#   "marimo>=0.16",
#   "pillow>=10",
# ]
# ///

import marimo

__generated_with = "0.25.0"
app = marimo.App(width="full")


@app.cell
def _():
    import base64
    import io
    import random

    import marimo as mo
    from PIL import Image, ImageDraw, ImageFilter, ImageFont

    return Image, ImageDraw, ImageFilter, ImageFont, base64, io, mo, random


@app.cell
def _(mo):
    mo.md(r"""
    # Salt-and-pepper noise removal

    This animation illustrates neighborhood filtering of an **8-bit
    grayscale image** containing salt-and-pepper noise.

    - **Min filter:** removes isolated bright salt pixels.
    - **Max filter:** removes isolated dark pepper pixels.
    - **Median filter:** removes both types while usually preserving
      edges better.

    The red box shows the current neighborhood. The middle panel shows
    its pixel values. The right panel reveals the filtered result as the
    window moves across the image.
    """)
    return


@app.cell
def _(mo):
    filter_type = mo.ui.dropdown(
        options=["Min", "Max", "Median"],
        value="Median",
        label="Filter",
    )
    kernel_size = mo.ui.dropdown(
        options=[3, 5, 7],
        value=3,
        label="Kernel size",
    )
    noise_amount = mo.ui.slider(
        start=0.01,
        stop=0.20,
        step=0.01,
        value=0.08,
        label="Salt-and-pepper amount",
        show_value=True,
    )
    seed = mo.ui.number(
        start=0,
        stop=9999,
        step=1,
        value=7,
        label="Random seed",
    )
    imagesize = mo.ui.dropdown(
        options=list(range(8, 129, 8)),
        value=16,
        label="Image size",
    )
    mo.hstack(
        [imagesize,filter_type, kernel_size, noise_amount, seed],
        justify="start",
        gap=2,
    )


    return filter_type, imagesize, kernel_size, noise_amount, seed


@app.cell
def _(Image, ImageDraw, imagesize, noise_amount, random, seed):
    # Generate a small synthetic 8-bit grayscale test image locally.
    # This avoids skimage/scipy and makes the app self-contained.
    _width = int(imagesize.value)
    _height = int(imagesize.value)
    original = Image.new("L", (_width, _height))
    _pixels = original.load()

    # Smooth gradient background.
    for _y in range(_height):
        for _x in range(_width):
            _pixels[_x, _y] = int(35 + 170 * _x / (_width - 1))

    # Add structures/edges so the effect of filter size is easy to see.
    _draw = ImageDraw.Draw(original)
    _draw.rectangle((7, 8, 27, 27), fill=205)
    _draw.rectangle((33, 7, 55, 22), fill=65)
    _draw.ellipse((11, 35, 31, 55), fill=85)
    _draw.ellipse((37, 33, 57, 55), fill=220)
    _draw.line((4, 31, 59, 31), fill=130, width=2)

    noisy = original.copy()
    _noisy_pixels = noisy.load()

    _rng = random.Random(int(seed.value))
    _n_corrupt = int(float(noise_amount.value) * _width * _height)
    _positions = _rng.sample(range(_width * _height), _n_corrupt)

    _half = len(_positions) // 2
    for _i, _index in enumerate(_positions):
        _x = _index % _width
        _y = _index // _width
        _noisy_pixels[_x, _y] = 0 if _i < _half else 255
    return (noisy,)


@app.cell
def _(ImageFilter, filter_type, kernel_size, noisy):
    size = int(kernel_size.value)

    if filter_type.value == "Min":
        filtered = noisy.filter(ImageFilter.MinFilter(size=size))
    elif filter_type.value == "Max":
        filtered = noisy.filter(ImageFilter.MaxFilter(size=size))
    else:
        filtered = noisy.filter(ImageFilter.MedianFilter(size=size))
    return filtered, size


@app.cell
def _(
    Image,
    ImageDraw,
    ImageFont,
    base64,
    filter_type,
    filtered,
    io,
    mo,
    noisy,
    size,
):
    _width, _height = noisy.size
    _radius = size // 2

    _valid_positions = [
        (_x, _y)
        for _y in range(_radius, _height - _radius)
        for _x in range(_radius, _width - _radius)
    ]

    # Roughly 60 frames sampled over the raster scan.
    _frame_count = min(60, len(_valid_positions))
    _step = 2

    _sampled = [
        (_x, _y)
        for _y in range(_radius, _height - _radius)
        for _x in range(_radius, _width - _radius, _step)
    ]

    for _i in range(_frame_count):
        _index = round(_i * (len(_valid_positions) - 1) / (_frame_count - 1))
        _sampled.append(_valid_positions[_index])

    scale = 4
    panel_w = _width * scale
    panel_h = _height * scale
    gap = 24
    title_h = 30
    footer_h = 40
    canvas_w = 3 * panel_w + 2 * gap
    canvas_h = title_h + panel_h + footer_h

    font = ImageFont.load_default()
    frames = []

    _result_pixels = filtered.load()

    for current_x, current_y in _sampled:
        canvas = Image.new("RGB", (canvas_w, canvas_h), "white")
        draw = ImageDraw.Draw(canvas)

        # Left: noisy image with current filter position.
        left = noisy.resize(
            (panel_w, panel_h),
            Image.Resampling.NEAREST,
        ).convert("RGB")
        canvas.paste(left, (0, title_h))
        draw.text((8, 8), "Noisy image", fill="black", font=font)

        box = (
            (current_x - _radius) * scale,
            title_h + (current_y - _radius) * scale,
            (current_x + _radius + 1) * scale - 1,
            title_h + (current_y + _radius + 1) * scale - 1,
        )
        draw.rectangle(box, outline="red", width=3)

        # Middle: enlarged neighborhood with 0..255 values.
        x_mid = panel_w + gap
        draw.text(
            (x_mid + 8, 8),
            f"{size}x{size} neighborhood",
            fill="black",
            font=font,
        )

        cell = panel_w // size
        _noisy_pixels = noisy.load()
        values = []

        for j in range(size):
            row = []
            for i in range(size):
                px = current_x - _radius + i
                py = current_y - _radius + j
                value = _noisy_pixels[px, py]
                row.append(value)

                x0 = x_mid + i * cell
                y0 = title_h + j * cell
                x1 = x_mid + (i + 1) * cell - 1
                y1 = title_h + (j + 1) * cell - 1
                shade = (value, value, value)
                draw.rectangle((x0, y0, x1, y1), fill=shade, outline="gray")

                label = str(value)
                bbox = draw.textbbox((0, 0), label, font=font)
                tw = bbox[2] - bbox[0]
                th = bbox[3] - bbox[1]
                text_color = "white" if value < 128 else "black"
                draw.text(
                    (x0 + (cell - tw) / 2, y0 + (cell - th) / 2),
                    label,
                    fill=text_color,
                    font=font,
                )
            values.extend(row)

        center = size // 2
        x0 = x_mid + center * cell
        y0 = title_h + center * cell
        x1 = x_mid + (center + 1) * cell - 1
        y1 = title_h + (center + 1) * cell - 1
        draw.rectangle((x0, y0, x1, y1), outline="red", width=3)

        # Right: progressively reveal the filtered image.
        progressive = Image.new("L", (_width, _height), 127)
        progressive_pixels = progressive.load()
        current_index = current_y * _width + current_x

        for _y in range(_radius, _height - _radius):
            for _x in range(_radius, _width - _radius):
                if _y * _width + _x <= current_index:
                    progressive_pixels[_x, _y] = _result_pixels[_x, _y]

        right = progressive.resize(
            (panel_w, panel_h),
            Image.Resampling.NEAREST,
        ).convert("RGB")
        x_right = 2 * (panel_w + gap)
        canvas.paste(right, (x_right, title_h))
        draw.text(
            (x_right + 8, 8),
            f"{filter_type.value} result",
            fill="black",
            font=font,
        )

        input_value = _noisy_pixels[current_x, current_y]
        output_value = _result_pixels[current_x, current_y]

        if filter_type.value == "Min":
            operation = min(values)
        elif filter_type.value == "Max":
            operation = max(values)
        else:
            ordered = sorted(values)
            operation = ordered[len(ordered) // 2]

        footer = (
            f"center = {input_value}     "
            f"{filter_type.value.lower()}(neighborhood) = {operation}     "
            f"output = {output_value}"
        )
        draw.text(
            (8, title_h + panel_h + 13),
            footer,
            fill="black",
            font=font,
        )

        frames.append(canvas)

    buffer = io.BytesIO()
    frames[0].save(
        buffer,
        format="GIF",
        save_all=True,
        append_images=frames[1:],
        duration=160,
        loop=0,
        optimize=False,
    )

    encoded = base64.b64encode(buffer.getvalue()).decode("ascii")
    mo.Html(
        f'''<img src="data:image/gif;base64,{encoded}"
        style="max-width:100%;height:auto;image-rendering:pixelated"
        alt="Salt-and-pepper filtering animation">'''
    )
    return


@app.cell
def _(filter_type, kernel_size, mo):
    if filter_type.value == "Min":
        explanation = f"""
        ### Interpretation

        A **{kernel_size.value}x{kernel_size.value} minimum filter** selects
        the darkest pixel in each neighborhood. Bright salt pixels disappear
        if at least one darker value is present, but dark structures expand.
        """
    elif filter_type.value == "Max":
        explanation = f"""
        ### Interpretation

        A **{kernel_size.value}x{kernel_size.value} maximum filter** selects
        the brightest pixel in each neighborhood. Dark pepper pixels disappear
        if at least one brighter value is present, but bright structures expand.
        """
    else:
        explanation = f"""
        ### Interpretation

        A **{kernel_size.value}x{kernel_size.value} median filter** selects the
        middle value after sorting the neighborhood. It can suppress both salt
        and pepper noise without the directional bias of min/max filters.

        Larger neighborhoods remove larger noise clusters, but also remove
        more fine detail.
        """

    mo.md(explanation)
    return


@app.cell
def _():
    return


if __name__ == "__main__":
    app.run()
