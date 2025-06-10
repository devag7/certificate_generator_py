"""
Certificate Generation Producer
==============================

Author: devag7 (Deva Garwalla)
Description: Certificate generation client for testing and production use.
             Supports both synchronous and asynchronous processing modes.

Usage:
    python producer.py  # Run with default test data
    
    # For custom data, modify cert_data dictionary below
"""

from tasks import generate_certificate
import os
import sys
from pathlib import Path
from datetime import datetime

def main():
    """Main function to generate certificates"""
    
    # Sample certificate data - modify as needed
    cert_data = {
        "user_name": "Deva Garwalla",
        "college": "Computer Society of India", 
        "certificate_id": f"CSI-CERT-{datetime.now().strftime('%Y%m%d-%H%M%S')}",
        "issued_at": datetime.now().isoformat(),
        "topic": "Advanced Python Development & Automation",
        # Optional fields
        "user_id": 7,
        "test_id": 2025
    }
    
    print("🎓 Certificate Generation System - devag7")
    print("=" * 50)
    print(f"Generating certificate for: {cert_data['user_name']}")
    print(f"Institution: {cert_data['college']}")
    print(f"Topic: {cert_data['topic']}")
    print(f"Certificate ID: {cert_data['certificate_id']}")
    print("-" * 50)
    
    try:
        # Choose processing mode
        async_mode = os.getenv('ASYNC_MODE', 'true').lower() == 'true'
        
        if async_mode:
            # Asynchronous processing with Celery (production mode)
            print("🔄 Starting asynchronous processing...")
            result = generate_certificate.delay(cert_data)
            print(f"✅ Task queued successfully!")
            print(f"📋 Task ID: {result.id}")
            print(f"🔍 Monitor task status with: celery -A tasks inspect active")
            
            # Optional: Wait for result (with timeout)
            if os.getenv('WAIT_FOR_RESULT', 'false').lower() == 'true':
                print("⏳ Waiting for result...")
                try:
                    certificate_path = result.get(timeout=300)  # 5 minute timeout
                    print(f"✅ Certificate generated successfully!")
                    print(f"📁 Location: {certificate_path}")
                    
                    # Verify file exists
                    if Path(certificate_path).exists():
                        size_mb = Path(certificate_path).stat().st_size / (1024 * 1024)
                        print(f"📊 File size: {size_mb:.2f} MB")
                    else:
                        print("⚠️  Warning: Certificate file not found at expected location")
                        
                except Exception as wait_error:
                    print(f"⚠️  Task timeout or error: {wait_error}")
                    print("💡 Certificate may still be processing. Check Celery worker logs.")
        else:
            # Synchronous processing (testing/debugging mode)
            print("🔄 Starting synchronous processing...")
            certificate_path = generate_certificate(cert_data)
            print(f"✅ Certificate generated successfully!")
            print(f"📁 Location: {certificate_path}")
            
            # Verify and show file info
            if Path(certificate_path).exists():
                size_mb = Path(certificate_path).stat().st_size / (1024 * 1024)
                print(f"📊 File size: {size_mb:.2f} MB")
                print(f"🔍 File exists: {Path(certificate_path).exists()}")
            else:
                print("❌ Error: Certificate file not found!")
    
    except Exception as e:
        print(f"❌ Error during certificate generation: {str(e)}")
        print("💡 Troubleshooting tips:")
        print("   - Ensure all required dependencies are installed")
        print("   - Check if template and font files exist")
        print("   - Verify FFmpeg and ImageMagick are installed")
        print("   - For async mode, ensure Redis/Celery broker is running")
        sys.exit(1)

def batch_generate():
    """Generate multiple certificates for testing"""
    print("🎯 Batch Certificate Generation")
    print("=" * 50)
    
    # Sample batch data
    batch_data = [
        {
            "user_name": "Alice Johnson",
            "college": "Tech University",
            "certificate_id": f"BATCH-001-{datetime.now().strftime('%Y%m%d')}",
            "issued_at": datetime.now().isoformat(),
            "topic": "Data Science Fundamentals"
        },
        {
            "user_name": "Bob Smith",
            "college": "Engineering College",
            "certificate_id": f"BATCH-002-{datetime.now().strftime('%Y%m%d')}",
            "issued_at": datetime.now().isoformat(),
            "topic": "Machine Learning Applications"
        },
        {
            "user_name": "Carol Davis",
            "college": "Computer Science Institute",
            "certificate_id": f"BATCH-003-{datetime.now().strftime('%Y%m%d')}",
            "issued_at": datetime.now().isoformat(),
            "topic": "Advanced Algorithms"
        }
    ]
    
    tasks = []
    for data in batch_data:
        try:
            task = generate_certificate.delay(data)
            tasks.append((task, data['user_name']))
            print(f"✅ Queued: {data['user_name']} - Task ID: {task.id}")
        except Exception as e:
            print(f"❌ Failed to queue {data['user_name']}: {e}")
    
    print(f"\n🎯 Batch processing started: {len(tasks)} certificates queued")
    print("📋 Monitor progress with: celery -A tasks inspect active")

if __name__ == "__main__":
    # Check command line arguments
    if len(sys.argv) > 1 and sys.argv[1] == "batch":
        batch_generate()
    else:
        main()
