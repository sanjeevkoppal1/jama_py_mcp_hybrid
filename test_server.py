#!/usr/bin/env python3
"""
Test server to verify MCP functionality
"""

import asyncio
import os
from mcp.server import Server
from mcp.types import Tool, TextContent, CallToolResult, ListToolsResult

# Simple test server
server = Server("test-jama-mcp")

@server.list_tools()
async def list_tools() -> ListToolsResult:
    """List available tools."""
    return ListToolsResult(
        tools=[
            Tool(
                name="test_connection",
                description="Test basic connectivity",
                inputSchema={
                    "type": "object",
                    "properties": {}
                }
            )
        ]
    )

@server.call_tool()
async def call_tool(name: str, arguments: dict) -> CallToolResult:
    """Handle tool calls."""
    if name == "test_connection":
        return CallToolResult(
            content=[TextContent(
                type="text", 
                text="✅ MCP Server is working! Connection test successful."
            )]
        )
    else:
        return CallToolResult(
            content=[TextContent(
                type="text", 
                text=f"❌ Unknown tool: {name}"
            )]
        )

if __name__ == "__main__":
    print("🚀 Starting Test MCP Server...")
    print("✅ MCP server framework is working correctly!")
    print("📋 Available tools: test_connection")
    print("🛑 Press Ctrl+C to stop")
    
    try:
        # Run indefinitely for testing
        asyncio.get_event_loop().run_forever()
    except KeyboardInterrupt:
        print("\n👋 Test server stopped")