import os
import json
import numpy as np


def write_txt(path_json, path_txt):
    with open(path_json, 'r', encoding='gb18030') as path_json:
        jsonx = json.load(path_json)
        with open(path_txt, 'w+') as ftxt:
            for shape in jsonx['shapes']:
                xy = np.array(shape['points'])
                label = str(shape['label'])
                strxy = ''
                for m, n in xy:
                    # strxy += str(m) + ' ' + str(n) + ' '
                    strxy += ' ' + str(m) + ' ' + str(n)
                # strxy += label
                label += strxy
                # ftxt.writelines(strxy + "\n")
                ftxt.writelines(label + "\n")


def json_poly_to_txt(json_path, txt_path):
    if not os.path.exists(txt_path):
        os.makedirs(txt_path)
    list_json = os.listdir(json_path)
    for cnt, json_name in enumerate(list_json):
        # print('cnt=%d,name=%s' % (cnt, json_name))
        json_file = os.path.join(json_path, json_name)
        txt_file = os.path.join(txt_path, json_name.replace('.json', '.txt'))
        # path_txt = dir_txt + json_name.replace('.json', '.txt')
        # print(path_json, path_txt)
        write_txt(json_file, txt_file)

# dir_json = r'F:\ServerSpace\InitDataSet\AIRSAR\json'  # json路径
# dir_txt = r'F:\ServerSpace\InitDataSet\AIRSAR\labels'  # 存取的txt路径
# if not os.path.exists(dir_txt):
#     os.makedirs(dir_txt)
# list_json = os.listdir(dir_json)
# for cnt, json_name in enumerate(list_json):
#     print('cnt=%d,name=%s' % (cnt, json_name))
#     path_json = os.path.join(dir_json, json_name)
#     path_txt = os.path.join(dir_txt, json_name.replace('.json', '.txt'))
#     # path_txt = dir_txt + json_name.replace('.json', '.txt')
#     # print(path_json, path_txt)
#     write_txt(path_json, path_txt)
