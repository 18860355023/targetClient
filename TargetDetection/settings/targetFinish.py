import os
import shutil
import json


def file_text(opf, name):
    with open(opf, 'r') as fs:
        json_con = json.loads(fs.read())
        for shape in json_con['shapes']:
            shape['label'] = name + '_' + shape['label']
    return json_con


def merge_json_y(files, op, np, name, im_path):
    ex_files = os.listdir(np)
    for file in files:
        fp = os.path.join(op, file)
        sp = os.path.join(np, file)
        print(sp)
        json_con = file_text(fp, name)
        json_con['imagePath'] = os.path.join(im_path, json_con['imagePath'].split('\\')[-1])
        if file in ex_files:
            # print('新组合的::',json_con['shapes'])
            with open(sp, 'r') as fb:
                ini_json_con = json.loads(fb.read())
                # print('已存在的::',ini_json_con['shapes'])
                # ini_json_con['shapes'] = json_con['shapes'] + ini_json_con['shapes']
                json_con['shapes'] = json_con['shapes'] + ini_json_con['shapes']
                # print('合并的::',ini_json_con)
                print('合并的::',json_con)
            with open(sp, 'w') as fc:
                # fc.write(json.dumps(ini_json_con))
                fc.write(json.dumps(json_con))
        else:
            with open(sp, 'w') as fg:
                fg.write(json.dumps(json_con))

    # shutil.rmtree(op)


def merge_json_n(files, op, np, name, im_path):
    for file in files:
        fp = os.path.join(op, file)
        sp = os.path.join(np, file)
        json_con = file_text(fp, name)
        json_con['imagePath'] = os.path.join(im_path, json_con['imagePath'].split('\\')[-1])
        with open(sp, 'w') as ff:
            ff.write(json.dumps(json_con))

    shutil.rmtree(op)
