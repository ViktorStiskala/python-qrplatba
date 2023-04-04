from decimal import Decimal

from qrplatba import QRPlatbaGenerator
from datetime import datetime, timedelta
import xml.etree.ElementTree as ET


class TestSVGImage:
    data = {
        'account': '123456789/0123',
        'amount': 400.56,
        'x_vs': 2034456,
        'message': 'text',
        'due_date': datetime.now() + timedelta(days=14)
    }

    def make_image(self, **kwargs):
        generator = QRPlatbaGenerator(**self.data)
        img = generator.make_image(**kwargs)

        return img.to_string(encoding='unicode')

    def test_svg_content(self):
        svg_data = self.make_image()

        assert 'http://www.w3.org/2000/svg' in svg_data

        root = ET.fromstring(svg_data)
        text = root.find('.//{http://www.w3.org/2000/svg}text')
        assert text is not None
        assert text.text == 'QR platba'

        paths = root.findall('.//{http://www.w3.org/2000/svg}path')
        assert len(paths) == 2

        for path in paths:
            assert path.get('id') is not None
            assert path.get('id') in ('qr-path', 'qrplatba-border')

    def test_svg_scaling(self):
        svg_data = self.make_image(box_size=40)

        root = ET.fromstring(svg_data)

        assert root is not None
        assert root.get('width') == '198mm'
        assert root.get('height') == '201.2mm'

    def test_file_save(self, tmp_path):
        generator = QRPlatbaGenerator(**self.data)
        img = generator.make_image()

        filename = tmp_path / 'example.svg'

        img.save(filename)
        assert filename.exists()

        root = ET.parse(filename).getroot()
        assert root is not None
        viewbox = root.get('viewBox')
        assert viewbox is not None

        data = map(Decimal, viewbox.split(' '))
        assert list(data) == [Decimal(0), Decimal(0), Decimal('59.4'), Decimal('60.36')]
