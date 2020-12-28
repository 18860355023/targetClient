import os


def find_img(path):
    files = os.listdir(path)
    img_list = []
    for file in files:
        if not os.path.exists(file):
            suffix = file.split('.')[-1].lower()
            if suffix == 'png' or suffix == 'jpg' or suffix == 'jpeg' or suffix == 'gif' or suffix == 'bmp':
                img_list.append(file)
    return img_list
