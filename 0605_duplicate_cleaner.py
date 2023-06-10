''' duplicate cleaner DIY'''

import os
import filecmp
import re
import shutil
import tempfile



def exchange_better_name(folder_a, folder_b, transfer_folder):
    '''
    基于文件查重和文件名选优的图片文件替换\n
    以folder_a为修正后图片库（但库存不一定完整）
    检查folder_b的图片库完整性并进行文件名修正
    '''
    image_files_a = get_image_files(folder_a)
    image_files_b = get_image_files(folder_b)

    image_files_a.sort(key=os.path.getsize)
    image_files_b.sort(key=os.path.getsize)

    iter_a = iter(image_files_a)

    while True:
        try:
            file_a = next(iter_a)
        except StopIteration:
            break

        iter_b = iter(image_files_b)
        while True:
            try:
                file_b = next(iter_b)
            except StopIteration:
                break

            size_a = os.path.getsize(file_a)
            size_b = os.path.getsize(file_b)

            if size_a > size_b:
                continue

            if size_a < size_b:
                break

            if compare_images(file_a, file_b):
                if better_filename(file_a, file_b):
                    exchange_files(file_a, file_b, transfer_folder)
                    image_files_a.remove(file_a)
                    image_files_b.remove(file_b)
                    break

def complement_images(folder_a, folder_b, destination_folder):
    '''
    基于文件查重的图片文件补全\n
    以folder_a为补充图片库
    检查folder_b中图片库存的完整性
    并向destination_folder中补充缺失的图片文件
    '''
    image_files_a = get_image_files(folder_a)
    image_files_b = get_image_files(folder_b)
    
    image_files_a.sort(key=os.path.getsize)
    image_files_b.sort(key=os.path.getsize)

    iter_a = iter(image_files_a)

    while True:
        try:
            file_a = next(iter_a)
        except StopIteration:
            break

        iter_b = iter(image_files_b)
        while True:
            try:
                file_b = next(iter_b)
            except StopIteration:
                break

            size_a = os.path.getsize(file_a)
            size_b = os.path.getsize(file_b)

            if size_a > size_b:
                continue

            if size_a < size_b:
                move_file(file_a, destination_folder)
                image_files_a.remove(file_a)
                break

            if compare_images(file_a, file_b):
                break

            move_file(file_a, destination_folder)
            image_files_a.remove(file_a)
            break

def remove_duplicate_images(folder, recycle_folder):
    '''同文件夹内的图片去重'''
    image_files = get_image_files(folder)
    image_files.sort(key=os.path.getsize)

    iterator = iter(image_files)

    file_a = next(iterator)
    while True:
        try:
            file_b = next(iterator)
        except StopIteration:
            break

        size_a = os.path.getsize(file_a)
        size_b = os.path.getsize(file_b)

        if size_a < size_b:
            file_a = file_b

        elif compare_images(file_a,file_b):

            if better_filename(file_a,file_b):
                move_file(file_b,recycle_folder)
                image_files.remove(file_b)
                print(f'Removed {file_b} and kept {file_a}')

            else:
                move_file(file_a,recycle_folder)
                image_files.remove(file_a)
                print(f'Removed {file_a} and kept {file_b}')
                file_a = file_b



def get_image_files(folder):
    '''获取一个文件夹内所有的图片类型文件'''
    image_files = []
    for root, _, files in os.walk(folder):
        for file in files:
            if is_image_file(file):
                file_path = os.path.join(root, file)
                image_files.append(file_path)
    return image_files

def is_image_file(file) -> bool:
    '''检查是否是图片类型的文件'''
    image_extensions = ['.png', '.jpg', '.jpeg', '.jpe', '.jif', '.jfif', '.jfi',
                   '.gif', '.bmp', '.tiff', '.tif', '.webp', '.ico', '.psd',
                   '.svg', '.eps', '.ai', '.pdf', '.raw', '.heic']
    _, ext = os.path.splitext(file)
    return ext.lower() in image_extensions

def compare_images(file_a, file_b, name = False) -> bool:
    '''检查两个图片文件是否完全相同（格式、大小和内容）\n
    name == True 时才会比较文件名是否相同（未实现）
    '''
    if compare_file_extensions(file_a,file_b) and compare_file_size(file_a,file_b):
        if filecmp.cmp(file_a, file_b, shallow=False):
            return True
    return False


def get_video_files(folder):
    '''获取一个文件夹内所有的图片类型文件'''
    video_files = []
    for root, _, files in os.walk(folder):
        for file in files:
            if is_video_file(file):
                file_path = os.path.join(root, file)
                video_files.append(file_path)
    return video_files

def is_video_file(file):
    '''判断文件扩展名是否为视频格式'''
    video_extensions = [
        '.mp4', '.avi', '.mov', '.mkv', '.flv', '.wmv', '.m4v', '.webm',
        '.3gp', '.mpeg', '.mpg', '.rm', '.swf', '.vob', '.ts', '.mts',
        '.divx', '.xvid', '.asf', '.m2ts', '.ogv', '.ogg', '.f4v', '.mxf'
    ]
    return any(file.lower().endswith(ext) for ext in video_extensions)



