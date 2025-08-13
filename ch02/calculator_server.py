#!/usr/bin/env python3
"""
第二课配套代码：智能计算器服务器
=============================

一个功能完整的计算器MCP服务器，支持基础和高级数学运算。

作者: MCP开发入门系列
版本: 1.0
"""

from fastmcp import FastMCP
import math

mcp = FastMCP("智能计算器")

# 基础运算工具
@mcp.tool
def add(a: float, b: float) -> float:
    """计算两个数的和
    
    Args:
        a: 第一个数
        b: 第二个数
        
    Returns:
        两数之和
    """
    return a + b

@mcp.tool  
def subtract(a: float, b: float) -> float:
    """计算两个数的差（a减去b）
    
    Args:
        a: 被减数
        b: 减数
        
    Returns:
        差值
    """
    return a - b

@mcp.tool
def multiply(a: float, b: float) -> float:
    """计算两个数的积
    
    Args:
        a: 第一个数
        b: 第二个数
        
    Returns:
        两数之积
    """
    return a * b

@mcp.tool
def divide(a: float, b: float) -> float:
    """计算两个数的商（a除以b）
    
    Args:
        a: 被除数
        b: 除数
        
    Returns:
        商值
        
    Raises:
        ValueError: 当除数为零时
    """
    if b == 0:
        raise ValueError("除数不能为零")
    return a / b

# 高级运算工具
@mcp.tool
def power(base: float, exponent: float) -> float:
    """计算base的exponent次方
    
    Args:
        base: 底数
        exponent: 指数
        
    Returns:
        幂运算结果
    """
    return math.pow(base, exponent)

@mcp.tool
def sqrt(number: float) -> float:
    """计算平方根
    
    Args:
        number: 被开方数
        
    Returns:
        平方根
        
    Raises:
        ValueError: 当输入负数时
    """
    if number < 0:
        raise ValueError("负数没有实数平方根")
    return math.sqrt(number)

@mcp.tool
def factorial(n: int) -> int:
    """计算阶乘
    
    Args:
        n: 非负整数
        
    Returns:
        n的阶乘
        
    Raises:
        ValueError: 当输入负数时
    """
    if n < 0:
        raise ValueError("阶乘的输入必须是非负整数")
    return math.factorial(n)

@mcp.tool
def sin(angle: float, unit: str = "radians") -> float:
    """计算正弦值
    
    Args:
        angle: 角度
        unit: 角度单位，"radians"或"degrees"
        
    Returns:
        正弦值
    """
    if unit == "degrees":
        angle = math.radians(angle)
    return math.sin(angle)

@mcp.tool
def cos(angle: float, unit: str = "radians") -> float:
    """计算余弦值
    
    Args:
        angle: 角度
        unit: 角度单位，"radians"或"degrees"
        
    Returns:
        余弦值
    """
    if unit == "degrees":
        angle = math.radians(angle)
    return math.cos(angle)

# 资源：帮助信息
@mcp.resource("calculator://help")
def get_help() -> str:
    """获取计算器使用帮助"""
    return """
智能计算器使用说明
=================

基础运算：
- add(a, b): 加法运算
- subtract(a, b): 减法运算  
- multiply(a, b): 乘法运算
- divide(a, b): 除法运算

高级运算：
- power(base, exponent): 幂运算
- sqrt(number): 平方根运算
- factorial(n): 阶乘运算

三角函数：
- sin(angle, unit): 正弦值（单位可选：radians/degrees）
- cos(angle, unit): 余弦值（单位可选：radians/degrees）

数学常数：
- π (pi) ≈ 3.14159
- e ≈ 2.71828

注意事项：
- 除法运算时分母不能为零
- 平方根运算时被开方数不能为负数
- 阶乘运算时输入必须是非负整数
- 三角函数默认使用弧度制，可指定degrees使用角度制

示例用法：
- "计算 10 + 5"
- "求 16 的平方根"
- "计算 2 的 8 次方"
- "求 5 的阶乘"
- "计算 sin(30度)"
"""

@mcp.resource("calculator://constants")  
def get_constants() -> dict:
    """获取数学常数"""
    return {
        "pi": math.pi,
        "e": math.e,
        "golden_ratio": (1 + math.sqrt(5)) / 2,
        "sqrt2": math.sqrt(2),
        "sqrt3": math.sqrt(3),
        "ln2": math.log(2),
        "ln10": math.log(10)
    }

@mcp.resource("calculator://examples")
def get_examples() -> list:
    """获取使用示例"""
    return [
        {
            "description": "基础四则运算",
            "examples": [
                "add(10, 5) = 15",
                "subtract(10, 3) = 7", 
                "multiply(6, 7) = 42",
                "divide(20, 4) = 5"
            ]
        },
        {
            "description": "高级数学运算",
            "examples": [
                "power(2, 8) = 256",
                "sqrt(16) = 4",
                "factorial(5) = 120"
            ]
        },
        {
            "description": "三角函数",
            "examples": [
                "sin(30, 'degrees') = 0.5",
                "cos(60, 'degrees') = 0.5",
                "sin(π/2) = 1"
            ]
        }
    ]

if __name__ == "__main__":
    print("🧮 智能计算器启动中...")
    print("=" * 50)
    print("📋 可用工具:")
    print("  🔢 基础运算: add, subtract, multiply, divide")
    print("  ⚡ 高级运算: power, sqrt, factorial")
    print("  📐 三角函数: sin, cos")
    print("\n📚 可用资源:")
    print("  📖 calculator://help - 使用说明")
    print("  🔢 calculator://constants - 数学常数")
    print("  💡 calculator://examples - 使用示例")
    print("\n💭 试试这些:")
    print("  '计算 23 乘以 45'")
    print("  '求 144 的平方根'")
    print("  '计算 2 的 10 次方'")
    print("  '获取帮助信息'")
    print("=" * 50)
    print("🛑 使用 Ctrl+C 停止服务器\n")
    
    try:
        mcp.run()
    except KeyboardInterrupt:
        print("\n🧮 计算器服务器已停止")