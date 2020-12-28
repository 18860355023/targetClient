import os
import numpy as np
import cv2


def convert_labels(path=r'F:\ServerSpace\labelfile', cats={'car': '0', 'bus': '1', 'tree': '2'}):
    imgs = os.path.join(path, 'images')
    folder = os.path.join(path, 'txt')
    save = os.path.join(path, 'labels2')
    os.mkdir(save)
    files = os.listdir(folder)
    for i in files:
        f = open(os.path.join(folder, i), 'r')
        f_out = open(os.path.join(save, i), 'w')
        if os.path.exists(os.path.join(imgs, i[:-3] + 'tif')):
            hh, ww, _ = cv2.imread(os.path.join(imgs, i[:-3] + 'tif')).shape
        elif os.path.exists(os.path.join(imgs, i[:-3] + 'png')):
            hh, ww, _ = cv2.imread(os.path.join(imgs, i[:-3] + 'png')).shape
        elif os.path.exists(os.path.join(imgs, i[:-3] + 'jpg')):
            hh, ww, _ = cv2.imread(os.path.join(imgs, i[:-3] + 'jpg')).shape
        elif os.path.exists(os.path.join(imgs, i[:-3] + 'bmp')):
            hh, ww, _ = cv2.imread(os.path.join(imgs, i[:-3] + 'bmp')).shape
        else:
            print(i)
            exit()

        while True:
            line = f.readline().strip()
            if line:
                splits = line.split(' ')
                name = splits[8]
                poly = np.array(splits[:8]).astype(float).reshape(4, 2)
                xmin, ymin = np.min(poly, axis=0)
                xmax, ymax = np.max(poly, axis=0)
                if xmax < 0 or ymax < 0:
                    continue
                if xmin > ww or ymin > hh:
                    continue
                xmax = min(xmax, ww)
                ymax = min(ymax, hh)
                xmin = max(xmin, 0)
                ymin = max(ymin, 0)
                xc = xmax / 2 + xmin / 2
                yc = ymax / 2 + ymin / 2
                w = xmax - xmin
                h = ymax - ymin
                f_out.write(
                    cats[name] + ' ' + str(xc / ww) + ' ' + str(yc / hh) + ' ' + str(w / ww) + ' ' + str(h / hh) + '\n')
            else:
                break
        f.close()
        f_out.close()


convert_labels()
