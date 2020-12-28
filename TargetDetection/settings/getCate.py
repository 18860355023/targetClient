import os
import json


def get_json_cate(files, path):
    di = {}
    for file in files:
        with open(os.path.join(path, file), 'r') as f:
            con = json.loads(f.read())
            # print(con['shapes'])
            li = [i['label'] for i in con['shapes']]
            for j in set(li):
                if j not in di.keys():
                    di[j] = 1
                else:
                    di[j] = di[j] + 1
    return di


def get_txt_cate(files, path):
    di = {}
    for file in files:
        with open(os.path.join(path, file), 'r') as f:
            labels = f.read().split('\n')
            # print(labels)
            li = [i.split(' ')[0] for i in labels if i != '']
            for j in set(li):
                if j not in di.keys():
                    di[j] = 1
                else:
                    di[j] = di[j] + 1
    return di


def get_xml_cate(files, path):
    di = {}
    return di
