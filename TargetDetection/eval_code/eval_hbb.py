import os
import numpy as np
import cv2
import json
import argparse

np.set_printoptions(suppress=True)
np.set_printoptions(precision=3)


def load_json(json_name, cats):
    # print(json_name)
    f = open(json_name, 'r')
    data = json.load(f)
    f.close()
    cons = []
    shapes = data['shapes']
    for i in range(0, len(shapes)):
        cat_name = shapes[i]['label']
        label = cats.index(cat_name) + 1
        points = np.array(shapes[i]['points'], dtype=np.int16)
        xmin, ymin = np.min(points[:, 0]), np.min(points[:, 1])
        xmax, ymax = np.max(points[:, 0]), np.max(points[:, 1])
        w, h = xmax - xmin, ymax - ymin
        cons.append([xmin, ymin, w, h, 1, label])
    arrs = np.array(cons)
    if arrs.ndim == 1:
        return np.array([cons])
    else:
        return np.array(cons)


def load_txt(txt_name, thresh=0.7):
    with open(txt_name, 'r') as f:
        contents = f.readlines()
    cons = []
    for i in range(0, len(contents)):
        content = contents[i].replace('\n', '').split(',')
        con = []
        for j in range(0, 6):
            con.append(float(content[j]))
        if con[4] >= thresh:
            cons.append(con)
    arrs = np.array(cons)
    if arrs.ndim == 1:
        return np.array([cons])
    else:
        return np.array(cons)


def cal_iou(rec1, rec2):  # 计算两个正矩形的面积
    x1, y1, w1, h1 = rec1[0], rec1[1], rec1[2], rec1[3]
    x2, y2, w2, h2 = rec2[0], rec2[1], rec2[2], rec2[3]
    inter_w = (w1 + w2) - (max(x1 + w1, x2 + w2) - min(x1, x2))
    inter_h = (h1 + h2) - (max(y1 + h1, y2 + h2) - min(y1, y2))
    if inter_h <= 0 or inter_w <= 0:  # 代表相交区域面积为0
        return 0
    # 往下进行应该inter 和 union都是正值
    inter = inter_w * inter_h
    union = w1 * h1 + w2 * h2 - inter
    return inter / union


def select_data(gt_data, pre_data):  # 根据gt_data的类别选出pre_data组成一个字典
    sel_datas = {}
    # print(gt_data)
    for i in range(0, gt_data.shape[0]):
        gt_label = gt_data[i, 5]
        if gt_label in sel_datas.keys():
            continue
        idxs = pre_data[:, 5] == gt_label
        sel_datas[gt_label] = pre_data[idxs]
    return sel_datas


def voc_ap(rec, prec, use_07_metric=False):
    """Compute VOC AP given precision and recall. If use_07_metric is true, uses
    the VOC 07 11-point method (default:False).
    """
    # 参考https://zhuanlan.zhihu.com/p/70667071
    if use_07_metric:  # 使用07年方法
        # 11 个点
        ap = 0.
        for t in np.arange(0., 1.1, 0.1):
            if np.sum(rec >= t) == 0:
                p = 0
            else:
                p = np.max(prec[rec >= t])  # 插值
            ap = ap + p / 11.
    else:  # 新方式，计算所有点
        # correct AP calculation
        # first append sentinel values at the end
        mrec = np.concatenate(([0.], rec, [1.]))  # rec从小到大排序
        mpre = np.concatenate(([0.], prec, [0.]))  # compute the precision 曲线值（也用了插值）
        for i in range(mpre.size - 1, 0, -1):
            mpre[i - 1] = np.maximum(mpre[i - 1], mpre[i])  # to calculate area under PR curve, look for points
        # where X axis (recall) changes value
        i = np.where(mrec[1:] != mrec[:-1])[0]  # and sum (\Delta recall) * prec
        ap = np.sum((mrec[i + 1] - mrec[i]) * mpre[i + 1])
    return ap


def parse_args():
    parser = argparse.ArgumentParser(description='Eval Detect Results')
    parser.add_argument('--gt_root', help='标注所在路径，格式为json')
    parser.add_argument('--pre_root', help='检测结果所在路径，格式为txt')
    parser.add_argument('--label_name', default='1,2', help='类别名（需要按类别顺序),以英文逗号作为间隔区分')
    args = parser.parse_args()
    return args


