import json
import cv2
import base64
import os


def writeToJson(filePath, data):
    fb = open(filePath, 'w')
    # json.dumps(data).decode('unicode-escape')
    fb.write(json.dumps(data, indent=2, ensure_ascii=False))  # ,encoding='utf-8'
    fb.close()


# 转base64
def image_to_base64(image_np):
    image = cv2.imencode('.jpg', image_np)[1]
    image_code = str(base64.b64encode(image))[2:-1]
    return image_code


def readJson(jsonfile):
    with open(jsonfile, 'r') as f:
        jsonData = json.load(f)
    return jsonData


def rec2ploy(jsonPath, savePath):
    contentJson = readJson(jsonPath)
    ContenList = []
    sy = 0
    gk = 0
    lk = 0
    jsonList2 = {}
    # polygon
    for key, value in contentJson.items():
        if key == 'shapes':
            for i in range(len(value)):
                if value[i]['label'] == 'sy':
                    sy = sy + 1
                    jsonList = {}
                    for key2, value2 in value[i].items():
                        if key2 == 'label':
                            jsonList[key2] = 'sy%d' % sy
                        elif key2 == 'shape_type':
                            jsonList[key2] = "polygon"
                        elif key2 == 'points':
                            lt = value2[0]
                            rt = [value2[1][0], value2[0][1]]
                            rb = value2[1]
                            lb = [value2[0][0], value2[1][1]]
                            value2 = [lt, rt, rb, lb]
                            jsonList[key2] = value2
                            # print(value2)
                        else:
                            jsonList[key2] = value2
                    ContenList.append(jsonList)
                elif value[i]['label'] == 'gk':
                    gk = gk + 1
                    jsonList = {}
                    for key2, value2 in value[i].items():
                        if key2 == 'label':
                            jsonList[key2] = 'gk%d' % sy
                        elif key2 == 'shape_type':
                            jsonList[key2] = "polygon"
                        elif key2 == 'points':
                            lt = value2[0]
                            rt = [value2[1][0], value2[0][1]]
                            rb = value2[1]
                            lb = [value2[0][0], value2[1][1]]
                            value2 = [lt, rt, rb, lb]
                            jsonList[key2] = value2
                            # print(value2)
                        else:
                            jsonList[key2] = value2
                    ContenList.append(jsonList)
                elif value[i]['label'] == 'lk':
                    lk = lk + 1
                    jsonList = {}
                    for key2, value2 in value[i].items():
                        if key2 == 'label':
                            jsonList[key2] = 'lk%d' % sy
                        elif key2 == 'shape_type':
                            jsonList[key2] = "polygon"
                        elif key2 == 'points':
                            lt = value2[0]
                            rt = [value2[1][0], value2[0][1]]
                            rb = value2[1]
                            lb = [value2[0][0], value2[1][1]]
                            value2 = [lt, rt, rb, lb]
                            jsonList[key2] = value2
                            # print(value2)
                        else:
                            jsonList[key2] = value2
                    ContenList.append(jsonList)
            jsonList2[key] = ContenList
        else:
            jsonList2[key] = value
    writeToJson(savePath, jsonList2)


if __name__ == '__main__':
    json_rectanglePath = 'json_rectangle/'  # rectangle标注方式的json文件
    json_polyPath = "json_poly/"  # 转换后生成的polygon标注方式的json文件

    for json_filename in os.listdir(json_rectanglePath):
        print(json_filename)
        json_path = os.path.join(json_rectanglePath, json_filename)
        save_json_path = os.path.join(json_polyPath, json_filename.replace(".json", ".json"))
        print(json_path, save_json_path)
        rec2ploy(json_path, save_json_path)
