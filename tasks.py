"""
Certificate Generation Task Module
==================================

Author: devag7 (Deva Garwalla)
Description: Advanced certificate generation system using Celery, FF        # Method 1: ImageMagick (best quality) - using modern 'magick' command
        try:
            img_to_pdf_cmd = [
                'magick', str(temp_img_path),
                '-density', '200',
                '-quality', '85',
                '-compress', 'jpeg',
                str(pdf_output_path)
            ]
            subprocess.run(img_to_pdf_cmd, check=True)
            conversion_success = True
            logger.info("PDF conversion successful using ImageMagick")
        except (subprocess.CalledProcessError, FileNotFoundError):
            # Fallback to legacy convert command
            try:
                img_to_pdf_cmd = [
                    'convert', str(temp_img_path),
                    '-density', '200',
                    '-quality', '85',
                    '-compress', 'jpeg',
                    str(pdf_output_path)
                ]
                subprocess.run(img_to_pdf_cmd, check=True)
                conversion_success = True
                logger.info("PDF conversion successful using ImageMagick (legacy)")
            except (subprocess.CalledProcessError, FileNotFoundError):
                logger.warning("ImageMagick conversion failed, trying FFmpeg")rtLab
             Supports dynamic content, QR codes, and optimized PDF generation.

Features:
- Dynamic text overlays with custom fonts
- QR code generation and embedding
- Multiple output formats (PDF, PNG, JPG)
- Optimized file sizes for production use
- Error handling and recovery mechanisms
- Background processing with Celery
"""

import os
import subprocess
import logging
from pathlib import Path
from datetime import datetime
from typing import Dict, Any
from celery import Celery
from utils import generate_qr_code, format_datetime

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Celery configuration
app = Celery('certificate_generator', broker='pyamqp://localhost//')

# Base configuration
BASE_DIR = Path(__file__).parent.resolve()
FONT_PATH = BASE_DIR / "fonts" / "Open Sans Bold.ttf"
TEMPLATE_PATH = BASE_DIR / "templates" / "certificate_template.jpg"
CERTIFICATES_DIR = BASE_DIR / "certificates"
TEMP_DIR = BASE_DIR / "temp"

# Required fields for certificate generation
REQUIRED_KEYS = ['user_name', 'college', 'certificate_id', 'issued_at', 'topic']

class CertificateGenerationError(Exception):
    """Custom exception for certificate generation errors"""
    pass

def validate_data(data: Dict[str, Any]) -> Dict[str, Any]:
    """Validate input data for certificate generation"""
    missing = [key for key in REQUIRED_KEYS if key not in data or not data[key]]
    if missing:
        raise ValueError(f"Missing or empty required fields: {', '.join(missing)}")
    
    # Validate data types and lengths
    if not isinstance(data['user_name'], str) or len(data['user_name']) > 100:
        raise ValueError("user_name must be a string with max 100 characters")
    
    if not isinstance(data['college'], str) or len(data['college']) > 200:
        raise ValueError("college must be a string with max 200 characters")
    
    if not isinstance(data['topic'], str) or len(data['topic']) > 150:
        raise ValueError("topic must be a string with max 150 characters")
        
    # Validate date format
    try:
        datetime.fromisoformat(data['issued_at'])
    except ValueError:
        raise ValueError("issued_at must be in ISO format")
    
    return data

def ensure_directories():
    """Ensure required directories exist"""
    for directory in [CERTIFICATES_DIR, TEMP_DIR]:
        directory.mkdir(exist_ok=True)

def text_escape(text: str) -> str:
    """Escape special characters for FFmpeg text filters"""
    return (
        str(text)
        .replace("\\", "\\\\")
        .replace(":", "\\:")
        .replace("'", r"\'")
        .replace('"', r'\"')
        .replace("[", r"\[")
        .replace("]", r"\]")
        .replace(",", r"\,")
        .replace(";", r"\;")
    )

