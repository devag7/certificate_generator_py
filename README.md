# 🎓 Professional Certificate Generator

> **Created by [devag7 (Dev Agarwalla)](https://github.com/devag7)**  
> Generate beautiful, professional certificates with QR codes in seconds!

[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![FFmpeg](https://img.shields.io/badge/FFmpeg-Required-red.svg)](https://ffmpeg.org/)

## ✨ What This Project Does

This is a **complete certificate generation system** that automatically creates professional PDF certificates with:

- 📝 **Custom text** (names, courses, dates, etc.)
- 🔍 **QR codes** for verification
- 🎨 **Beautiful design** using your template
- ⚡ **Fast processing** (under 1 second per certificate)
- 📄 **PDF output** ready for printing or sharing

Perfect for schools, training centers, online courses, or any organization that issues certificates!

## 🎯 Quick Demo

**Input:**
```python
{
    "user_name": "John Doe",
    "college": "Tech Academy", 
    "topic": "Python Programming",
    "certificate_id": "CERT-2024-001"
}
```

**Output:** Beautiful PDF certificate with QR code verification!

## 🚀 Super Quick Start (3 Steps)

### 1️⃣ Install Requirements
```bash
# macOS
brew install ffmpeg imagemagick

# Ubuntu/Linux
sudo apt install ffmpeg imagemagick

# Windows (with Chocolatey)
choco install ffmpeg imagemagick
```

### 2️⃣ Setup Project
```bash
git clone https://github.com/devag7/certificate-generator.git
cd certificate-generator
pip install -r requirements.txt
```

### 3️⃣ Generate Your First Certificate
```bash
python producer.py
```

**That's it!** Your certificate will be in the `certificates/` folder! 🎉

## 📁 Project Structure

```
certificate-generator/
├── 📜 producer.py          # Main script to generate certificates
├── ⚙️ tasks.py             # Core generation logic  
├── 🛠️ utils.py             # Helper functions
├── 🧪 test_suite.py        # Tests
├── 📋 requirements.txt     # Dependencies
├── 🐳 Dockerfile          # Docker setup
├── 📄 templates/           # Certificate template images
├── 🔤 fonts/               # Font files
└── 📑 certificates/        # Generated certificates (created automatically)
```

## 🎨 How to Use

### Method 1: Simple Generation (Recommended for beginners)

1. **Edit the data** in `producer.py`:
```python
cert_data = {
    "user_name": "Your Name Here",        # Student/recipient name
    "college": "Your Institution",        # School/company name  
    "topic": "Course Name",               # What the certificate is for
    "certificate_id": "CERT-001",         # Unique ID
    "issued_at": "2024-06-10"            # Date issued
}
```

2. **Run the generator**:
```bash
python producer.py
```

3. **Find your certificate** in the `certificates/` folder!

### Method 2: Direct Python Usage

```python
from tasks import generate_certificate

# Your certificate data
data = {
    "user_name": "Jane Smith",
    "college": "Digital University", 
    "topic": "Web Development",
    "certificate_id": "WEB-2024-001",
    "issued_at": "2024-06-10T15:30:00"
}

# Generate certificate
certificate_path = generate_certificate(data)
print(f"Certificate created: {certificate_path}")
```

### Method 3: Batch Generation (Multiple Certificates)

```python
from tasks import generate_certificate

# List of students
students = [
    {"user_name": "Alice Johnson", "college": "Tech Academy", "topic": "Python Basics"},
    {"user_name": "Bob Smith", "college": "Code School", "topic": "Data Science"},
    {"user_name": "Carol Williams", "college": "Dev Institute", "topic": "Web Design"}
]

# Generate certificates for all students
for student in students:
    student["certificate_id"] = f"BATCH-{student['user_name'].replace(' ', '-')}"
    student["issued_at"] = "2024-06-10"
    
    certificate_path = generate_certificate(student)
    print(f"✅ Generated: {certificate_path}")
```

## 🎨 Customize Your Certificates

### Change the Template

1. **Add your template image** to the `templates/` folder
2. **Update the path** in `tasks.py`:
```python
TEMPLATE_PATH = BASE_DIR / "templates" / "your_template.jpg"  # Change this line
```

### Adjust Text Positions

Edit the text positions in `tasks.py` (around line 100):
```python
filter_chain = (
    f"drawtext=text='{esc['name']}':x=90:y=880:fontsize=50:"      # Name position
    f"fontfile='{font_path}':fontcolor=black,"
    f"drawtext=text='{esc['college']}':x=90:y=1050:fontsize=45:"  # College position  
    f"fontfile='{font_path}':fontcolor=black,"
    # Adjust x,y coordinates for your template
)
```

### Use Different Fonts

1. **Add `.ttf` font files** to the `fonts/` folder
2. **Update font path** in `tasks.py`:
```python
FONT_PATH = BASE_DIR / "fonts" / "your_font.ttf"  # Change this line
```

## 🔧 Advanced Features

### Async Processing (For High Volume)

**Start Redis and Celery** (for processing many certificates):
```bash
# Terminal 1: Start Redis
redis-server

# Terminal 2: Start Celery worker  
celery -A tasks worker --loglevel=info

# Terminal 3: Generate certificates
python producer.py  # Will now use async processing
```

### Environment Configuration

Create `.env` file for custom settings:
```env
# Copy from .env.example and modify
ASYNC_MODE=false           # true for async processing
FONT_SIZE_NAME=50         # Name text size
FONT_SIZE_COLLEGE=45      # College text size  
OUTPUT_DIR=certificates   # Where to save certificates
```

### Docker Deployment

```bash
# Build and run with Docker
docker-compose up -d

# Generate certificates via API
curl -X POST http://localhost:8000/generate \
  -H "Content-Type: application/json" \
  -d '{"user_name":"Test User","college":"Test College","topic":"Test Course"}'
```

## 🧪 Testing

```bash
# Run all tests
python test_suite.py

# Check system health  
python -c "from tasks import health_check; import json; print(json.dumps(health_check(), indent=2))"
```

## 🐛 Troubleshooting

### "FFmpeg not found"
```bash
# Install FFmpeg
brew install ffmpeg        # macOS
sudo apt install ffmpeg   # Ubuntu
choco install ffmpeg      # Windows
```

### "ImageMagick not found"  
```bash
# Install ImageMagick
brew install imagemagick        # macOS
sudo apt install imagemagick   # Ubuntu
choco install imagemagick      # Windows
```

### "Template not found"
- Make sure `certificate_template.jpg` exists in `templates/` folder
- Check the file path in `tasks.py`

### "Font not found"
- Ensure your font file exists in `fonts/` folder
- The system will use default font if custom font is missing

### PDF Conversion Issues (Ubuntu)
```bash
# Fix ImageMagick policy for PDF
sudo sed -i 's/rights="none" pattern="PDF"/rights="read|write" pattern="PDF"/' /etc/ImageMagick-6/policy.xml
```

## 📊 Performance

- ⚡ **Generation time**: ~200ms per certificate
- 📄 **Output size**: ~200KB per PDF
- 🔍 **QR code**: High resolution, fast scanning
- 💾 **Memory usage**: Minimal (< 50MB)

## 🔍 How It Works

1. **Input Validation** - Checks that all required data is provided
2. **QR Code Generation** - Creates verification QR code with certificate ID  
3. **Text Overlay** - Uses FFmpeg to add text to certificate template
4. **PDF Conversion** - Converts to PDF using ImageMagick
5. **File Optimization** - Compresses output for smaller file size
6. **Cleanup** - Removes temporary files

## 🎯 Use Cases

- 🎓 **Educational institutions** - Course completion certificates
- 🏢 **Corporate training** - Employee certification
- 🌐 **Online courses** - MOOC/e-learning certificates  
- 🏆 **Events & competitions** - Award certificates
- 🤝 **Professional development** - Skill certification

## 🔮 What You Can Build

- **Certificate API** - REST API for certificate generation
- **Web interface** - Upload CSV, generate bulk certificates
- **Integration** - Add to existing LMS/education platforms
- **Verification system** - QR code verification portal
- **White-label solution** - Customize for clients

## 🤝 Contributing

Found a bug? Have an idea? Contributions welcome!

1. Fork the repository
2. Create feature branch: `git checkout -b feature/awesome-feature`
3. Make changes and test: `python test_suite.py`
4. Commit: `git commit -m 'Add awesome feature'`
5. Push: `git push origin feature/awesome-feature`
6. Create Pull Request

## 📞 Need Help?

- 🐛 **Bug reports**: [Create an issue](https://github.com/devag7/certificate-generator/issues)
- 💡 **Feature requests**: [Start a discussion](https://github.com/devag7/certificate-generator/discussions)  
- 📧 **Email**: dev.agarwalla@example.com

## 📄 License

MIT License - feel free to use in your projects!

## 🙏 Credits

**Created with ❤️ by [devag7 (Dev Agarwalla)](https://github.com/devag7)**

Special thanks to:
- FFmpeg team for video/image processing
- ImageMagick for PDF conversion
- Celery for async task processing
- Python community for amazing libraries

---

<div align="center">

**⭐ Found this useful? Give it a star! ⭐**

**🚀 Ready to generate your first certificate? Run `python producer.py` now! 🚀**

</div>
