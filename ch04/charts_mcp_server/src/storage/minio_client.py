import uuid
from datetime import timedelta
from typing import Optional
from pathlib import Path
from minio import Minio
from minio.error import S3Error
from loguru import logger

from ..config import settings


class MinIOClient:
    """MinIO客户端，用于文件上传和URL生成"""
    
    def __init__(self):
        """初始化MinIO客户端"""
        self.endpoint = settings.minio.endpoint
        self.access_key = settings.minio.access_key
        self.secret_key = settings.minio.secret_key
        self.bucket_name = settings.minio.bucket_name
        self.secure = settings.minio.secure
        self.url_expiry_hours = settings.minio.url_expiry_hours
        self.custom_domain = getattr(settings.minio, 'custom_domain', '')
        
        # 创建MinIO客户端实例
        self.client = Minio(
            endpoint=self.endpoint,
            access_key=self.access_key,
            secret_key=self.secret_key,
            secure=self.secure
        )
        
        # 确保bucket存在
        self._ensure_bucket_exists()
    
    def _ensure_bucket_exists(self) -> None:
        """确保bucket存在，如果不存在则创建"""
        try:
            if not self.client.bucket_exists(self.bucket_name):
                self.client.make_bucket(self.bucket_name)
                logger.info(f"创建bucket: {self.bucket_name}")
            else:
                logger.debug(f"Bucket {self.bucket_name} 已存在")
        except S3Error as e:
            logger.error(f"检查或创建bucket失败: {e}")
            raise
    
    def upload_file(self, file_path: Path, object_name: Optional[str] = None) -> str:
        """
        上传文件到MinIO
        
        Args:
            file_path: 本地文件路径
            object_name: 对象名称，如果为None则自动生成
            
        Returns:
            str: 文件的公网访问URL
            
        Raises:
            S3Error: 上传失败时抛出异常
        """
        if not file_path.exists():
            raise FileNotFoundError(f"文件不存在: {file_path}")
        
        # 生成唯一的对象名称
        if object_name is None:
            file_extension = file_path.suffix
            object_name = f"charts/{uuid.uuid4().hex}{file_extension}"
        
        try:
            # 上传文件
            result = self.client.fput_object(
                bucket_name=self.bucket_name,
                object_name=object_name,
                file_path=str(file_path),
                content_type=self._get_content_type(file_path)
            )
            
            logger.info(f"文件上传成功: {object_name}, etag: {result.etag}")
            
            # 生成预签名URL
            url = self._generate_presigned_url(object_name)
            return url
            
        except S3Error as e:
            logger.error(f"文件上传失败: {e}")
            raise
    
    def _get_content_type(self, file_path: Path) -> str:
        """根据文件扩展名获取content type"""
        content_types = {
            '.png': 'image/png',
            '.jpg': 'image/jpeg',
            '.jpeg': 'image/jpeg',
            '.gif': 'image/gif',
            '.webp': 'image/webp',
            '.svg': 'image/svg+xml'
        }
        return content_types.get(file_path.suffix.lower(), 'application/octet-stream')
    
    def _generate_presigned_url(self, object_name: str) -> str:
        """
        生成预签名URL
        
        Args:
            object_name: 对象名称
            
        Returns:
            str: 预签名URL
        """
        try:
            expiry = timedelta(hours=self.url_expiry_hours)
            url = self.client.presigned_get_object(
                bucket_name=self.bucket_name,
                object_name=object_name,
                expires=expiry
            )
            
            # 如果配置了自定义域名，替换URL中的域名部分
            if self.custom_domain:
                from urllib.parse import urlparse, urlunparse
                parsed = urlparse(url)
                custom_parsed = parsed._replace(netloc=self.custom_domain)
                url = urlunparse(custom_parsed)
            
            return url
            
        except S3Error as e:
            logger.error(f"生成预签名URL失败: {e}")
            raise
    
    def delete_object(self, object_name: str) -> bool:
        """
        删除对象
        
        Args:
            object_name: 对象名称
            
        Returns:
            bool: 删除是否成功
        """
        try:
            self.client.remove_object(self.bucket_name, object_name)
            logger.info(f"删除对象成功: {object_name}")
            return True
        except S3Error as e:
            logger.error(f"删除对象失败: {e}")
            return False
    
    def get_object_info(self, object_name: str) -> dict:
        """
        获取对象信息
        
        Args:
            object_name: 对象名称
            
        Returns:
            dict: 对象信息
        """
        try:
            stat = self.client.stat_object(self.bucket_name, object_name)
            return {
                'object_name': stat.object_name,
                'size': stat.size,
                'last_modified': stat.last_modified,
                'etag': stat.etag,
                'content_type': stat.content_type
            }
        except S3Error as e:
            logger.error(f"获取对象信息失败: {e}")
            raise


# 创建全局MinIO客户端实例
minio_client = MinIOClient()