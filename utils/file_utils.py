import os
import shutil

def create_folders_from_txt(txt_path, output_folder):
    with open(txt_path, 'r', encoding='utf-8') as f:
        names = [line.strip() for line in f if line.strip()]
    
    os.makedirs(output_folder, exist_ok=True)
    for name in names:
        folder_path = os.path.join(output_folder, name)
        os.makedirs(folder_path, exist_ok=True)
    
    return names

def copy_selected_files_to_folders(source_folder, output_folder, names, selected_files):
    for name in names:
        dest_folder = os.path.join(output_folder, name)
        for file_name in selected_files:
            src_path = os.path.join(source_folder, file_name)
            dst_path = os.path.join(dest_folder, file_name)
            if os.path.exists(src_path):
                shutil.copy2(src_path, dst_path)