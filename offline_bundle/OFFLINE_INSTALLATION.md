# 📦 Jama Python MCP Server - Offline Installation

This bundle contains all dependencies needed to install the Jama Python MCP Server in an air-gapped environment.

## 📋 Prerequisites

- Python 3.9 or higher
- pip package manager
- ~2GB free disk space

## 🚀 Installation Instructions

### Linux/macOS:
```bash
# Extract the bundle
tar -xzf jama-mcp-offline-bundle.tar.gz
cd offline_bundle

# Run installation script
./install_offline.sh
```

### Windows:
```cmd
REM Extract the bundle and navigate to it
cd offline_bundle

REM Run installation script  
install_offline.bat
```

### Manual Installation:
```bash
# Install Python dependencies
pip install --no-index --find-links ./dependencies --force-reinstall dependencies/*.whl dependencies/*.tar.gz

# Install spaCy model
pip install --no-index --find-links ./spacy_models spacy_models/*.tar.gz

# Copy project files
cp -r project/* .

# Test installation
python test_tools.py
```

## 📁 Bundle Contents

- `dependencies/` - All Python packages (.whl and .tar.gz files)
- `spacy_models/` - spaCy English model
- `project/` - Complete Jama MCP Server source code
- `install_offline.sh` - Linux/Mac installation script
- `install_offline.bat` - Windows installation script
- `requirements.txt` - List of all dependencies

## ✅ Verification

After installation, test the server:

```bash
# Test basic functionality
python test_tools.py

# Test file ingestion
python create_samples.py
python test_file_ingestion.py

# Run in test mode
python simple_main.py

# Run production server (requires .env configuration)
python main.py
```

## 🛠️ Troubleshooting

If installation fails:

1. **Python version**: Ensure Python 3.9+
2. **Permissions**: Run with appropriate permissions
3. **Disk space**: Ensure 2GB+ free space
4. **Manual install**: Use manual installation steps above

## 📊 File Sizes (Approximate)

- Python dependencies: ~1.2GB
- spaCy model: ~50MB  
- Project files: ~5MB
- **Total bundle size: ~1.3GB**

## 🎯 Next Steps

1. Configure your .env file with Jama Connect credentials
2. Use file ingestion for testing without Jama Connect
3. Start with `python simple_main.py` for basic testing
4. Deploy with `python main.py` for production use

✅ **Your air-gapped Jama Python MCP Server is ready!**
