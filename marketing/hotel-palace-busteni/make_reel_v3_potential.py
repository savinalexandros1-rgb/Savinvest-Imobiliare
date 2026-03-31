from pathlib import Path
import numpy as np
from PIL import Image, ImageOps, ImageDraw, ImageFont
from moviepy import (
    VideoFileClip,
    ImageClip,
    ColorClip,
    CompositeVideoClip,
    concatenate_videoclips,
)


ROOT = Path("/Users/alexandrossavin/Documents/1/Savinvest-Imobiliare/marketing/hotel-palace-busteni")
MEDIA = Path("/Users/alexandrossavin/Documents/9 MAI POZE:FILMARI")
INTERIORS = ROOT / "interiors-copy"
MASTER = Path("/Users/alexandrossavin/Downloads/Hotel_Palace_Busteni_SAVINVEST_HQ 2.MP4")
OUT = ROOT / "hotel_palace_busteni_reel_v3_potential_en.mp4"

W, H = 1080, 1920
FPS = 24

FONT_DISPLAY = "/System/Library/Fonts/Supplemental/Baskerville.ttc"
FONT_SANS = "/System/Library/Fonts/Supplemental/Arial.ttf"
FONT_BOLD = "/System/Library/Fonts/Supplemental/Arial Bold.ttf"


def text_layer(headline: str, subheadline: str = "", kicker: str = "", website: str = "savinvestimobiliare.ro"):
    layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    draw = ImageDraw.Draw(layer)

    font_kicker = ImageFont.truetype(FONT_BOLD, 36)
    font_head = ImageFont.truetype(FONT_DISPLAY, 88)
    font_sub = ImageFont.truetype(FONT_SANS, 38)
    font_site = ImageFont.truetype(FONT_BOLD, 28)

    box_x = 74
    box_y = 1210
    box_w = W - 148
    box_h = 430 if subheadline else 300

    draw.rounded_rectangle(
        (box_x, box_y, box_x + box_w, box_y + box_h),
        radius=32,
        fill=(7, 18, 14, 198),
    )

    cursor_y = box_y + 34
    text_x = box_x + 40

    if kicker:
        draw.text((text_x, cursor_y), kicker.upper(), font=font_kicker, fill=(155, 224, 193, 255))
        cursor_y += 50

    draw.multiline_text((text_x, cursor_y), headline, font=font_head, fill=(255, 255, 255, 255), spacing=8)
    cursor_y += 180 if "\n" not in headline else 240

    if subheadline:
        draw.multiline_text(
            (text_x, cursor_y),
            subheadline,
            font=font_sub,
            fill=(240, 245, 242, 255),
            spacing=10,
        )

    pill_w = draw.textlength(website, font=font_site)
    site_x = (W - int(pill_w)) // 2
    site_y = H - 94
    draw.rounded_rectangle(
        (site_x - 22, site_y - 16, site_x + pill_w + 22, site_y + 36),
        radius=22,
        fill=(7, 18, 14, 210),
    )
    draw.text((site_x, site_y), website, font=font_site, fill=(255, 255, 255, 255))

    return ImageClip(np.array(layer)).with_duration(1)


def vertical_video_segment(
    path: Path,
    start: float,
    end: float,
    headline: str,
    subheadline: str = "",
    kicker: str = "",
    x_center: float | None = None,
):
    base = VideoFileClip(str(path)).without_audio().subclipped(start, end).resized(height=H)
    if x_center is None:
        x_center = base.w / 2
    clip = base.cropped(x_center=x_center, y_center=H / 2, width=W, height=H)
    overlay = ColorClip((W, H), color=(0, 0, 0), duration=clip.duration).with_opacity(0.12)
    text = text_layer(headline, subheadline, kicker).with_duration(clip.duration)
    return CompositeVideoClip([clip, overlay, text], size=(W, H))


def vertical_image_segment(path: Path, duration: float, headline: str, subheadline: str = "", kicker: str = ""):
    image = Image.open(path).convert("RGB")
    image = ImageOps.fit(image, (W, H), method=Image.Resampling.LANCZOS)
    clip = ImageClip(np.array(image)).with_duration(duration)
    overlay = ColorClip((W, H), color=(0, 0, 0), duration=duration).with_opacity(0.14)
    text = text_layer(headline, subheadline, kicker).with_duration(duration)
    return CompositeVideoClip([clip, overlay, text], size=(W, H))


def closing_card(duration: float):
    bg = VideoFileClip(str(MEDIA / "7 da.MP4")).without_audio().subclipped(8.5, 12.0).resized(height=H)
    bg = bg.cropped(x_center=bg.w / 2, y_center=H / 2, width=W, height=H)
    overlay = ColorClip((W, H), color=(0, 0, 0), duration=duration).with_opacity(0.24)
    text = text_layer(
        "Boutique hotel,\nwellness or events",
        "Private property with flexible repositioning potential. Full memorandum available on request.",
        "Use Cases",
    ).with_duration(duration)
    return CompositeVideoClip([bg.with_duration(duration), overlay, text], size=(W, H))


def main():
    segments = [
        vertical_video_segment(
            MEDIA / "4 da.MP4",
            3.2,
            6.8,
            "Historic scale and\narchitectural identity",
            "A building with immediate presence, suitable for destination-led redevelopment.",
            "Asset",
        ),
        vertical_image_segment(
            INTERIORS / "7.jpeg",
            3.6,
            "Distinctive internal\nvolume",
            "The structure offers memorable arrival and circulation moments for a future concept.",
            "Interior",
        ),
        vertical_image_segment(
            INTERIORS / "WhatsApp Image 2026-02-11 at 14.33.50.jpeg",
            3.6,
            "Character-rich\nrestoration story",
            "Historic fabric and visible scale can support a strong repositioning narrative.",
            "Story",
        ),
        vertical_image_segment(
            INTERIORS / "WhatsApp Image 2026-02-11 at 14.33.54.jpeg",
            3.6,
            "Strong frontage and\nmountain backdrop",
            "A rare visual combination for hospitality, wellness or branded experiential use.",
            "Presence",
        ),
        vertical_video_segment(
            MEDIA / "7 da.MP4",
            8.8,
            12.3,
            "Approx. 7,700 sqm\nbuilt area",
            "Approx. 4,300 sqm land plot with ample room for a clear business case.",
            "Scale",
        ),
        closing_card(4.0),
    ]

    final = concatenate_videoclips(segments, method="compose")

    master_audio = VideoFileClip(str(MASTER)).audio
    if master_audio is not None:
        final = final.with_audio(master_audio.subclipped(0, final.duration).with_volume_scaled(0.92))

    final.write_videofile(
        str(OUT),
        fps=FPS,
        codec="libx264",
        audio_codec="aac",
        preset="medium",
        threads=4,
    )

    for clip in segments:
        clip.close()
    final.close()


if __name__ == "__main__":
    main()
