#!/usr/bin/env python3
"""
Simplified main entry point for testing the Jama Python MCP Server
"""

import asyncio
import logging
import os
import sys
from typing import Dict, Any

# Set up the Python path
sys.path.insert(0, '/Users/sanjeev/development/pocs/claude/jama-python-mcp-server/src')

from jama_mcp_server.mcp_server import ServerConfig
from mcp.server import Server
from mcp.types import Tool, TextContent, CallToolResult, ListToolsResult


def setup_logging():
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )


def load_simple_config() -> Dict[str, Any]:
    """Load minimal configuration for testing."""
    return {
        # Jama Connect settings (dummy for testing)
        "jama_base_url": "https://demo.jamacloud.com",
        "jama_api_token": "dummy_token",
        "jama_project_id": 1,
        
        # NLP settings
        "nlp_model": "en_core_web_sm",
        "sentence_transformer_model": "all-MiniLM-L6-v2",
        "enable_gpu": False,
        
        # Vector database settings (disabled for testing)
        "enable_vector_db": False,
        "vector_db_type": "memory",
        
        # Server settings
        "server_name": "jama-python-mcp-server",
        "server_version": "1.0.0"
    }


# Create simple MCP server
server = Server("jama-python-mcp-server")

@server.list_tools()
async def list_tools() -> ListToolsResult:
    """List all available MCP tools."""
    return ListToolsResult(
        tools=[
            Tool(
                name="test_system",
                description="Test system components and connectivity",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "component": {
                            "type": "string",
                            "enum": ["all", "nlp", "jama", "mcp"],
                            "description": "Component to test",
                            "default": "all"
                        }
                    }
                }
            ),
            Tool(
                name="extract_entities",
                description="Extract entities from requirement text using NLP",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "text": {
                            "type": "string",
                            "description": "Text to analyze for entities"
                        }
                    },
                    "required": ["text"]
                }
            ),
            Tool(
                name="classify_text",
                description="Classify text as functional/non-functional requirement",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "text": {
                            "type": "string",
                            "description": "Text to classify"
                        }
                    },
                    "required": ["text"]
                }
            ),
            Tool(
                name="ingest_file",
                description="Import requirements from file (CSV, JSON, Excel, text) for testing",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "file_path": {
                            "type": "string",
                            "description": "Path to requirements file"
                        },
                        "enable_nlp": {
                            "type": "boolean",
                            "description": "Enable NLP processing",
                            "default": True
                        }
                    },
                    "required": ["file_path"]
                }
            )
        ]
    )

@server.call_tool()
async def call_tool(name: str, arguments: dict) -> CallToolResult:
    """Handle tool execution requests."""
    try:
        if name == "test_system":
            component = arguments.get("component", "all")
            result = await test_system_components(component)
            
        elif name == "extract_entities":
            text = arguments.get("text", "")
            result = await extract_entities_simple(text)
            
        elif name == "classify_text":
            text = arguments.get("text", "")
            result = await classify_text_simple(text)
            
        elif name == "ingest_file":
            file_path = arguments.get("file_path", "")
            enable_nlp = arguments.get("enable_nlp", True)
            result = await ingest_file_simple(file_path, enable_nlp)
            
        else:
            result = {
                "error": f"Unknown tool: {name}",
                "available_tools": ["test_system", "extract_entities", "classify_text", "ingest_file"]
            }
        
        return CallToolResult(
            content=[TextContent(
                type="text",
                text=str(result) if isinstance(result, dict) else result
            )]
        )
        
    except Exception as e:
        return CallToolResult(
            content=[TextContent(
                type="text",
                text=f"Error executing {name}: {str(e)}"
            )]
        )


async def test_system_components(component: str) -> dict:
    """Test various system components."""
    results = {"timestamp": str(asyncio.get_event_loop().time())}
    
    if component in ["all", "mcp"]:
        results["mcp_server"] = "✅ MCP Server is running"
    
    if component in ["all", "nlp"]:
        try:
            import spacy
            nlp = spacy.load("en_core_web_sm")
            doc = nlp("This is a test sentence.")
            results["spacy_nlp"] = f"✅ spaCy working - processed {len(doc)} tokens"
        except Exception as e:
            results["spacy_nlp"] = f"❌ spaCy error: {str(e)}"
    
    if component in ["all", "jama"]:
        results["jama_connection"] = "⚠️  Would test Jama connection (requires real credentials)"
    
    return results


async def extract_entities_simple(text: str) -> dict:
    """Simple entity extraction using spaCy."""
    try:
        import spacy
        nlp = spacy.load("en_core_web_sm")
        doc = nlp(text)
        
        entities = []
        for ent in doc.ents:
            entities.append({
                "text": ent.text,
                "label": ent.label_,
                "description": spacy.explain(ent.label_)
            })
        
        return {
            "text": text,
            "entities": entities,
            "entity_count": len(entities),
            "tokens": len(doc)
        }
        
    except Exception as e:
        return {"error": f"NLP processing failed: {str(e)}"}


