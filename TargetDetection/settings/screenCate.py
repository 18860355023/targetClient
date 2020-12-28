import os
import json


def screen_json_cate(data, path, oc):
    ll = []
    for i in data:
        f = open(os.path.join(path, i), 'r')
        con = json.loads(f.read())['shapes']
        kk = [j['label'] for j in con]
        if oc in kk:
            ll.append(i)
    return ll


def screen_txt_cate(data, path, oc):
    ll = []
    for i in data:
        with open(os.path.join(path, i), 'r') as f:
            labels = f.read().split('\n')
            li = [i.split(' ')[0] for i in labels if i != '']
            if oc in li:
                ll.append(i)
    return ll
