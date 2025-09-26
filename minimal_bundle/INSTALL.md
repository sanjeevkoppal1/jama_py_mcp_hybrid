# 📦 Jama Python MCP Server - Minimal Offline Bundle

## 🚀 Quick Installation

### Linux/macOS:
```bash
./install.sh
```

### Windows:
```cmd
install.bat
```

### Manual Installation:
```bash
# Install dependencies
pip3 install --find-links ./wheels --no-index wheels/*.whl wheels/*.tar.gz

# Install spaCy model (requires internet - one time only)
python3 -m spacy download en_core_web_sm

# Test installation
python3 test_tools.py
```

## 📋 What's Included

- **Essential Python packages** (~200-300MB)
- **Complete source code** with all 11 MCP tools
- **Sample data** for testing without Jama Connect
- **Installation scripts** for Linux/Mac/Windows

## ✅ Testing

```bash
# Test all components
python3 test_tools.py

# Test file ingestion
python3 create_samples.py
python3 test_file_ingestion.py  

# Run test server
python3 simple_main.py
```

## 🔧 Configuration

1. Copy `.env.example` to `.env`
2. Edit `.env` with your Jama Connect credentials
3. Run `python3 main.py` for production

## 📊 Bundle Size

- **Minimal bundle**: ~300-400MB (vs 1.3GB full bundle)
- **Core functionality**: All 11 MCP tools included
- **NLP capabilities**: Business rule extraction working
- **File formats**: CSV, JSON, Excel, Text support

✅ **Ready for air-gapped deployment!**
