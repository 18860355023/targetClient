import os
import shutil


def purification(fi, old_cate, new_cate, path):
    '''
    提纯 重命名
    :param fi: 文件
    :param old_cate: 选中类别
    :param new_cate: 设置类别
    :param path: 路径
    :return:
    '''
    with open(os.path.join(path, fi), 'r') as f:
        labels = [i for i in f.read().split('\n') if i != '']
        new_labels = []
        for s in labels[:]:
            c_list = s.split(' ')
            if c_list[0] != old_cate:
                labels.remove(s)
            else:
                if new_cate:
                    c_list[0] = new_cate
                    new_labels.append(' '.join(c_list))
                else:
                    new_labels.append(s)
        return new_labels


def copy_img_file(file_list, old_path, new_path):
    '''
    复制文件到另一个文件夹
    :param file_list: 需要复制的文件名列表
    :param old_path: 上述文件的初始路径
    :param new_path: 复制的文件的目标路径
    :return:
    '''
    files = os.listdir(new_path)
    for file in file_list:
        src = os.path.join(old_path, file)
        dst = os.path.join(new_path, file)
        try:
            if file not in files:
                shutil.copyfile(src, dst)
        except Exception as e:
            print(e)


def copy_label_file(file_list, oc, nc, label_path, sp):
    ex_files = os.listdir(sp)
    # es = []
    for file in file_list:
        cfi = purification(file, oc, nc, label_path)  # 提纯
        if file in ex_files:
            # print('已存在文件::',file)
            # es.append(file)
            with open(os.path.join(sp, file), 'a') as f2:
                for i in cfi:
                    f2.write(i + '\n')
        else:
            with open(os.path.join(sp, file), 'w') as f1:
                for i in cfi:
                    f1.write(i + '\n')
    # print(len(es))
