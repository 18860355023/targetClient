import json
import cv2
import base64
import os
import numpy as np


def write_to_txt(file_path, data):
    with open(file_path, 'w+') as ftxt:
        for shape in data:
            xy = np.array(shape['points'])
            label = str(shape['label'])
            strxy = ''
            for m, n in xy:
                strxy += str(m) + ' ' + str(n) + ' '
            strxy += label
            ftxt.writelines(strxy + "\n")
    # fb = open(filePath, 'w')
    # # json.dumps(data).decode('unicode-escape')
    # fb.write(json.dumps(data, indent=2, ensure_ascii=False))  # ,encoding='utf-8'
    # fb.close()


# 转base64
def image_to_base64(image_np):
    image = cv2.imencode('.jpg', image_np)[1]
    image_code = str(base64.b64encode(image))[2:-1]
    return image_code


def read_json(jsonfile):
    with open(jsonfile, 'r') as f:
        json_data = json.loads(f.read())
    return json_data


def rec2ploy_to_txt(json_dir_path, save_path):
    con = read_json(json_dir_path)
    # ContenList = []
    # jsonList2 = {}
    jsonList2 = []
    # polygon
    for i in con['shapes']:
        jsonList = {}
        for key2, value2 in i.items():
            if key2 == 'label':
                jsonList[key2] = value2
            elif key2 == 'shape_type':
                jsonList[key2] = "polygon"
            elif key2 == 'points':
                lt = value2[0]
                rt = [value2[1][0], value2[0][1]]
                rb = value2[1]
                lb = [value2[0][0], value2[1][1]]
                value2 = [lt, rt, rb, lb]
                jsonList[key2] = value2
        print(jsonList)
        jsonList2.append(jsonList)
    write_to_txt(save_path, jsonList2)


def json_rec_to_txt(json_rectangle_path, txt_path):
    for json_filename in os.listdir(json_rectangle_path):
        # print(json_filename)
        json_path = os.path.join(json_rectangle_path, json_filename)
        # save_json_path = os.path.join(json_polyPath, json_filename.replace(".json", ".json"))
        save_txt_path = os.path.join(txt_path, json_filename.replace(".json", ".txt"))
        # print(json_path, save_json_path)
        # rec2ploy(json_path, save_json_path)
        rec2ploy_to_txt(json_path, save_txt_path)

# if __name__ == '__main__':
#     # json_rectanglePath = 'json_rectangle/'  # rectangle标注方式的json文件
#     json_rectanglePath = r'F:\ServerSpace\InitDataSet\SSDD\json'  # rectangle标注方式的json文件
#
#     # json_polyPath = "json_poly/"  # 转换后生成的polygon标注方式的json文件
#     txt_path = r'F:\ServerSpace\InitDataSet\SSDD\labels'  # 转换成txt标注的txt文件
#     # if not os.path.exists(txt_path): os.makedirs(txt_path)
#
#     for json_filename in os.listdir(json_rectanglePath):
#         print(json_filename)
#         json_path = os.path.join(json_rectanglePath, json_filename)
#         # save_json_path = os.path.join(json_polyPath, json_filename.replace(".json", ".json"))
#         save_txt_path = os.path.join(txt_path, json_filename.replace(".json", ".txt"))
#         # print(json_path, save_json_path)
#         # rec2ploy(json_path, save_json_path)
#         rec2ploy_to_txt(json_path, save_txt_path)
