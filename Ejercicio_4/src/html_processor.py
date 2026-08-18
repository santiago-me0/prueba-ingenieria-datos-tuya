"""HTML image embedding utilities."""

from dataclasses import dataclass, field
from html import escape
from html.parser import HTMLParser
from pathlib import Path

from Ejercicio_4.src.image_encoder import ImageEncoder


@dataclass
class ProcessingReport:
    """Store successful and failed image processing results."""

    success: dict[str, list[str]] = field(default_factory=dict)
    fail: dict[str, list[dict[str, str]]] = field(default_factory=dict)

    def add_success(
        self,
        html_path: Path,
        image_source: str,
    ) -> None:
        """Register a successfully processed image."""

        key = str(html_path)

        self.success.setdefault(
            key,
            [],
        ).append(image_source)

    def add_failure(
        self,
        html_path: Path,
        image_source: str,
        error: str,
    ) -> None:
        """Register an image that could not be processed."""

        key = str(html_path)

        self.fail.setdefault(
            key,
            [],
        ).append(
            {
                "src": image_source,
                "error": error,
            }
        )

    def to_dict(self) -> dict:
        """Return the report using the required structure."""

        return {
            "success": self.success,
            "fail": self.fail,
        }


class ImageTagParser(HTMLParser):
    """
    Locate image tags and prepare replacements.

    The parser records the exact position of each <img> tag
    inside the original document. Only those tags are replaced,
    leaving the rest of the HTML untouched.
    """

    def __init__(
        self,
        html_content: str,
        html_path: Path,
        encoder: ImageEncoder,
        report: ProcessingReport,
    ) -> None:
        super().__init__(convert_charrefs=False)

        self.html_content = html_content
        self.html_path = html_path
        self.encoder = encoder
        self.report = report

        self.replacements: list[
            tuple[int, int, str]
        ] = []

        self.line_offsets = self._build_line_offsets(
            html_content
        )

    @staticmethod
    def _build_line_offsets(content: str) -> list[int]:
        """Return the absolute offset where each line starts."""

        offsets = [0]

        for index, character in enumerate(content):
            if character == "\n":
                offsets.append(index + 1)

        return offsets

    def _absolute_position(self) -> int:
        """Convert HTMLParser line/column coordinates to index."""

        line_number, column = self.getpos()

        return (
            self.line_offsets[line_number - 1]
            + column
        )

    def handle_starttag(
        self,
        tag: str,
        attrs: list[tuple[str, str | None]],
    ) -> None:
        """Process normal <img> start tags."""

        if tag.lower() != "img":
            return

        self._process_image_tag(
            attrs=attrs,
            self_closing=False,
        )

    def handle_startendtag(
        self,
        tag: str,
        attrs: list[tuple[str, str | None]],
    ) -> None:
        """Process self-closing <img /> tags."""

        if tag.lower() != "img":
            return

        self._process_image_tag(
            attrs=attrs,
            self_closing=True,
        )

    def _process_image_tag(
        self,
        attrs: list[tuple[str, str | None]],
        self_closing: bool,
    ) -> None:
        """Encode the src attribute and record tag replacement."""

        raw_tag = self.get_starttag_text()

        if raw_tag is None:
            return

        start = self._absolute_position()
        end = start + len(raw_tag)

        new_attrs = []
        source_found = False

        for name, value in attrs:
            if name.lower() == "src":
                source_found = True

                source = value or ""

                try:
                    value = self.encoder.encode(
                        image_source=source,
                        html_path=self.html_path,
                    )

                    self.report.add_success(
                        self.html_path,
                        source,
                    )

                except (
                    FileNotFoundError,
                    OSError,
                    ValueError,
                ) as exc:
                    self.report.add_failure(
                        self.html_path,
                        source,
                        str(exc),
                    )

            new_attrs.append(
                (name, value)
            )

        if not source_found:
            self.report.add_failure(
                self.html_path,
                "",
                "Image tag does not contain a src attribute.",
            )

        new_tag = self._build_tag(
            attrs=new_attrs,
            self_closing=self_closing,
        )

        self.replacements.append(
            (
                start,
                end,
                new_tag,
            )
        )

    @staticmethod
    def _build_tag(
        attrs: list[tuple[str, str | None]],
        self_closing: bool,
    ) -> str:
        """Build a new img tag from parsed attributes."""

        rendered_attrs = []

        for name, value in attrs:
            if value is None:
                rendered_attrs.append(name)
            else:
                rendered_attrs.append(
                    f'{name}="{escape(value, quote=True)}"'
                )

        attributes = " ".join(rendered_attrs)

        if attributes:
            attributes = f" {attributes}"

        closing = " /" if self_closing else ""

        return f"<img{attributes}{closing}>"

    def render(self) -> str:
        """Apply all recorded replacements to the original HTML."""

        result = self.html_content

        for start, end, replacement in reversed(
            self.replacements
        ):
            result = (
                result[:start]
                + replacement
                + result[end:]
            )

        return result


class HtmlProcessor:
    """Process all images referenced by an HTML file."""

    def __init__(
        self,
        encoder: ImageEncoder | None = None,
        output_suffix: str = "_base64",
    ) -> None:
        self.encoder = encoder or ImageEncoder()
        self.output_suffix = output_suffix

    def process(
        self,
        html_path: Path,
        report: ProcessingReport,
    ) -> Path:
        """
        Process an HTML file without modifying the original.

        Returns the path of the generated HTML document.
        """

        html_path = html_path.resolve()

        content = html_path.read_text(
            encoding="utf-8"
        )

        parser = ImageTagParser(
            html_content=content,
            html_path=html_path,
            encoder=self.encoder,
            report=report,
        )

        parser.feed(content)
        parser.close()

        processed_content = parser.render()

        output_path = html_path.with_name(
            f"{html_path.stem}"
            f"{self.output_suffix}"
            f"{html_path.suffix}"
        )

        output_path.write_text(
            processed_content,
            encoding="utf-8",
        )

        return output_path