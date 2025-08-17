#!/usr/bin/env python3
"""
简单的MCP客户端测试脚本
"""
import asyncio
from fastmcp import Client

async def test_charts_server():
    """测试图表服务器"""
    try:
        # 连接到本地服务器  
        async with Client("http://127.0.0.1:8000/mcp/") as client:
            print("✅ 成功连接到服务器")
            
            # 测试ping
            ping_result = await client.ping()
            print(f"🏓 Ping结果: {ping_result}")
            
            # 获取工具列表
            tools = await client.list_tools()
            print(f"🔧 可用工具: {[tool.name for tool in tools.tools]}")
            
            # 测试柱状图生成
            print("\n📊 测试柱状图生成...")
            bar_result = await client.call_tool("generate_bar_chart", {
                "title": "测试柱状图",
                "x_data": ["A", "B", "C"],
                "series_data": [
                    {"name": "系列1", "data": [10, 20, 30]}
                ],
                "width": 800,
                "height": 600,
                "theme": "white"
            })
            print(f"✅ 柱状图生成成功: {bar_result}")
            
            # 测试饼图生成
            print("\n🥧 测试饼图生成...")
            pie_result = await client.call_tool("generate_pie_chart", {
                "title": "测试饼图",
                "data": [
                    {"name": "A", "value": 30},
                    {"name": "B", "value": 45},
                    {"name": "C", "value": 25}
                ],
                "width": 800,
                "height": 600,
                "theme": "white"
            })
            print(f"✅ 饼图生成成功: {pie_result}")
            
            # 测试折线图生成
            print("\n📈 测试折线图生成...")
            line_result = await client.call_tool("generate_line_chart", {
                "title": "测试折线图",
                "x_data": ["1月", "2月", "3月"],
                "series_data": [
                    {"name": "系列1", "data": [10, 15, 20]}
                ],
                "width": 800,
                "height": 600,
                "theme": "white"
            })
            print(f"✅ 折线图生成成功: {line_result}")
            
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_charts_server())