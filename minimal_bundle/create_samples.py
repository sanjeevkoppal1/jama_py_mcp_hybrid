#!/usr/bin/env python3
"""
Create sample requirement files for testing file ingestion
"""

import sys
sys.path.insert(0, '/Users/sanjeev/development/pocs/claude/jama-python-mcp-server/src')

from jama_mcp_server.file_ingestion import create_sample_requirements_file

def main():
    print("🏗️ Creating sample requirement files...")
    
    # Create sample files in different formats
    sample_dir = "/Users/sanjeev/development/pocs/claude/jama-python-mcp-server/sample_data"
    
    try:
        # CSV format
        create_sample_requirements_file(f"{sample_dir}/requirements.csv", "csv")
        print("✅ Created requirements.csv")
        
        # JSON format  
        create_sample_requirements_file(f"{sample_dir}/requirements.json", "json")
        print("✅ Created requirements.json")
        
        # Excel format
        create_sample_requirements_file(f"{sample_dir}/requirements.xlsx", "excel")
        print("✅ Created requirements.xlsx")
        
        # Text format
        create_sample_requirements_file(f"{sample_dir}/requirements.txt", "text")
        print("✅ Created requirements.txt")
        
        print(f"\n📁 Sample files created in: {sample_dir}")
        print(f"📋 Files contain 10 sample mortgage requirements including:")
        print(f"   - Business rules (mortgage rules, interdiction conditions)")
        print(f"   - Functional requirements")  
        print(f"   - Non-functional requirements")
        print(f"   - Security and compliance requirements")
        
    except Exception as e:
        print(f"❌ Error creating sample files: {e}")
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main())