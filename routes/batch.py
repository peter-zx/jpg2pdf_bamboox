from flask import Blueprint, render_template, request, jsonify
import os
from datetime import datetime
from utils.file_utils import create_folders_from_txt, copy_selected_files_to_folders
import urllib.parse
import re

batch_bp = Blueprint('batch', __name__)

# 获取桌面路径
DESKTOP_PATH = os.path.join(os.path.expanduser("~"), "Desktop")

@batch_bp.route("/", methods=["GET", "POST"])
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

    if request.method == "POST" and request.form.get("action") == "batch":
        txt_file = request.files.get("txtFile")
        source_folder_raw = request.form.get("sourceFolder")
        if source_folder_raw is None:
            batch_data["error"] = "请提供源文件夹路径！"
        else:
            source_folder = re.sub(r'^"|"$', '', urllib.parse.unquote(source_folder_raw)).strip()
            if not source_folder or not os.path.isdir(source_folder):
                batch_data["error"] = "无效的源文件夹路径，请确保路径存在且为文件夹！"
            else:
                selected_files = request.form.get("selectedFiles", "").split(",") if request.form.get("selectedFiles") else []

                if not txt_file or not txt_file.filename.endswith('.txt'):
                    batch_data["error"] = "请上传一个TXT文件！"
                else:
                    try:
                        temp_txt_path = os.path.join(DESKTOP_PATH, f"temp_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt")
                        txt_file.save(temp_txt_path)

                        timestamp = datetime.now().strftime("%m%d_%H%M")
                        batch_data["output_folder"] = os.path.join(DESKTOP_PATH, f"批量文件复制_{timestamp}")
                        batch_data["names"] = create_folders_from_txt(temp_txt_path, batch_data["output_folder"])
                        batch_data["progress"] = f"已创建 {len(batch_data['names'])} 个文件夹"

                        copy_selected_files_to_folders(source_folder, batch_data["output_folder"], batch_data["names"], selected_files)
                        batch_data["progress"] = f"已复制文件到 {len(batch_data['names'])} 个文件夹"
                        batch_data["completed"] = "创建完毕"

                        os.remove(temp_txt_path)

                    except Exception as e:
                        batch_data["error"] = f"批量处理失败：{str(e)}"

    return render_template("index.html", batch=batch_data, single=single_data)

@batch_bp.route("/list_files", methods=["POST"])
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