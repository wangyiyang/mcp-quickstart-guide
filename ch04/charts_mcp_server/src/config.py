from dynaconf import Dynaconf
from pathlib import Path

# 获取项目根目录
PROJECT_ROOT = Path(__file__).parent.parent

# 配置文件路径
config_dir = PROJECT_ROOT / "config"

# 初始化Dynaconf配置
settings = Dynaconf(
    # 环境变量前缀
    envvar_prefix="CHARTS_MCP",
    # 配置文件目录
    settings_files=[
        str(config_dir / "settings.toml"),
        str(config_dir / ".secrets.toml"),
    ],
    # 环境设置（关闭以避免配置问题）
    environments=False,
    # 从环境变量加载
    load_dotenv=True,
)

# 导出配置实例
__all__ = ["settings", "PROJECT_ROOT"]