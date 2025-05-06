```
jpg2pdf/
├── app.py
├── utils/
│   ├── file_utils.py
│   └── pdf_utils.py
├── templates/
│   ├── index.html
│   └── batch.html
├── static/
│   ├── styles.css
│   ├── script.js
│   └── batch.js
├── README.md
├── .gitignore
├── requirements.txt
├── venv/

```
JPG to PDF Converter
一个基于Python和Flask的Web工具，支持单文件和批量JPG到PDF转换。
功能
单文件转换

选择多个JPG文件，显示文件名列表，支持上下移动调整顺序。
输入保存文件名，自动创建同名文件夹和PDF文件。
保存到桌面（带时间戳，如myfile_20250219_123456/myfile.pdf）。

批量处理

上传TXT文件（每行一个人员名字）。
创建个人文件夹，复制指定文件夹的文件到每个人的文件夹。
手动选择每个人的文件夹，合并其中的JPG为PDF，保存到桌面（文件名为人名）。

环境要求

Python 3.8+
虚拟环境（推荐）
依赖：Flask, img2pdf, Pillow

安装

克隆或下载项目到本地。
导航到项目目录：cd jpg2pdf


创建并激活虚拟环境：python -m venv venv
.\venv\Scripts\activate


安装依赖：pip install -r requirements.txt



运行

确保虚拟环境已激活。
运行Flask应用：python app.py


打开浏览器：
单文件转换：http://127.0.0.1:5000
批量处理：http://127.0.0.1:5000/batch



使用

单文件转换：
选择JPG文件，调整顺序，输入保存文件名。
点击“合并并保存PDF”。


批量处理：
上传包含人员名字的TXT文件。
输入源文件夹路径（如D:\data）。
点击“创建文件夹和复制文件”。
手动输入每个人的文件夹路径，点击“合并”生成PDF。



注意事项

仅支持标准JPG文件（.jpg/.jpeg）。
批量处理支持常见文件格式（JPG, PNG, PDF, DOCX, TXT等）复制。
输出文件夹和PDF保存在桌面，批量文件夹带时间戳。

贡献
欢迎提交Issue或Pull Request！
许可证
MIT License
