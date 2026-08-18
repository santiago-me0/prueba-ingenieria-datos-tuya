"""Image-to-Base64 encoding utilities."""

import base64
import mimetypes
from pathlib import Path
from urllib.parse import unquote, urlsplit


class ImageEncoder:
    """Convert local image references into Base64 data URIs."""

    def encode(
        self,
        image_source: str,
        html_path: Path,
    ) -> str:
        """
        Encode an image referenced by an HTML file.

        Relative paths are resolved from the directory that
        contains the HTML document.
        """

        if not image_source:
            raise ValueError("Image source cannot be empty.")

        # If the image is already embedded, no work is required.
        if image_source.startswith("data:"):
            return image_source

        parsed_source = urlsplit(image_source)

        if parsed_source.scheme not in {"", "file"}:
            raise ValueError(
                "Only local image sources are supported. "
                f"Received scheme: {parsed_source.scheme!r}"
            )

        image_path = self._resolve_path(
            parsed_source.path,
            html_path,
        )

        if not image_path.exists():
            raise FileNotFoundError(
                f"Image not found: {image_path}"
            )

        if not image_path.is_file():
            raise ValueError(
                f"Image source is not a file: {image_path}"
            )

        mime_type, _ = mimetypes.guess_type(image_path.name)

        if mime_type is None or not mime_type.startswith("image/"):
            raise ValueError(
                f"Unable to determine image MIME type: {image_path}"
            )

        image_bytes = image_path.read_bytes()

        encoded = base64.b64encode(
            image_bytes
        ).decode("ascii")

        return (
            f"data:{mime_type};base64,"
            f"{encoded}"
        )

    @staticmethod
    def _resolve_path(
        source_path: str,
        html_path: Path,
    ) -> Path:
        """Resolve an image source relative to the HTML file."""

        decoded_path = unquote(source_path)
        path = Path(decoded_path)

        if path.is_absolute():
            return path.resolve()

        return (
            html_path.parent
            / path
        ).resolve()