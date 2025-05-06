```

jpg2pdf/
├── app.py              # Flask主程序，处理Web逻辑
├── templates/          # HTML模板目录
│   └── index.html      # WebUI界面
├── README.md           # 项目说明
├── .gitignore          # Git忽略文件
├── requirements.txt    # 依赖清单

```

JPG to PDF Converter
一个基于Python和Flask的Web工具，用于将多个JPG文件合并成一个PDF文件，并保存到桌面指定文件夹。
功能

通过Web界面选择多个JPG文件。
显示选中的文件名列表，支持上下移动调整顺序。
输入单一保存文件名，自动创建同名文件夹和PDF文件。
自动在桌面创建文件夹（带时间戳），合并JPG为PDF并保存。
显示错误提示（如文件格式错误）。

环境要求

Python 3.8+
虚拟环境（推荐）
依赖：Flask, img2pdf

安装

克隆或下载项目到本地。
导航到项目目录：cd jpg2pdf


创建并激活虚拟环境：python -m venv venv
.\venv\Scripts\activate


安装依赖：pip install -r requirements.txt



运行

确保虚拟环境已激活。
运行Flask应用：python app.py


打开浏览器，访问http://127.0.0.1:5000。
选择JPG文件，调整文件顺序，输入保存文件名，点击“合并并保存PDF”。

部署

可部署到ECS，使用Nginx+Gunicorn（参考Flask官方文档）。
确保服务器安装Python和依赖。

注意事项

仅支持标准JPG文件（.jpg/.jpeg）。
输出文件夹自动添加时间戳（如myfile_20250219_123456）。
PDF文件保存在桌面指定文件夹（如myfile_20250219_123456/myfile.pdf）。

贡献
欢迎提交Issue或Pull Request！
许可证
MIT License
