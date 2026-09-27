"""Image preprocessing for the food-analysis pipeline.

Deliberately does NOT re-implement upload validation — that's already
handled by app.core.file_validation.validate_upload_file (magic-byte
signature check, size cap, filename sanitization), which every upload path
in this app should share. This module picks up *after* that validation
has already produced trusted image bytes, and handles what's specific to
feeding an image into a vision LLM: resizing to a sane bound (large phone
photos are wasted tokens/bandwidth for no accuracy gain past a point),
re-compressing to control payload size, and extracting basic metadata for
the audit trail (original dimensions, format, byte size before/after).
"""

import io
from dataclasses import dataclass

from PIL import Image

from app.agents.exceptions import AIOutputValidationError

# Vision models don't benefit from resolutions much beyond this — sending
# a 12MP photo uncompressed just costs latency and provider token spend for
# no meaningful gain in food-recognition accuracy.
MAX_DIMENSION_PX = 1024
JPEG_QUALITY = 85


@dataclass(frozen=True)
class ProcessedImage:
    content: bytes
    mime_type: str
    original_width: int
    original_height: int
    processed_width: int
    processed_height: int
    original_size_bytes: int
    processed_size_bytes: int


def preprocess_image(raw_bytes: bytes) -> ProcessedImage:
    """Resizes (preserving aspect ratio, bounded by MAX_DIMENSION_PX) and
    re-encodes as JPEG for a consistent, compact payload regardless of the
    original format. Raises AIOutputValidationError if the bytes can't be
    decoded as an image at all — this should be unreachable in practice
    since validate_upload_file already confirmed the magic bytes, but a
    corrupted-after-the-header file is still possible, and failing loudly
    here beats a confusing downstream provider error.
    """
    try:
        image = Image.open(io.BytesIO(raw_bytes))
        image.load()
    except Exception as exc:  # Pillow raises several distinct exception types
        raise AIOutputValidationError(f"Could not decode image: {exc}") from exc

    original_width, original_height = image.size

    # Normalize to RGB (drops alpha/CMYK edge cases that JPEG can't encode).
    if image.mode != "RGB":
        image = image.convert("RGB")

    image.thumbnail((MAX_DIMENSION_PX, MAX_DIMENSION_PX), Image.LANCZOS)

    buffer = io.BytesIO()
    image.save(buffer, format="JPEG", quality=JPEG_QUALITY, optimize=True)
    processed_bytes = buffer.getvalue()

    return ProcessedImage(
        content=processed_bytes,
        mime_type="image/jpeg",
        original_width=original_width,
        original_height=original_height,
        processed_width=image.width,
        processed_height=image.height,
        original_size_bytes=len(raw_bytes),
        processed_size_bytes=len(processed_bytes),
    )
