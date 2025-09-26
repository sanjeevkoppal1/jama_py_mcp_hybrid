#!/bin/bash
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
