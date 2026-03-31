from pathlib import Path
import numpy as np
from PIL import Image, ImageOps, ImageDraw, ImageFont
from moviepy import (
    VideoFileClip,
    AudioFileClip,
    ImageClip,
    ColorClip,
    CompositeVideoClip,
    concatenate_videoclips,
)


ROOT = Path("/Users/alexandrossavin/Documents/1/Savinvest-Imobiliare/marketing/hotel-palace-busteni")
MEDIA = Path("/Users/alexandrossavin/Documents/9 MAI POZE:FILMARI")
MASTER = Path("/Users/alexandrossavin/Downloads/Hotel_Palace_Busteni_SAVINVEST_HQ 2.MP4")
OUT = ROOT / "hotel_palace_busteni_teaser_v1_en.mp4"

W, H = 1920, 1080
FPS = 24

FONT_DISPLAY = "/System/Library/Fonts/Supplemental/Baskerville.ttc"
FONT_SANS = "/System/Library/Fonts/Supplemental/Arial.ttf"
FONT_BOLD = "/System/Library/Fonts/Supplemental/Arial Bold.ttf"


def fit_image(path: Path, size=(W, H)):
    img = Image.open(path).convert("RGB")
    return ImageOps.fit(img, size, method=Image.Resampling.LANCZOS)


def transparent_text_layer(
    headline: str,
    subheadline: str = "",
    kicker: str = "",
    website: str = "savinvestimobiliare.ro",
    center: bool = False,
):
    layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    draw = ImageDraw.Draw(layer)

    font_kicker = ImageFont.truetype(FONT_BOLD, 32)
    font_head = ImageFont.truetype(FONT_DISPLAY, 78)
    font_sub = ImageFont.truetype(FONT_SANS, 38)
    font_site = ImageFont.truetype(FONT_BOLD, 28)

    box_w = 1120 if not center else 1240
    box_h = 330 if subheadline else 250
    x = 100 if not center else (W - box_w) // 2
    y = 650 if not center else 620

    draw.rounded_rectangle((x, y, x + box_w, y + box_h), radius=28, fill=(7, 18, 14, 190))
    inner_x = x + 42
    current_y = y + 32

    if kicker:
        draw.text((inner_x, current_y), kicker.upper(), font=font_kicker, fill=(155, 224, 193, 255))
        current_y += 48

    draw.multiline_text((inner_x, current_y), headline, font=font_head, fill=(255, 255, 255, 255), spacing=6)
    current_y += 118 if "\n" not in headline else 160

    if subheadline:
        draw.multiline_text(
            (inner_x, current_y),
            subheadline,
            font=font_sub,
            fill=(238, 245, 241, 255),
            spacing=8,
        )

    site_w = draw.textlength(website, font=font_site)
    site_x = W - int(site_w) - 56
    site_y = H - 74
    draw.rounded_rectangle((site_x - 18, site_y - 12, site_x + site_w + 18, site_y + 38), radius=20, fill=(7, 18, 14, 178))
    draw.text((site_x, site_y), website, font=font_site, fill=(255, 255, 255, 255))

    return ImageClip(np.array(layer)).with_duration(1)


def segment_from_video(path: Path, start: float, end: float, headline: str, subheadline: str = "", kicker: str = ""):
    clip = VideoFileClip(str(path)).without_audio().subclipped(start, end).resized((W, H))
    overlay = ColorClip((W, H), color=(0, 0, 0), duration=clip.duration).with_opacity(0.12)
    text = transparent_text_layer(headline, subheadline, kicker).with_duration(clip.duration)
    return CompositeVideoClip([clip, overlay, text], size=(W, H))


