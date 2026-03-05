import qrcode

from qrplatba.spayd import SpaydGenerator
from qrplatba.svg import QRPlatbaSVGImage


class QRPlatbaGenerator(SpaydGenerator):
    """QR Platba generator -- creates SPAYD QR code images."""

    def make_image(self, border=2, box_size=10, error_correction=qrcode.constants.ERROR_CORRECT_M):
        qr = qrcode.QRCode(
            version=None,
            error_correction=error_correction,
            image_factory=QRPlatbaSVGImage,
            border=border,
            box_size=box_size,
        )
        qr.add_data(self.get_text())
        qr.make(fit=True)
        return qr.make_image()
