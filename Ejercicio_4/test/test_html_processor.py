import base64
import tempfile
import unittest
from pathlib import Path

from Ejercicio_4.src.html_processor import (
    HtmlProcessor,
    ProcessingReport,
)


class TestHtmlProcessor(unittest.TestCase):

    def test_image_is_converted_to_base64(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)

            image_bytes = b"fake image content"

            image_path = root / "image.png"
            image_path.write_bytes(image_bytes)

            html_path = root / "index.html"
            html_path.write_text(
                '<html><body><img src="image.png"></body></html>',
                encoding="utf-8",
            )

            report = ProcessingReport()
            processor = HtmlProcessor()

            output_path = processor.process(
                html_path,
                report,
            )

            result = output_path.read_text(encoding="utf-8")

            expected_base64 = base64.b64encode(
                image_bytes
            ).decode("ascii")

            self.assertIn(
                f"data:image/png;base64,{expected_base64}",
                result,
            )

    def test_original_html_is_not_modified(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)

            image_path = root / "image.png"
            image_path.write_bytes(b"image")

            original_content = (
                '<html><body>'
                '<img src="image.png">'
                '</body></html>'
            )

            html_path = root / "index.html"
            html_path.write_text(
                original_content,
                encoding="utf-8",
            )

            report = ProcessingReport()
            processor = HtmlProcessor()

            processor.process(
                html_path,
                report,
            )

            self.assertEqual(
                html_path.read_text(encoding="utf-8"),
                original_content,
            )

    def test_output_file_is_created(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)

            image_path = root / "image.png"
            image_path.write_bytes(b"image")

            html_path = root / "index.html"
            html_path.write_text(
                '<img src="image.png">',
                encoding="utf-8",
            )

            report = ProcessingReport()
            processor = HtmlProcessor()

            output_path = processor.process(
                html_path,
                report,
            )

            self.assertTrue(output_path.exists())

            self.assertEqual(
                output_path.name,
                "index_base64.html",
            )

    def test_multiple_images_are_processed(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)

            (root / "first.png").write_bytes(b"first")
            (root / "second.jpg").write_bytes(b"second")

            html_path = root / "index.html"

            html_path.write_text(
                """
                <html>
                    <body>
                        <img src="first.png">
                        <img src="second.jpg">
                    </body>
                </html>
                """,
                encoding="utf-8",
            )

            report = ProcessingReport()
            processor = HtmlProcessor()

            output_path = processor.process(
                html_path,
                report,
            )

            result = output_path.read_text(encoding="utf-8")

            self.assertIn(
                "data:image/png;base64,",
                result,
            )

            self.assertIn(
                "data:image/jpeg;base64,",
                result,
            )

            successes = report.success[str(html_path.resolve())]

            self.assertEqual(len(successes), 2)

    def test_missing_image_is_reported_as_failure(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)

            html_path = root / "index.html"

            html_path.write_text(
                '<img src="missing.png">',
                encoding="utf-8",
            )

            report = ProcessingReport()
            processor = HtmlProcessor()

            output_path = processor.process(
                html_path,
                report,
            )

            key = str(html_path.resolve())

            self.assertIn(key, report.fail)

            self.assertEqual(
                report.fail[key][0]["src"],
                "missing.png",
            )

            result = output_path.read_text(encoding="utf-8")

            self.assertIn(
                'src="missing.png"',
                result,
            )

    def test_partial_failure_does_not_stop_processing(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)

            (root / "valid.png").write_bytes(b"valid")

            html_path = root / "index.html"

            html_path.write_text(
                """
                <img src="valid.png">
                <img src="missing.png">
                """,
                encoding="utf-8",
            )

            report = ProcessingReport()
            processor = HtmlProcessor()

            output_path = processor.process(
                html_path,
                report,
            )

            result = output_path.read_text(encoding="utf-8")

            self.assertIn(
                "data:image/png;base64,",
                result,
            )

            self.assertIn(
                'src="missing.png"',
                result,
            )

            key = str(html_path.resolve())

            self.assertEqual(
                len(report.success[key]),
                1,
            )

            self.assertEqual(
                len(report.fail[key]),
                1,
            )

    def test_relative_image_path_is_resolved_from_html_directory(
        self,
    ):
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)

            images_dir = root / "images"
            images_dir.mkdir()

            image_path = images_dir / "logo.png"
            image_path.write_bytes(b"logo")

            html_path = root / "index.html"

            html_path.write_text(
                '<img src="images/logo.png">',
                encoding="utf-8",
            )

            report = ProcessingReport()
            processor = HtmlProcessor()

            output_path = processor.process(
                html_path,
                report,
            )

            result = output_path.read_text(encoding="utf-8")

            self.assertIn(
                "data:image/png;base64,",
                result,
            )

    def test_existing_data_uri_is_preserved(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)

            data_uri = "data:image/png;base64,YWJj"

            html_path = root / "index.html"

            html_path.write_text(
                f'<img src="{data_uri}">',
                encoding="utf-8",
            )

            report = ProcessingReport()
            processor = HtmlProcessor()

            output_path = processor.process(
                html_path,
                report,
            )

            result = output_path.read_text(encoding="utf-8")

            self.assertIn(
                data_uri,
                result,
            )

    def test_self_closing_image_tag_is_processed(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)

            image_path = root / "image.png"
            image_path.write_bytes(b"image")

            html_path = root / "index.html"

            html_path.write_text(
                '<img src="image.png" />',
                encoding="utf-8",
            )

            report = ProcessingReport()
            processor = HtmlProcessor()

            output_path = processor.process(
                html_path,
                report,
            )

            result = output_path.read_text(encoding="utf-8")

            self.assertIn(
                "data:image/png;base64,",
                result,
            )

    def test_img_without_src_is_reported(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)

            html_path = root / "index.html"

            html_path.write_text(
                '<img alt="No source">',
                encoding="utf-8",
            )

            report = ProcessingReport()
            processor = HtmlProcessor()

            processor.process(
                html_path,
                report,
            )

            key = str(html_path.resolve())

            self.assertIn(key, report.fail)

            self.assertEqual(
                report.fail[key][0]["src"],
                "",
            )


if __name__ == "__main__":
    unittest.main()