def eval_hbb(gt_root, pre_root, cats):
    iou_thresh = 0.5
    #####################
    cats = cats.split(',')
    label_count = len(cats)
    files = os.listdir(gt_root)
    scores_threshs = []
    scores_results = {}
    for i in range(0, 19):
        score = round(0.05 + i * 0.05, 2)
        scores_threshs.append(score)
        scores_results[str(score)] = []
    print(scores_threshs)
    # 先遍历一遍所有的GT和检测结果，获取各个类别的GT数目和检测数目
    GT_label = np.zeros((len(scores_threshs), label_count), dtype=np.int32)
    PRE_label = np.zeros((len(scores_threshs), label_count), dtype=np.int32)
    for i in range(0, len(scores_threshs)):
        for file in files:
            # 加载GT结果
            gt_name = os.path.join(gt_root, file)
            gt_data = load_json(gt_name, cats)
            for j in range(0, gt_data.shape[0]):
                gt_label = int(gt_data[j, 5])
                GT_label[i, gt_label - 1] += 1
            # 加载pre结果
            pre_name = os.path.join(pre_root, file.split('.json')[0] + '.txt')
            pre_size = os.path.getsize(pre_name)
            if pre_size == 0:
                continue
            pre_data = load_txt(pre_name, thresh=scores_threshs[i])
            if pre_data.shape[0] == 0 or pre_data.shape[1] == 0:
                continue
            for j in range(0, pre_data.shape[0]):
                pre_label = int(pre_data[j, 5])
                PRE_label[i, pre_label - 1] += 1
    # print(GT_label.shape)
    # 初始化每个类别在每个置信度下检测正确的数目
    TP_label = np.zeros((len(scores_threshs), label_count), dtype=np.int32)
    # 求p、r
    for num in range(0, len(scores_threshs)):
        scores_thresh = scores_threshs[num]
        TP, FP, FN = 0, 0, 0
        for i in range(0, len(files)):
            gt_json = os.path.join(gt_root, files[i])
            pre_txt = os.path.join(pre_root, files[i].split('.json')[0] + '.txt')
            gt_size = os.path.getsize(gt_json)
            pre_size = os.path.getsize(pre_txt)
            if gt_size == 0 and pre_size == 0:  # pre和gt都没有目标，直接进入下一张
                continue
            elif gt_size > 0 and pre_size == 0:  # 有目标但没有检测出来
                # print('gt_data:', gt_data)
                gt_data = load_json(gt_json, cats)
                FN += gt_data.shape[0]
                continue
            elif gt_size == 0 and pre_size > 0:  # 没有目标检测出虚警
                pre_data = load_txt(pre_txt, thresh=scores_thresh)
                FP += pre_data.shape[0]
                continue
            elif gt_size > 0 and pre_size > 0:
                gt_data = load_json(gt_json, cats)
                pre_data = load_txt(pre_txt, thresh=scores_thresh)
                ori_pre_data_num = pre_data.shape[0]  # 统计一开始的数目，因为后面对对pre_data进行删除操作
                if pre_data.shape[0] == 0 or pre_data.shape[1] == 0:
                    FN += gt_data.shape[0]
                    continue
                count_TP = 0  # 计算正确检测出来的目标的数目
                select_pre_datas = select_data(gt_data, pre_data)
                for j in range(0, gt_data.shape[0]):
                    gt_rec = gt_data[j][0:4]
                    gt_label = gt_data[j][5]
                    sel_pre_data = select_pre_datas[gt_label]
                    ious = []
                    for k in range(0, sel_pre_data.shape[0]):
                        pre_rec = sel_pre_data[k][0:4]
                        pre_label = sel_pre_data[k][5]
                        iou = cal_iou(gt_rec, pre_rec)
                        ious.append(iou)
                    # print('ious:',ious)
                    # ff.write(str(ious) + '\n')
                    if ious == []:
                        break
                    iou_max = max(ious)
                    idx = ious.index(iou_max)
                    # print(iou_max,idx)
                    if iou_max > iou_thresh:
                        count_TP += 1  # 统计出一张图中正确检测出来的目标数
                        TP_label[num, int(gt_label) - 1] += 1
                        # pre_data=np.delete(pre_data,idx,axis=0) #防止一个pre和多个gt之间的iou大于阈值
                        select_pre_datas[gt_label] = np.delete(select_pre_datas[gt_label], idx, axis=0)
                        # print('delete:',pre_data.shape)

                count_FP = ori_pre_data_num - count_TP
                count_FN = gt_data.shape[0] - count_TP
                TP += count_TP
                # print(TP)
                FP += count_FP
                FN += count_FN
        if TP == 0:
            P = 0
            R = 0
            F1 = 0
        else:
            P = TP / (TP + FP)
            R = TP / (TP + FN)
            F1 = 2 * P * R / (P + R)
        # print('iou_' + str(iou_thresh) + '_conf_' + str(scores_thresh)+','+'P:' + str(P) + ',' + 'R:' + str(R) + ',' + 'F1:' + str(F1))

    # 根据获得的GT_count、pre_count和TP_label求所有的评测结果
    FP_label = PRE_label - TP_label
    FN_label = GT_label - TP_label
    P_label = TP_label / PRE_label
    R_label = TP_label / GT_label
    FA_label = 1 - P_label
    # 获得每个类别的P值和R值算每个类别的AP
    AP_label = np.zeros((label_count,))
    for i in range(0, label_count):
        R_this = R_label[:, i][::-1]  # 将R值从小到大排列
        P_this = P_label[:, i][::-1]
        AP_label[i] = voc_ap(R_this, P_this)

    # 将获得的信息整理成19个二维数组,每个二维数组的尺寸为(label_count,8)
    all_infos = []
    f = open('info.txt', 'w+')
    for i in range(0, len(scores_threshs)):
        eval_metric = np.zeros((label_count, 8))
        print('********score=', scores_threshs[i], '**************')
        f.write('********score=' + str(scores_threshs[i]) + '**************\n')
        for j in range(0, label_count):
            eval_metric[j, 0] = GT_label[i, j]
            eval_metric[j, 1] = PRE_label[i, j]
            eval_metric[j, 2] = TP_label[i, j]
            eval_metric[j, 3] = FP_label[i, j]
            eval_metric[j, 4] = FN_label[i, j]
            eval_metric[j, 5] = P_label[i, j]
            eval_metric[j, 6] = R_label[i, j]
            eval_metric[j, 7] = FA_label[i, j]
            print(eval_metric[j])
            f.write(str(eval_metric[j])+'\n')
        all_infos.append(eval_metric)
    print('每一类的AP如下：')
    print(AP_label)
    mAP = np.mean(AP_label)
    print('mAP=', mAP)
    f.write('每一类的AP如下：\n' + str(AP_label) + '\nmAP=' + str(mAP) + '\n')
    return all_infos, AP_label, mAP


if __name__ == '__main__':
    args = parse_args()
    gt_root = args.gt_root
    pre_root = args.pre_root
    label_name = args.label_name
    all_infos, AP_label, mAP = eval_hbb(gt_root, pre_root, label_name)
    print(all_infos)
    print(AP_label)
    print(mAP)
