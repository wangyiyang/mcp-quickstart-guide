import tempfile
import uuid
from pathlib import Path
from typing import Optional
import atexit
import os
from loguru import logger

from ..config import settings, PROJECT_ROOT


class TempFileManager:
    """临时文件管理器"""
    
    def __init__(self):
        """初始化临时文件管理器"""
        self.temp_dir = PROJECT_ROOT / settings.charts.temp_dir
        self.temp_dir.mkdir(exist_ok=True)
        self._temp_files = set()
        
        # 注册退出时清理函数
        atexit.register(self.cleanup_all)
    
    def create_temp_file(self, suffix: str = "", prefix: str = "chart_") -> Path:
        """
        创建临时文件
        
        Args:
            suffix: 文件后缀
            prefix: 文件前缀
            
        Returns:
            Path: 临时文件路径
        """
        filename = f"{prefix}{uuid.uuid4().hex}{suffix}"
        temp_file_path = self.temp_dir / filename
        self._temp_files.add(temp_file_path)
        return temp_file_path
    
    def create_temp_html(self, content: str, filename: Optional[str] = None) -> Path:
        """
        创建临时HTML文件
        
        Args:
            content: HTML内容
            filename: 文件名，如果为None则自动生成
            
        Returns:
            Path: HTML文件路径
        """
        if filename is None:
            temp_file = self.create_temp_file(suffix=".html")
        else:
            temp_file = self.temp_dir / filename
            self._temp_files.add(temp_file)
        
        with open(temp_file, 'w', encoding='utf-8') as f:
            f.write(content)
        
        logger.debug(f"创建临时HTML文件: {temp_file}")
        return temp_file
    
    def cleanup_file(self, file_path: Path) -> bool:
        """
        清理单个临时文件
        
        Args:
            file_path: 文件路径
            
        Returns:
            bool: 清理是否成功
        """
        try:
            if file_path.exists():
                file_path.unlink()
                logger.debug(f"清理临时文件: {file_path}")
            
            if file_path in self._temp_files:
                self._temp_files.remove(file_path)
            
            return True
        except Exception as e:
            logger.error(f"清理临时文件失败 {file_path}: {e}")
            return False
    
    def cleanup_all(self) -> None:
        """清理所有临时文件"""
        if not self._temp_files:
            return
        
        logger.info(f"开始清理 {len(self._temp_files)} 个临时文件")
        
        cleaned_count = 0
        for temp_file in list(self._temp_files):
            if self.cleanup_file(temp_file):
                cleaned_count += 1
        
        logger.info(f"清理完成，成功清理 {cleaned_count} 个文件")
        self._temp_files.clear()
    
    def get_temp_dir(self) -> Path:
        """获取临时目录路径"""
        return self.temp_dir
    
    def ensure_temp_dir(self) -> None:
        """确保临时目录存在"""
        self.temp_dir.mkdir(exist_ok=True)


# 创建全局临时文件管理器实例
temp_manager = TempFileManager()