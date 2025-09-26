#!/usr/bin/env python3
"""
Create offline bundle with all dependencies for air-gapped deployment
"""

import os
import subprocess
import sys
import shutil
from pathlib import Path

def create_offline_bundle():
    """Create a complete offline bundle with all dependencies."""
    print("📦 Creating Offline Bundle for Jama Python MCP Server")
    print("=" * 60)
    
    project_dir = Path(__file__).parent
    bundle_dir = project_dir / "offline_bundle"
    
    # Create bundle directory
    if bundle_dir.exists():
        shutil.rmtree(bundle_dir)
    bundle_dir.mkdir()
    
    print(f"📁 Bundle directory: {bundle_dir}")
    
    # Step 1: Download all Python dependencies
    print("\n1️⃣ Downloading Python Dependencies...")
    deps_dir = bundle_dir / "dependencies"
    deps_dir.mkdir()
    
    # Get all dependencies from pyproject.toml
    dependencies = [
        # Core MCP and web
        "mcp>=0.4.0",
        "fastapi>=0.104.0",
        "uvicorn[standard]>=0.24.0",
        "requests>=2.31.0",
        "aiohttp>=3.9.0",
        "httpx>=0.25.0",
        
        # Data processing
        "pandas>=2.1.0",
        "numpy>=1.24.0",
        
        # NLP libraries
        "spacy>=3.7.0",
        "transformers>=4.35.0",
        "sentence-transformers>=2.2.0",
        "nltk>=3.8.0",
        "scikit-learn>=1.3.0",
        "textblob>=0.17.0",
        
        # Vector database (optional)
        "chromadb>=0.4.0",
        "faiss-cpu>=1.7.4",
        
        # Configuration
        "pydantic>=2.5.0",
        "pydantic-settings>=2.1.0",
        "python-dotenv>=1.0.0",
        
        # File processing
        "openpyxl>=3.1.0",
        
        # Utilities
        "rich>=13.7.0",
        "typer>=0.9.0",
    ]
    
    # Download all packages
    cmd = [
        sys.executable, "-m", "pip", "download",
        "--dest", str(deps_dir),
        "--no-deps",  # Download without dependencies first
    ] + dependencies
    
    try:
        print("   📥 Downloading main packages...")
        subprocess.run(cmd, check=True, capture_output=True)
        
        # Now download with all dependencies
        cmd_with_deps = [
            sys.executable, "-m", "pip", "download",
            "--dest", str(deps_dir),
        ] + dependencies
        
        print("   📥 Downloading all dependencies...")
        subprocess.run(cmd_with_deps, check=True, capture_output=True)
        
        # Count downloaded files
        wheel_files = list(deps_dir.glob("*.whl")) + list(deps_dir.glob("*.tar.gz"))
        print(f"   ✅ Downloaded {len(wheel_files)} package files")
        
    except subprocess.CalledProcessError as e:
        print(f"   ❌ Error downloading dependencies: {e}")
        return False
    
    # Step 2: Download spaCy model
    print("\n2️⃣ Downloading spaCy Model...")
    spacy_dir = bundle_dir / "spacy_models"
    spacy_dir.mkdir()
    
    try:
        # Download spaCy model
        model_cmd = [
            sys.executable, "-m", "spacy", "download", "en_core_web_sm",
            "--direct"
        ]
        subprocess.run(model_cmd, check=True, capture_output=True)
        
        # Find the downloaded model and copy it
        import spacy
        model_path = spacy.util.find_model("en_core_web_sm")
        if model_path:
            shutil.copytree(model_path, spacy_dir / "en_core_web_sm")
            print("   ✅ spaCy model downloaded and bundled")
        else:
            print("   ⚠️  spaCy model download may have failed")
            
    except Exception as e:
        print(f"   ❌ Error downloading spaCy model: {e}")
        # Try alternative method - download wheel directly
        try:
            spacy_model_cmd = [
                sys.executable, "-m", "pip", "download",
                "--dest", str(spacy_dir),
                "https://github.com/explosion/spacy-models/releases/download/en_core_web_sm-3.8.0/en_core_web_sm-3.8.0.tar.gz"
            ]
            subprocess.run(spacy_model_cmd, check=True, capture_output=True)
            print("   ✅ spaCy model wheel downloaded")
        except:
            print("   ⚠️  Could not download spaCy model - manual download needed")
    
    # Step 3: Copy project files
    print("\n3️⃣ Copying Project Files...")
    project_files_dir = bundle_dir / "project"
    project_files_dir.mkdir()
    
    # Files and directories to copy
    items_to_copy = [
        "src/",
        "sample_data/",
        "config/",
        "main.py",
        "simple_main.py", 
        "test_tools.py",
        "test_file_ingestion.py",
        "create_samples.py",
        "pyproject.toml",
        "README.md",
        "STATUS.md",
        ".env.example"
    ]
    
    for item in items_to_copy:
        src_path = project_dir / item
        if src_path.exists():
            if src_path.is_dir():
                shutil.copytree(src_path, project_files_dir / item, 
                              ignore=shutil.ignore_patterns("__pycache__", "*.pyc"))
            else:
                shutil.copy2(src_path, project_files_dir / item)
            print(f"   📄 Copied {item}")
    
    print("   ✅ Project files copied")
    
    # Step 4: Create installation scripts
    print("\n4️⃣ Creating Installation Scripts...")
    
    # Linux/Mac installation script
    install_script = bundle_dir / "install_offline.sh"
    install_script.write_text('''#!/bin/bash
# Offline Installation Script for Jama Python MCP Server

echo "🚀 Installing Jama Python MCP Server (Offline)"
echo "================================================"

# Check Python version
python3 --version
if [ $? -ne 0 ]; then
    echo "❌ Python 3 is not installed or not in PATH"
    exit 1
fi

echo "📦 Installing Python dependencies..."
pip3 install --no-index --find-links ./dependencies --force-reinstall dependencies/*.whl dependencies/*.tar.gz

echo "🧠 Installing spaCy model..."
if [ -d "./spacy_models/en_core_web_sm" ]; then
    cp -r ./spacy_models/en_core_web_sm /tmp/
    pip3 install /tmp/en_core_web_sm
else
    pip3 install --no-index --find-links ./spacy_models spacy_models/*.tar.gz
fi

echo "📁 Setting up project..."
cp -r project/* .
chmod +x *.py

echo "🧪 Testing installation..."
python3 -c "
import mcp
import spacy
import pandas as pd
import sentence_transformers
print('✅ All core dependencies working')
nlp = spacy.load('en_core_web_sm')
print('✅ spaCy model loaded')
print('🎉 Installation successful!')
"

echo "✅ Installation complete!"
echo "📖 Run 'python3 simple_main.py' to test"
echo "🚀 Run 'python3 main.py' for production"
''')
    install_script.chmod(0o755)
    
    # Windows installation script
    install_bat = bundle_dir / "install_offline.bat"
    install_bat.write_text('''@echo off
REM Offline Installation Script for Jama Python MCP Server

echo 🚀 Installing Jama Python MCP Server (Offline)
echo ================================================

REM Check Python
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Python is not installed or not in PATH
    exit /b 1
)

echo 📦 Installing Python dependencies...
pip install --no-index --find-links ./dependencies --force-reinstall dependencies/*.whl

echo 🧠 Installing spaCy model...
if exist "./spacy_models/en_core_web_sm" (
    xcopy /E /I "./spacy_models/en_core_web_sm" "%TEMP%\\en_core_web_sm"
    pip install "%TEMP%\\en_core_web_sm"
) else (
    pip install --no-index --find-links ./spacy_models spacy_models/*.tar.gz
)

echo 📁 Setting up project...
xcopy /E /I project\\* .

echo 🧪 Testing installation...
python -c "import mcp, spacy, pandas; print('✅ Dependencies OK'); nlp=spacy.load('en_core_web_sm'); print('✅ spaCy model OK'); print('🎉 Installation successful!')"

echo ✅ Installation complete!
echo 📖 Run 'python simple_main.py' to test
echo 🚀 Run 'python main.py' for production
pause
''')
    
    # Step 5: Create requirements.txt for reference
    requirements_file = bundle_dir / "requirements.txt"
    requirements_file.write_text('\n'.join(dependencies))
    
    # Step 6: Create README for offline bundle
    offline_readme = bundle_dir / "OFFLINE_INSTALLATION.md"
    offline_readme.write_text('''# 📦 Jama Python MCP Server - Offline Installation

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
''')
    
    # Step 7: Create bundle package info
    print("\n5️⃣ Creating Bundle Information...")
    
    bundle_info = {
        "name": "Jama Python MCP Server Offline Bundle",
        "version": "1.0.0",
        "created": str(subprocess.run(["date"], capture_output=True, text=True).stdout.strip()),
        "python_packages": len(list(deps_dir.glob("*.whl")) + list(deps_dir.glob("*.tar.gz"))),
        "spacy_model": "en_core_web_sm",
        "total_size_mb": sum(f.stat().st_size for f in bundle_dir.rglob('*') if f.is_file()) / 1024 / 1024
    }
    
    info_file = bundle_dir / "bundle_info.json"
    import json
    info_file.write_text(json.dumps(bundle_info, indent=2))
    
    print(f"   ✅ Bundle created successfully")
    print(f"   📦 Total size: {bundle_info['total_size_mb']:.1f} MB")
    print(f"   🐍 Python packages: {bundle_info['python_packages']}")
    
    # Step 8: Create archive
    print("\n6️⃣ Creating Archive...")
    archive_name = "jama-mcp-offline-bundle"
    
    try:
        # Create tar.gz archive
        shutil.make_archive(
            str(project_dir / archive_name), 
            'gztar', 
            str(bundle_dir.parent), 
            bundle_dir.name
        )
        archive_path = project_dir / f"{archive_name}.tar.gz"
        archive_size = archive_path.stat().st_size / 1024 / 1024
        
        print(f"   ✅ Archive created: {archive_path}")
        print(f"   📦 Archive size: {archive_size:.1f} MB")
        
    except Exception as e:
        print(f"   ⚠️  Could not create archive: {e}")
        print(f"   📁 Bundle available in: {bundle_dir}")
    
    # Final summary
    print("\n" + "=" * 60)
    print("🎉 OFFLINE BUNDLE CREATION COMPLETE!")
    print("=" * 60)
    print(f"📦 Bundle location: {bundle_dir}")
    if 'archive_path' in locals():
        print(f"📦 Archive: {archive_path}")
        print(f"📏 Archive size: {archive_size:.1f} MB")
    
    print("\n📋 What's included:")
    print(f"   • {bundle_info['python_packages']} Python packages")
    print(f"   • spaCy English model (en_core_web_sm)")
    print(f"   • Complete Jama MCP Server source code")
    print(f"   • Sample data and test files")
    print(f"   • Installation scripts (Linux/Mac/Windows)")
    print(f"   • Documentation and setup guides")
    
    print("\n🚀 Deployment instructions:")
    print("   1. Transfer the bundle to your air-gapped environment")
    print("   2. Extract: tar -xzf jama-mcp-offline-bundle.tar.gz")
    print("   3. Install: cd offline_bundle && ./install_offline.sh")
    print("   4. Test: python test_tools.py")
    
    return True

if __name__ == "__main__":
    try:
        success = create_offline_bundle()
        if success:
            print("\n✅ Offline bundle created successfully!")
            sys.exit(0)
        else:
            print("\n❌ Bundle creation failed")
            sys.exit(1)
    except KeyboardInterrupt:
        print("\n⚠️  Bundle creation interrupted")
        sys.exit(1)
    except Exception as e:
        print(f"\n💥 Unexpected error: {e}")
        sys.exit(1)