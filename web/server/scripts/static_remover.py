import os
from detection.utils import get_static_file_url


def run(*args, **kwargs):
    image_folder_path = get_static_file_url("images")
    image_files = os.listdir(image_folder_path)
    print(f"Removing {len(image_files)} images ...")
    for file in image_files:
        file_path = os.path.join(image_folder_path, file)
        os.remove(file_path)
    print("Finished clear the image folder.")

    video_folder_path = get_static_file_url("media")
    video_files = os.listdir(video_folder_path)
    print(f"Removing {len(video_files)} videos ...")
    for file in video_files:
        file_path = os.path.join(video_folder_path, file)
        os.remove(file_path)
    print("Finished clear the video folder.")
