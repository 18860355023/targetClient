import os
import shutil
import numpy as np


def copy_img_task(img_list, old_path, new_path):
    for file in img_list:
        src = os.path.join(old_path, file)
        dst = os.path.join(new_path, file)
        try:
            shutil.copyfile(src, dst)
        except Exception as e:
            print(e)


def create_task_dir_no(im_path, ns, task_path):
    ims = os.listdir(im_path)  # 获取原始图片列表
    # print(len(ns))
    np.random.shuffle(ims)  # 打乱文件列表
    # print(ims)
    file_num = int(len(ims) / len(ns))
    # print(file_num)
    end_num = len(ims) % len(ns)
    s = 0
    for i in range(0, len(ims), file_num):
        if s > len(ns) - 1:
            ee_path = os.path.join(task_path, ns[s - 1], 'images')
            copy_img_task(ims[-end_num:], im_path, ee_path)
        else:
            nn_path = os.path.join(task_path, ns[s], 'images')
            if not os.path.exists(nn_path): os.makedirs(nn_path)
            copy_img_task(ims[i:i + file_num], im_path, nn_path)
        s += 1


def create_task_dir_yes(im_path, ns, task_path):
    ims = os.listdir(im_path)  # 获取原始图片列表
    # print(len(ns))
    np.random.shuffle(ims)  # 打乱文件列表
    # print(ims)
    file_num = int(len(ims) / len(ns))
    # print(file_num)
    end_num = len(ims) % len(ns)
    s = 0
    t_user = []
    for i in range(0, len(ims), file_num):
        if s > len(ns) - 1:
            ee_path = os.path.join(task_path, ns[s - 1] + '_' + ns[0], 'images')
            copy_img_task(ims[-end_num:], im_path, ee_path)
        else:
            if s == len(ns) - 1:
                nn_path = os.path.join(task_path, ns[s] + '_' + ns[0], 'images')
                t_user.append(ns[s] + '_' + ns[0])
            else:
                nn_path = os.path.join(task_path, ns[s] + '_' + ns[s + 1], 'images')
                t_user.append(ns[s] + '_' + ns[s + 1])
            if not os.path.exists(nn_path): os.makedirs(nn_path)
            copy_img_task(ims[i:i + file_num], im_path, nn_path)
        s += 1
    return t_user
