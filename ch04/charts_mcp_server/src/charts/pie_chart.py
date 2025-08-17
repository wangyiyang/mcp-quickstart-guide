from typing import List, Dict, Any, Optional, Union
from pathlib import Path
from pyecharts.charts import Pie
from pyecharts import options as opts
from pyecharts.globals import ThemeType
from loguru import logger

from ..config import settings
from ..utils.temp_files import temp_manager
from ..utils.screenshot import screenshot_tool
from ..storage.minio_client import minio_client


class PieChartGenerator:
    """饼图生成器"""
    
    def __init__(self):
        """初始化饼图生成器"""
        self.default_width = f"{settings.charts.default_width}px"
        self.default_height = f"{settings.charts.default_height}px"
        self.default_theme = settings.charts.default_theme
    
    def generate_chart_url(
        self,
        title: str,
        data: List[Dict[str, Any]],
        width: Optional[int] = None,
        height: Optional[int] = None,
        theme: Optional[str] = None,
        chart_options: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        生成饼图并返回图片URL
        
        Args:
            title: 图表标题
            data: 饼图数据，格式: [{"name": "名称", "value": 数值}]
            width: 图表宽度（像素）
            height: 图表高度（像素）  
            theme: 主题名称
            chart_options: 额外的图表选项
            
        Returns:
            str: 图片的URL
            
        Example:
            data = [
                {"name": "产品A", "value": 335},
                {"name": "产品B", "value": 310},
                {"name": "产品C", "value": 274},
                {"name": "产品D", "value": 235}
            ]
        """
        try:
            # 创建饼图
            chart = self._create_pie_chart(
                title=title,
                data=data,
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
            
            logger.info(f"饼图生成成功: {title}")
            return url
            
        except Exception as e:
            logger.error(f"饼图生成失败: {e}")
            raise
    
    def _create_pie_chart(
        self,
        title: str,
        data: List[Dict[str, Any]],
        width: int,
        height: int,
        theme: str,
        chart_options: Dict[str, Any]
    ) -> Pie:
        """
        创建饼图对象
        
        Args:
            title: 图表标题
            data: 饼图数据
            width: 宽度
            height: 高度
            theme: 主题
            chart_options: 图表选项
            
        Returns:
            Pie: pyecharts饼图对象
        """
        # 获取主题类型
        theme_type = self._get_theme_type(theme)
        
        # 创建饼图实例
        pie = Pie(init_opts=opts.InitOpts(
            width=f"{width}px",
            height=f"{height}px",
            theme=theme_type
        ))
        
        # 处理数据格式
        pie_data = []
        for item in data:
            pie_data.append([item["name"], item["value"]])
        
        # 获取饼图特定选项
        pie_opts = chart_options.get("pie", {})
        
        # 设置半径
        radius = pie_opts.get("radius", ["40%", "75%"])
        if isinstance(radius, (int, str)):
            radius = [0, radius]
        
        # 设置中心位置
        center = pie_opts.get("center", ["50%", "50%"])
        
        # 设置玫瑰图类型
        rosetype = pie_opts.get("rosetype", None)
        
        # 添加数据系列
        pie.add(
            series_name=title,
            data_pair=pie_data,
            radius=radius,
            center=center,
            rosetype=rosetype,
            label_opts=opts.LabelOpts(
                formatter="{b}: {c} ({d}%)"
            )
        )
        
        # 设置全局选项
        global_opts = self._build_global_options(title, chart_options)
        pie.set_global_opts(**global_opts)
        
        # 设置系列选项
        series_opts = self._build_series_options(chart_options)
        if series_opts:
            pie.set_series_opts(**series_opts)
        
        return pie
    
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
            'title_opts': opts.TitleOpts(
                title=title,
                pos_left="center",
                pos_top="20px"
            ),
            'legend_opts': opts.LegendOpts(
                pos_left="center",
                pos_bottom="20px",
                orient="horizontal"
            )
        }
        
        # 合并用户自定义选项
        if 'title' in chart_options:
            title_config = chart_options['title']
            options['title_opts'] = opts.TitleOpts(**title_config)
        
        if 'legend' in chart_options:
            legend_config = chart_options['legend']
            options['legend_opts'] = opts.LegendOpts(**legend_config)
        
        if 'tooltip' in chart_options:
            tooltip_config = chart_options['tooltip']
            options['tooltip_opts'] = opts.TooltipOpts(**tooltip_config)
        else:
            # 默认提示框配置
            options['tooltip_opts'] = opts.TooltipOpts(
                trigger="item",
                formatter="{a} <br/>{b}: {c} ({d}%)"
            )
        
        return options
    
    def _build_series_options(self, chart_options: Dict[str, Any]) -> Dict[str, Any]:
        """构建系列选项"""
        options = {}
        
        if 'label' in chart_options:
            label_config = chart_options['label']
            options['label_opts'] = opts.LabelOpts(**label_config)
        
        if 'itemstyle' in chart_options:
            itemstyle_config = chart_options['itemstyle']
            options['itemstyle_opts'] = opts.ItemStyleOpts(**itemstyle_config)
        
        return options
    
    def _render_to_html(self, chart: Pie) -> Path:
        """将图表渲染为HTML文件"""
        # 使用render()生成包含完整ECharts库的HTML
        html_file = temp_manager.create_temp_file('.html')
        chart.render(str(html_file))
        return html_file


# 创建全局饼图生成器实例
pie_chart_generator = PieChartGenerator()