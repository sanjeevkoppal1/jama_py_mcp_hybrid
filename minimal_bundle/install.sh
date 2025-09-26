#!/bin/bash
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
