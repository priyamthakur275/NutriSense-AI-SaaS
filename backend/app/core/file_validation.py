"""File upload validation framework.

No upload endpoint exists yet (MealImage currently accepts a pre-uploaded
`storage_path` string, not a file — see app/api/v1/endpoints/meal_images.py
from Phase 4D), but this is the reusable validation layer any future
multipart upload endpoint (tray photo capture, profile pictures, etc.)
should depend on, so every upload path enforces the same rules rather than
each endpoint improvising its own ad-hoc checks.

Validates:
  - declared size vs an actual byte-count cap (never trust Content-Length
    alone — it's client-supplied and can lie)
  - extension AND magic-byte signature both agree on the file type (an
    attacker renaming a .php file to .jpg won't pass — the extension check
    alone is insufficient)
  - filename is sanitized before ever being used to build a storage path
    (blocks path traversal via "../" and null-byte tricks)
"""

import os
import re
import uuid

from fastapi import UploadFile

from app.core.exceptions import ValidationAppError

# Magic-byte signatures for the file types this platform actually needs
# (meal tray photos). Extend deliberately, not by accepting any type the
# client claims — an allow-list, not a deny-list.
_MAGIC_SIGNATURES: dict[str, tuple[bytes, ...]] = {
    "image/jpeg": (b"\xff\xd8\xff",),
    "image/png": (b"\x89PNG\r\n\x1a\n",),
    "image/webp": (b"RIFF",),  # followed by "WEBP" at offset 8; checked separately below
}

_EXTENSION_FOR_CONTENT_TYPE = {
    "image/jpeg": {".jpg", ".jpeg"},
    "image/png": {".png"},
    "image/webp": {".webp"},
}

DEFAULT_MAX_UPLOAD_BYTES = 10 * 1024 * 1024  # 10 MB — generous for a phone photo, not for abuse


def sanitize_filename(filename: str) -> str:
    """Strips directory components and any character that isn't
    alphanumeric/dot/dash/underscore, then prefixes a UUID so two uploads
    can never collide or overwrite each other on disk."""
    base_name = os.path.basename(filename)
    safe_name = re.sub(r"[^A-Za-z0-9._-]", "_", base_name)
    if not safe_name or safe_name in {".", ".."}:
        safe_name = "upload"
    return f"{uuid.uuid4().hex}_{safe_name}"


def _detect_content_type(header_bytes: bytes) -> str | None:
    for content_type, signatures in _MAGIC_SIGNATURES.items():
        for signature in signatures:
            if header_bytes.startswith(signature):
                if content_type == "image/webp":
                    # RIFF is shared by other formats; WEBP is confirmed by
                    # the 4-byte tag at offset 8.
                    if header_bytes[8:12] == b"WEBP":
                        return content_type
                    continue
                return content_type
    return None


async def validate_upload_file(
    file: UploadFile,
    *,
    max_bytes: int = DEFAULT_MAX_UPLOAD_BYTES,
    allowed_content_types: set[str] | None = None,
) -> bytes:
    """Reads, validates, and returns the file's full contents. Raises
    ValidationAppError (-> HTTP 422) on any violation. Call sites should
    use the returned bytes rather than re-reading `file` (the stream has
    already been consumed).
    """
    allowed = allowed_content_types or set(_MAGIC_SIGNATURES.keys())

    contents = await file.read()
    if len(contents) == 0:
        raise ValidationAppError("Uploaded file is empty")
    if len(contents) > max_bytes:
        raise ValidationAppError(
            f"File exceeds the maximum allowed size of {max_bytes // (1024 * 1024)}MB"
        )

    detected_type = _detect_content_type(contents[:16])
    if detected_type is None or detected_type not in allowed:
        raise ValidationAppError(
            "File content does not match an allowed image type (jpeg, png, webp) — "
            "checked by file signature, not just the filename extension"
        )

    declared_extension = os.path.splitext(file.filename or "")[1].lower()
    if declared_extension not in _EXTENSION_FOR_CONTENT_TYPE.get(detected_type, set()):
        raise ValidationAppError(
            "File extension does not match its actual content type "
            f"(detected {detected_type}, filename suggests otherwise)"
        )

    return contents
