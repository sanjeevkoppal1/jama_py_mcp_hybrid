@echo off
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
    xcopy /E /I "./spacy_models/en_core_web_sm" "%TEMP%\en_core_web_sm"
    pip install "%TEMP%\en_core_web_sm"
) else (
    pip install --no-index --find-links ./spacy_models spacy_models/*.tar.gz
)

echo 📁 Setting up project...
xcopy /E /I project\* .

echo 🧪 Testing installation...
python -c "import mcp, spacy, pandas; print('✅ Dependencies OK'); nlp=spacy.load('en_core_web_sm'); print('✅ spaCy model OK'); print('🎉 Installation successful!')"

echo ✅ Installation complete!
echo 📖 Run 'python simple_main.py' to test
echo 🚀 Run 'python main.py' for production
pause
