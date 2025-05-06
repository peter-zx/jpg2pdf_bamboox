from PIL import Image
import os

def merge_jpgs_to_pdf(jpg_paths, output_pdf):
    if not jpg_paths:
        print("没有提供JPG文件路径")
        return False

    images = []
    for jpg_path in jpg_paths:
        try:
            if os.path.exists(jpg_path) and os.access(jpg_path, os.R_OK):
                img = Image.open(jpg_path)
                if img.mode != 'RGB':
                    img = img.convert('RGB')
                images.append(img)
            else:
                print(f"文件不可访问或不存在：{jpg_path}")
        except Exception as e:
            print(f"无法打开文件 {jpg_path}：{str(e)}")
            continue

    if not images:
        print("没有有效的图像文件可以合并")
        return False

    try:
        images[0].save(output_pdf, save_all=True, append_images=images[1:], quality=95)
        print(f"PDF已生成：{output_pdf}")
        return True
    except Exception as e:
        print(f"PDF合并失败：{str(e)}")
        return False