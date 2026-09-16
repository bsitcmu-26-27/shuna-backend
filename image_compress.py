from PIL import Image
from io import BytesIO

MAX_DIMENSION = 1600
WEBP_QUALITY = 75

def compress_image(file_bytes: bytes) -> tuple[bytes, str]:
    img = Image.open(BytesIO(file_bytes))
    img = img.convert("RGB")  # drops alpha/CMYK edge cases, WebP handles RGB cleanly

    if max(img.size) > MAX_DIMENSION:
        img.thumbnail((MAX_DIMENSION, MAX_DIMENSION), Image.LANCZOS)

    out = BytesIO()
    img.save(out, format="WEBP", quality=WEBP_QUALITY)
    return out.getvalue(), "image/webp"