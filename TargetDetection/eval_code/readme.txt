(1)eval_hbb.py���÷�ʽ���£�
a.ubuntu����
python eval_hbb.py --gt_root /home/spl/lsl/gt_root --pre_root /home/spl/lsl/pre_root --label_name 1,2

b.windows����
python eval_hbb.py --gt_root E:\\beijing20201216\\changguang\\gt_root --pre_root E:\\beijing20201216\\changguang\\pre_root --label_name 1,2

(2)�������˵����
gt_root����ע����·������ʽΪjson
pre_root�����������·������ʽΪtxt
label_name:���������Ҫ�����˳��),��Ӣ�Ķ�����Ϊ������֡���������������ֱַ��1��2�����������Ϊ 1,2

(3)���������
all_infos������һ������Ϊ19���б�19������19�����Ŷ��£����б��е�ÿ��Ԫ����һ���ߴ�Ϊ���������8���Ķ�άnumpy���飬����ÿ������8�����������ΪGT��Ŀ�������Ŀ����ȷ�����Ŀ����������Ŀ��©�����Ŀ��׼ȷ�ʡ��ٻ��ʡ��龯��
AP_label��ÿ������APֵ���������Ŷ��޹أ��ж��ٸ������ж��ٸ�
mAP��AP_label��ƽ��ֵ��������һ����0��1֮�����