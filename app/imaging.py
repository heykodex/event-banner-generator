from datetime import datetime

from PIL import Image, ImageDraw, ImageFont


def ordinal(n: int) -> str:
    if 11 <= (n % 100) <= 13:
        suffix = "TH"
    else:
        suffix = {1: "ST", 2: "ND", 3: "RD"}.get(n % 10, "TH")
    return f"{n}{suffix}"


def format_date_range(start_str: str, end_str: str) -> str:
    start = datetime.strptime(start_str, "%Y-%m-%d")
    end = datetime.strptime(end_str, "%Y-%m-%d")

    start_part = f"{start.strftime('%B').upper()} {ordinal(start.day)}"
    end_part = f"{end.strftime('%B').upper()} {ordinal(end.day)}"

    if start.date() == end.date():
        return start_part

    return f"{start_part} \u2013 {end_part}"


def fit_font(draw, text, max_width, start_size, min_size, font_path):
    size = start_size
    while size > min_size:
        font = ImageFont.truetype(font_path, size)
        bbox = draw.textbbox((0, 0), text, font=font)
        width = bbox[2] - bbox[0]
        if width <= max_width:
            return font
        size -= 2
    return ImageFont.truetype(font_path, min_size)


def generate_banner_image(banner_path: str, font_path: str, title: str, displayed_date: str) -> Image.Image:
    """Render a banner using whichever background image is passed in.

    banner_path may be the shared default banner or a user's uploaded
    custom banner -- the caller resolves which one applies.
    """
    base = Image.open(banner_path).convert("RGB")
    img = base.copy()
    draw = ImageDraw.Draw(img)

    W, H = img.size
    max_text_width = int(W * 0.85)

    title = (title or "").strip().upper()
    displayed_date = (displayed_date or "").strip()

    # Title: large, shrinks to fit width
    title_font = fit_font(draw, title if title else " ", max_text_width, 96, 28, font_path)
    title_bbox = draw.textbbox((0, 0), title, font=title_font)
    title_w = title_bbox[2] - title_bbox[0]
    title_h = title_bbox[3] - title_bbox[1]

    # Date: smaller, fixed-ish size but also shrinks if needed
    date_font = fit_font(draw, displayed_date if displayed_date else " ", max_text_width, 40, 18, font_path)
    date_bbox = draw.textbbox((0, 0), displayed_date, font=date_font)
    date_w = date_bbox[2] - date_bbox[0]
    date_h = date_bbox[3] - date_bbox[1]

    gap = int(H * 0.03)
    block_h = title_h + gap + date_h
    start_y = (H - block_h) // 2

    title_x = (W - title_w) // 2 - title_bbox[0]
    title_y = start_y - title_bbox[1]
    draw.text((title_x, title_y), title, font=title_font, fill=(255, 255, 255))

    date_x = (W - date_w) // 2 - date_bbox[0]
    date_y = start_y + title_h + gap - date_bbox[1]
    draw.text((date_x, date_y), displayed_date, font=date_font, fill=(230, 230, 230))

    return img
