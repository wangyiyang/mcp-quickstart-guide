from typing import List, Dict, Any, Optional, Union
from pathlib import Path
from pyecharts.charts import Bar
from pyecharts import options as opts
from pyecharts.globals import ThemeType
from loguru import logger

from ..config import settings
from ..utils.temp_files import temp_manager
from ..utils.screenshot import screenshot_tool
from ..storage.minio_client import minio_client


class BarChartGenerator:
    """柱状图生成器"""
    
    def __init__(self):
        """初始化柱状图生成器"""
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
        生成柱状图并返回图片URL
        
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
                {"name": "商家A", "data": [114, 55, 27, 101]},
                {"name": "商家B", "data": [57, 134, 137, 129]}
            ]
        """
        try:
            # 创建柱状图
            chart = self._create_bar_chart(
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
            
            # 转换为图片
            image_file = screenshot_tool.html_to_image_sync(html_file)
            
            # 上传到MinIO并获取URL
            url = minio_client.upload_file(image_file)
            
            # 清理临时文件
            temp_manager.cleanup_file(html_file)
            temp_manager.cleanup_file(image_file)
            
            logger.info(f"柱状图生成成功: {title}")
            return url
            
        except Exception as e:
            logger.error(f"柱状图生成失败: {e}")
            raise
    
    def _create_bar_chart(
        self,
        title: str,
        x_data: List[str],
        series_data: List[Dict[str, Any]],
        width: int,
        height: int,
        theme: str,
        chart_options: Dict[str, Any]
    ) -> Bar:
        """
        创建柱状图对象
        
        Args:
            title: 图表标题
            x_data: X轴数据
            series_data: 系列数据
            width: 宽度
            height: 高度
            theme: 主题
            chart_options: 图表选项
            
        Returns:
            Bar: pyecharts柱状图对象
        """
        # 获取主题类型
        theme_type = self._get_theme_type(theme)
        
        # 创建柱状图实例
        bar = Bar(init_opts=opts.InitOpts(
            width=f"{width}px",
            height=f"{height}px",
            theme=theme_type
        ))
        
        # 添加X轴数据
        bar.add_xaxis(x_data)
        
        # 添加系列数据
        for series in series_data:
            series_name = series.get("name", "数据")
            series_values = series.get("data", [])
            
            # 获取系列特定选项
            series_opts = series.get("options", {})
            label_opts = series_opts.get("label", {})
            itemstyle_opts = series_opts.get("itemstyle", {})
            
            bar.add_yaxis(
                series_name=series_name,
                y_axis=series_values,
                label_opts=opts.LabelOpts(**label_opts) if label_opts else None,
                itemstyle_opts=opts.ItemStyleOpts(**itemstyle_opts) if itemstyle_opts else None
            )
        
        # 设置全局选项
        global_opts = self._build_global_options(title, chart_options)
        bar.set_global_opts(**global_opts)
        
        return bar
    
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
        """构建全局选项"""
        options = {
            'title_opts': opts.TitleOpts(title=title),
            'toolbox_opts': opts.ToolboxOpts(
                feature=opts.ToolBoxFeatureOpts(
                    save_as_image=opts.ToolBoxFeatureSaveAsImageOpts(),
                    restore=opts.ToolBoxFeatureRestoreOpts(),
                    data_view=opts.ToolBoxFeatureDataViewOpts(),
                    data_zoom=opts.ToolBoxFeatureDataZoomOpts(),
                    magic_type=opts.ToolBoxFeatureMagicTypeOpts()
                )
            ),
            'legend_opts': opts.LegendOpts(pos_left="center", pos_top="bottom"),
            'datazoom_opts': [
                opts.DataZoomOpts(range_start=0, range_end=100),
                opts.DataZoomOpts(type_="inside", range_start=0, range_end=100)
            ]
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
        
        if 'yaxis' in chart_options:
            yaxis_config = chart_options['yaxis']
            options['yaxis_opts'] = opts.AxisOpts(**yaxis_config)
        
        if 'tooltip' in chart_options:
            tooltip_config = chart_options['tooltip']
            options['tooltip_opts'] = opts.TooltipOpts(**tooltip_config)
        
        return options
    
    def _render_to_html(self, chart: Bar) -> Path:
        """将图表渲染为HTML文件"""
        html_content = chart.render_embed()
        
        # 创建完整的HTML文档
        full_html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <title>Bar Chart</title>
            <style>
                body {{
                    margin: 0;
                    padding: 20px;
                    background-color: white;
                }}
            </style>
        </head>
        <body>
            {html_content}
        </body>
        </html>
        """
        
        # 保存为临时HTML文件
        html_file = temp_manager.create_temp_html(full_html)
        return html_file


# 创建全局柱状图生成器实例
bar_chart_generator = BarChartGenerator()