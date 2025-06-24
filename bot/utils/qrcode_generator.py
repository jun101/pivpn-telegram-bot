import qrcode
from io import BytesIO

class QRCodeGenerator:
    @staticmethod
    def generate_qr(data: str) -> BytesIO:
        qr = qrcode.make(data)
        buf = BytesIO()
        qr.save(buf, format='PNG')
        buf.seek(0)
        return buf