def segment_from_image(path: Path, duration: float, headline: str, subheadline: str = "", kicker: str = "", center: bool = False):
    img = fit_image(path)
    clip = ImageClip(np.array(img)).with_duration(duration)
    overlay = ColorClip((W, H), color=(0, 0, 0), duration=duration).with_opacity(0.16)
    text = transparent_text_layer(headline, subheadline, kicker, center=center).with_duration(duration)
    return CompositeVideoClip([clip, overlay, text], size=(W, H))


def make_interior_board():
    picks = [
        MEDIA / "Screenshot 2026-03-06 at 02.59.30.png",
        MEDIA / "Screenshot 2026-03-06 at 03.01.53.png",
        MEDIA / "Screenshot 2026-03-06 at 03.03.55.png",
    ]
    canvas = Image.new("RGB", (W, H), (15, 22, 18))
    card_w, card_h = 510, 760
    gap = 36
    start_x = (W - (card_w * 3 + gap * 2)) // 2
    y = 140
    for i, path in enumerate(picks):
        img = Image.open(path).convert("RGB")
        card = ImageOps.fit(img, (card_w, card_h), method=Image.Resampling.LANCZOS)
        x = start_x + i * (card_w + gap)
        canvas.paste(card, (x, y))
    return canvas


def segment_interior_board(duration: float):
    img = make_interior_board()
    clip = ImageClip(np.array(img)).with_duration(duration)
    overlay = ColorClip((W, H), color=(0, 0, 0), duration=duration).with_opacity(0.08)
    text = transparent_text_layer(
        "Strong visual presence\nfrom every approach",
        "Multiple aerial perspectives help communicate scale, frontage and the building's rare position in central Busteni.",
        "Presence",
    ).with_duration(duration)
    return CompositeVideoClip([clip, overlay, text], size=(W, H))


def main():
    segments = [
        segment_from_video(
            MEDIA / "3 DA.MP4",
            3.0,
            8.2,
            "Hotel Palace Busteni",
            "Former Casino & Spa Establishment in one of Romania's strongest mountain resort corridors.",
            "Prahova Valley",
        ),
        segment_from_video(
            MEDIA / "4 da.MP4",
            3.0,
            8.0,
            "Founded in 1907",
            "A historic landmark-scale building with immediate visual presence and redevelopment appeal.",
            "Heritage Story",
        ),
        segment_from_video(
            MEDIA / "7 da.MP4",
            4.0,
            9.0,
            "Approx. 7,700 sqm built area",
            "Approx. 4,300 sqm land plot in Busteni, at the foot of the Bucegi Mountains.",
            "Scale",
        ),
        segment_from_image(
            MEDIA / "2.png",
            4.4,
            "Private property",
            "Flexible redevelopment potential without the constraints typically associated with heritage-listed assets.",
            "Positioning",
        ),
        segment_from_video(
            MEDIA / "DJI_0017.MP4",
            4.0,
            9.0,
            "Conversion-ready concept",
            "Boutique hotel, wellness retreat, medical destination or events-led hospitality asset.",
            "Opportunity",
        ),
        segment_interior_board(5.0),
        segment_from_video(
            MEDIA / "6 da.MP4",
            6.0,
            11.0,
            "Strategic mountain location",
            "Approx. 135 km from Bucharest and approx. 55 km from Brasov-Ghimbav International Airport.",
            "Access",
        ),
        segment_from_image(
            MEDIA / "1.png",
            4.6,
            "Year-round destination demand",
            "Busteni combines mountain tourism, ski access, hiking routes and fast access from Bucharest.",
            "Market Context",
        ),
        segment_from_image(
            MEDIA / "5.png",
            6.0,
            "Asking price: EUR 1,550,000",
            "Investment memorandum and private viewings available on request.\nVisit savinvestimobiliare.ro",
            "Call To Action",
            center=True,
        ),
    ]

    final = concatenate_videoclips(segments, method="compose")

    master_audio = VideoFileClip(str(MASTER)).audio
    if master_audio is not None:
        final = final.with_audio(master_audio.subclipped(0, final.duration).with_volume_scaled(0.9))

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
