from typing import List, Dict, Any, Optional, Union
from pathlib import Path
from pyecharts.charts import Line
from pyecharts import options as opts
from pyecharts.globals import ThemeType
from loguru import logger

from ..config import settings
from ..utils.temp_files import temp_manager
from ..utils.screenshot import screenshot_tool
from ..storage.minio_client import minio_client


class LineChartGenerator:
    """折线图生成器"""
    
    def __init__(self):
        """初始化折线图生成器"""
        self.default_width = f"{settings.charts.default_width}px"
        self.default_height = f"{settings.charts.default_height}px"
        self.default_theme = settings.charts.default_theme
    
    def generate_chart_url(
        self,
        title: str,
        x_data: List[str],
        series_data: List[Dict[str, Any]],
        width: Optional[int] = None,
        height: Optional[int] = None,
        theme: Optional[str] = None,
        chart_options: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        生成折线图并返回图片URL
        
        Args:
            title: 图表标题
            x_data: X轴数据（类目）
            series_data: 系列数据，格式: [{"name": "系列名", "data": [数值列表]}]
            width: 图表宽度（像素）
            height: 图表高度（像素）  
            theme: 主题名称
            chart_options: 额外的图表选项
            
        Returns:
            str: 图片的URL
            
        Example:
            series_data = [
                {"name": "温度", "data": [11, 11, 15, 13, 12, 13, 10]},
                {"name": "湿度", "data": [1, -2, 2, 5, 3, 2, 0]}
            ]
        """
        try:
            # 创建折线图
            chart = self._create_line_chart(
                title=title,
                x_data=x_data,
                series_data=series_data,
                width=width or settings.charts.default_width,
                height=height or settings.charts.default_height,
                theme=theme or self.default_theme,
                chart_options=chart_options or {}
            )
            
            # 渲染HTML
            html_file = self._render_to_html(chart)
            logger.debug(f"HTML文件已生成: {html_file}")
            
            # 转换为图片
            image_file = screenshot_tool.html_to_image_sync(html_file)
            logger.debug(f"图片文件已生成: {image_file}")
            
            # 上传到MinIO并获取URL
            url = minio_client.upload_file(image_file)
            
            # 暂时不清理临时文件，用于调试
            # temp_manager.cleanup_file(html_file)
            # temp_manager.cleanup_file(image_file)
            logger.info(f"调试信息 - HTML: {html_file}, 图片: {image_file}")
            
            logger.info(f"折线图生成成功: {title}")
            return url
            
        except Exception as e:
            logger.error(f"折线图生成失败: {e}")
            raise
    
    def _create_line_chart(
        self,
        title: str,
        x_data: List[str],
        series_data: List[Dict[str, Any]],
        width: int,
        height: int,
        theme: str,
        chart_options: Dict[str, Any]
    ) -> Line:
        """
        创建折线图对象
        
        Args:
            title: 图表标题
            x_data: X轴数据
            series_data: 系列数据
            width: 宽度
            height: 高度
            theme: 主题
            chart_options: 图表选项
            
        Returns:
            Line: pyecharts折线图对象
        """
        # 获取主题类型
        theme_type = self._get_theme_type(theme)
        
        # 创建折线图实例
        line = Line(init_opts=opts.InitOpts(
            width=f"{width}px",
            height=f"{height}px",
            theme=theme_type
        ))
        
        # 添加X轴数据
        line.add_xaxis(x_data)
        
        # 添加系列数据
        for series in series_data:
            series_name = series.get("name", "数据")
            series_values = series.get("data", [])
            
            # 获取系列特定选项
            series_opts = series.get("options", {})
            label_opts = series_opts.get("label", {})
            linestyle_opts = series_opts.get("linestyle", {})
            markpoint_opts = series_opts.get("markpoint", {})
            markline_opts = series_opts.get("markline", {})
            
            # 处理线条样式
            is_smooth = series_opts.get("smooth", False)
            is_symbol_show = series_opts.get("symbol_show", True)
            symbol = series_opts.get("symbol", "circle")
            symbol_size = series_opts.get("symbol_size", 4)
            
            # 处理区域填充
            areastyle_opts = series_opts.get("areastyle", None)
            if areastyle_opts:
                areastyle_opts = opts.AreaStyleOpts(**areastyle_opts)
            
            line.add_yaxis(
                series_name=series_name,
                y_axis=series_values,
                is_smooth=is_smooth,
                is_symbol_show=is_symbol_show,
                symbol=symbol,
                symbol_size=symbol_size,
                label_opts=opts.LabelOpts(**label_opts) if label_opts else None,
                linestyle_opts=opts.LineStyleOpts(**linestyle_opts) if linestyle_opts else None,
                areastyle_opts=areastyle_opts,
                markpoint_opts=opts.MarkPointOpts(**markpoint_opts) if markpoint_opts else None,
                markline_opts=opts.MarkLineOpts(**markline_opts) if markline_opts else None
            )
        
        # 设置全局选项
        global_opts = self._build_global_options(title, chart_options)
        line.set_global_opts(**global_opts)
        
        return line
    
    def _get_theme_type(self, theme: str) -> Optional[str]:
        """获取pyecharts主题类型"""
        theme_mapping = {
            'white': ThemeType.WHITE,
            'light': ThemeType.LIGHT,
            'dark': ThemeType.DARK,
            'chalk': ThemeType.CHALK,
            'essos': ThemeType.ESSOS,
            'infographic': ThemeType.INFOGRAPHIC,
            'macarons': ThemeType.MACARONS,
            'purple_passion': ThemeType.PURPLE_PASSION,
            'roma': ThemeType.ROMA,
            'romantic': ThemeType.ROMANTIC,
            'shine': ThemeType.SHINE,
            'vintage': ThemeType.VINTAGE,
            'walden': ThemeType.WALDEN,
            'westeros': ThemeType.WESTEROS,
            'wonderland': ThemeType.WONDERLAND
        }
        return theme_mapping.get(theme.lower(), ThemeType.WHITE)
    
    def _build_global_options(self, title: str, chart_options: Dict[str, Any]) -> Dict[str, Any]:
        """构建全局选项 - 简化版本"""
        options = {
            'title_opts': opts.TitleOpts(title=title),
            'legend_opts': opts.LegendOpts(pos_left="center", pos_top="bottom")
        }
        
        # 合并用户自定义选项
        if 'title' in chart_options:
            title_config = chart_options['title']
            options['title_opts'] = opts.TitleOpts(**title_config)
        
        if 'legend' in chart_options:
            legend_config = chart_options['legend']
            options['legend_opts'] = opts.LegendOpts(**legend_config)
        
        if 'xaxis' in chart_options:
            xaxis_config = chart_options['xaxis']
            options['xaxis_opts'] = opts.AxisOpts(**xaxis_config)
        else:
            # 默认X轴配置
            options['xaxis_opts'] = opts.AxisOpts(
                type_="category",
                boundary_gap=False
            )
        
        if 'yaxis' in chart_options:
            yaxis_config = chart_options['yaxis']
            options['yaxis_opts'] = opts.AxisOpts(**yaxis_config)
        else:
            # 默认Y轴配置
            options['yaxis_opts'] = opts.AxisOpts(
                type_="value",
                axistick_opts=opts.AxisTickOpts(is_show=True),
                splitline_opts=opts.SplitLineOpts(is_show=True)
            )
        
        if 'tooltip' in chart_options:
            tooltip_config = chart_options['tooltip']
            options['tooltip_opts'] = opts.TooltipOpts(**tooltip_config)
        else:
            # 默认提示框配置
            options['tooltip_opts'] = opts.TooltipOpts(
                trigger="axis",
                axis_pointer_type="cross"
            )
        
        return options
    
    def _render_to_html(self, chart: Line) -> Path:
        """将图表渲染为HTML文件"""
        # 使用render()生成包含完整ECharts库的HTML
        html_file = temp_manager.create_temp_file('.html')
        chart.render(str(html_file))
        return html_file


# 创建全局折线图生成器实例
line_chart_generator = LineChartGenerator()