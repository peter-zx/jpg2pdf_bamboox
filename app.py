from flask import Flask, render_template, request, send_file, jsonify
import os
from datetime import datetime
from utils.file_utils import create_folders_from_txt, copy_selected_files_to_folders
from utils.pdf_utils import merge_jpgs_to_pdf
import urllib.parse
import time
import re
import zipfile

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
    subfolders = None
    processed_folders = None

    if request.method == "POST":
        action = request.form.get("action")

        if action == "batch":
            txt_file = request.files.get("txtFile")
            source_folder_raw = request.form.get("sourceFolder")
            if source_folder_raw is None:
                error = "请提供源文件夹路径！"
            else:
                source_folder = re.sub(r'^"|"$', '', urllib.parse.unquote(source_folder_raw)).strip()
                if not source_folder or not os.path.isdir(source_folder):
                    error = "无效的源文件夹路径，请确保路径存在且为文件夹！"
                else:
                    selected_files = request.form.get("selectedFiles", "").split(",") if request.form.get("selectedFiles") else []

                    if not txt_file or not txt_file.filename.endswith('.txt'):
                        error = "请上传一个TXT文件！"
                    else:
                        try:
                            temp_txt_path = os.path.join(DESKTOP_PATH, f"temp_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt")
                            txt_file.save(temp_txt_path)

                            timestamp = datetime.now().strftime("%m%d_%H%M")
                            output_folder = os.path.join(DESKTOP_PATH, f"批量文件复制_{timestamp}")
                            names = create_folders_from_txt(temp_txt_path, output_folder)
                            progress = f"已创建 {len(names)} 个文件夹"

                            copy_selected_files_to_folders(source_folder, output_folder, names, selected_files)
                            progress = f"已复制文件到 {len(names)} 个文件夹"
                            completed = "创建完毕"

                            os.remove(temp_txt_path)

                        except Exception as e:
                            error = f"批量处理失败：{str(e)}"

        elif action == "single":
            mode = request.form.get("mode", "single")
            if mode == "single":
                files = request.files.getlist("jpgFiles")
                save_name = request.form.get("saveName").strip()
                file_order = request.form.get("fileOrder").split(",") if request.form.get("fileOrder") else []

                if not files or not any(f.filename for f in files):
                    error = "请至少选择一个JPG文件！"
                elif not save_name:
                    error = "请输入保存文件名！"
                else:
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

                        if not jpg_paths:
                            error = "未找到可转换的JPG文件！"
                        else:
                            output_pdf = os.path.join(output_folder_single, f"{save_name}.pdf")
                            merge_jpgs_to_pdf(jpg_paths, output_pdf)
                            return send_file(output_pdf, as_attachment=True)

                    except Exception as e:
                        error = f"转换失败：{str(e)}"

            elif mode == "multi":
                parent_folder_raw = request.form.get("parentFolder")
                selected_subfolders = request.form.get("selectedSubfolders", "").split(",") if request.form.get("selectedSubfolders") else []

                if parent_folder_raw is None:
                    error = "请提供一级文件夹路径！"
                else:
                    parent_folder = re.sub(r'^"|"$', '', urllib.parse.unquote(parent_folder_raw)).strip()
                    if not parent_folder or not os.path.isdir(parent_folder):
                        error = "无效的一级文件夹路径，请确保路径存在且为文件夹！"
                    elif not selected_subfolders:
                        error = "请至少选择一个子文件夹！"
                    else:
                        try:
                            processed_folders = []
                            for subfolder in selected_subfolders:
                                subfolder_path = os.path.join(parent_folder, subfolder)
                                if os.path.isdir(subfolder_path):
                                    jpg_paths = [
                                        os.path.join(subfolder_path, f) for f in os.listdir(subfolder_path)
                                        if f.lower().endswith(('.jpg', '.jpeg')) and os.path.isfile(os.path.join(subfolder_path, f))
                                    ]
                                    if jpg_paths:
                                        output_pdf = os.path.join(subfolder_path, f"{subfolder}.pdf")
                                        merge_jpgs_to_pdf(jpg_paths, output_pdf)
                                        processed_folders.append(subfolder)

                            if not processed_folders:
                                error = "未找到可转换的JPG文件！"
                            else:
                                zip_path = os.path.join(DESKTOP_PATH, f"converted_pdfs_{datetime.now().strftime('%m%d_%H%M')}.zip")
                                with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
                                    for subfolder in processed_folders:
                                        pdf_path = os.path.join(parent_folder, subfolder, f"{subfolder}.pdf")
                                        if os.path.exists(pdf_path):
                                            zipf.write(pdf_path, os.path.join(subfolder, f"{subfolder}.pdf"))
                                return send_file(zip_path, as_attachment=True)

                        except Exception as e:
                            error = f"多层文件夹转换失败：{str(e)}"

    return render_template("index.html", error=error, names=names, output_folder=output_folder, files_in_folder=files_in_folder, source_folder=source_folder, progress=progress, completed=completed, subfolders=subfolders, processed_folders=processed_folders)

@app.route("/list_files", methods=["POST"])
def list_files():
    source_folder_raw = request.form.get("sourceFolder")
    if source_folder_raw is None:
        return jsonify({"error": "请提供源文件夹路径！"}), 400

    source_folder = re.sub(r'^"|"$', '', urllib.parse.unquote(source_folder_raw)).strip()
    if not source_folder or not os.path.isdir(source_folder):
        return jsonify({"error": "无效的文件夹路径，请确保路径存在且为文件夹！"}), 400

    try:
        files = [f for f in os.listdir(source_folder) if os.path.isfile(os.path.join(source_folder, f))]
        return jsonify({"files": files})
    except Exception as e:
        return jsonify({"error": f"读取文件失败：{str(e)}"}), 500

@app.route("/list_subfolders", methods=["POST"])
def list_subfolders():
    parent_folder_raw = request.form.get("parentFolder")
    if parent_folder_raw is None:
        return jsonify({"error": "请提供一级文件夹路径！"}), 400

    parent_folder = re.sub(r'^"|"$', '', urllib.parse.unquote(parent_folder_raw)).strip()
    if not parent_folder or not os.path.isdir(parent_folder):
        return jsonify({"error": "无效的一级文件夹路径，请确保路径存在且为文件夹！"}), 400

    try:
        subfolders = [f for f in os.listdir(parent_folder) if os.path.isdir(os.path.join(parent_folder, f))]
        return jsonify({"subfolders": subfolders})
    except Exception as e:
        return jsonify({"error": f"读取子文件夹失败：{str(e)}"}), 500

if __name__ == "__main__":
    app.run(debug=True)