"""
Certificate Generation Utilities
================================

Author: devag7 (Deva Garwalla)
Description: Utility functions for certificate generation including QR code generation
             and date formatting.
"""

import qrcode
from datetime import datetime
from pathlib import Path
from typing import Union

def generate_qr_code(certificate_id: str, output_dir: Union[str, Path] = "temp") -> Path:
    """
    Generate QR code for certificate ID
    
    Args:
        certificate_id: The certificate ID to encode in QR code
        output_dir: Directory to save the QR code image
        
    Returns:
        Path to the generated QR code image
    """
    # Ensure output directory exists
    output_path = Path(output_dir)
    output_path.mkdir(exist_ok=True)
    
    # Create QR code with optimized settings
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_H,
        box_size=10,
        border=4,
    )
    
    # Add certificate verification URL or just the ID
    qr_data = f"Certificate ID: {certificate_id}"
    # You can modify this to include a verification URL:
    # qr_data = f"https://yoursite.com/verify/{certificate_id}"
    
    qr.add_data(qr_data)
    qr.make(fit=True)
    
    # Create image with custom colors
    img = qr.make_image(
        fill_color="#2c3e50",  # Dark blue-gray
        back_color="white"
    )
    
    # Save QR code
    qr_path = output_path / f"{certificate_id}_qr.png"
    img.save(qr_path)
    
    return qr_path

def format_datetime(iso_str: str) -> str:
    """
    Format ISO datetime string to human-readable format
    
    Args:
        iso_str: ISO format datetime string
        
    Returns:
        Formatted date string
    """
    try:
        dt = datetime.fromisoformat(iso_str)
        return dt.strftime("%d-%b-%Y %H:%M")
    except ValueError:
        # Fallback for any parsing issues
        return "Invalid Date"

def validate_certificate_id(certificate_id: str) -> bool:
    """
    Validate certificate ID format
    
    Args:
        certificate_id: Certificate ID to validate
        
    Returns:
        True if valid, False otherwise
    """
    if not certificate_id or len(certificate_id) < 5:
        return False
    
    # Basic validation - adjust based on your requirements
    # Expected format: CERT-XXXXXXXXXXXXXXXX or similar
    allowed_chars = set("ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789-_")
    return all(c in allowed_chars for c in certificate_id.upper())

def get_file_size_mb(file_path: Union[str, Path]) -> float:
    """
    Get file size in megabytes
    
    Args:
        file_path: Path to the file
        
    Returns:
        File size in MB
    """
    path = Path(file_path)
    if path.exists():
        return path.stat().st_size / (1024 * 1024)
    return 0.0

def cleanup_temp_files(temp_dir: Union[str, Path] = "temp", max_age_hours: int = 24):
    """
    Clean up temporary files older than specified hours
    
    Args:
        temp_dir: Directory containing temporary files
        max_age_hours: Maximum age in hours for files to be kept
    """
    import time
    
    temp_path = Path(temp_dir)
    if not temp_path.exists():
        return
    
    current_time = time.time()
    cutoff_time = current_time - (max_age_hours * 3600)
    
    for file_path in temp_path.glob("*"):
        if file_path.is_file() and file_path.stat().st_mtime < cutoff_time:
            try:
                file_path.unlink()
            except OSError:
                pass  # Ignore files that can't be deleted


# Additional utility functions can be added here as needed
# This module provides core utilities for the certificate generation system