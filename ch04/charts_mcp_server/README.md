# Charts MCP Server

基于FastMCP、pyecharts和MinIO的图表生成MCP服务器，支持生成柱状图、饼图和折线图，并自动转换为图片上传到对象存储。

## 功能特性

- ✨ **多种图表类型**：支持柱状图、饼图、折线图
- 🎨 **丰富主题**：支持15种预设主题样式
- 📸 **自动截图**：使用Playwright自动将HTML图表转换为高质量图片
- ☁️ **云存储**：自动上传到MinIO对象存储并返回访问URL
- ⚙️ **配置化管理**：使用Dynaconf进行灵活的配置管理
- 🔧 **MCP协议**：基于FastMCP框架，支持HTTP传输
- 📝 **详细日志**：使用loguru提供完整的操作日志

## 系统要求

- Python 3.8+
- MinIO服务器（用于图片存储）
- 足够的磁盘空间用于临时文件

## 安装部署

### 1. 安装依赖

```bash
pip install -r requirements.txt
```

### 2. 安装Playwright浏览器

```bash
playwright install chromium
```

### 3. 配置MinIO

确保MinIO服务器正在运行，并修改 `config/.secrets.toml` 文件：

```toml
[minio]
access_key = "your_access_key"
secret_key = "your_secret_key"
custom_domain = "your_custom_domain"  # 可选，自定义域名
```

### 4. 启动服务器

```bash
python main.py
```

服务器将在 `http://127.0.0.1:8000/mcp` 启动。

## 配置说明

### 主配置文件 (config/settings.toml)

```toml
[mcp_server]
host = "127.0.0.1"
port = 8000
path = "/mcp"

[minio]
endpoint = "localhost:9000"
bucket_name = "charts"
secure = false
url_expiry_hours = 24

[charts]
default_width = 800
default_height = 600
default_theme = "white"
temp_dir = "temp"

[screenshot]
viewport_width = 1024
viewport_height = 768
wait_time = 2000

[logging]
level = "INFO"
format = "{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {message}"
```

## MCP工具使用

### 1. 生成柱状图

```python
generate_bar_chart(
    title="销售数据",
    x_data=["Q1", "Q2", "Q3", "Q4"],
    series_data=[
        {"name": "商家A", "data": [114, 55, 27, 101]},
        {"name": "商家B", "data": [57, 134, 137, 129]}
    ],
    width=800,
    height=600,
    theme="macarons"
)
```

### 2. 生成饼图

```python
generate_pie_chart(
    title="产品销售占比",
    data=[
        {"name": "产品A", "value": 335},
        {"name": "产品B", "value": 310},
        {"name": "产品C", "value": 274},
        {"name": "产品D", "value": 235}
    ],
    theme="infographic"
)
```

### 3. 生成折线图

```python
generate_line_chart(
    title="温度变化趋势",
    x_data=["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"],
    series_data=[
        {"name": "温度", "data": [11, 11, 15, 13, 12, 13, 10]},
        {"name": "湿度", "data": [1, -2, 2, 5, 3, 2, 0]}
    ],
    chart_options={
        "tooltip": {"trigger": "axis"},
        "grid": {"left": "5%", "right": "5%"}
    }
)
```

### 4. 获取服务器信息

```python
get_server_info()
```

## 支持的主题

- `white` - 白色主题（默认）
- `light` - 浅色主题
- `dark` - 深色主题
- `chalk` - 粉笔主题
- `essos` - essos主题
- `infographic` - 信息图主题
- `macarons` - 马卡龙主题
- `purple_passion` - 紫色激情主题
- `roma` - 罗马主题
- `romantic` - 浪漫主题
- `shine` - 闪耀主题
- `vintage` - 复古主题
- `walden` - 瓦尔登主题
- `westeros` - 维斯特洛主题
- `wonderland` - 仙境主题

## Claude Code集成

### 1. 在Claude Code中配置MCP服务器

在Claude Code的设置中添加MCP服务器配置：

```json
{
  "mcpServers": {
    "charts": {
      "url": "http://localhost:8000/mcp",
      "transport": "http"
    }
  }
}
```

### 2. 使用示例

在Claude Code中，你可以通过自然语言请求生成图表：

```
"请生成一个显示Q1到Q4季度销售数据的柱状图，商家A的数据是[114, 55, 27, 101]，商家B的数据是[57, 134, 137, 129]"
```

Claude会自动调用相应的MCP工具生成图表并返回图片URL。

## 高级配置

### 图表选项 (chart_options)

每个图表工具都支持 `chart_options` 参数，用于自定义图表样式：

```python
chart_options = {
    "title": {"text": "自定义标题", "left": "center"},
    "legend": {"bottom": "10px"},
    "tooltip": {"trigger": "axis"},
    "xaxis": {"name": "X轴标题"},
    "yaxis": {"name": "Y轴标题"},
    "grid": {"left": "5%", "right": "5%", "top": "15%", "bottom": "15%"}
}
```

### 系列特定选项

在 `series_data` 中可以为每个系列指定特殊选项：

```python
series_data = [
    {
        "name": "系列1",
        "data": [10, 20, 30, 40],
        "options": {
            "smooth": True,  # 折线图专用：平滑曲线
            "symbol_show": False,  # 折线图专用：隐藏数据点
            "areastyle": {"opacity": 0.5}  # 折线图专用：区域填充
        }
    }
]
```

## 故障排除

### 常见问题

1. **MinIO连接失败**
   - 检查MinIO服务器是否运行
   - 验证 `config/.secrets.toml` 中的凭据
   - 确认网络连接

2. **Playwright截图失败**
   - 确保已安装Chromium: `playwright install chromium`
   - 检查系统依赖是否完整

3. **临时文件积累**
   - 服务器会自动清理临时文件
   - 可手动清理 `temp/` 目录

4. **图表渲染问题**
   - 检查数据格式是否正确
   - 验证pyecharts版本兼容性

### 日志查看

服务器运行时会输出详细日志，包括：
- 请求处理状态
- 图表生成进度
- 文件上传结果
- 错误信息

## 项目结构

```
charts_mcp_server/
├── main.py                    # FastMCP服务器入口
├── requirements.txt           # 依赖包列表
├── README.md                 # 项目说明
├── config/                   # 配置文件
│   ├── settings.toml         # 主配置
│   └── .secrets.toml         # 敏感信息配置
├── src/                      # 源代码
│   ├── config.py             # 配置加载
│   ├── charts/               # 图表生成模块
│   │   ├── bar_chart.py      # 柱状图
│   │   ├── pie_chart.py      # 饼图
│   │   └── line_chart.py     # 折线图
│   ├── storage/              # 存储模块
│   │   └── minio_client.py   # MinIO客户端
│   └── utils/                # 工具模块
│       ├── screenshot.py     # 截图工具
│       └── temp_files.py     # 临时文件管理
└── temp/                     # 临时文件目录
```

## 许可证

本项目遵循 MIT 许可证。

## 贡献

欢迎提交Issue和Pull Request来改进这个项目。

## 联系

如有问题，请在项目GitHub页面创建Issue。