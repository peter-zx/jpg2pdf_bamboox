from flask import Flask, render_template, request, send_file
import img2pdf
import os
from datetime import datetime

app = Flask(__name__)

# 获取桌面路径
DESKTOP_PATH = os.path.join(os.path.expanduser("~"), "Desktop")

@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        # 获取上传的文件和输入
        files = request.files.getlist("jpgFiles")
        save_name = request.form.get("saveName").strip()
        file_order = request.form.get("fileOrder").split(",") if request.form.get("fileOrder") else []

        # 验证输入
        if not files or not any(f.filename for f in files):
            return render_template("index.html", error="请至少选择一个JPG文件！")
        if not save_name:
            return render_template("index.html", error="请输入保存文件名！")

        # 确保是JPG文件
        for file in files:
            if not file.filename.lower().endswith(('.jpg', '.jpeg')):
                return render_template("index.html", error="请确保所有文件都是JPG格式！")

        try:
            # 创建目标文件夹
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_folder = os.path.join(DESKTOP_PATH, f"{save_name}_{timestamp}")
            os.makedirs(output_folder, exist_ok=True)

            # 保存上传的JPG文件，按用户指定的顺序
            jpg_paths = []
            file_map = {file.filename: file for file in files}
            ordered_files = [file_map[filename] for filename in file_order if filename in file_map] or files
            for file in ordered_files:
                jpg_path = os.path.join(output_folder, file.filename)
                file.save(jpg_path)
                jpg_paths.append(jpg_path)

            # 合并为PDF
            output_pdf = os.path.join(output_folder, f"{save_name}.pdf")
            with open(output_pdf, "wb") as f:
                f.write(img2pdf.convert(jpg_paths))

            # 返回PDF文件
            return send_file(output_pdf, as_attachment=True)

        except Exception as e:
            return render_template("index.html", error=f"转换失败：{str(e)}")

    return render_template("index.html", error=None)

if __name__ == "__main__":
    app.run(debug=True)