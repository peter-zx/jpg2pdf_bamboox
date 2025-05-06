from flask import Blueprint, render_template, request, send_file, jsonify
import os
from datetime import datetime
from utils.pdf_utils import merge_jpgs_to_pdf
import urllib.parse
import re
import shutil

single_bp = Blueprint('single', __name__)

# 获取桌面路径
DESKTOP_PATH = os.path.join(os.path.expanduser("~"), "Desktop")

@single_bp.route("/", methods=["GET", "POST"])
def index():
    batch_data = {
        "error": None,
        "names": None,
        "output_folder": None,
        "files_in_folder": None,
        "source_folder": None,
        "progress": None,
        "completed": None
    }
    single_data = {
        "error": None,
        "subfolders": None,
        "processed_folders": None,
        "completed": None,
        "progress": None
    }

    return render_template("index.html", batch=batch_data, single=single_data)

@single_bp.route("/process_single", methods=["POST"])
def process_single():
    mode = request.form.get("mode", "single")
    response = {"error": None, "processed_folders": [], "progress": None, "completed": None}

    if mode == "single":
        files = request.files.getlist("jpgFiles")
        save_name = request.form.get("saveName").strip()
        file_order = request.form.get("fileOrder").split(",") if request.form.get("fileOrder") else []

        if not files or not any(f.filename for f in files):
            response["error"] = "请至少选择一个JPG文件！"
            return jsonify(response), 400
        elif not save_name:
            response["error"] = "请输入保存文件名！"
            return jsonify(response), 400

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
                response["error"] = "未找到可转换的JPG文件！"
                return jsonify(response), 400

            output_pdf = os.path.join(output_folder_single, f"{save_name}.pdf")
            merge_jpgs_to_pdf(jpg_paths, output_pdf)
            response["completed"] = "保存完毕：单个PDF已生成"
            return jsonify(response)

        except Exception as e:
            response["error"] = f"转换失败：{str(e)}"
            return jsonify(response), 500

    elif mode == "multi":
        parent_folder_raw = request.form.get("parentFolder")
        selected_subfolders = request.form.get("selectedSubfolders", "").split(",") if request.form.get("selectedSubfolders") else []

        if parent_folder_raw is None:
            response["error"] = "请提供一级文件夹路径！"
            return jsonify(response), 400

        parent_folder = re.sub(r'^"|"$', '', urllib.parse.unquote(parent_folder_raw)).strip()
        if not parent_folder or not os.path.isdir(parent_folder):
            response["error"] = "无效的一级文件夹路径，请确保路径存在且为文件夹！"
            return jsonify(response), 400
        elif not selected_subfolders:
            response["error"] = "请至少选择一个子文件夹！"
            return jsonify(response), 400

        try:
            output_base = os.path.join(DESKTOP_PATH, "jpg2pdf合并")
            os.makedirs(output_base, exist_ok=True)
            response["processed_folders"] = []
            total_folders = len(selected_subfolders)
            for idx, subfolder in enumerate(selected_subfolders, 1):
                subfolder_path = os.path.join(parent_folder, subfolder)
                if os.path.isdir(subfolder_path):
                    jpg_paths = [
                        os.path.join(subfolder_path, f) for f in os.listdir(subfolder_path)
                        if f.lower().endswith(('.jpg', '.jpeg')) and os.path.isfile(os.path.join(subfolder_path, f))
                    ]
                    if jpg_paths:
                        dest_subfolder = os.path.join(output_base, subfolder)
                        os.makedirs(dest_subfolder, exist_ok=True)
                        for jpg in jpg_paths:
                            shutil.copy2(jpg, dest_subfolder)
                        output_pdf = os.path.join(dest_subfolder, f"{subfolder}.pdf")
                        merge_jpgs_to_pdf(jpg_paths, output_pdf)
                        if os.path.exists(output_pdf):
                            response["processed_folders"].append(subfolder)
                        else:
                            print(f"PDF未生成：{output_pdf}")
                    else:
                        print(f"未找到JPG文件：{subfolder_path}")
                response["progress"] = f"处理中：{idx}/{total_folders}"

            if not response["processed_folders"]:
                response["error"] = "未找到可转换的JPG文件！"
                return jsonify(response), 400

            response["completed"] = f"合并完毕：已为 {len(response['processed_folders'])} 个子文件夹生成PDF"
            return jsonify(response)

        except Exception as e:
            response["error"] = f"多层文件夹转换失败：{str(e)}"
            return jsonify(response), 500

@single_bp.route("/list_subfolders", methods=["POST"])
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