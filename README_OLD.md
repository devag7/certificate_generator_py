# 🎓 Certificate Generator System

<div align="center">

![Python](https://img.shields.io/badge/Python-3.11+-blue?style=for-the-badge&logo=python)
![Celery](https://img.shields.io/badge/Celery-5.3+-green?style=for-the-badge&logo=celery)
![Redis](https://img.shields.io/badge/Redis-7.0+-red?style=for-the-badge&logo=redis)
![FFmpeg](https://img.shields.io/badge/FFmpeg-Latest-orange?style=for-the-badge&logo=ffmpeg)
![License](https://img.shields.io/badge/License-MIT-yellow?style=for-the-badge)

**Professional Certificate Generation System with Dynamic Content & QR Codes**

*Created by [devag7 (Deva Garwalla)](https://github.com/devag7)*

[Features](#-features) • [Quick Start](#-quick-start) • [Installation](#-installation) • [Usage](#-usage) • [API](#-api-reference) • [Docker](#-docker-deployment) • [Contributing](#-contributing)

</div>

---

## 🌟 Features

✨ **Dynamic Certificate Generation**
- Custom text overlays with professional fonts
- Automated date and ID generation
- Support for international characters and special symbols

🔒 **QR Code Integration**
- Automatic QR code generation for certificate verification
- Customizable QR code content and styling
- High error correction for reliable scanning

⚡ **High Performance**
- Asynchronous processing with Celery
- Sub-second certificate generation
- Optimized file sizes (~220KB per PDF)
- Batch processing capabilities

🛠 **Production Ready**
- Comprehensive error handling and recovery
- Health monitoring and logging
- Docker containerization
- CI/CD pipeline integration

🎨 **Multiple Output Formats**
- High-quality PDF generation
- PNG and JPG support
- Customizable templates and fonts

## 🚀 Quick Start

### Prerequisites
- Python 3.11 or higher
- Redis server
- FFmpeg and ImageMagick

### 5-Minute Setup

1. **Clone the repository**
```bash
git clone https://github.com/your-username/certificate_generator_py.git
cd certificate_generator_py
```

2. **Run the automated setup**
```bash
chmod +x setup.sh
./setup.sh
```

3. **Generate your first certificate**
```bash
source my_project_env/bin/activate
python producer.py
```

That's it! Your certificate will be generated in the `certificates/` directory.

---

## 📋 Detailed Installation

### System Dependencies

**macOS (with Homebrew):**
```bash
brew install python@3.11 redis ffmpeg imagemagick
brew services start redis
```

**Ubuntu/Debian:**
```bash
sudo apt update
sudo apt install python3.11 python3.11-venv redis-server ffmpeg imagemagick
sudo systemctl start redis-server
```

**CentOS/RHEL:**
```bash
sudo dnf install python3.11 redis ffmpeg ImageMagick
sudo systemctl start redis
```

### Project Setup

1. **Create virtual environment**
```bash
python3.11 -m venv my_project_env
source my_project_env/bin/activate  # Linux/macOS
# or
my_project_env\\Scripts\\activate     # Windows
```

2. **Install Python dependencies**
```bash
pip install -r requirements.txt
```

3. **Create required directories**
```bash
mkdir -p certificates temp templates fonts logs pids
```

4. **Add your template and font files**
```bash
# Copy your certificate template to templates/certificate_template.jpg
# Copy your font file to fonts/Open Sans Bold.ttf
```

---

## 🎯 Usage

### Basic Certificate Generation

**Synchronous (for testing):**
```python
from tasks import generate_certificate
from datetime import datetime

cert_data = {
    "user_name": "John Doe",
    "college": "Tech University",
    "certificate_id": f"CERT-{datetime.now().strftime('%Y%m%d-%H%M%S')}",
    "issued_at": datetime.now().isoformat(),
    "topic": "Python Programming"
}

# Generate certificate
certificate_path = generate_certificate(cert_data)
print(f"Certificate generated: {certificate_path}")
```

**Asynchronous (production):**
```python
from tasks import generate_certificate

# Queue certificate generation
result = generate_certificate.delay(cert_data)
print(f"Task ID: {result.id}")

# Get result (optional)
certificate_path = result.get(timeout=300)
```

### Command Line Usage

**Single certificate:**
```bash
ASYNC_MODE=false python producer.py
```

**Batch processing:**
```bash
python producer.py batch
```

### Environment Configuration

Create a `.env` file for custom configuration:
```env
# Celery Settings
CELERY_BROKER_URL=redis://localhost:6379/0
CELERY_RESULT_BACKEND=redis://localhost:6379/0

# Processing Mode
ASYNC_MODE=true
DEV_MODE=false

# Monitoring
WAIT_FOR_RESULT=false
```

---

## 🔧 API Reference

### Core Functions

#### `generate_certificate(data: Dict[str, Any]) -> str`
Generates a certificate with the provided data.

**Parameters:**
- `user_name` (str): Recipient's name (max 100 chars)
- `college` (str): Institution name (max 200 chars)
- `certificate_id` (str): Unique certificate identifier
- `issued_at` (str): ISO format datetime
- `topic` (str): Certificate topic (max 150 chars)

**Returns:**
- Path to generated PDF certificate

**Example:**
```python
data = {
    "user_name": "Alice Johnson",
    "college": "MIT",
    "certificate_id": "MIT-2024-001",
    "issued_at": "2024-06-10T14:30:00",
    "topic": "Machine Learning"
}
path = generate_certificate(data)
```

#### `health_check() -> Dict[str, Any]`
Returns system health status.

#### `cleanup_old_certificates(days_old: int = 30) -> Dict[str, int]`
Cleans up old certificate files.

---

## 🐳 Docker Deployment

### Quick Docker Setup

1. **Build and run with Docker Compose:**
```bash
docker-compose up -d
```

2. **Monitor with Flower:**
Visit `http://localhost:5555` for Celery monitoring.

---

## 🧪 Testing

### Run Test Suite
```bash
source my_project_env/bin/activate
python -m unittest test_suite.py -v
```

### Health Check
```bash
python -c "from tasks import health_check; import json; print(json.dumps(health_check(), indent=2))"
```

---

## 🛠 Troubleshooting

### Common Issues

**1. Certificate generation fails:**
```bash
# Check system dependencies
ffmpeg -version
convert -version
redis-cli ping

# Check file permissions
ls -la templates/certificate_template.jpg
ls -la fonts/Open\ Sans\ Bold.ttf
```

**2. Celery worker not starting:**
```bash
# Check Redis connection
redis-cli ping

# Check logs
tail -f logs/worker.log

# Test simple task
python -c "from tasks import health_check; print(health_check())"
```

---

## 📄 License

This project is licensed under the MIT License.

**Created with ❤️ by [devag7 (Deva Garwalla)](https://github.com/devag7)**

---

## 👥 Credits

### Created by
**[Deva Garwalla (devag7)](https://github.com/devag7)**
- 🎯 System Architecture & Design
- 💻 Core Development
- 🔧 Performance Optimization
- 📚 Documentation

### Technologies Used
- **Python 3.11+** - Core language
- **Celery 5.3+** - Asynchronous task processing
- **Redis 7.0+** - Message broker and result backend
- **FFmpeg** - Video/image processing
- **ImageMagick** - Image manipulation
- **Pillow** - Python image processing
- **QRCode** - QR code generation