import cv2
import numpy as np
import os


def calIOU(point1, point2):
    point1 = point1.reshape(4, 2).astype(int)
    point2 = point2.reshape(4, 2).astype(int)
    rec1 = cv2.minAreaRect(point1)
    rec2 = cv2.minAreaRect(point2)
    jiao = cv2.rotatedRectangleIntersection(rec1, rec2)
    w1, h1 = rec1[1]
    w2, h2 = rec2[1]
    mode = jiao[0]
    if mode == 0:
        return 0.0
    points = jiao[1]
    inter = cv2.contourArea(points)
    over = (w1 * h1) + (w2 * h2) - inter
    iou = inter / over
    return iou


def eval(gtfolder='../config/gt', prefolder='../config/predict', cats=['car', 'bigcar'], iouScore=0.5, Score=0.7):
    tongji = np.zeros((len(cats), 3))
    for i in os.listdir(gtfolder):
        gt_dict = {}
        for cat in cats:
            gt_dict[cat] = []
        f = open(os.path.join(gtfolder, i), 'r')
        while True:
            line = f.readline()
            if line:
                splitlines = line.strip().split(' ')
                if len(splitlines) < 9:
                    continue
                gt_dict[splitlines[8]].append(np.array(splitlines[:8]).astype(float))
                tongji[cats.index(splitlines[8])][0] += 1
            else:
                break
        f.close()
        if not os.path.exists(os.path.join(prefolder, i)):
            print(i, '  no predict')

        pre_dict = {}
        for cat in cats:
            pre_dict[cat] = []
        f = open(os.path.join(prefolder, i), 'r')
        while True:
            line = f.readline()
            if line:
                splitlines = line.strip().split(' ')
                if len(splitlines) < 10 or float(splitlines[8]) < Score:
                    continue
                pre_dict[splitlines[9]].append(np.array(splitlines[:9]).astype(float))
                tongji[cats.index(splitlines[9])][1] += 1
            else:
                break
        f.close()
        for cat in cats:
            pre_dict[cat].sort(key=lambda t: -t[8])
            for j in pre_dict[cat]:
                if len(gt_dict[cat]) > 0:
                    overlaps = [calIOU(j[:8], points) for points in gt_dict[cat]]
                    ovmax = np.max(overlaps)
                    jmax = np.argmax(overlaps)
                    if ovmax > iouScore:
                        gt_dict[cat].pop(jmax)
                        tongji[cats.index(cat)][2] += 1
    for cat in cats:
        print('---', cat, '---')
        print('gt_num: ', tongji[cats.index(cat)][0])
        print('pre_num: ', tongji[cats.index(cat)][1])
        print('true_num: ', tongji[cats.index(cat)][2])
    res = np.sum(tongji, axis=0)
    print('---total---')
    print('gt_num: ', res[0])
    print('pre_num: ', res[1])
    print('true_num: ', res[2])
    print('p: ', res[2] / res[1])
    print('r: ', res[2] / res[0])


eval()
