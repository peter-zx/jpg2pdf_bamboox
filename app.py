from flask import Flask, render_template, request, send_file, jsonify
import os
from datetime import datetime
from utils.file_utils import create_folders_from_txt, copy_selected_files_to_folders
from utils.pdf_utils import merge_jpgs_to_pdf
import urllib.parse
import time

app = Flask(__name__)

# 获取桌面路径
DESKTOP_PATH = os.path.join(os.path.expanduser("~"), "Desktop")

@app.route("/", methods=["GET", "POST"])
def index():
    error = None
    names = None
    output_folder = None
    files_in_folder = None
    source_folder = None
    progress = None
    completed = None

    if request.method == "POST":
        action = request.form.get("action")

        if action == "batch":
            txt_file = request.files.get("txtFile")
            source_folder_raw = request.form.get("sourceFolder")
            if source_folder_raw is None:
                error = "请提供源文件夹路径！"
            else:
                source_folder = urllib.parse.unquote(source_folder_raw).strip()
                selected_files = request.form.get("selectedFiles", "").split(",") if request.form.get("selectedFiles") else []

                if not txt_file or not txt_file.filename.endswith('.txt'):
                    error = "请上传一个TXT文件！"
                elif not source_folder or not os.path.isdir(source_folder):
                    error = "请输入有效的源文件夹路径！"
                else:
                    try:
                        # 保存TXT到临时路径
                        temp_txt_path = os.path.join(DESKTOP_PATH, f"temp_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt")
                        txt_file.save(temp_txt_path)

                        # 步骤1：创建个人文件夹
                        timestamp = datetime.now().strftime("%m%d_%H%M")
                        output_folder = os.path.join(DESKTOP_PATH, f"批量文件复制_{timestamp}")
                        names = create_folders_from_txt(temp_txt_path, output_folder)
                        progress = f"已创建 {len(names)} 个文件夹"

                        # 步骤2：复制选中的文件
                        copy_selected_files_to_folders(source_folder, output_folder, names, selected_files)
                        progress = f"已复制文件到 {len(names)} 个文件夹"
                        completed = "创建完毕"

                        # 清理临时TXT
                        os.remove(temp_txt_path)

                    except Exception as e:
                        error = f"批量处理失败：{str(e)}"

        elif action == "single":
            files = request.files.getlist("jpgFiles")
            save_name = request.form.get("saveName").strip()
            file_order = request.form.get("fileOrder").split(",") if request.form.get("fileOrder") else []

            if not files or not any(f.filename for f in files):
                error = "请至少选择一个JPG文件！"
            elif not save_name:
                error = "请输入保存文件名！"
            else:
                for file in files:
                    if not file.filename.lower().endswith(('.jpg', '.jpeg')):
                        error = "请确保至少有一个文件是JPG格式！"
                        break

                if not error:
                    try:
                        output_folder_single = os.path.join(DESKTOP_PATH, save_name)
                        os.makedirs(output_folder_single, exist_ok=True)

                        jpg_paths = []
                        file_map = {file.filename: file for file in files}
                        ordered_files = [file_map[filename] for filename in file_order if filename in file_map] or files
                        for file in ordered_files:
                            jpg_path = os.path.join(output_folder_single, file.filename)
                            file.save(jpg_path)
                            if file.filename.lower().endswith(('.jpg', '.jpeg')):
                                jpg_paths.append(jpg_path)

                        if jpg_paths:
                            output_pdf = os.path.join(output_folder_single, f"{save_name}.pdf")
                            merge_jpgs_to_pdf(jpg_paths, output_pdf)
                            return send_file(output_pdf, as_attachment=True)
                        else:
                            error = "未找到可转换的JPG文件！"

                    except Exception as e:
                        error = f"转换失败：{str(e)}"

    return render_template("index.html", error=error, names=names, output_folder=output_folder, files_in_folder=files_in_folder, source_folder=source_folder, progress=progress, completed=completed)

@app.route("/list_files", methods=["POST"])
def list_files():
    source_folder_raw = request.form.get("sourceFolder")
    if source_folder_raw is None:
        return jsonify({"error": "请提供源文件夹路径！"}), 400

    source_folder = urllib.parse.unquote(source_folder_raw).strip()
    if not source_folder or not os.path.isdir(source_folder):
        return jsonify({"error": "无效的文件夹路径！"}), 400

    try:
        files = [f for f in os.listdir(source_folder) if os.path.isfile(os.path.join(source_folder, f))]
        return jsonify({"files": files})
    except Exception as e:
        return jsonify({"error": f"读取文件失败：{str(e)}"}), 500

if __name__ == "__main__":
    app.run(debug=True)