@app.task(bind=True, max_retries=3)
def generate_certificate(self, data: Dict[str, Any]) -> str:
    """
    Main task for generating certificates
    
    Args:
        data: Dictionary containing certificate information
            Required keys: user_name, college, certificate_id, issued_at, topic
            
    Returns:
        Path to generated certificate PDF
        
    Raises:
        CertificateGenerationError: If generation fails
    """
    try:
        logger.info(f"Starting certificate generation for {data.get('certificate_id', 'unknown')}")
        
        # Validate input data
        data = validate_data(data)
        
        # Ensure directories exist
        ensure_directories()
        
        # Check if template exists
        if not TEMPLATE_PATH.exists():
            raise FileNotFoundError(f"Template not found: {TEMPLATE_PATH}")
        if not FONT_PATH.exists():
            logger.warning(f"Font not found: {FONT_PATH}, using system default")
        
        # Generate QR code
        qr_path = generate_qr_code(data['certificate_id'])
        
        # Prepare escaped text
        esc = {
            'name': text_escape(data['user_name']),
            'college': text_escape(data['college']),
            'topic': text_escape(data['topic']),
            'cid': text_escape(data['certificate_id']),
            'date': text_escape(format_datetime(data['issued_at'])),
        }
        
        # Build filter chain with developer credit
        font_file = str(FONT_PATH).replace(" ", "\\ ")
        
        filter_chain = (
            f"drawtext=text='{esc['name']}':x=90:y=880:fontsize=50:"
            f"fontcolor=black:fontfile='{font_file}',"
            f"drawtext=text='{esc['college']}':x=90:y=1095:fontsize=45:"
            f"fontcolor=black:fontfile='{font_file}',"
            f"drawtext=text='{esc['topic']}':x=90:y=1285:fontsize=40:"
            f"fontcolor=black:fontfile='{font_file}',"
            f"drawtext=text='{esc['cid']}':x=1695:y=110:"
            f"fontsize=20:fontcolor=darkred:fontfile='{font_file}',"
            f"drawtext=text='Date\\: {esc['date']}':x=1650:y=135:"
            f"fontsize=25:fontcolor=black:fontfile='{font_file}',"
            f"drawtext=text='Generated by devag7':x=50:y=50:fontsize=12:"
            f"fontcolor=gray:fontfile='{font_file}'"
        )
        
        # Generate high-quality intermediate image
        temp_img_path = TEMP_DIR / f"{data['certificate_id']}_temp.jpg"
        
        ffmpeg_cmd = [
            'ffmpeg', '-y',
            '-i', str(TEMPLATE_PATH),
            '-vf', f"{filter_chain},scale=1500:-1",
            '-q:v', '2',
            str(temp_img_path)
        ]
        
        try:
            result = subprocess.run(ffmpeg_cmd, check=True, capture_output=True, text=True)
            logger.info("FFmpeg image generation successful")
        except subprocess.CalledProcessError as e:
            logger.error(f"FFmpeg failed: {e.stderr}")
            raise CertificateGenerationError(f"Image generation failed: {e.stderr}")
        
        # Convert to PDF with optimization
        pdf_output_path = CERTIFICATES_DIR / f"{data['certificate_id']}.pdf"
        
        # Try multiple conversion methods for best results
        conversion_success = False
        
        # Method 1: ImageMagick (best quality)
        try:
            img_to_pdf_cmd = [
                'convert', str(temp_img_path),
                '-density', '200',
                '-quality', '85',
                '-compress', 'jpeg',
                str(pdf_output_path)
            ]
            subprocess.run(img_to_pdf_cmd, check=True)
            conversion_success = True
            logger.info("PDF conversion successful using ImageMagick")
        except (subprocess.CalledProcessError, FileNotFoundError):
            logger.warning("ImageMagick conversion failed, trying FFmpeg")
        
        # Method 2: FFmpeg direct conversion
        if not conversion_success:
            try:
                ffmpeg_pdf_cmd = [
                    'ffmpeg', '-y',
                    '-i', str(temp_img_path),
                    '-f', 'pdf',
                    str(pdf_output_path)
                ]
                subprocess.run(ffmpeg_pdf_cmd, check=True)
                conversion_success = True
                logger.info("PDF conversion successful using FFmpeg")
            except subprocess.CalledProcessError:
                raise CertificateGenerationError("All PDF conversion methods failed")
        
        # Cleanup
        if temp_img_path.exists():
            temp_img_path.unlink()
        if qr_path.exists():
            qr_path.unlink()
        
        # Verify file size
        if pdf_output_path.exists():
            size_mb = pdf_output_path.stat().st_size / (1024 * 1024)
            logger.info(f"Certificate generated successfully. Size: {size_mb:.2f} MB")
            
            if size_mb > 3:
                logger.warning(f"File size ({size_mb:.2f} MB) exceeds 3MB limit")
        
        return str(pdf_output_path)
            
    except Exception as e:
        logger.error(f"Certificate generation failed: {str(e)}")
        
        # Retry logic
        if self.request.retries < self.max_retries:
            logger.info(f"Retrying... Attempt {self.request.retries + 1}")
            raise self.retry(countdown=60, exc=e)
        
        raise CertificateGenerationError(f"Failed to generate certificate after {self.max_retries} attempts: {str(e)}")

