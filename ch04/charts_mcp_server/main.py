#!/usr/bin/env python3
"""
Charts MCP Server - 图表生成MCP服务器

基于FastMCP、pyecharts和MinIO的图表生成服务，支持：
- 柱状图 (Bar Chart)
- 饼图 (Pie Chart)  
- 折线图 (Line Chart)

生成的图表会自动转换为图片并上传到MinIO，返回可访问的URL。
"""

import sys
from typing import List, Dict, Any, Optional
from fastmcp import FastMCP, Context
from loguru import logger

# 导入配置和组件
from src.config import settings
from src.charts.bar_chart import bar_chart_generator
from src.charts.pie_chart import pie_chart_generator
from src.charts.line_chart import line_chart_generator


# 配置日志
logger.remove()
logger.add(
    sys.stderr,
    level=settings.logging.level,
    format=settings.logging.format
)

# 创建FastMCP服务器实例
mcp = FastMCP("Charts MCP Server")


@mcp.tool
def generate_bar_chart(
    title: str,
    x_data: List[str],
    series_data: List[Dict[str, Any]],
    width: Optional[int] = None,
    height: Optional[int] = None,
    theme: Optional[str] = None,
    chart_options: Optional[Dict[str, Any]] = None,
    ctx: Context = None
) -> str:
    """
    生成柱状图并返回图片URL
    
    Args:
        title: 图表标题
        x_data: X轴数据（类目列表），例如: ["衬衫", "毛衣", "领带", "裤子"]
        series_data: 系列数据列表，格式: [{"name": "系列名", "data": [数值列表]}]
        width: 图表宽度（像素），默认800
        height: 图表高度（像素），默认600
        theme: 主题名称，可选: white, light, dark, chalk, essos, infographic, macarons, purple_passion, roma, romantic, shine, vintage, walden, westeros, wonderland
        chart_options: 额外的图表选项（可选）
        
    Returns:
        str: 生成的图表图片URL
        
    Example:
        generate_bar_chart(
            title="销售数据",
            x_data=["Q1", "Q2", "Q3", "Q4"],
            series_data=[
                {"name": "商家A", "data": [114, 55, 27, 101]},
                {"name": "商家B", "data": [57, 134, 137, 129]}
            ]
        )
    """
    if ctx:
        logger.info(f"开始生成柱状图: {title}")
    
    try:
        url = bar_chart_generator.generate_chart_url(
            title=title,
            x_data=x_data,
            series_data=series_data,
            width=width,
            height=height,
            theme=theme,
            chart_options=chart_options
        )
        
        if ctx:
            logger.info(f"柱状图生成成功: {url}")
        
        return url
        
    except Exception as e:
        error_msg = f"柱状图生成失败: {str(e)}"
        logger.error(error_msg)
        raise Exception(error_msg)


@mcp.tool
def generate_pie_chart(
    title: str,
    data: List[Dict[str, Any]],
    width: Optional[int] = None,
    height: Optional[int] = None,
    theme: Optional[str] = None,
    chart_options: Optional[Dict[str, Any]] = None,
    ctx: Context = None
) -> str:
    """
    生成饼图并返回图片URL
    
    Args:
        title: 图表标题
        data: 饼图数据，格式: [{"name": "名称", "value": 数值}]
        width: 图表宽度（像素），默认800
        height: 图表高度（像素），默认600
        theme: 主题名称，可选: white, light, dark, chalk, essos, infographic, macarons, purple_passion, roma, romantic, shine, vintage, walden, westeros, wonderland
        chart_options: 额外的图表选项（可选）
        
    Returns:
        str: 生成的图表图片URL
        
    Example:
        generate_pie_chart(
            title="产品销售占比",
            data=[
                {"name": "产品A", "value": 335},
                {"name": "产品B", "value": 310},
                {"name": "产品C", "value": 274},
                {"name": "产品D", "value": 235}
            ]
        )
    """
    if ctx:
        logger.info(f"开始生成饼图: {title}")
    
    try:
        url = pie_chart_generator.generate_chart_url(
            title=title,
            data=data,
            width=width,
            height=height,
            theme=theme,
            chart_options=chart_options
        )
        
        if ctx:
            logger.info(f"饼图生成成功: {url}")
        
        return url
        
    except Exception as e:
        error_msg = f"饼图生成失败: {str(e)}"
        logger.error(error_msg)
        raise Exception(error_msg)


@mcp.tool
def generate_line_chart(
    title: str,
    x_data: List[str],
    series_data: List[Dict[str, Any]],
    width: Optional[int] = None,
    height: Optional[int] = None,
    theme: Optional[str] = None,
    chart_options: Optional[Dict[str, Any]] = None,
    ctx: Context = None
) -> str:
    """
    生成折线图并返回图片URL
    
    Args:
        title: 图表标题
        x_data: X轴数据（类目列表），例如: ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
        series_data: 系列数据列表，格式: [{"name": "系列名", "data": [数值列表]}]
        width: 图表宽度（像素），默认800
        height: 图表高度（像素），默认600
        theme: 主题名称，可选: white, light, dark, chalk, essos, infographic, macarons, purple_passion, roma, romantic, shine, vintage, walden, westeros, wonderland
        chart_options: 额外的图表选项（可选）
        
    Returns:
        str: 生成的图表图片URL
        
    Example:
        generate_line_chart(
            title="温度变化趋势",
            x_data=["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"],
            series_data=[
                {"name": "温度", "data": [11, 11, 15, 13, 12, 13, 10]},
                {"name": "湿度", "data": [1, -2, 2, 5, 3, 2, 0]}
            ]
        )
    """
    if ctx:
        logger.info(f"开始生成折线图: {title}")
    
    try:
        url = line_chart_generator.generate_chart_url(
            title=title,
            x_data=x_data,
            series_data=series_data,
            width=width,
            height=height,
            theme=theme,
            chart_options=chart_options
        )
        
        if ctx:
            logger.info(f"折线图生成成功: {url}")
        
        return url
        
    except Exception as e:
        error_msg = f"折线图生成失败: {str(e)}"
        logger.error(error_msg)
        raise Exception(error_msg)


@mcp.tool
def get_server_info(ctx: Context = None) -> Dict[str, Any]:
    """
    获取服务器信息和配置
    
    Returns:
        dict: 服务器信息
    """
    return {
        "server_name": "Charts MCP Server",
        "version": "1.0.0",
        "description": "基于FastMCP、pyecharts和MinIO的图表生成服务",
        "supported_charts": ["bar", "pie", "line"],
        "config": {
            "default_width": settings.charts.default_width,
            "default_height": settings.charts.default_height,
            "default_theme": settings.charts.default_theme,
            "minio_endpoint": settings.minio.endpoint,
            "minio_bucket": settings.minio.bucket_name
        },
        "available_themes": [
            "white", "light", "dark", "chalk", "essos", "infographic", 
            "macarons", "purple_passion", "roma", "romantic", "shine", 
            "vintage", "walden", "westeros", "wonderland"
        ]
    }


def main():
    """主函数，启动MCP服务器"""
    logger.info("启动Charts MCP Server...")
    
    try:
        # 启动HTTP服务器
        mcp.run(
            transport="http",
            host=settings.mcp_server.host,
            port=settings.mcp_server.port,
            path=settings.mcp_server.path,
            show_banner=True
        )
    except KeyboardInterrupt:
        logger.info("服务器已停止")
    except Exception as e:
        logger.error(f"服务器启动失败: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()