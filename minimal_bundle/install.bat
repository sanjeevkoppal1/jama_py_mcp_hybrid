@echo off
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
