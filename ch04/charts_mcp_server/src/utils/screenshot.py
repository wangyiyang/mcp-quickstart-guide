import asyncio
import tempfile
from pathlib import Path
from typing import Optional
from playwright.async_api import async_playwright
from loguru import logger

from ..config import settings


class ScreenshotTool:
    """截图工具，用于将HTML转换为图片"""
    
    def __init__(self):
        """初始化截图工具"""
        self.viewport_width = settings.screenshot.viewport_width
        self.viewport_height = settings.screenshot.viewport_height
        self.wait_time = settings.screenshot.wait_time
    
    async def html_to_image(
        self, 
        html_file_path: Path, 
        output_path: Optional[Path] = None,
        image_format: str = "png"
    ) -> Path:
        """
        将HTML文件转换为图片
        
        Args:
            html_file_path: HTML文件路径
            output_path: 输出图片路径，如果为None则自动生成
            image_format: 图片格式 (png, jpeg)
            
        Returns:
            Path: 生成的图片文件路径
            
        Raises:
            FileNotFoundError: HTML文件不存在
            Exception: 截图过程中的其他错误
        """
        if not html_file_path.exists():
            raise FileNotFoundError(f"HTML文件不存在: {html_file_path}")
        
        # 生成输出文件路径
        if output_path is None:
            temp_dir = Path(settings.charts.temp_dir)
            temp_dir.mkdir(exist_ok=True)
            output_path = temp_dir / f"{html_file_path.stem}.{image_format}"
        
        try:
            async with async_playwright() as p:
                # 启动浏览器
                browser = await p.chromium.launch(headless=True)
                
                # 创建页面
                page = await browser.new_page(
                    viewport={
                        'width': self.viewport_width,
                        'height': self.viewport_height
                    }
                )
                
                # 访问HTML文件
                file_url = f"file://{html_file_path.absolute()}"
                await page.goto(file_url)
                
                # 等待页面完全加载
                await asyncio.sleep(self.wait_time / 1000)
                
                # 等待图表渲染完成（查找ECharts容器）
                try:
                    await page.wait_for_selector('[_echarts_instance_]', timeout=5000)
                    logger.debug("ECharts图表已渲染完成")
                except Exception:
                    logger.warning("未检测到ECharts实例，继续截图")
                
                # 截图
                await page.screenshot(
                    path=str(output_path),
                    type=image_format,
                    full_page=False,
                    clip=await self._get_chart_clip_rect(page)
                )
                
                await browser.close()
                
                logger.info(f"HTML转图片成功: {output_path}")
                return output_path
                
        except Exception as e:
            logger.error(f"HTML转图片失败: {e}")
            raise
    
    async def _get_chart_clip_rect(self, page) -> Optional[dict]:
        """
        获取图表的裁剪区域，自动检测内容边界
        
        Args:
            page: Playwright页面对象
            
        Returns:
            dict: 裁剪区域 {x, y, width, height} 或 None
        """
        try:
            # 尝试找到ECharts容器
            chart_element = await page.query_selector('[_echarts_instance_]')
            if chart_element:
                bounding_box = await chart_element.bounding_box()
                if bounding_box:
                    # 添加一些边距
                    margin = 20
                    return {
                        'x': max(0, bounding_box['x'] - margin),
                        'y': max(0, bounding_box['y'] - margin),
                        'width': bounding_box['width'] + 2 * margin,
                        'height': bounding_box['height'] + 2 * margin
                    }
            
            # 如果没有找到ECharts容器，尝试找到包含内容的区域
            body_element = await page.query_selector('body')
            if body_element:
                bounding_box = await body_element.bounding_box()
                if bounding_box and bounding_box['width'] > 0 and bounding_box['height'] > 0:
                    return {
                        'x': 0,
                        'y': 0,
                        'width': min(bounding_box['width'], self.viewport_width),
                        'height': min(bounding_box['height'], self.viewport_height)
                    }
                    
        except Exception as e:
            logger.warning(f"获取裁剪区域失败，使用全屏截图: {e}")
        
        return None
    
    def html_to_image_sync(
        self, 
        html_file_path: Path, 
        output_path: Optional[Path] = None,
        image_format: str = "png"
    ) -> Path:
        """
        同步版本的HTML转图片方法
        
        Args:
            html_file_path: HTML文件路径
            output_path: 输出图片路径
            image_format: 图片格式
            
        Returns:
            Path: 生成的图片文件路径
        """
        return asyncio.run(self.html_to_image(html_file_path, output_path, image_format))


# 创建全局截图工具实例
screenshot_tool = ScreenshotTool()