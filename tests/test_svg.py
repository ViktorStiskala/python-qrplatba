import importlib.util
import re
import xml.etree.ElementTree as ET
from datetime import datetime, timedelta
from decimal import Decimal

import pytest

from qrplatba import QRPlatbaGenerator


class TestSVGImage:
    """Tests for SVG image generation, dimensions, and structural correctness."""

    data = {
        "account": "123456789/0123",
        "amount": 400.56,
        "x_vs": 2034456,
        "message": "text",
        "due_date": datetime.now() + timedelta(days=14),
    }

    def make_image(self, **kwargs):
        generator = QRPlatbaGenerator(**self.data)
        img = generator.make_image(**kwargs)

        return img.to_string(encoding="unicode")

    def test_svg_content(self):
        svg_data = self.make_image()

        assert "http://www.w3.org/2000/svg" in svg_data

        root = ET.fromstring(svg_data)
        text = root.find(".//{http://www.w3.org/2000/svg}text")
        assert text is not None
        assert text.text == "QR platba"

        paths = root.findall(".//{http://www.w3.org/2000/svg}path")
        assert len(paths) == 2

        path_ids = {path.get("id") for path in paths}
        assert path_ids == {"qr-path", "qrplatba-border"}

    def test_svg_scaling(self):
        svg_data = self.make_image(box_size=40)

        root = ET.fromstring(svg_data)

        assert root is not None
        assert root.get("width") == "200mm"
        assert root.get("height") == "204mm"

    def test_file_save(self, tmp_path):
        generator = QRPlatbaGenerator(**self.data)
        img = generator.make_image()

        filename = tmp_path / "example.svg"

        img.save(filename)
        assert filename.exists()

        root = ET.parse(filename).getroot()
        assert root is not None
        viewbox = root.get("viewBox")
        assert viewbox is not None

        data = map(Decimal, viewbox.split(" "))
        assert list(data) == [Decimal(0), Decimal(0), Decimal("50"), Decimal("51")]

    @pytest.mark.parametrize("box_size", [1, 10, 12, 40, 100])
    def test_svg_valid_structure(self, box_size):
        svg_data = self.make_image(box_size=box_size)
        root = ET.fromstring(svg_data)
        assert root.get("width") is not None
        assert root.get("height") is not None
        assert root.get("viewBox") is not None

        width_val = float(root.get("width").rstrip("mm"))
        height_val = float(root.get("height").rstrip("mm"))
        assert height_val > width_val

    @pytest.mark.parametrize("border", [0, 2, 5])
    def test_svg_border_values(self, border):
        svg_data = self.make_image(border=border)
        root = ET.fromstring(svg_data)
        assert root is not None
        paths = root.findall(".//{http://www.w3.org/2000/svg}path")
        assert len(paths) == 2

    @pytest.mark.parametrize("box_size", [10, 20, 40])
    def test_integer_dimensions(self, box_size):
        """Width, height, and viewBox must be integer mm for box_size multiples of 10."""
        svg_data = self.make_image(box_size=box_size)
        root = ET.fromstring(svg_data)

        width_val = float(root.get("width").rstrip("mm"))
        height_val = float(root.get("height").rstrip("mm"))
        assert width_val == int(width_val), f"width {root.get('width')} is not integer mm"
        assert height_val == int(height_val), f"height {root.get('height')} is not integer mm"

        for val in root.get("viewBox").split():
            assert float(val) == int(float(val)), f"viewBox value {val} is not integer"

    @pytest.mark.parametrize("box_size", [20, 40])
    def test_integer_coordinates(self, box_size):
        """All path and text coordinates must be integers for box_size multiples of 20.

        At box_size=10 (default), LINE_SIZE=0.5 produces .5 fractions in coordinates.
        At multiples of 20, LINE_SIZE*ratio becomes integer, so all coordinates are clean.
        """
        svg_data = self.make_image(box_size=box_size)
        root = ET.fromstring(svg_data)
        ns = "http://www.w3.org/2000/svg"

        for path in root.findall(f".//{{{ns}}}path"):
            for num in re.findall(r"-?\d+\.?\d*", path.get("d")):
                val = float(num)
                assert val == int(val), f"Fractional coordinate {num} in path id={path.get('id')}"

        text = root.find(f".//{{{ns}}}text")
        for attr in ("x", "y"):
            val = float(text.get(attr))
            assert val == int(val), f"Fractional text {attr}={text.get(attr)}"


class TestPNGMissingDependency(TestSVGImage):
    """Must run regardless of whether resvg_py is installed."""

    def test_missing_resvg(self, tmp_path, monkeypatch):
        """PNG save must raise ImportError with install instructions when resvg-py is absent."""
        import sys

        monkeypatch.setitem(sys.modules, "resvg_py", None)
        generator = QRPlatbaGenerator(**self.data)
        img = generator.make_image()
        with pytest.raises(ImportError, match="pip install qrplatba"):
            img.save(tmp_path / "out.png", format="png")

    def test_unsupported_format(self):
        """Requesting an unsupported format must raise ValueError."""
        generator = QRPlatbaGenerator(**self.data)
        img = generator.make_image()
        with pytest.raises(ValueError, match="Unsupported format"):
            img.save("out.bmp", format="bmp")


@pytest.mark.skipif(
    not importlib.util.find_spec("resvg_py"),
    reason="resvg_py not installed",
)
class TestPNGSave(TestSVGImage):
    """PNG save tests. Skipped when resvg-py is not installed."""

    def test_png_save(self, tmp_path):
        """Saved PNG must start with the PNG magic bytes."""
        generator = QRPlatbaGenerator(**self.data)
        img = generator.make_image()
        filename = tmp_path / "example.png"
        img.save(filename, format="png")
        content = filename.read_bytes()
        assert content[:4] == b"\x89PNG"

    def test_png_zoom(self, tmp_path):
        """Higher zoom must produce a larger PNG file."""
        generator = QRPlatbaGenerator(**self.data)
        img = generator.make_image()
        f1 = tmp_path / "z1.png"
        f2 = tmp_path / "z2.png"
        img.save(f1, format="png", zoom=1)
        img.save(f2, format="png", zoom=2)
        assert f2.stat().st_size > f1.stat().st_size

    def test_png_uses_bundled_font(self, tmp_path):
        """Verify the bundled Inter Bold font is used by default for PNG rendering.

        Checks two things:
        - Default save() output is identical to explicitly passing the bundled font,
          proving the font_files/skip_system_fonts defaults are correctly wired.
        - Default output differs from a no-font render (skip_system_fonts=True without
          font_files), proving the bundled font actually renders visible text. This also
          guards against the coupled-pair condition being changed to independent setdefault.
        """
        from qrplatba.svg import _INTER_BOLD

        generator = QRPlatbaGenerator(**self.data)
        img = generator.make_image()

        f_default = tmp_path / "default.png"
        f_explicit = tmp_path / "explicit.png"
        f_no_fonts = tmp_path / "no_fonts.png"

        img.save(f_default, format="png", zoom=2)
        img.save(
            f_explicit, format="png", zoom=2, resvg_kwargs={"font_files": [_INTER_BOLD], "skip_system_fonts": True}
        )
        img.save(f_no_fonts, format="png", zoom=2, resvg_kwargs={"skip_system_fonts": True})

        assert f_default.read_bytes() == f_explicit.read_bytes()
        assert f_default.read_bytes() != f_no_fonts.read_bytes()
