import os
import img2pdf
from PIL import Image

def merge_jpgs_to_pdf(input_path, output_pdf):
    """合并指定路径（文件夹或文件列表）的JPG到PDF"""
    if isinstance(input_path, list):
        jpg_paths = [p for p in input_path if p.lower().endswith(('.jpg', '.jpeg'))]
    else:
        jpg_paths = [
            os.path.join(input_path, f) for f in os.listdir(input_path)
            if f.lower().endswith(('.jpg', '.jpeg')) and os.path.isfile(os.path.join(input_path, f))
        ]

    if not jpg_paths:
        return 0

    # 转换为JPG（确保兼容）
    valid_paths = []
    for path in jpg_paths:
        try:
            with Image.open(path) as img:
                if img.format in ['JPEG']:
                    valid_paths.append(path)
        except:
            continue

    if valid_paths:
        with open(output_pdf, "wb") as f:
            f.write(img2pdf.convert(valid_paths))
    return len(valid_paths)