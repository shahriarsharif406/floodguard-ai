import io
import pytest
from PIL import Image
from floodguard.imaging import ImageRejected, ahash, hamming, validate_and_clean


def _img(size=(300, 200), fmt="JPEG", exif=False):
    im = Image.new("RGB", size, (30, 90, 160))
    for x in range(0, size[0], 20):
        for y in range(0, size[1], 20):
            if (x + y) % 40 == 0:
                im.paste((220, 200, 120), (x, y, x + 10, y + 10))
    b = io.BytesIO()
    if exif:
        e = Image.Exif(); e[0x010F] = "TestCam"
        im.save(b, fmt, exif=e)
    else:
        im.save(b, fmt)
    return b.getvalue()


def test_rejects_bad_inputs():
    with pytest.raises(ImageRejected): validate_and_clean(b"", "a.jpg")
    with pytest.raises(ImageRejected): validate_and_clean(b"GIF89a....", "a.jpg")
    with pytest.raises(ImageRejected): validate_and_clean(b"x" * (5 * 1024 * 1024 + 1), "a.jpg")
    with pytest.raises(ImageRejected): validate_and_clean(_img(), "a.gif")


def test_exif_stripped():
    out, _ = validate_and_clean(_img(exif=True), "a.jpg")
    assert len(Image.open(io.BytesIO(out)).getexif()) == 0


def test_ahash_robust_to_resize():
    raw = _img((400, 300))
    h1 = ahash(Image.open(io.BytesIO(raw)))
    h2 = ahash(Image.open(io.BytesIO(raw)).resize((200, 150)))
    assert hamming(h1, h2) <= 5
