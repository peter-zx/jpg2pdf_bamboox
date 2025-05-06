from flask import Flask, render_template, request, send_file
import os
from datetime import datetime
from utils.file_utils import create_folders_from_txt, copy_files_to_folders
from utils.pdf_utils import merge_jpgs_to_pdf

app = Flask(__name__)

# 获取桌面路径
DESKTOP_PATH = os.path.join(os.path.expanduser("~"), "Desktop")

@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        files = request.files.getlist("jpgFiles")
        save_name = request.form.get("saveName").strip()
        file_order = request.form.get("fileOrder").split(",") if request.form.get("fileOrder") else []

        if not files or not any(f.filename for f in files):
            return render_template("index.html", error="请至少选择一个JPG文件！")
        if not save_name:
            return render_template("index.html", error="请输入保存文件名！")

        for file in files:
            if not file.filename.lower().endswith(('.jpg', '.jpeg')):
                return render_template("index.html", error="请确保所有文件都是JPG格式！")

        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_folder = os.path.join(DESKTOP_PATH, f"{save_name}_{timestamp}")
            os.makedirs(output_folder, exist_ok=True)

            jpg_paths = []
            file_map = {file.filename: file for file in files}
            ordered_files = [file_map[filename] for filename in file_order if filename in file_map] or files
            for file in ordered_files:
                jpg_path = os.path.join(output_folder, file.filename)
                file.save(jpg_path)
                jpg_paths.append(jpg_path)

            output_pdf = os.path.join(output_folder, f"{save_name}.pdf")
            merge_jpgs_to_pdf(jpg_paths, output_pdf)

            return send_file(output_pdf, as_attachment=True)

        except Exception as e:
            return render_template("index.html", error=f"转换失败：{str(e)}")

    return render_template("index.html", error=None)

@app.route("/batch", methods=["GET", "POST"])
def batch():
    if request.method == "POST":
        txt_file = request.files.get("txtFile")
        source_folder = request.form.get("sourceFolder").strip()
        output_base = DESKTOP_PATH  # 默认输出到桌面

        if not txt_file or not txt_file.filename.endswith('.txt'):
            return render_template("batch.html", error="请上传一个TXT文件！")
        if not source_folder or not os.path.isdir(source_folder):
            return render_template("batch.html", error="请输入有效的源文件夹路径！")

        try:
            # 保存TXT文件到临时路径
            temp_txt_path = os.path.join(output_base, f"temp_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt")
            txt_file.save(temp_txt_path)

            # 步骤1：创建个人文件夹
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_folder = os.path.join(output_base, f"batch_{timestamp}")
            names = create_folders_from_txt(temp_txt_path, output_folder)

            # 步骤2：复制文件到每个文件夹
            copy_files_to_folders(source_folder, output_folder, names)

            # 步骤3：合并每个文件夹的JPG到PDF
            results = []
            for name in names:
                person_folder = os.path.join(output_folder, name)
                output_pdf = os.path.join(DESKTOP_PATH, f"{name}.pdf")
                jpg_count = merge_jpgs_to_pdf(person_folder, output_pdf)
                results.append(f"{name}: 合并了 {jpg_count} 个JPG文件到 {output_pdf}")

            # 清理临时TXT
            os.remove(temp_txt_path)

            return render_template("batch.html", results=results, error=None)

        except Exception as e:
            return render_template("batch.html", error=f"批量处理失败：{str(e)}")

    return render_template("batch.html", error=None, results=None)

if __name__ == "__main__":
    app.run(debug=True)