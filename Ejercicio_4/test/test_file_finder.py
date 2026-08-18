import tempfile
import unittest
from pathlib import Path

from Ejercicio_4.src.file_finder import HtmlFileFinder


class TestHtmlFileFinder(unittest.TestCase):

    def test_find_html_file(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)

            html_file = root / "index.html"
            html_file.write_text("<html></html>", encoding="utf-8")

            finder = HtmlFileFinder()

            result = finder.find([html_file])

            self.assertEqual(
                result,
                [html_file.resolve()],
            )

    def test_find_html_files_recursively(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)

            nested = root / "pages"
            nested.mkdir()

            first = root / "index.html"
            second = nested / "about.htm"

            first.write_text("<html></html>", encoding="utf-8")
            second.write_text("<html></html>", encoding="utf-8")

            finder = HtmlFileFinder()

            result = finder.find([root])

            self.assertEqual(
                set(result),
                {
                    first.resolve(),
                    second.resolve(),
                },
            )

    def test_ignore_non_html_files(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)

            html_file = root / "index.html"
            text_file = root / "notes.txt"

            html_file.write_text("<html></html>", encoding="utf-8")
            text_file.write_text("text", encoding="utf-8")

            finder = HtmlFileFinder()

            result = finder.find([root])

            self.assertEqual(
                result,
                [html_file.resolve()],
            )

    def test_ignore_generated_base64_html(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)

            original = root / "index.html"
            generated = root / "index_base64.html"

            original.write_text("<html></html>", encoding="utf-8")
            generated.write_text("<html></html>", encoding="utf-8")

            finder = HtmlFileFinder()

            result = finder.find([root])

            self.assertEqual(
                result,
                [original.resolve()],
            )

    def test_duplicated_inputs_return_unique_files(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)

            html_file = root / "index.html"
            html_file.write_text("<html></html>", encoding="utf-8")

            finder = HtmlFileFinder()

            result = finder.find(
                [
                    html_file,
                    root,
                ]
            )

            self.assertEqual(
                result,
                [html_file.resolve()],
            )

    def test_invalid_path_raises_error(self):
        finder = HtmlFileFinder()

        with self.assertRaises(FileNotFoundError):
            finder.find(
                ["/path/that/does/not/exist"]
            )


if __name__ == "__main__":
    unittest.main()