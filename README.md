# python-qrplatba

[![Stable Version](https://img.shields.io/pypi/v/qrplatba?label=stable)](https://pypi.org/project/qrplatba/#description)

Python library for generating QR codes for QR platba.

![Example QR platba image](https://raw.githubusercontent.com/ViktorStiskala/python-qrplatba/refs/heads/master/example.svg)

See http://qr-platba.cz/pro-vyvojare/ for more information about the specification (available only in czech).

```python
from qrplatba import QRPlatbaGenerator
from datetime import datetime, timedelta


due = datetime.now() + timedelta(days=14)
generator = QRPlatbaGenerator('123456789/0123', 400.56, x_vs=2034456, message='text', due_date=due)
img = generator.make_image()
img.save('example.svg')

# PNG export (requires: pip install qrplatba[png])
img.save('example.png', output_format='png', zoom=2)

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

For PNG export support:

```bash
$ pip install qrplatba[png]
```

## Note on image file formats

This module generates SVG files by default. PNG export is supported when installed with `qrplatba[png]` – see the example above.

For other formats (e.g. PDF), you can use external tools like `libRSVG` to convert SVG images.

### libRSVG

[libRSVG](https://wiki.gnome.org/action/show/Projects/LibRsvg?action=show) renders SVG files using cairo and supports many output image formats. It can also be used directly in console with `rsvg-convert` command.

```bash
$ rsvg-convert -f pdf example.svg -o example.pdf
```

## SPAYD format

QR Platba uses SPAYD format (`application/x-shortpaymentdescriptor`) for encoding information related to bank transfer. You can generate the SPAYD string directly using `SpaydGenerator`:

```python
from qrplatba import SpaydGenerator

generator = SpaydGenerator('123456789/0123', 400.56, x_vs=2034456, message='text', due_date=due)
spayd = generator.get_text()
```

## License

This software is licensed under [MIT license](https://opensource.org/license/mit/) since version `1.0.0`.

## Changelog

### `1.2.0` (5 March 2026)

> [!CAUTION]
> **Breaking changes in `1.2.0`:**
> - Changed package structure: **`from qrplatba.spayd import QRPlatbaGenerator`** is deprecated and will be removed in a future version. Use `from qrplatba import QRPlatbaGenerator` instead. The SPAYD string generator class is available as `from qrplatba import SpaydGenerator`.
> - Updated default settings: **Default `box_size` changed from 12 to 10**, producing smaller SVG output with clean integer mm dimensions (e.g. `50mm x 51mm` instead of `59.4mm x 60.36mm`). Pass `box_size=12` to `make_image()` to restore the previous overall dimensions. Note: SVG visual changes (border thickness, text height) apply at all sizes; `box_size=12` only restores the overall dimensions, not the exact visual appearance.
> - **SVG visual output changed:** border thickness doubled (`LINE_SIZE` 0.25 to 0.5), text area below the QR code is taller (`FONT_HEIGHT` 8 to 10), and text positioning adjusted. These changes affect all SVGs regardless of `box_size`.
> - **Dropped support for Python 3.8**

- Added Python 3.12, 3.13 and 3.14
- Added `SpaydGenerator` class for standalone SPAYD string generation
- Refactored `QRPlatbaGenerator` to inherit from `SpaydGenerator`
- Added PNG export support via `save(output_format='png')` with optional dependency (`pip install qrplatba[png]`)
- Updated SVG font stack to `Inter, Arial, Helvetica, sans-serif`
- Migrated from [Poetry](https://python-poetry.org/) to [uv](https://docs.astral.sh/uv/)
- Replaced `black` with `ruff format` for code formatting
- Fixed `_format_item_string` silently dropping zero values (e.g. `x_vs=0`)
- Added comprehensive test suite including backward compatibility and PNG rendering tests
- Release tags now use `v` prefix (e.g. `v1.2.0` instead of `1.2.0`)

### `1.1.1` (24 April 2023)
- Added compatibility with `lxml` library. Fixes `TypeError` when using this library while `lxml` is installed in the same virtualenv.

### `1.1.0` (5 April 2023)

- Dropped support for Python 3.7
- Added pre-commit, ruff for code linting and formatting

### `1.0.0` (4 April 2023)

**Warning:** While the API is mostly backwards compatible, the look and size of the generated QR codes has changed.

- Updated requirements to support the latest `qrcode` version
- Added support for custom output sizes using `box_size` and `border` parameters
- Changed legacy setuptools to [poetry](https://python-poetry.org/), later migrated to [uv](https://docs.astral.sh/uv/)
- Dropped support for Python `2.x` and `<3.7`
- Changed license to MIT
- Added unit tests