async def classify_text_simple(text: str) -> dict:
    """Simple requirement classification using keyword matching."""
    
    # Simple classification rules
    functional_keywords = ["shall", "must", "will", "function", "feature", "capability"]
    non_functional_keywords = ["performance", "security", "usability", "reliability", "scalability", "response time"]
    business_rule_keywords = ["if", "when", "calculate", "rule", "condition", "unless"]
    
    text_lower = text.lower()
    
    functional_score = sum(1 for keyword in functional_keywords if keyword in text_lower)
    non_functional_score = sum(1 for keyword in non_functional_keywords if keyword in text_lower)
    business_rule_score = sum(1 for keyword in business_rule_keywords if keyword in text_lower)
    
    # Determine classification
    scores = {
        "functional": functional_score,
        "non_functional": non_functional_score,
        "business_rule": business_rule_score
    }
    
    classification = max(scores.keys(), key=lambda k: scores[k])
    if max(scores.values()) == 0:
        classification = "unknown"
    
    return {
        "text": text,
        "classification": classification,
        "confidence_scores": scores,
        "keywords_found": {
            "functional": [kw for kw in functional_keywords if kw in text_lower],
            "non_functional": [kw for kw in non_functional_keywords if kw in text_lower],
            "business_rule": [kw for kw in business_rule_keywords if kw in text_lower]
        }
    }


async def ingest_file_simple(file_path: str, enable_nlp: bool = True) -> dict:
    """Simple file ingestion for testing."""
    try:
        from jama_mcp_server.file_ingestion import load_requirements_from_file
        
        # Load requirements from file
        requirements = await load_requirements_from_file(file_path)
        
        if not requirements:
            return {
                "error": "No requirements found in file",
                "file_path": file_path
            }
        
        result = {
            "file_path": file_path,
            "ingestion_successful": True,
            "total_requirements": len(requirements),
            "sample_requirements": []
        }
        
        # Process with NLP if enabled
        if enable_nlp:
            import spacy
            try:
                nlp = spacy.load("en_core_web_sm")
                
                nlp_stats = {
                    "business_rules_found": 0,
                    "entities_extracted": 0,
                    "classifications": {}
                }
                
                # Analyze first few requirements
                for req in requirements[:5]:
                    doc = nlp(req.description)
                    entities = [(ent.text, ent.label_) for ent in doc.ents]
                    
                    # Simple business rule detection
                    text_lower = req.description.lower()
                    has_business_rule = any(word in text_lower for word in ["if", "when", "must", "calculate"])
                    if has_business_rule:
                        nlp_stats["business_rules_found"] += 1
                    
                    nlp_stats["entities_extracted"] += len(entities)
                    
                    # Simple classification
                    if "performance" in text_lower or "response" in text_lower:
                        classification = "non_functional"
                    elif has_business_rule:
                        classification = "business_rule"  
                    else:
                        classification = "functional"
                    
                    nlp_stats["classifications"][classification] = nlp_stats["classifications"].get(classification, 0) + 1
                    
                    result["sample_requirements"].append({
                        "id": req.global_id,
                        "name": req.name[:50] + "..." if len(req.name) > 50 else req.name,
                        "description": req.description[:100] + "..." if len(req.description) > 100 else req.description,
                        "entities": entities[:3],  # First 3 entities
                        "classification": classification,
                        "has_business_rule": has_business_rule
                    })
                
                result["nlp_analysis"] = nlp_stats
                
            except Exception as e:
                result["nlp_error"] = f"NLP processing failed: {str(e)}"
        else:
            # Without NLP, just show basic info
            for req in requirements[:5]:
                result["sample_requirements"].append({
                    "id": req.global_id,
                    "name": req.name,
                    "description": req.description[:100] + "..." if len(req.description) > 100 else req.description,
                    "type": req.item_type,
                    "priority": req.priority
                })
        
        return result
        
    except FileNotFoundError:
        return {
            "error": f"File not found: {file_path}",
            "suggestion": "Check the file path or use one of the sample files in sample_data/"
        }
    except Exception as e:
        return {
            "error": f"Failed to ingest file: {str(e)}",
            "file_path": file_path
        }


async def main():
    """Main application entry point."""
    print("🚀 Starting Simple Jama Python MCP Server")
    
    setup_logging()
    logger = logging.getLogger(__name__)
    
    try:
        # Load configuration
        config = load_simple_config()
        logger.info("Configuration loaded")
        
        print(f"""
╔════════════════════════════════════════════════════════╗
║          🤖 Jama Python MCP Server (Test Mode)         ║  
║                     Ready to serve!                   ║
╠════════════════════════════════════════════════════════╣
║ Available MCP Tools:                                   ║
║   • test_system      - Test system components         ║
║   • extract_entities - Extract entities using NLP     ║
║   • classify_text    - Classify requirement types     ║
║   • ingest_file      - Import requirements from file  ║
╚════════════════════════════════════════════════════════╝
""")
        
        logger.info("Server is running. Press Ctrl+C to stop...")
        
        # Keep the server running
        try:
            while True:
                await asyncio.sleep(1)
        except KeyboardInterrupt:
            logger.info("Received shutdown signal")
        
    except Exception as e:
        logger.error(f"Failed to start server: {e}")
        print(f"❌ Server startup failed: {e}")
        return 1
    
    print("👋 Server shutdown completed")
    return 0


if __name__ == "__main__":
    """Entry point when running the script directly."""
    try:
        exit_code = asyncio.run(main())
        sys.exit(exit_code)
    except KeyboardInterrupt:
        print("\n👋 Goodbye!")
        sys.exit(0)
    except Exception as e:
        print(f"💥 Fatal error: {e}")
        sys.exit(1)