def compare_file_extensions(file1, file2) -> bool:
    '''检查两个文件的扩展名是否相同'''
    ext1 = os.path.splitext(file1)[1]
    ext2 = os.path.splitext(file2)[1]    
    return ext1 == ext2

def compare_file_size(file1, file2) -> bool:
    '''检查两个文件的大小是否相等'''
    size1 = os.path.getsize(file1)
    size2 = os.path.getsize(file2)
    return size1 == size2


def move_file(file, destination_folder) -> str:
    '''将文件移动到指定文件夹'''
    file_name = os.path.basename(file)
    destination_file = os.path.join(destination_folder, file_name)
    try:
        shutil.move(file, destination_file)
        print(f"Successfully moved {file} to {destination_folder}")
    except shutil.Error:
        # 处理目标位置已存在同名文件的情况
        print("移动操作被取消，目标位置已存在同名文件")
    return destination_file

def exchange_files(file1, file2, transfer_folder):
    '''采用移动的方式交换两个文件的位置'''
    # 创建一个临时的中转文件夹
    temp_dir1 = tempfile.mkdtemp(dir=transfer_folder)
    temp_dir2 = tempfile.mkdtemp(dir=transfer_folder)

    # 获取file1和file2的文件名
    file1_name = os.path.basename(file1)
    file2_name = os.path.basename(file2)

    # 获取file1和file2的目录路径
    file1_dir = os.path.dirname(file1)
    file2_dir = os.path.dirname(file2)

    # 构造中转文件的路径
    transfer_file1 = os.path.join(temp_dir1, file1_name)
    transfer_file2 = os.path.join(temp_dir2, file2_name)

    # 将文件1移动到中转文件夹1
    shutil.move(file1, transfer_file1)
    # 将文件2移动到中转文件夹2
    shutil.move(file2, transfer_file2)

    while True:
        try:
            # 将文件1移动到文件夹2
            shutil.move(transfer_file1, file2_dir)
        except shutil.Error:
            # 处理目标位置已存在同名文件的情况
            print("移动操作被取消，目标位置已存在同名文件")
            # 各回各家
            shutil.move(transfer_file1, file1_dir)
            shutil.move(transfer_file2, file2_dir)
            break

        try:
            # 将文件2移动到文件夹1
            shutil.move(transfer_file2, file1_dir)
        except shutil.Error:
            # 处理目标位置已存在同名文件的情况
            print("移动操作被取消，目标位置已存在同名文件")
            # 追去file2原本的文件夹把file1找回来
            callback_file1 = os.path.join(file2_dir,file1_name)
            shutil.move(callback_file1, file1_dir)
            # 再把file2放回去
            shutil.move(transfer_file2, file2_dir)
            break

        print(f'exchange {file1_name} <-> {file2_name}')
        break
    # 删除临时的中转文件夹
    os.rmdir(temp_dir1)
    os.rmdir(temp_dir2)


def better_filename(file_a, file_b) -> bool:
    '''基于汉字字符包含优先、汉字字符数量更多优先、文件名更短优先和创建时间更早优先的文件名选优'''
    file_a_name = os.path.basename(file_a)
    file_b_name = os.path.basename(file_b)

    better = False

    if has_chinese_characters(file_a_name) or has_chinese_characters(file_b_name):
        if has_chinese_characters(file_a_name) and has_chinese_characters(file_b_name):
            if compare_chinese_characters(file_a_name, file_b_name):
                better = True
            elif len(file_a_name) < len(file_b_name):
                better = True
        elif has_chinese_characters(file_a_name):
            better = True
    else:
        file_a_ctime = os.path.getctime(file_a)
        file_b_ctime = os.path.getctime(file_b)
        if file_a_ctime < file_b_ctime:
            better = True

    return better

def has_chinese_characters(string) -> bool:
    '''检查字符串是否包含汉字字符'''
    for char in string:
        if '\u4e00' <= char <= '\u9fff':
            return True
    return False

def compare_chinese_characters(str1, str2) -> bool:
    '''检查哪一个字符串包含的汉字字符数量更多'''
    chinese_pattern = re.compile(r'[\u4e00-\u9fff]')  # 匹配汉字字符的正则表达式
    count1 = len(re.findall(chinese_pattern, str1))  # 获取str1中汉字字符的数量
    count2 = len(re.findall(chinese_pattern, str2))  # 获取str2中汉字字符的数量

    return count1 > count2


if __name__ == '__main__':
    
    pass

    # 示例用法
    # folder_a = r"E:\中转站\images"
    # folder_b = r"E:\中转站\fullMI"
    # transfer_folder = r"E:\中转站\transfer_folder"

    # exchange_better_name(folder_a, folder_b, transfer_folder)



    # FOLDER_A = r"E:\中转站\images"
    # FOLDER_B = r"E:\中转站\fullMI"
    # DESTINATION_FOLDER = r"E:\中转站\destination_folder"
    # complement_images(FOLDER_A, FOLDER_B, DESTINATION_FOLDER)


    # FOLDER = r"E:\中转站\fullMI"
    # RECYCLE_FOLDER = r"E:\中转站\recycle_folder"

    # remove_duplicate_images(FOLDER, RECYCLE_FOLDER)
