(1)eval_hbb.py调用方式如下：
a.ubuntu调用
python eval_hbb.py --gt_root /home/spl/lsl/gt_root --pre_root /home/spl/lsl/pre_root --label_name 1,2

b.windows调用
python eval_hbb.py --gt_root E:\\beijing20201216\\changguang\\gt_root --pre_root E:\\beijing20201216\\changguang\\pre_root --label_name 1,2

(2)输入参数说明：
gt_root：标注所在路径，格式为json
pre_root：检测结果所在路径，格式为txt
label_name:类别名（需要按类别顺序),以英文逗号作为间隔区分。比如有两类的名字分别叫1和2，则参数输入为 1,2

(3)输出参数：
all_infos：它是一个长度为19的列表（19代表在19个置信度下），列表中的每个元素是一个尺寸为（类别数×8）的二维numpy数组，代表每个类别的8个结果，依次为GT数目、检测数目、正确检测数目、错误检测数目、漏检测数目、准确率、召回率、虚警率
AP_label：每个类别的AP值，它与置信度无关，有多少个类别就有多少个
mAP：AP_label的平均值，它就是一个在0到1之间的数