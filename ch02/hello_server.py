#!/usr/bin/env python3
"""
第二课配套代码：Hello World MCP服务器
=================================

最简单的MCP服务器示例，展示基础用法。

作者: MCP开发入门系列
版本: 1.0
"""

from fastmcp import FastMCP

# 创建MCP服务器
mcp = FastMCP("我的第一个AI助手")

@mcp.tool
def say_hello(name: str) -> str:
    """向用户问好
    
    Args:
        name: 要问候的人的姓名
        
    Returns:
        包含问候语的字符串
    """
    return f"你好，{name}！欢迎来到MCP的世界！"

@mcp.tool
def get_server_info() -> dict:
    """获取服务器基本信息
    
    Returns:
        包含服务器信息的字典
    """
    return {
        "name": "我的第一个AI助手",
        "version": "1.0",
        "description": "这是一个用于学习MCP开发的示例服务器",
        "author": "MCP开发入门系列",
        "capabilities": ["问候", "信息查询"]
    }

if __name__ == "__main__":
    print("🚀 我的第一个AI助手启动中...")
    print("📋 可用工具:")
    print("  👋 say_hello - 向用户问好")
    print("  ℹ️  get_server_info - 获取服务器信息")
    print("💡 在Claude中试试: '你好' 或 '服务器信息'")
    print("🛑 使用 Ctrl+C 停止服务器\n")
    
    try:
        mcp.run()
    except KeyboardInterrupt:
        print("\n👋 服务器已停止，再见！")