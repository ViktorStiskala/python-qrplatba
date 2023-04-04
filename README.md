# python-qrplatba

![https://badge.fury.io/py/qrplatba.png](http://badge.fury.io/py/qrplatba)

Python library for generating QR codes for QR platba.

![https://raw.github.com/viktorstiskala/python-qrplatba/gh-pages/example.png](http://viktorstiskala.github.io/python-qrplatba/example.svg)

See http://qr-platba.cz/pro-vyvojare/ for more information about the specification (available only in czech).

```python
from qrplatba import QRPlatbaGenerator
from datetime import datetime, timedelta


due = datetime.now() + timedelta(days=14)
generator = QRPlatbaGenerator('123456789/0123', 400.56, x_vs=2034456, message='text', due_date=due)
img = generator.make_image()
img.save('example.svg')

# optional: custom box size and border
img = generator.make_image(box_size=20, border=4)

# optional: get SVG as a string.
# Encoding has to be 'unicode', otherwise it will be encoded as bytes
svg_data = img.to_string(encoding='unicode')
```

## Installation

To install qrplatba, simply:

```bash
$ pip install qrplatba
```

## Note on image file formats

This module generates SVG file which is an XML-based vector image format. You can use various libraries and/or utilities to convert it to other vector or bitmap image formats. Below is an example how to use ``libRSVG`` to convert SVG images.

### libRSVG

[`libRSVG`](https://wiki.gnome.org/action/show/Projects/LibRsvg?action=show) renders SVG files using cairo and supports many output image formats. It can also be used directly in console with ``rsvg-convert`` command.

```bash
$ rsvg-convert -f pdf example.svg -o example.pdf
```

## License

This software is licensed under [MIT license](https://opensource.org/license/mit/) since version `1.0.0`.

## Changelog

### `1.0.0` (4 April 2023)

**Warning:** While the API is mostly backwards compatible, the look and size of the generated QR codes has changed.

- Updated requirements to support the latest `qrcode` version
- Added support for custom output sizes using `box_size` and `border` parameters
- Changed legacy setuptools to [poetry](https://python-poetry.org/)
- Dropped support for Python `2.x` and `<3.7`
- Changed license to MIT
- Added unit tests



