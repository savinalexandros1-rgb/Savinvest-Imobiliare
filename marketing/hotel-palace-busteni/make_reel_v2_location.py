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
MASTER = Path("/Users/alexandrossavin/Downloads/Hotel_Palace_Busteni_SAVINVEST_HQ 2.MP4")
OUT = ROOT / "hotel_palace_busteni_reel_v2_location_en.mp4"

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
    box_h = 420 if subheadline else 300

    draw.rounded_rectangle(
        (box_x, box_y, box_x + box_w, box_y + box_h),
        radius=32,
        fill=(7, 18, 14, 196),
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
    overlay = ColorClip((W, H), color=(0, 0, 0), duration=duration).with_opacity(0.15)
    text = text_layer(headline, subheadline, kicker).with_duration(duration)
    return CompositeVideoClip([clip, overlay, text], size=(W, H))


def closing_card(duration: float):
    bg = Image.open(MEDIA / "5.png").convert("RGB")
    bg = ImageOps.fit(bg, (W, H), method=Image.Resampling.LANCZOS)
    clip = ImageClip(np.array(bg)).with_duration(duration)
    overlay = ColorClip((W, H), color=(0, 0, 0), duration=duration).with_opacity(0.22)
    text = text_layer(
        "Mountain resort access",
        "Approx. 135 km from Bucharest and approx. 55 km from Brasov-Ghimbav International Airport.",
        "Access",
    ).with_duration(duration)
    return CompositeVideoClip([clip, overlay, text], size=(W, H))


def main():
    segments = [
        vertical_video_segment(
            MEDIA / "3 DA.MP4",
            3.5,
            7.2,
            "Bucegi Mountains\nsetting",
            "A rare historic asset in one of Romania's strongest mountain resort corridors.",
            "Destination",
        ),
        vertical_video_segment(
            MEDIA / "6 da.MP4",
            6.8,
            10.5,
            "Year-round\ndestination demand",
            "Ski access, hiking routes and sustained mountain tourism across all seasons.",
            "Demand",
        ),
        vertical_image_segment(
            MEDIA / "1.png",
            3.6,
            "Approx. 135 km\nfrom Bucharest",
            "Fast road access makes the property reachable for leisure, medical and event-driven demand.",
            "Capital Access",
        ),
        vertical_image_segment(
            MEDIA / "6.png",
            3.6,
            "Approx. 55 km to\nBrasov airport",
            "Improved international accessibility strengthens the long-term hospitality case.",
            "International Reach",
        ),
        vertical_video_segment(
            MEDIA / "3 DA.MP4",
            8.4,
            12.0,
            "Near Cantacuzino Castle\nand Sinaia corridor",
            "An established premium tourism zone with strong brand recognition.",
            "Context",
        ),
        closing_card(3.8),
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
