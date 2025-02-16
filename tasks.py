import os
import subprocess
from pathlib import Path
from celery import Celery
from utils import generate_qr_code, format_datetime

app = Celery('tasks', broker='pyamqp://localhost//')

BASE_DIR = Path(__file__).parent.resolve()
FONT_PATH = BASE_DIR / "fonts/Open Sans Bold.ttf"
TEMPLATE_PATH = BASE_DIR / "templates/certificate_template.jpg"

REQUIRED_KEYS = ['user_name', 'college', 'certificate_id', 'issued_at']  # Changed

def validate_data(data):
    missing = [key for key in REQUIRED_KEYS if key not in data]
    if missing:
        raise ValueError(f"Missing fields: {', '.join(missing)}")
    return data

def ffmpeg_escape(text):
    return (
        text.replace(":", "\\:")
            .replace("'", r"\'")
            .replace(" ", "\\ ")
    )

@app.task
def generate_certificate(data):
    try:
        data = validate_data(data)
        if not TEMPLATE_PATH.exists():
            raise FileNotFoundError(f"Template missing: {TEMPLATE_PATH}")
        if not FONT_PATH.exists():
            raise FileNotFoundError(f"Font missing: {FONT_PATH}")

        os.makedirs("certificates", exist_ok=True)
        os.makedirs("temp", exist_ok=True)
        
        qr_path = generate_qr_code(data['certificate_id'])

        # Changed 'test' to 'college'
        esc = {
            'name': ffmpeg_escape(data['user_name']),
            'college': ffmpeg_escape(data['college']),  # Changed
            'cid': ffmpeg_escape(data['certificate_id']),
            'date': ffmpeg_escape(format_datetime(data['issued_at'])),
            'font': str(FONT_PATH).replace(" ", "\\ "),
            'template': str(TEMPLATE_PATH).replace(" ", "\\ ")
        }

        # Updated filter chain with college
        filter_chain = (
            f"[0:v]drawtext=text='{esc['name']}':x=90:y=880:fontsize=50:"
            f"fontcolor=black:fontfile='{esc['font']}',"
            f"drawtext=text='{esc['college']}':x=90:y=1095:fontsize=50:"  # Changed
            f"fontcolor=black:fontfile='{esc['font']}',"
            f"drawtext=text='{esc['cid']}':x=1675:y=110:"
            f"fontsize=20:fontcolor=darkred:fontfile='{esc['font']}',"
            f"drawtext=text='Date\\:{esc['date']}':x=1675:y=135:"
            f"fontsize=25:fontcolor=black:fontfile='{esc['font']}',"
            #f"format=yuva420p[base];[1]format=yuva420p[qr];[base][qr]overlay=100:100"
        )

        ffmpeg_cmd = [
            'ffmpeg', '-y',
            '-i', esc['template'],
            '-i', str(qr_path),
            '-filter_complex', filter_chain,
            '-q:v', '1',
            f"certificates/{esc['cid']}.jpg"
        ]

        subprocess.run(ffmpeg_cmd, check=True)
        return f"certificates/{esc['cid']}.jpg"

    except subprocess.CalledProcessError as e:
        print(f"FFmpeg Error: {e.stderr.decode()}")
        raise
    except Exception as e:
        print(f"Error: {str(e)}")
        raise
    finally:
        if qr_path.exists():
            qr_path.unlink()