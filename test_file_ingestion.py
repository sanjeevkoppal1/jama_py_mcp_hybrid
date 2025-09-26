#!/usr/bin/env python3
"""
Test file ingestion functionality
"""

import sys
import os
import asyncio
sys.path.insert(0, '/Users/sanjeev/development/pocs/claude/jama-python-mcp-server/src')

from jama_mcp_server.file_ingestion import load_requirements_from_file, create_sample_requirements_file


async def test_file_ingestion():
    """Test file ingestion with various formats."""
    print("🧪 Testing File Ingestion Functionality\n")
    
    sample_dir = "/Users/sanjeev/development/pocs/claude/jama-python-mcp-server/sample_data"
    
    # Test files
    test_files = [
        f"{sample_dir}/requirements.csv",
        f"{sample_dir}/requirements.json", 
        f"{sample_dir}/requirements.xlsx",
        f"{sample_dir}/requirements.txt"
    ]
    
    for file_path in test_files:
        if os.path.exists(file_path):
            print(f"📄 Testing {os.path.basename(file_path)}...")
            
            try:
                requirements = await load_requirements_from_file(file_path)
                
                print(f"   ✅ Loaded {len(requirements)} requirements")
                
                # Show first requirement
                if requirements:
                    req = requirements[0]
                    print(f"   📋 Sample requirement:")
                    print(f"      ID: {req.global_id}")
                    print(f"      Name: {req.name}")
                    print(f"      Type: {req.item_type}")
                    print(f"      Description: {req.description[:100]}...")
                    if req.tags:
                        print(f"      Tags: {', '.join(req.tags[:3])}")
                
                # Count business rules
                business_rule_count = sum(1 for req in requirements 
                                        if any(keyword in req.description.lower() 
                                             for keyword in ["if", "when", "must", "calculate"]))
                print(f"   🎯 Potential business rules found: {business_rule_count}")
                
            except Exception as e:
                print(f"   ❌ Failed to load {file_path}: {e}")
            
            print()
        else:
            print(f"   ⚠️  File not found: {file_path}")
    
    # Test business rule examples
    print("🔍 Testing Business Rule Detection:")
    
    business_rule_examples = [
        "If credit score is above 650, then approve mortgage application automatically.",
        "When loan amount exceeds $500,000, additional documentation is required.",
        "The interest rate must be calculated as base rate plus risk premium.",
        "System shall process mortgage applications within 5 seconds.",
        "Users are prohibited from accessing accounts without authentication."
    ]
    
    for i, rule_text in enumerate(business_rule_examples, 1):
        print(f"\n   {i}. {rule_text}")
        
        # Simple pattern matching
        patterns_found = []
        if "if" in rule_text.lower() and "then" in rule_text.lower():
            patterns_found.append("Conditional (if-then)")
        if any(word in rule_text.lower() for word in ["when", "must", "calculate", "shall"]):
            patterns_found.append("Business constraint")
        if "prohibited" in rule_text.lower() or "not allowed" in rule_text.lower():
            patterns_found.append("Restriction")
        
        print(f"      🎯 Patterns: {', '.join(patterns_found) if patterns_found else 'None detected'}")


async def test_nlp_on_sample_data():
    """Test NLP processing on sample requirements."""
    print("🧠 Testing NLP Processing on Sample Requirements\n")
    
    sample_file = "/Users/sanjeev/development/pocs/claude/jama-python-mcp-server/sample_data/requirements.json"
    
    if not os.path.exists(sample_file):
        print("   ⚠️  Sample file not found, creating...")
        create_sample_requirements_file(sample_file, "json")
    
    try:
        requirements = await load_requirements_from_file(sample_file)
        print(f"✅ Loaded {len(requirements)} sample requirements")
        
        # Test with spaCy
        import spacy
        nlp = spacy.load("en_core_web_sm")
        
        print("\n📊 NLP Analysis Results:")
        
        business_rules = []
        total_entities = 0
        classifications = {"functional": 0, "business_rule": 0, "non_functional": 0, "security": 0}
        
        for req in requirements:
            doc = nlp(req.description)
            entities = list(doc.ents)
            total_entities += len(entities)
            
            # Business rule detection
            text_lower = req.description.lower()
            if any(word in text_lower for word in ["if", "when", "calculate", "must", "shall"]):
                business_rules.append({
                    "id": req.global_id,
                    "text": req.description,
                    "patterns": [word for word in ["if", "when", "calculate", "must", "shall"] if word in text_lower]
                })
                classifications["business_rule"] += 1
            elif any(word in text_lower for word in ["security", "encryption", "authentication"]):
                classifications["security"] += 1
            elif any(word in text_lower for word in ["performance", "response", "time", "load"]):
                classifications["non_functional"] += 1
            else:
                classifications["functional"] += 1
        
        print(f"   🎯 Business rules found: {len(business_rules)}")
        print(f"   🏷️  Total entities extracted: {total_entities}")
        print(f"   📋 Classifications:")
        for cls, count in classifications.items():
            print(f"      - {cls}: {count}")
        
        # Show business rules
        print(f"\n🎯 Sample Business Rules:")
        for i, rule in enumerate(business_rules[:3], 1):
            print(f"   {i}. {rule['id']}: {rule['text'][:100]}...")
            print(f"      Keywords: {', '.join(rule['patterns'])}")
        
        print(f"\n✅ NLP processing completed successfully!")
        
    except Exception as e:
        print(f"❌ NLP testing failed: {e}")


async def main():
    """Run all file ingestion tests."""
    print("🚀 Starting File Ingestion Tests\n")
    
    # Ensure sample files exist
    sample_dir = "/Users/sanjeev/development/pocs/claude/jama-python-mcp-server/sample_data"
    os.makedirs(sample_dir, exist_ok=True)
    
    # Create sample files if they don't exist
    sample_files = [
        ("requirements.csv", "csv"),
        ("requirements.json", "json"),
        ("requirements.xlsx", "excel"),
        ("requirements.txt", "text")
    ]
    
    for filename, format_type in sample_files:
        file_path = f"{sample_dir}/{filename}"
        if not os.path.exists(file_path):
            print(f"📝 Creating sample file: {filename}")
            create_sample_requirements_file(file_path, format_type)
    
    print()
    
    # Run tests
    await test_file_ingestion()
    await test_nlp_on_sample_data()
    
    print("\n🎉 File ingestion testing completed!")
    print(f"\n📁 Sample files available in: {sample_dir}")
    print("🚀 Ready to test file ingestion with MCP server!")


if __name__ == "__main__":
    asyncio.run(main())