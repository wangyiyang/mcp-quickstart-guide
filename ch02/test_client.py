#!/usr/bin/env python3
"""
第二课配套代码：MCP客户端测试脚本
==============================

演示如何使用FastMCP客户端测试MCP服务器功能。

作者: MCP开发入门系列
版本: 1.0
"""

import asyncio
from fastmcp import Client

async def test_hello_server():
    """测试Hello服务器"""
    print("=== 测试Hello服务器 ===")
    
    # 导入Hello服务器
    from hello_server import mcp as hello_mcp
    
    async with Client(hello_mcp) as client:
        # 测试问候功能
        print("1. 测试问候功能:")
        test_names = ["张三", "李四", "Alice", "世界"]
        
        for name in test_names:
            try:
                result = await client.call_tool("say_hello", {"name": name})
                print(f"   ✅ {name}: {result.data}")
            except Exception as e:
                print(f"   ❌ {name}: {e}")
        
        # 测试服务器信息
        print("\n2. 测试服务器信息:")
        try:
            result = await client.call_tool("get_server_info", {})
            info = result.data
            print(f"   ✅ 服务器名称: {info['name']}")
            print(f"   ✅ 版本: {info['version']}")
            print(f"   ✅ 描述: {info['description']}")
            print(f"   ✅ 功能: {', '.join(info['capabilities'])}")
        except Exception as e:
            print(f"   ❌ 获取服务器信息失败: {e}")

async def test_calculator_server():
    """测试计算器服务器"""
    print("\n=== 测试计算器服务器 ===")
    
    # 导入计算器服务器
    from calculator_server import mcp as calc_mcp
    
    async with Client(calc_mcp) as client:
        # 测试基础运算
        print("1. 测试基础运算:")
        basic_tests = [
            ("add", {"a": 10, "b": 5}, 15),
            ("subtract", {"a": 10, "b": 3}, 7),
            ("multiply", {"a": 6, "b": 7}, 42),
            ("divide", {"a": 20, "b": 4}, 5),
        ]
        
        for tool_name, params, expected in basic_tests:
            try:
                result = await client.call_tool(tool_name, params)
                actual = result.data
                status = "✅" if actual == expected else "❌"
                print(f"   {status} {tool_name}{params} = {actual} (期望: {expected})")
            except Exception as e:
                print(f"   ❌ {tool_name}{params}: {e}")
        
        # 测试高级运算
        print("\n2. 测试高级运算:")
        advanced_tests = [
            ("power", {"base": 2, "exponent": 8}, 256),
            ("sqrt", {"number": 16}, 4),
            ("factorial", {"n": 5}, 120),
        ]
        
        for tool_name, params, expected in advanced_tests:
            try:
                result = await client.call_tool(tool_name, params)
                actual = result.data
                status = "✅" if actual == expected else "❌"
                print(f"   {status} {tool_name}{params} = {actual} (期望: {expected})")
            except Exception as e:
                print(f"   ❌ {tool_name}{params}: {e}")
        
        # 测试三角函数
        print("\n3. 测试三角函数:")
        trig_tests = [
            ("sin", {"angle": 30, "unit": "degrees"}, 0.5),
            ("cos", {"angle": 60, "unit": "degrees"}, 0.5),
        ]
        
        for tool_name, params, expected in trig_tests:
            try:
                result = await client.call_tool(tool_name, params)
                actual = round(result.data, 1)  # 四舍五入到1位小数
                status = "✅" if actual == expected else "❌"
                print(f"   {status} {tool_name}{params} = {actual} (期望: {expected})")
            except Exception as e:
                print(f"   ❌ {tool_name}{params}: {e}")
        
        # 测试错误处理
        print("\n4. 测试错误处理:")
        error_tests = [
            ("divide", {"a": 10, "b": 0}, "除数不能为零"),
            ("sqrt", {"number": -4}, "负数没有实数平方根"),
            ("factorial", {"n": -1}, "阶乘的输入必须是非负整数"),
        ]
        
        for tool_name, params, expected_error in error_tests:
            try:
                result = await client.call_tool(tool_name, params)
                print(f"   ❌ {tool_name}{params}: 应该失败但成功了，结果={result.data}")
            except Exception as e:
                if expected_error in str(e):
                    print(f"   ✅ {tool_name}{params}: 正确处理错误 - {e}")
                else:
                    print(f"   ⚠️  {tool_name}{params}: 错误信息不匹配 - {e}")
        
        # 测试资源
        print("\n5. 测试资源:")
        resources = [
            ("calculator://help", "帮助信息"),
            ("calculator://constants", "数学常数"),
            ("calculator://examples", "使用示例"),
        ]
        
        for resource_uri, description in resources:
            try:
                result = await client.read_resource(resource_uri)
                content = result.contents[0].text
                print(f"   ✅ {description}: {len(content)}个字符")
                # 显示前50个字符作为预览
                preview = content[:50].replace('\n', ' ') + "..."
                print(f"      预览: {preview}")
            except Exception as e:
                print(f"   ❌ {description}: {e}")

async def test_tools_discovery():
    """测试工具发现功能"""
    print("\n=== 测试工具发现 ===")
    
    from calculator_server import mcp as calc_mcp
    
    async with Client(calc_mcp) as client:
        try:
            tools = await client.get_tools()
            print(f"发现 {len(tools)} 个工具:")
            
            for tool_name, tool_info in tools.items():
                print(f"  📋 {tool_name}")
                if hasattr(tool_info, 'description') and tool_info.description:
                    print(f"     {tool_info.description}")
                
        except Exception as e:
            print(f"❌ 获取工具列表失败: {e}")

async def test_resources_discovery():
    """测试资源发现功能"""
    print("\n=== 测试资源发现 ===")
    
    from calculator_server import mcp as calc_mcp
    
    async with Client(calc_mcp) as client:
        try:
            resources = await client.get_resources()
            print(f"发现 {len(resources)} 个资源:")
            
            for resource in resources:
                print(f"  📄 {resource.uri}")
                if hasattr(resource, 'description') and resource.description:
                    print(f"     {resource.description}")
                
        except Exception as e:
            print(f"❌ 获取资源列表失败: {e}")

async def main():
    """主测试函数"""
    print("🧪 MCP服务器功能测试")
    print("=" * 60)
    
    try:
        await test_hello_server()
        await test_calculator_server()
        await test_tools_discovery()
        await test_resources_discovery()
        
        print("\n" + "=" * 60)
        print("🎉 所有测试完成！")
        print("💡 现在你可以把这些服务器连接到Claude Desktop了")
        
    except Exception as e:
        print(f"\n💥 测试过程中发生错误: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(main())