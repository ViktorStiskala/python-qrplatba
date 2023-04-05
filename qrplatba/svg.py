from decimal import Decimal
from typing import NamedTuple

from qrcode.image import svg
import xml.etree.ElementTree as ET


class ScaledSizes(NamedTuple):
    inside_border: Decimal
    outside_border: Decimal
    width: Decimal
    line_size: Decimal
    ratio: Decimal


class QRPlatbaSVGImage(svg.SvgPathImage):
    """
    QR Platba SVG image generator.

    Inner padding is created according to specification (http://qr-platba.cz/pro-vyvojare/specifikace-formatu/),
    text size is computed to achieve width of 16 QR points.
    """

    QR_TEXT_STYLE = "font-size:{size}px;font-weight:bold;fill:#000000;font-family:Arial;"
    FONT_SIZE = Decimal("3.5")
    FONT_HEIGHT = Decimal("8")

    LINE_SIZE = Decimal("0.25")
    INSIDE_BORDER = 4

    BOTTOM_LINE_SEGMENTS = (2, 22)

    def __init__(self, border, width, box_size, *args, **kwargs):
        self.outside_border = border
        border += self.INSIDE_BORDER + self.LINE_SIZE  # outside border + inside border + line size

        super().__init__(border, width, box_size, *args, **kwargs)

    def _get_scaled_sizes(self):
        """Computes sizes of the QR code and QR text according to the scale ratio"""
        scale_ratio = self.units(self.box_size, text=False)

        def strip_zeros(value):
            return Decimal(str(value).rstrip("0").rstrip(".")) if "." in str(value) else value

        return ScaledSizes(
            inside_border=strip_zeros(self.INSIDE_BORDER * scale_ratio),
            outside_border=strip_zeros(self.outside_border * scale_ratio),
            width=strip_zeros(self.width * scale_ratio),
            line_size=strip_zeros(self.LINE_SIZE * scale_ratio),
            ratio=scale_ratio,
        )

    def make_border(self):
        """Creates black thin border around QR code"""
        scaled = self._get_scaled_sizes()

        def sizes(ob, ib, wd, ln):  # size helper
            return ob * scaled.outside_border + ib * scaled.inside_border + wd * scaled.width + ln * scaled.line_size

        horizontal_line = "M{x0},{y0}h{length}v{width}h-{length}z"
        vertical_line = "M{x0},{y0}v{length}h{width}v-{length}z"

        def get_subpaths():
            # top line
            yield horizontal_line.format(
                x0=scaled.outside_border,
                y0=scaled.outside_border,
                length=sizes(0, 2, 1, 2),
                width=scaled.line_size,
            )

            b_first, b_second = self.BOTTOM_LINE_SEGMENTS

            # bottom line - first segment
            yield horizontal_line.format(
                x0=scaled.outside_border,
                y0=sizes(1, 2, 1, 1),
                length=b_first * scaled.ratio,
                width=scaled.line_size,
            )

            # bottom line - second segment
            yield horizontal_line.format(
                x0=scaled.outside_border + b_second * scaled.ratio,
                y0=sizes(1, 2, 1, 1),
                length=sizes(0, 2, 1, 2) - b_second * scaled.ratio,
                width=scaled.line_size,
            )

            # left line
            yield vertical_line.format(
                x0=scaled.outside_border,
                y0=scaled.outside_border + scaled.line_size,
                length=scaled.width + 2 * scaled.inside_border,
                width=scaled.line_size,
            )

            # right line
            yield vertical_line.format(
                x0=sizes(1, 2, 1, 1),
                y0=sizes(1, 0, 0, 1),
                length=sizes(0, 2, 1, 0),
                width=scaled.line_size,
            )

        subpaths = " ".join(get_subpaths())
        return ET.Element("path", d=subpaths, id="qrplatba-border", **self.QR_PATH_STYLE)

    def make_text(self):
        """Creates "QR platba" text element"""
        scaled = self._get_scaled_sizes()
        text_style = self.QR_TEXT_STYLE.format(size=(self.FONT_SIZE * scaled.ratio).quantize(Decimal("0.01")))

        x_pos = str(scaled.outside_border + scaled.line_size + 4 * scaled.ratio)
        y_pos = str(
            scaled.outside_border
            + scaled.line_size
            + 2 * scaled.inside_border
            + scaled.width
            + (self.FONT_HEIGHT / 4) * scaled.ratio
        )

        text_el = ET.Element("text", style=text_style, x=x_pos, y=y_pos, id="qrplatba-text")
        text_el.text = "QR platba"

        return text_el

    def _svg(self, viewBox=None, **kwargs):
        scaled = self._get_scaled_sizes()
        h_pixels = self.pixel_size + (self.FONT_HEIGHT * scaled.ratio)

        box = "0 0 {w} {h}".format(
            w=self.units(self.pixel_size, text=False),
            h=self.units(h_pixels, text=False),
        )
        svg_el = super()._svg(viewBox=box, **kwargs)
        svg_el.append(self.make_border())
        svg_el.append(self.make_text())

        # update size of the SVG element
        svg_el.attrib["height"] = str(self.units(h_pixels))

        return svg_el
