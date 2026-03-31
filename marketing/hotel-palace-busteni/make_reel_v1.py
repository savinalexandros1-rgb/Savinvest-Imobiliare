from pathlib import Path
import numpy as np
from PIL import Image, ImageDraw, ImageFont
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
OUT = ROOT / "hotel_palace_busteni_reel_v1_en.mp4"

W, H = 1080, 1920
FPS = 24

FONT_DISPLAY = "/System/Library/Fonts/Supplemental/Baskerville.ttc"
FONT_SANS = "/System/Library/Fonts/Supplemental/Arial.ttf"
FONT_BOLD = "/System/Library/Fonts/Supplemental/Arial Bold.ttf"


def text_layer(headline: str, subheadline: str = "", kicker: str = "", website: str = "savinvestimobiliare.ro"):
    layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    draw = ImageDraw.Draw(layer)

    font_kicker = ImageFont.truetype(FONT_BOLD, 36)
    font_head = ImageFont.truetype(FONT_DISPLAY, 92)
    font_sub = ImageFont.truetype(FONT_SANS, 38)
    font_site = ImageFont.truetype(FONT_BOLD, 28)

    box_x = 74
    box_y = 1210
    box_w = W - 148
    box_h = 440 if subheadline else 320

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


def closing_card(duration: float):
    bg = VideoFileClip(str(MEDIA / "7 da.MP4")).without_audio().subclipped(8.2, 11.8).resized(height=H)
    bg = bg.cropped(x_center=bg.w / 2, y_center=H / 2, width=W, height=H)
    overlay = ColorClip((W, H), color=(0, 0, 0), duration=duration).with_opacity(0.24)
    text = text_layer(
        "EUR 1,550,000",
        "Private property. Investment memorandum and viewings available on request.",
        "Call to Action",
    ).with_duration(duration)
    return CompositeVideoClip([bg.with_duration(duration), overlay, text], size=(W, H))


def main():
    segments = [
        vertical_video_segment(
            MEDIA / "3 DA.MP4",
            3.2,
            6.8,
            "Historic mountain\ninvestment opportunity",
            "A rare large-scale asset in Busteni, Romania.",
            "Romania",
        ),
        vertical_video_segment(
            MEDIA / "4 da.MP4",
            3.2,
            6.7,
            "Hotel Palace\nBusteni",
            "Former Casino & Spa Establishment founded in 1907.",
            "Identity",
        ),
        vertical_video_segment(
            MEDIA / "7 da.MP4",
            4.0,
            7.6,
            "Approx. 7,700 sqm\nbuilt area",
            "Landmark-scale volume with strong redevelopment potential.",
            "Scale",
        ),
        vertical_video_segment(
            MEDIA / "DJI_0017.MP4",
            4.2,
            7.9,
            "Approx. 4,300 sqm\nland plot",
            "Prominent frontage and immediate visual presence.",
            "Footprint",
        ),
        vertical_video_segment(
            MEDIA / "4 da.MP4",
            9.0,
            12.5,
            "Boutique hotel,\nwellness or events",
            "Flexible repositioning potential in a year-round destination.",
            "Potential",
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