@app.task
def cleanup_old_certificates(days_old: int = 30) -> Dict[str, int]:
    """
    Clean up old certificate files
    
    Args:
        days_old: Number of days old files should be to be considered for cleanup
        
    Returns:
        Dictionary with cleanup statistics
    """
    from datetime import timedelta
    
    cutoff_date = datetime.now() - timedelta(days=days_old)
    cleaned_count = 0
    total_size_mb = 0
    
    for cert_file in CERTIFICATES_DIR.glob("*.pdf"):
        file_time = datetime.fromtimestamp(cert_file.stat().st_mtime)
        if file_time < cutoff_date:
            size_mb = cert_file.stat().st_size / (1024 * 1024)
            cert_file.unlink()
            cleaned_count += 1
            total_size_mb += size_mb
    
    # Clean temp directory
    for temp_file in TEMP_DIR.glob("*"):
        file_time = datetime.fromtimestamp(temp_file.stat().st_mtime)
        if file_time < cutoff_date:
            temp_file.unlink()
    
    logger.info(f"Cleanup completed: {cleaned_count} files removed, {total_size_mb:.2f} MB freed")
    
    return {
        'files_removed': cleaned_count,
        'space_freed_mb': round(total_size_mb, 2)
    }

@app.task
def health_check() -> Dict[str, Any]:
    """
    Health check task for monitoring
    
    Returns:
        System health status
    """
    status = {
        'timestamp': datetime.now().isoformat(),
        'template_exists': TEMPLATE_PATH.exists(),
        'font_exists': FONT_PATH.exists(),
        'directories_writable': True,
        'ffmpeg_available': False,
        'imagemagick_available': False
    }
    
    # Check directory permissions
    try:
        test_file = TEMP_DIR / "health_check.tmp"
        test_file.touch()
        test_file.unlink()
    except Exception:
        status['directories_writable'] = False
    
    # Check FFmpeg availability
    try:
        subprocess.run(['ffmpeg', '-version'], capture_output=True, check=True)
        status['ffmpeg_available'] = True
    except (subprocess.CalledProcessError, FileNotFoundError):
        pass
    
    # Check ImageMagick availability
    try:
        subprocess.run(['convert', '-version'], capture_output=True, check=True)
        status['imagemagick_available'] = True
    except (subprocess.CalledProcessError, FileNotFoundError):
        pass
    
    return status

if __name__ == "__main__":
    # For testing purposes
    test_data = {
        "user_name": "Test User",
        "college": "Test University",
        "certificate_id": f"TEST-{datetime.now().strftime('%Y%m%d-%H%M%S')}",
        "issued_at": datetime.now().isoformat(),
        "topic": "Test Topic"
    }
    
    try:
        result = generate_certificate(test_data)
        print(f"Test certificate generated: {result}")
    except Exception as e:
        print(f"Test failed: {e}")