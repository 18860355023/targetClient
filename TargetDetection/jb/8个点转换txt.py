import os
import json
import numpy as np


def json2txt(path_json, path_txt):
    with open(path_json, 'r', encoding='gb18030') as path_json:
        jsonx = json.load(path_json)
        with open(path_txt, 'w+') as ftxt:
            for shape in jsonx['shapes']:
                xy = np.array(shape['points'])
                label = str(shape['label'])
                strxy = ''
                for m, n in xy:
                    strxy += str(m) + ' ' + str(n) + ' '
                strxy += label
                ftxt.writelines(strxy + "\n")


dir_json = r'F:\ServerSpace\labelfile\json'  # json路径
dir_txt = r'F:\ServerSpace\labelfile\txt'  # 存取的txt路径
if not os.path.exists(dir_txt):
    os.makedirs(dir_txt)
list_json = os.listdir(dir_json)
for cnt, json_name in enumerate(list_json):
    print('cnt=%d,name=%s' % (cnt, json_name))
    path_json = os.path.join(dir_json, json_name)
    path_txt = os.path.join(dir_txt, json_name.replace('.json', '.txt'))
    # path_txt = dir_txt + json_name.replace('.json', '.txt')
    # print(path_json, path_txt)
    json2txt(path_json, path_txt)
