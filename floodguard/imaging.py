from __future__ import annotations
import io
from PIL import Image, ImageOps

MAX_BYTES = 5 * 1024 * 1024
MAX_PIXELS = 40_000_000
Image.MAX_IMAGE_PIXELS = MAX_PIXELS


class ImageRejected(Exception):
    pass


def ahash(img: Image.Image) -> str:
    g = img.convert("L").resize((8, 8), Image.LANCZOS)
    px = list(g.get_flattened_data()) if hasattr(g, "get_flattened_data") else list(g.getdata())
    avg = sum(px) / 64.0
    bits = "".join("1" if p >= avg else "0" for p in px)
    return f"{int(bits, 2):016x}"


def hamming(h1: str, h2: str) -> int:
    return bin(int(h1, 16) ^ int(h2, 16)).count("1")


def validate_and_clean(raw: bytes, filename: str) -> tuple[bytes, str]:
    if not raw:
        raise ImageRejected("Empty file.")
    if len(raw) > MAX_BYTES:
        raise ImageRejected("Image is larger than 5 MB.")
    if not filename.lower().endswith((".png", ".jpg", ".jpeg")):
        raise ImageRejected("Only PNG or JPG images are accepted.")
    try:
        probe = Image.open(io.BytesIO(raw))
        probe.verify()
        img = Image.open(io.BytesIO(raw))
        if img.format not in ("PNG", "JPEG"):
            raise ImageRejected("File content is not a PNG or JPG image.")
        if img.width * img.height > MAX_PIXELS:
            raise ImageRejected("Image resolution is too large.")
        img = ImageOps.exif_transpose(img)
        img = img.convert("RGB")
    except ImageRejected:
        raise
    except Exception as e:  # noqa: BLE001
        raise ImageRejected("Could not read this image.") from e
    img.thumbnail((1600, 1600))
    h = ahash(img)
    out = io.BytesIO()
    img.save(out, format="JPEG", quality=85)   # re-encode drops EXIF/GPS
    return out.getvalue(), h
