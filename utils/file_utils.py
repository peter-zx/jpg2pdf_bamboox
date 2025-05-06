import os
import shutil

def create_folders_from_txt(txt_path, output_folder):
    """从TXT文件读取名字，创建对应文件夹"""
    names = []
    with open(txt_path, 'r', encoding='utf-8') as f:
        for line in f:
            name = line.strip()
            if name:
                names.append(name)
                folder_path = os.path.join(output_folder, name)
                os.makedirs(folder_path, exist_ok=True)
    return names

def copy_selected_files_to_folders(source_folder, output_folder, names, selected_files):
    """将源文件夹中选中的文件复制到每个人的文件夹"""
    if not selected_files:
        return  # 如果没有选择文件，则不执行复制

    for name in names:
        dest_folder = os.path.join(output_folder, name)
        for filename in selected_files:
            src_path = os.path.join(source_folder, filename)
            dest_path = os.path.join(dest_folder, filename)
            if os.path.isfile(src_path):
                shutil.copy2(src_path, dest_path)