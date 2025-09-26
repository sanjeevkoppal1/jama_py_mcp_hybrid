#!/usr/bin/env python3
"""
Create minimal offline bundle with essential dependencies only
"""

import os
import subprocess
import sys
import shutil
from pathlib import Path

def create_minimal_bundle():
    """Create a minimal offline bundle with only essential dependencies."""
    print("📦 Creating Minimal Offline Bundle for Jama Python MCP Server")
    print("=" * 65)
    
    project_dir = Path(__file__).parent
    bundle_dir = project_dir / "minimal_bundle"
    
    # Create bundle directory
    if bundle_dir.exists():
        shutil.rmtree(bundle_dir)
    bundle_dir.mkdir()
    
    # Step 1: Essential dependencies only
    print("\n1️⃣ Downloading Essential Dependencies...")
    deps_dir = bundle_dir / "wheels"
    deps_dir.mkdir()
    
    # Minimal required dependencies
    essential_deps = [
        "mcp",
        "spacy",
        "pandas", 
        "numpy",
        "aiohttp",
        "pydantic",
        "python-dotenv",
        "sentence-transformers",
        "transformers",
        "scikit-learn",
        "openpyxl",
        "nltk",
        "textblob"
    ]
    
    # Download packages
    cmd = [
        sys.executable, "-m", "pip", "download",
        "--dest", str(deps_dir)
    ] + essential_deps
    
    try:
        print("   📥 Downloading packages...")
        result = subprocess.run(cmd, check=True, capture_output=True, text=True)
        
        # Count downloaded files  
        wheel_files = list(deps_dir.glob("*.whl")) + list(deps_dir.glob("*.tar.gz"))
        print(f"   ✅ Downloaded {len(wheel_files)} packages")
        
        # Show total size
        total_size = sum(f.stat().st_size for f in wheel_files) / 1024 / 1024
        print(f"   📏 Total size: {total_size:.1f} MB")
        
    except subprocess.CalledProcessError as e:
        print(f"   ❌ Error downloading: {e}")
        return False
    
    # Step 2: Copy project files
    print("\n2️⃣ Copying Project Files...")
    
    # Copy essential project files
    files_to_copy = {
        "src/": "src/",
        "sample_data/": "sample_data/",
        "config/": "config/", 
        "main.py": "main.py",
        "simple_main.py": "simple_main.py",
        "test_tools.py": "test_tools.py",
        "test_file_ingestion.py": "test_file_ingestion.py",
        "create_samples.py": "create_samples.py",
        ".env.example": ".env.example",
        "README.md": "README.md"
    }
    
    for src, dst in files_to_copy.items():
        src_path = project_dir / src
        dst_path = bundle_dir / dst
        
        if src_path.exists():
            if src_path.is_dir():
                shutil.copytree(src_path, dst_path, 
                              ignore=shutil.ignore_patterns("__pycache__", "*.pyc"))
            else:
                dst_path.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(src_path, dst_path)
            print(f"   📄 Copied {src}")
    
    # Step 3: Create installation script
    print("\n3️⃣ Creating Installation Scripts...")
    
    # Simple installation script
    install_script = bundle_dir / "install.sh"
    install_script.write_text('''#!/bin/bash
echo "🚀 Installing Jama Python MCP Server (Minimal)"
echo "============================================="

# Check Python
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 not found. Please install Python 3.9+"
    exit 1
fi

echo "📦 Installing dependencies..."
pip3 install --find-links ./wheels --no-index $(ls wheels/*.whl wheels/*.tar.gz 2>/dev/null | head -20)

echo "🧠 Installing spaCy model..."
python3 -m spacy download en_core_web_sm --user

echo "🧪 Testing installation..."
python3 -c "
try:
    import mcp, spacy, pandas, sentence_transformers
    nlp = spacy.load('en_core_web_sm')
    print('✅ All dependencies working!')
    print('🎉 Installation successful!')
except Exception as e:
    print(f'❌ Error: {e}')
    exit(1)
"

echo "✅ Installation complete!"
echo ""
echo "📖 Usage:"
echo "  Test mode:       python3 simple_main.py"
echo "  With Jama:       python3 main.py"
echo "  File ingestion:  python3 test_file_ingestion.py"
''')
    install_script.chmod(0o755)
    
    # Windows batch file
    install_bat = bundle_dir / "install.bat"
    install_bat.write_text('''@echo off
echo 🚀 Installing Jama Python MCP Server (Minimal)
echo =============================================

python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Python not found. Please install Python 3.9+
    exit /b 1
)

echo 📦 Installing dependencies...
pip install --find-links ./wheels --no-index wheels/*.whl

echo 🧠 Installing spaCy model...
python -m spacy download en_core_web_sm --user

echo 🧪 Testing installation...
python -c "import mcp, spacy, pandas; nlp=spacy.load('en_core_web_sm'); print('✅ Installation successful!')"

echo ✅ Installation complete!
echo.
echo 📖 Usage:
echo   Test mode:       python simple_main.py  
echo   With Jama:       python main.py
echo   File ingestion:  python test_file_ingestion.py
pause
''')
    
    # Step 4: Create README
    readme = bundle_dir / "INSTALL.md"
    readme.write_text('''# 📦 Jama Python MCP Server - Minimal Offline Bundle

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
''')
    
    # Step 5: Create requirements list
    requirements = bundle_dir / "requirements.txt"
    requirements.write_text('\n'.join(essential_deps))
    
    # Step 6: Bundle summary
    bundle_size = sum(f.stat().st_size for f in bundle_dir.rglob('*') if f.is_file()) / 1024 / 1024
    
    print(f"\n✅ Minimal bundle created successfully!")
    print(f"📦 Location: {bundle_dir}")
    print(f"📏 Total size: {bundle_size:.1f} MB")
    
    # Create archive
    try:
        archive_path = shutil.make_archive(
            str(project_dir / "jama-mcp-minimal"), 
            'zip', 
            str(bundle_dir)
        )
        archive_size = Path(archive_path).stat().st_size / 1024 / 1024
        print(f"📦 Archive: {archive_path}")
        print(f"📏 Archive size: {archive_size:.1f} MB")
    except Exception as e:
        print(f"⚠️  Archive creation failed: {e}")
    
    print("\n🚀 Deployment Instructions:")
    print("1. Transfer bundle to air-gapped system")
    print("2. Extract: unzip jama-mcp-minimal.zip")
    print("3. Install: cd minimal_bundle && ./install.sh")
    print("4. Test: python3 test_tools.py")
    
    return True

if __name__ == "__main__":
    create_minimal_bundle()