#!/usr/bin/env python3
"""
Test server startup without running indefinitely
"""

import sys
import os
sys.path.insert(0, '/Users/sanjeev/development/pocs/claude/jama-python-mcp-server/src')

from dotenv import load_dotenv

def test_startup():
    print("🧪 Testing Server Startup Configuration")
    
    # Load .env file
    load_dotenv()
    print("✅ Loaded .env file")
    
    # Check required variables
    jama_url = os.getenv("JAMA_BASE_URL")
    jama_token = os.getenv("JAMA_API_TOKEN") 
    jama_username = os.getenv("JAMA_USERNAME")
    
    print(f"📡 Jama URL: {jama_url}")
    print(f"🔑 Has API Token: {'Yes' if jama_token else 'No'}")
    print(f"👤 Has Username: {'Yes' if jama_username else 'No'}")
    
    if jama_url:
        print("✅ Required JAMA_BASE_URL is set")
    else:
        print("❌ JAMA_BASE_URL is missing")
        return False
    
    # Test server config creation
    try:
        from jama_mcp_server.mcp_server import ServerConfig
        
        config_dict = {
            "jama_base_url": jama_url,
            "jama_api_token": jama_token,
            "jama_username": jama_username,
            "jama_password": os.getenv("JAMA_PASSWORD"),
            "jama_project_id": 1,
            "nlp_model": "en_core_web_sm",
            "sentence_transformer_model": "all-MiniLM-L6-v2",
            "enable_gpu": False,
            "enable_vector_db": True,
            "vector_db_type": "memory",
            "server_name": "jama-python-mcp-server",
            "server_version": "1.0.0"
        }
        
        config = ServerConfig(**config_dict)
        print("✅ Server configuration created successfully")
        
        return True
        
    except Exception as e:
        print(f"❌ Server configuration failed: {e}")
        return False

if __name__ == "__main__":
    success = test_startup()
    if success:
        print("\n🚀 Server startup configuration is working!")
        print("💡 The server can now be started with: python main.py")
        print("🔧 Or test mode with: python simple_main.py")
        sys.exit(0)
    else:
        print("\n❌ Server startup configuration has issues")
        sys.exit(1)