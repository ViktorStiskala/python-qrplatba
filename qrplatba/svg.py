# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.

from qrcode.image import svg
import xml.etree.ElementTree as ET


class QRPlatbaSVGImage(svg.SvgFragmentImage):
    """
    QR Platba SVG image generator.

    Inner padding is created according to specification (http://qr-platba.cz/pro-vyvojare/specifikace-formatu/),
    text size is computed to achieve width of 16 QR points. Width of the black border around the QR code is only guessed
    (1/5 of the QR point size), because the specification declares width of 1.5pt which is quite unusable in SVG image.
    """

    QR_TEXT_STYLE = 'font-size:{size}{units};font-weight:bold;fill:#000000;font-family:Arial;'
    QR_PATH_STYLE = 'fill:#000000;fill-opacity:1;fill-rule:nonzero;stroke:none'
    UNITS = 'px'
    SCALE = 5

    def __init__(self, border, width, box_size):
        self._points = set()
        self.outside_border = border
        self.inside_border = 4
        self.line_size = self.SCALE / 5
        self.font_height = 2.5 * self.SCALE

        super(QRPlatbaSVGImage, self).__init__(border, width, box_size)
        self.border = self.inside_border + border  # inside border

    def drawrect(self, row, col):
        # (x, y)
        self._points.add((col, row))

    def _svg(self, tag=ET.QName("svg")):
        dimension = 2 * (self.outside_border + self.inside_border) * self.SCALE
        dimension += self.width * self.SCALE + 2 * self.line_size

        # height of the SVG image have to be bigger due to text element
        height = dimension + self.font_height + 0.679 * self.SCALE
        svg = ET.Element(
            tag,
            version="1.1",
            width="{0}{units}".format(dimension, units=self.UNITS),
            height="{0}{units}".format(height, units=self.UNITS),
            viewBox="0 0 {w} {h}".format(w=dimension, h=height)
        )
        svg.set("xmlns", self._SVG_namespace)
        return svg

    def make_border(self):
        """Creates black thin border around QR code"""

        scaled_inside = self.inside_border * self.SCALE
        scaled_outside = self.outside_border * self.SCALE
        scaled_width = self.width * self.SCALE

        horizontal_line = 'M {x0} {y0} h {length} v {width} h -{length} z'
        vertical_line = 'M {x0} {y0} v {length} h {width} v -{length} z'

        subpaths = list()
        # top line
        subpaths.append(horizontal_line.format(
            x0=scaled_outside,
            y0=scaled_outside,
            length=scaled_inside * 2 + scaled_width + 2 * self.line_size,
            width=self.line_size
        ))

        # bottom line - first segment
        subpaths.append(horizontal_line.format(
            x0=scaled_outside,
            y0=scaled_outside + self.line_size + 2 * scaled_inside + scaled_width,
            length=self.SCALE * 2,
            width=self.line_size
        ))

        # bottom line - second segment
        subpaths.append(horizontal_line.format(
            x0=scaled_outside + 22 * self.SCALE,
            y0=scaled_outside + self.line_size + 2 * scaled_inside + scaled_width,
            length=scaled_width + 2 * scaled_inside + 2 * self.line_size - 22 * self.SCALE,  # 22 = 2 + 2 + 16 + 2
            width=self.line_size
        ))

        # left line
        subpaths.append(vertical_line.format(
            x0=scaled_outside,
            y0=scaled_outside + self.line_size,
            length=scaled_width + 2 * scaled_inside,
            width=self.line_size
        ))

        # right line
        subpaths.append(vertical_line.format(
            x0=scaled_outside + self.line_size + 2 * scaled_inside + scaled_width,
            y0=scaled_outside + self.line_size,
            length=scaled_width + 2 * scaled_inside,
            width=self.line_size
        ))

        return ET.Element(ET.QName("path"), style=self.QR_PATH_STYLE, d=' '.join(subpaths), id="qrplatba-border")

    def make_text(self):
        """Creates "QR platba" text element"""

        text_style = self.QR_TEXT_STYLE.format(size=3.443101883 * self.SCALE, units=self.UNITS)

        x_pos = str(self.outside_border * self.SCALE + self.line_size + 4 * self.SCALE)
        y_pos = str(self.outside_border * self.SCALE + 2 * self.line_size + 2 * self.inside_border * self.SCALE
                    + self.width * self.SCALE + self.font_height)
        text_el = ET.Element(ET.QName("text"), style=text_style, x=x_pos, y=y_pos, id="qrplatba-text")
        text_el.text = 'QR platba'
        return text_el

    def _generate_subpaths(self):
        """Generates individual QR points as subpaths"""

        scale = self.SCALE

        for point in self._points:
            x_base = point[0] * scale + self.border * scale + self.line_size
            y_base = point[1] * scale + self.border * scale + self.line_size

            yield 'M {x0} {y0} L {x0} {y1} L {x1} {y1} L {x1} {y0} z'.format(
                x0=x_base,
                y0=y_base,
                x1=x_base + scale,
                y1=y_base + scale
            )

    def make_path(self):
        """Creates path element consisting of QR points"""

        subpaths = self._generate_subpaths()

        return ET.Element(
            ET.QName("path"),
            style=self.QR_PATH_STYLE,
            d=' '.join(subpaths),
            id="qr-path"
        )

    def _write(self, stream):
        """Appends all elements to SVG document"""

        self._img.append(self.make_path())
        self._img.append(self.make_border())
        self._img.append(self.make_text())

        ET.ElementTree(self._img).write(stream, encoding="UTF-8", xml_declaration=True)