"""Command-line interface for Exercise 4."""

from argparse import ArgumentParser
import json
from pathlib import Path

from Ejercicio_4.src.file_finder import HtmlFileFinder
from Ejercicio_4.src.html_processor import (
    HtmlProcessor,
    ProcessingReport,
)


class HtmlBatchProcessor:
    """Coordinate discovery and processing of HTML files."""

    def __init__(
        self,
        finder: HtmlFileFinder | None = None,
        processor: HtmlProcessor | None = None,
    ) -> None:
        self.finder = finder or HtmlFileFinder()
        self.processor = processor or HtmlProcessor()

    def process(
        self,
        inputs: list[str | Path],
    ) -> dict:
        """Process every HTML file found in the input paths."""

        html_files = self.finder.find(inputs)

        report = ProcessingReport()

        for html_path in html_files:
            self.processor.process(
                html_path=html_path,
                report=report,
            )

        return report.to_dict()


def main() -> None:
    """CLI entry point."""

    parser = ArgumentParser(
        description=(
            "Embed HTML image references as Base64 data URIs."
        )
    )

    parser.add_argument(
        "paths",
        nargs="+",
        help=(
            "HTML files or directories to process. "
            "Directories are searched recursively."
        ),
    )

    args = parser.parse_args()

    processor = HtmlBatchProcessor()

    try:
        result = processor.process(args.paths)
    except (FileNotFoundError, OSError, ValueError) as exc:
        parser.error(str(exc))

    print(
        json.dumps(
            result,
            indent=2,
            ensure_ascii=False,
        )
    )


if __name__ == "__main__":
    main()