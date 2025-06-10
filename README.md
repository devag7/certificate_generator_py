# 🎓 Professional Certificate Generator

> **Created by [devag7 (Dev Agarwalla)](https://github.com/devag7)**  
> An advanced, production-ready certificate generation system with dynamic content, QR codes, and scalable processing.

[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Celery](https://img.shields.io/badge/Celery-5.3+-green.svg)](https://docs.celeryproject.org/)
[![FFmpeg](https://img.shields.io/badge/FFmpeg-Required-red.svg)](https://ffmpeg.org/)

## 🌟 Features

- ✨ **Dynamic Certificate Generation** - Customizable templates with dynamic text overlays
- 🔍 **QR Code Integration** - Automatic QR code generation for certificate verification
- 📄 **Multiple Output Formats** - PDF, PNG, JPG with optimized file sizes
- ⚡ **High Performance** - Sub-second generation times with optimized processing
- 🔄 **Scalable Processing** - Celery-based async task queue for production environments
- 🛡️ **Robust Error Handling** - Comprehensive validation and retry mechanisms
- 🌍 **International Support** - Unicode and special character compatibility
- 📊 **Monitoring & Logging** - Built-in health checks and detailed logging
- 🧹 **Automatic Cleanup** - Scheduled cleanup of temporary and old files
- 🐳 **Docker Ready** - Complete containerization support

## 📋 Table of Contents

- [Quick Start](#-quick-start)
- [Installation](#-installation)
- [Usage](#-usage)
- [Configuration](#-configuration)
- [API Reference](#-api-reference)
- [Production Deployment](#-production-deployment)
- [Troubleshooting](#-troubleshooting)
- [Contributing](#-contributing)
- [License](#-license)

## 🚀 Quick Start

### Prerequisites

- Python 3.8 or higher
- FFmpeg (for image processing)
- ImageMagick (for PDF conversion)
- Redis (for async processing - optional)

### 30-Second Setup

```bash
# 1. Clone the repository
git clone https://github.com/devag7/certificate-generator.git
cd certificate-generator

# 2. Run the automated setup
chmod +x setup.sh
./setup.sh

# 3. Generate your first certificate!
python producer.py
```

That's it! Your certificate will be generated in the `certificates/` folder.

## 🔧 Installation

### Method 1: Automated Setup (Recommended)

```bash
# Download and run the setup script
curl -O https://raw.githubusercontent.com/devag7/certificate-generator/main/setup.sh
chmod +x setup.sh
./setup.sh
```

### Method 2: Manual Installation

#### Step 1: System Dependencies

**macOS:**
```bash
# Install Homebrew if not already installed
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

# Install dependencies
brew install ffmpeg imagemagick redis
```

**Ubuntu/Debian:**
```bash
sudo apt update
sudo apt install ffmpeg imagemagick redis-server python3-pip python3-venv
```

**Windows:**
```bash
# Install using Chocolatey
choco install ffmpeg imagemagick redis-64
```

#### Step 2: Python Environment

```bash
# Create virtual environment
python3 -m venv certificate_env
source certificate_env/bin/activate  # On Windows: certificate_env\Scripts\activate

# Install Python dependencies
pip install -r requirements.txt
```

#### Step 3: Verify Installation

```bash
# Run health check
python -c "from tasks import health_check; import json; print(json.dumps(health_check(), indent=2))"
```

## 📖 Usage

### Basic Certificate Generation

#### Method 1: Using the Producer Script

```bash
# Generate with default settings
python producer.py

# Generate with custom data (edit producer.py first)
ASYNC_MODE=false python producer.py
```

#### Method 2: Direct Python Usage

```python
from tasks import generate_certificate
from datetime import datetime

# Certificate data
cert_data = {
    "user_name": "John Doe",
    "college": "Tech University",
    "certificate_id": f"CERT-{datetime.now().strftime('%Y%m%d-%H%M%S')}",
    "issued_at": datetime.now().isoformat(),
    "topic": "Python Programming Fundamentals"
}

# Generate certificate
certificate_path = generate_certificate(cert_data)
print(f"Certificate generated: {certificate_path}")
```

### Batch Generation

```python
from producer import batch_generate

# Generate multiple certificates
users = [
    {"user_name": "Alice Smith", "college": "State University", "topic": "Data Science"},
    {"user_name": "Bob Johnson", "college": "Tech Institute", "topic": "Web Development"},
    # Add more users...
]

batch_generate(users)
```

### Async Processing with Celery

```bash
# Start Redis server
redis-server

# Start Celery worker
celery -A tasks worker --loglevel=info

# Queue certificate generation
python -c "
from tasks import generate_certificate
result = generate_certificate.delay({
    'user_name': 'Async User',
    'college': 'Cloud University',
    'certificate_id': 'ASYNC-001',
    'issued_at': '2025-06-10T19:00:00',
    'topic': 'Distributed Systems'
})
print(f'Task ID: {result.id}')
"
```

## ⚙️ Configuration

### Environment Variables

Create a `.env` file in the project root:

```env
# Processing Mode
ASYNC_MODE=false
WAIT_FOR_RESULT=false

# Celery Configuration
CELERY_BROKER_URL=redis://localhost:6379/0
CELERY_RESULT_BACKEND=redis://localhost:6379/0

# File Paths
TEMPLATE_PATH=templates/certificate_template.jpg
FONT_PATH=fonts/Open Sans Bold.ttf
OUTPUT_DIR=certificates

# Quality Settings
IMAGE_QUALITY=85
PDF_DENSITY=200
FONT_SIZE_NAME=50
FONT_SIZE_COLLEGE=45
FONT_SIZE_TOPIC=40

# Cleanup Settings
CLEANUP_DAYS=30
AUTO_CLEANUP=true
```

### Custom Templates

1. **Add your template image** to the `templates/` folder
2. **Update template path** in `tasks.py`:
   ```python
   TEMPLATE_PATH = BASE_DIR / "templates" / "your_template.jpg"
   ```
3. **Adjust text positions** in the `filter_chain` section of `generate_certificate()`:
   ```python
   filter_chain = (
       f"drawtext=text='{esc['name']}':x=90:y=880:fontsize=50:"
       # Modify x, y coordinates for your template
   )
   ```

### Custom Fonts

1. Add `.ttf` font files to the `fonts/` folder
2. Update the font path in `tasks.py`:
   ```python
   FONT_PATH = BASE_DIR / "fonts" / "your_font.ttf"
   ```

## 📚 API Reference

### Core Functions

#### `generate_certificate(data: Dict[str, Any]) -> str`

Generates a certificate with the provided data.

**Parameters:**
- `data` (dict): Certificate information

**Required Fields:**
- `user_name` (str): Recipient's name (max 100 chars)
- `college` (str): Institution name (max 200 chars)
- `certificate_id` (str): Unique certificate identifier
- `issued_at` (str): ISO format datetime
- `topic` (str): Certificate topic/course (max 150 chars)

**Optional Fields:**
- `user_id` (int): User identifier
- `test_id` (int): Test/course identifier

**Returns:**
- `str`: Path to generated certificate PDF

**Example:**
```python
result = generate_certificate({
    "user_name": "Jane Doe",
    "college": "Digital Academy",
    "certificate_id": "DA-2025-001",
    "issued_at": "2025-06-10T14:30:00",
    "topic": "Machine Learning Fundamentals"
})
```

#### `health_check() -> Dict[str, Any]`

Performs system health check.

**Returns:**
- `dict`: System status information

#### `cleanup_old_certificates(days_old: int = 30) -> Dict[str, int]`

Cleans up old certificate files.

**Parameters:**
- `days_old` (int): Age threshold in days

**Returns:**
- `dict`: Cleanup statistics

### Utility Functions

#### `generate_qr_code(certificate_id: str) -> Path`

Generates QR code for certificate verification.

#### `format_datetime(iso_str: str) -> str`

Formats ISO datetime to human-readable format.

#### `validate_certificate_id(certificate_id: str) -> bool`

Validates certificate ID format.

## 🚀 Production Deployment

### Docker Deployment

```bash
# Build and run with Docker Compose
docker-compose up -d

# Scale workers
docker-compose up -d --scale worker=3
```

### Manual Production Setup

```bash
# Deploy to production server
chmod +x deploy.sh
./deploy.sh production

# Start services
systemctl start redis
systemctl start celery-worker
systemctl start certificate-api
```

### Nginx Configuration

```nginx
server {
    listen 80;
    server_name your-domain.com;
    
    location /api/ {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
    
    location /certificates/ {
        alias /path/to/certificates/;
        expires 1d;
    }
}
```

## 🧪 Testing

### Run Test Suite

```bash
# Run all tests
python -m unittest test_suite.py -v

# Run specific test category
python -m unittest test_suite.TestUtils -v
python -m unittest test_suite.TestTasks -v
```

### Performance Testing

```bash
# Performance benchmark
python -c "
import time
from tasks import generate_certificate
from datetime import datetime

# Performance test
start_time = time.time()
for i in range(10):
    generate_certificate({
        'user_name': f'User {i}',
        'college': 'Test University',
        'certificate_id': f'PERF-{i:03d}',
        'issued_at': datetime.now().isoformat(),
        'topic': 'Performance Testing'
    })
end_time = time.time()

print(f'Generated 10 certificates in {end_time - start_time:.2f} seconds')
print(f'Average: {(end_time - start_time)/10:.2f} seconds per certificate')
"
```

## 🔍 Troubleshooting

### Common Issues

#### ❌ "FFmpeg not found"
```bash
# macOS
brew install ffmpeg

# Ubuntu
sudo apt install ffmpeg

# Windows
choco install ffmpeg
```

#### ❌ "ImageMagick convert failed"
```bash
# macOS
brew install imagemagick

# Ubuntu
sudo apt install imagemagick

# Fix policy issues (Ubuntu)
sudo sed -i 's/rights="none" pattern="PDF"/rights="read|write" pattern="PDF"/' /etc/ImageMagick-6/policy.xml
```

#### ❌ "Template not found"
- Ensure `certificate_template.jpg` exists in `templates/` folder
- Check file permissions and path

#### ❌ "Font not found"
- Ensure font file exists in `fonts/` folder
- System will use default font if custom font is missing

#### ❌ "Redis connection failed"
- Start Redis: `redis-server`
- Check Redis status: `redis-cli ping`

### Debug Mode

```bash
# Enable debug logging
export CELERY_LOG_LEVEL=DEBUG
export PYTHONPATH=.

# Run with debug output
python tasks.py
```

### Health Check

```bash
# Quick system check
python -c "
from tasks import health_check
import json
health = health_check()
print('System Status:')
for key, value in health.items():
    status = '✅' if value else '❌'
    if key != 'timestamp':
        print(f'{status} {key.replace('_', ' ').title()}: {value}')
"
```

## 📊 Monitoring

### Celery Monitoring

```bash
# Monitor active tasks
celery -A tasks inspect active

# Monitor worker status
celery -A tasks inspect stats

# Web monitoring with Flower
pip install flower
celery -A tasks flower
# Access at http://localhost:5555
```

### Log Files

```bash
# View application logs
tail -f logs/certificate_generator.log

# View Celery logs
tail -f logs/celery.log
```

## 🏗️ Architecture

### System Components

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Client API    │───▶│  Task Queue     │───▶│   Workers       │
│   (Producer)    │    │   (Celery)      │    │ (Certificate    │
└─────────────────┘    └─────────────────┘    │  Generation)    │
                                              └─────────────────┘
                                                       │
                       ┌─────────────────┐            │
                       │   File System   │◀───────────┘
                       │ (Certificates)  │
                       └─────────────────┘
```

### Data Flow

1. **Input Validation** - Validate certificate data
2. **QR Code Generation** - Create verification QR code
3. **Image Processing** - Apply text overlays with FFmpeg
4. **PDF Conversion** - Convert to PDF with ImageMagick
5. **File Optimization** - Compress and optimize output
6. **Cleanup** - Remove temporary files

## 🤝 Contributing

We welcome contributions! Please follow these guidelines:

### Development Setup

```bash
# Fork and clone the repository
git clone https://github.com/yourusername/certificate-generator.git
cd certificate-generator

# Create development environment
python -m venv dev_env
source dev_env/bin/activate
pip install -r requirements.txt
pip install -r requirements-dev.txt

# Run tests before making changes
python -m unittest test_suite.py
```

### Contribution Process

1. **Fork** the repository
2. **Create** a feature branch: `git checkout -b feature/amazing-feature`
3. **Make** your changes
4. **Add** tests for new functionality
5. **Run** the test suite: `python -m unittest test_suite.py`
6. **Commit** your changes: `git commit -m 'Add amazing feature'`
7. **Push** to the branch: `git push origin feature/amazing-feature`
8. **Create** a Pull Request

### Code Style

- Follow PEP 8 guidelines
- Add docstrings to all functions
- Include type hints where possible
- Add tests for new features
- Update documentation

## 📈 Roadmap

- [ ] **Web Interface** - Django/Flask web interface
- [ ] **REST API** - RESTful API endpoints
- [ ] **Database Integration** - PostgreSQL/MySQL support
- [ ] **Email Integration** - Automatic certificate delivery
- [ ] **Template Editor** - Visual template customization
- [ ] **Bulk Operations** - CSV/Excel import support
- [ ] **Digital Signatures** - Cryptographic certificate signing
- [ ] **Blockchain Verification** - Immutable certificate records

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- **Created by**: [devag7 (Dev Agarwalla)](https://github.com/devag7)
- **FFmpeg Team** - For excellent multimedia processing
- **ImageMagick** - For powerful image manipulation
- **Celery Project** - For distributed task processing
- **QR Code Library** - For QR code generation

## 📞 Support

- **GitHub Issues**: [Report bugs or request features](https://github.com/devag7/certificate-generator/issues)
- **Documentation**: [Full documentation](https://github.com/devag7/certificate-generator/wiki)
- **Email**: dev.agarwalla@example.com

---

<div align="center">

**⭐ If this project helped you, please give it a star! ⭐**

Made with ❤️ by [devag7 (Dev Agarwalla)](https://github.com/devag7)

</div>
