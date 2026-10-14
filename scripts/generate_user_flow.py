"""Create a user-journey GIF from real DOF-RAG interface screenshots."""

from __future__ import annotations

import argparse
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont, ImageOps

WIDTH, HEIGHT = 1000, 780
APP_BOX = (30, 88, 970, 675)
APP_SIZE = (APP_BOX[2] - APP_BOX[0], APP_BOX[3] - APP_BOX[1])
FONT_ROOT = Path("C:/Windows/Fonts")
BACKGROUND = "#081321"
PANEL = "#0d1a2b"
WHITE = "#f2f7fb"
MUTED = "#a8b9ca"
TEAL = "#53e1c0"

STEPS = (
    ("Sign in", "Enter the workspace through the Spanish-language login screen."),
    ("Open the archive", "Check the local DOF edition and available pages."),
    ("Get a cited answer", "Read the answer with document and page references."),
    ("Choose a document", "Browse available local editions and summaries."),
    ("Review the overview", "Read a concise view generated from selected excerpts."),
)
CAPTURE_NAMES = (
    "01-login.png",
    "02-home.png",
    "03-query-answer.png",
    "04-summary-list.png",
    "05-summary-open.png",
)


def load_font(size: int, *, bold: bool = False) -> ImageFont.FreeTypeFont | ImageFont.ImageFont:
    filename = "seguisb.ttf" if bold else "segoeui.ttf"
    try:
        return ImageFont.truetype(str(FONT_ROOT / filename), size)
    except OSError:
        return ImageFont.load_default()


def app_screenshot(path: Path) -> Image.Image:
    screenshot = Image.open(path).convert("RGB")
    if screenshot.width > 1200:
        screenshot = screenshot.crop((0, 0, screenshot.width - 12, screenshot.height))
    return ImageOps.fit(
        screenshot,
        APP_SIZE,
        method=Image.Resampling.LANCZOS,
        centering=(0.5, 0.5),
    )


def rounded_mask(size: tuple[int, int], radius: int) -> Image.Image:
    mask = Image.new("L", size, 0)
    ImageDraw.Draw(mask).rounded_rectangle(
        (0, 0, size[0] - 1, size[1] - 1), radius=radius, fill=255
    )
    return mask


def wrap_text(draw: ImageDraw.ImageDraw, text: str, font: ImageFont.ImageFont, width: int) -> list[str]:
    lines: list[str] = []
    line = ""
    for word in text.split():
        candidate = f"{line} {word}".strip()
        if line and draw.textbbox((0, 0), candidate, font=font)[2] > width:
            lines.append(line)
            line = word
        else:
            line = candidate
    if line:
        lines.append(line)
    return lines


def compose_frame(screenshot: Image.Image, step_index: int) -> Image.Image:
    image = Image.new("RGB", (WIDTH, HEIGHT), BACKGROUND)
    draw = ImageDraw.Draw(image)
    draw.ellipse((780, -330, 1230, 120), fill="#0b2330")
    draw.ellipse((-260, 570, 190, 1020), fill="#10182d")

    draw.text((32, 18), "DOF-RAG  /  USER JOURNEY", font=load_font(13, bold=True), fill=TEAL)
    draw.text((32, 41), "From a question to its source", font=load_font(23, bold=True), fill=WHITE)
    draw.text((915, 27), f"{step_index + 1:02d} / {len(STEPS):02d}", font=load_font(14, bold=True), fill=MUTED, anchor="ra")

    left, top, right, bottom = APP_BOX
    shadow = Image.new("RGBA", (WIDTH, HEIGHT), (0, 0, 0, 0))
    shadow_draw = ImageDraw.Draw(shadow)
    shadow_draw.rounded_rectangle((left, top + 5, right, bottom + 5), radius=14, fill=(0, 0, 0, 130))
    image = Image.alpha_composite(image.convert("RGBA"), shadow).convert("RGB")
    screenshot = screenshot.resize(APP_SIZE, Image.Resampling.LANCZOS)
    image.paste(screenshot, (left, top), rounded_mask(APP_SIZE, 12))
    ImageDraw.Draw(image).rounded_rectangle(
        APP_BOX, radius=12, outline="#26394e", width=1
    )

    number_font = load_font(22, bold=True)
    title_font = load_font(16, bold=True)
    subtitle_font = load_font(12)
    title, subtitle = STEPS[step_index]
    draw = ImageDraw.Draw(image)
    draw.text((32, 694), f"{step_index + 1:02d}", font=number_font, fill=TEAL)
    draw.text((84, 692), title.upper(), font=title_font, fill=WHITE)
    lines = wrap_text(draw, subtitle, subtitle_font, 820)
    for index, line in enumerate(lines[:2]):
        draw.text((84, 716 + index * 16), line, font=subtitle_font, fill=MUTED)

    rail_y = 760
    rail_start, rail_end = 84, 916
    draw.line((rail_start, rail_y, rail_end, rail_y), fill="#304258", width=2)
    spacing = (rail_end - rail_start) / (len(STEPS) - 1)
    for index in range(len(STEPS)):
        x = round(rail_start + index * spacing)
        color = TEAL if index == step_index else "#607286" if index < step_index else "#304258"
        radius = 5 if index == step_index else 3
        draw.ellipse((x - radius, rail_y - radius, x + radius, rail_y + radius), fill=color)
    return image


def make_gif(capture_dir: Path, output: Path) -> None:
    missing = [capture_dir / name for name in CAPTURE_NAMES if not (capture_dir / name).is_file()]
    if missing:
        raise FileNotFoundError("Missing app screenshots: " + ", ".join(map(str, missing)))

    frames = [
        compose_frame(app_screenshot(capture_dir / filename), index)
        for index, filename in enumerate(CAPTURE_NAMES)
    ]

    animation: list[Image.Image] = []
    hold_frames = 10
    transition_frames = 3
    for index, frame in enumerate(frames):
        animation.extend([frame] * hold_frames)
        next_frame = frames[(index + 1) % len(frames)]
        for transition in range(1, transition_frames + 1):
            animation.append(
                Image.blend(frame, next_frame, transition / (transition_frames + 1))
            )

    palette = animation[0].quantize(colors=192, method=Image.Quantize.MEDIANCUT)
    paletted = [frame.quantize(palette=palette, dither=Image.Dither.NONE) for frame in animation]
    output.parent.mkdir(parents=True, exist_ok=True)
    paletted[0].save(
        output,
        save_all=True,
        append_images=paletted[1:],
        duration=110,
        loop=0,
        optimize=True,
        disposal=2,
    )
    print(f"Saved {output}: {WIDTH}x{HEIGHT}, {len(paletted)} frames.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--captures", type=Path, default=Path("docs/user-flow"))
    parser.add_argument("--output", type=Path, default=Path("docs/system-flow.gif"))
    arguments = parser.parse_args()
    make_gif(arguments.captures, arguments.output)
