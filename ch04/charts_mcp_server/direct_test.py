#!/usr/bin/env python3
"""
直接调用测试脚本
"""
import asyncio
import sys
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

# 现在可以直接导入
from src.charts.bar_chart import BarChartGenerator
from src.charts.pie_chart import PieChartGenerator
from src.charts.line_chart import LineChartGenerator

async def test_charts_directly():
    """直接测试图表生成器"""
    try:
        # 测试柱状图
        print("📊 测试柱状图生成...")
        bar_generator = BarChartGenerator()
        bar_url = bar_generator.generate_chart_url(
            title="测试柱状图",
            x_data=["A", "B", "C"],
            series_data=[
                {"name": "系列1", "data": [10, 20, 30]}
            ],
            width=800,
            height=600,
            theme="white"
        )
        print(f"✅ 柱状图生成成功: {bar_url}")
        
        # 测试饼图
        print("\n🥧 测试饼图生成...")
        pie_generator = PieChartGenerator()
        pie_url = pie_generator.generate_chart_url(
            title="测试饼图",
            data=[
                {"name": "A", "value": 30},
                {"name": "B", "value": 45},
                {"name": "C", "value": 25}
            ],
            width=800,
            height=600,
            theme="white"
        )
        print(f"✅ 饼图生成成功: {pie_url}")
        
        # 测试折线图
        print("\n📈 测试折线图生成...")
        line_generator = LineChartGenerator()
        line_url = line_generator.generate_chart_url(
            title="测试折线图",
            x_data=["1月", "2月", "3月"],
            series_data=[
                {"name": "系列1", "data": [10, 15, 20]}
            ],
            width=800,
            height=600,
            theme="white"
        )
        print(f"✅ 折线图生成成功: {line_url}")
        
        print("\n🎉 所有图表生成测试通过！")
        
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_charts_directly())