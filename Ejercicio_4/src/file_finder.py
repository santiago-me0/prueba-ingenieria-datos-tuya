"""Utilities for discovering HTML files."""

from pathlib import Path
from typing import Iterable


class HtmlFileFinder:
    """Resolve files and directories into a unique list of HTML files."""

    HTML_EXTENSIONS = {".html", ".htm"}

    def __init__(self, generated_suffix: str = "_base64") -> None:
        self.generated_suffix = generated_suffix

    def find(self, inputs: Iterable[str | Path]) -> list[Path]:
        """
        Return all HTML files found in the provided paths.

        Directories are searched recursively.
        Generated *_base64.html files are ignored.
        """

        html_files: set[Path] = set()

        for input_path in inputs:
            path = Path(input_path).expanduser().resolve()

            if not path.exists():
                raise FileNotFoundError(
                    f"Input path does not exist: {path}"
                )

            if path.is_file():
                if self._is_source_html(path):
                    html_files.add(path)

                continue

            if path.is_dir():
                for candidate in path.rglob("*"):
                    if (
                        candidate.is_file()
                        and self._is_source_html(candidate)
                    ):
                        html_files.add(candidate.resolve())

        return sorted(html_files)

    def _is_source_html(self, path: Path) -> bool:
        """Return True when the file should be processed."""

        if path.suffix.lower() not in self.HTML_EXTENSIONS:
            return False

        return not path.stem.endswith(self.generated_suffix)