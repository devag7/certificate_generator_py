import qrcode
from datetime import datetime
from pathlib import Path

def generate_qr_code(certificate_id):
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_H,
        box_size=10,
        border=4,
    )
    qr.add_data(certificate_id)
    qr.make(fit=True)
    img = qr.make_image(fill_color="#2c3e50", back_color="white")
    qr_path = Path("temp") / f"{certificate_id}_qr.png"
    img.save(qr_path)
    return qr_path

def format_datetime(iso_str):
    dt = datetime.fromisoformat(iso_str)
    return dt.strftime("%d-%b-%Y %H:%M")