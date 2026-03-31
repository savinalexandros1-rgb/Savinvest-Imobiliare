from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFont
import pypdfium2 as pdfium


PDF_PATH = Path("/Users/alexandrossavin/Downloads/CCF01262021_00001 2.pdf")
OUT_DIR = Path("/Users/alexandrossavin/Documents/1/Savinvest-Imobiliare/marketing/hotel-palace-busteni/plans")

ROTATE_CW = {1, 8, 9, 20, 27, 28, 29}
PAIR_PAGES = [(3, 4), (5, 6), (17, 18), (23, 24), (25, 26), (27, 28)]

FONT = ImageFont.load_default()


def render_page(pdf: pdfium.PdfDocument, page_num: int, scale: float = 3.0) -> Image.Image:
    page = pdf[page_num - 1]
    image = page.render(scale=scale).to_pil().convert("RGB")
    if page_num in ROTATE_CW:
        image = image.rotate(-90, expand=True, fillcolor="white")
    return image


def crop_content(image: Image.Image, margin: int = 36) -> Image.Image:
    gray = np.array(image.convert("L"))
    mask = gray < 245
    row_counts = mask.sum(axis=1)
    col_counts = mask.sum(axis=0)

    row_threshold = max(8, int(image.width * 0.004))
    col_threshold = max(8, int(image.height * 0.004))

    rows = np.where(row_counts > row_threshold)[0]
    cols = np.where(col_counts > col_threshold)[0]

    if len(rows) == 0 or len(cols) == 0:
        return image

    top = max(0, int(rows[0]) - margin)
    bottom = min(image.height, int(rows[-1]) + margin)
    left = max(0, int(cols[0]) - margin)
    right = min(image.width, int(cols[-1]) + margin)
    return image.crop((left, top, right, bottom))


def add_label(image: Image.Image, label: str) -> Image.Image:
    canvas = Image.new("RGB", (image.width, image.height + 48), "white")
    canvas.paste(image, (0, 48))
    draw = ImageDraw.Draw(canvas)
    draw.rectangle((12, 10, 140, 38), fill="black")
    draw.text((24, 18), label, fill="white", font=FONT)
    return canvas


def fit_to_height(image: Image.Image, target_height: int) -> Image.Image:
    ratio = target_height / image.height
    width = max(1, int(image.width * ratio))
    return image.resize((width, target_height), Image.Resampling.LANCZOS)


def build_cleaned_pdf(pdf: pdfium.PdfDocument) -> Path:
    pages = []
    for page_num in range(1, len(pdf) + 1):
        image = render_page(pdf, page_num)
        image = crop_content(image)
        image = add_label(image, f"Page {page_num}")
        pages.append(image.convert("RGB"))

    out_path = OUT_DIR / "hotel_palace_plans_cleaned.pdf"
    pages[0].save(out_path, save_all=True, append_images=pages[1:], resolution=200.0)
    return out_path


def build_pair_spreads(pdf: pdfium.PdfDocument) -> Path:
    spreads = []
    for left_num, right_num in PAIR_PAGES:
        left = add_label(crop_content(render_page(pdf, left_num)), f"Page {left_num}")
        right = add_label(crop_content(render_page(pdf, right_num)), f"Page {right_num}")

        target_height = max(left.height, right.height)
        left = fit_to_height(left, target_height)
        right = fit_to_height(right, target_height)

        gutter = 40
        canvas = Image.new("RGB", (left.width + gutter + right.width, target_height), "white")
        canvas.paste(left, (0, 0))
        canvas.paste(right, (left.width + gutter, 0))
        spreads.append(canvas.convert("RGB"))

    out_path = OUT_DIR / "hotel_palace_plans_paired_spreads.pdf"
    spreads[0].save(out_path, save_all=True, append_images=spreads[1:], resolution=200.0)
    return out_path


def build_pair_contact_sheet(pdf: pdfium.PdfDocument) -> Path:
    thumbs = []
    for left_num, right_num in PAIR_PAGES:
        left = crop_content(render_page(pdf, left_num))
        right = crop_content(render_page(pdf, right_num))

        target_height = max(left.height, right.height)
        left = fit_to_height(left, target_height)
        right = fit_to_height(right, target_height)

        gutter = 30
        spread = Image.new("RGB", (left.width + gutter + right.width, target_height), "white")
        spread.paste(left, (0, 0))
        spread.paste(right, (left.width + gutter, 0))
        spread.thumbnail((1400, 700))

        canvas = Image.new("RGB", (spread.width, spread.height + 52), "white")
        canvas.paste(spread, (0, 52))
        draw = ImageDraw.Draw(canvas)
        draw.rectangle((10, 10, 180, 38), fill="black")
        draw.text((22, 18), f"Pages {left_num} + {right_num}", fill="white", font=FONT)
        thumbs.append(canvas)

    cols = 1
    total_h = sum(img.height for img in thumbs) + (len(thumbs) - 1) * 24
    max_w = max(img.width for img in thumbs)
    sheet = Image.new("RGB", (max_w, total_h), (235, 235, 235))
    y = 0
    for img in thumbs:
        sheet.paste(img, ((max_w - img.width) // 2, y))
        y += img.height + 24

    out_path = OUT_DIR / "hotel_palace_plans_paired_spreads_contact.jpg"
    sheet.save(out_path, quality=92)
    return out_path


def main():
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    pdf = pdfium.PdfDocument(str(PDF_PATH))
    cleaned = build_cleaned_pdf(pdf)
    spreads = build_pair_spreads(pdf)
    contact = build_pair_contact_sheet(pdf)
    print(cleaned)
    print(spreads)
    print(contact)


if __name__ == "__main__":
    main()
