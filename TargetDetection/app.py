from flask import Flask, render_template, request, jsonify, session, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from model.model import User, InitTargetTask, DstFile, TargetFile, Category, SaveCate, InitDataSet, \
    InitTargetFile, Field, ConfigFile, SourceLog, DstDataFile, DstDataImg, DstDataSet, SourceFile
# from flask_login import LoginManager, login_required, UserMixin
import os
import json, shutil, uuid, datetime, time, random, math
from datetime import date
from eval_code.eval_hbb import eval_hbb
from settings.getCate import get_txt_cate, get_json_cate
from settings.screenCate import screen_txt_cate
from settings.distributionTask import create_task_dir_no, create_task_dir_yes
from settings.copy_img_label_file import copy_img_file, copy_label_file
from settings.targetFinish import merge_json_n, merge_json_y
from ExecutableScript.json8ToTxt import json_poly_to_txt
from ExecutableScript.json4To8ToTxt import json_rec_to_txt
import sys
import hashlib
import tkinter as tk
from tkinter import filedialog

import threading

app = Flask(__name__)

app.config["SQLALCHEMY_DATABASE_URI"] = "mysql+pymysql://root:123456@localhost:3306/objectDetection?charset=utf8mb4"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = True

db = SQLAlchemy(app, use_native_unicode='utf8mb4')

app.config['PERMANENT_SESSION_LIFETIME'] = 100000

app.config['SECRET_KEY'] = 'update'
# app.config['SERVER_BASE_PATH'] = 'F:\\ServerSpace'

now_dir = os.path.split(os.path.realpath(__file__))[0]  # 当前文件所在目录

# 原始数据集服务器地址（部署时需修改此处地址）
init_base_path = r'F:\ServerSpace\InitDataSet'
# 目标数据集服务器地址（部署时需修改此处地址）
dst_base_path = r'F:\ServerSpace\DstDataSet'
if not os.path.exists(dst_base_path): os.makedirs(dst_base_path)
copy_path = r'F:\ServerSpace\SourceCopyImg'
if not os.path.exists(copy_path): os.makedirs(copy_path)


################################################################################################################
@app.route('/open_tk')
def open_tk():
    os.system("explorer.exe")
    # try:
    #     root = tk.Tk()
    #     root.attributes('-topmost', True)
    #     root.withdraw()
    #     dir_path = filedialog.askdirectory()
    #     root.destroy()
    #     root.mainloop()
    #     return jsonify(dir_path)
    # except Exception as e:
    #     print(e)
    #     return 'error'


@app.route('/client_test')
def client_test():
    if 'username' in session and session['level'] == 4:
        username = session['username']
        dst_dat_sets = db.session.query(DstDataSet).all()
        dst_sets_list = []
        for dst in dst_dat_sets:
            dst_sets_dic = {}
            print(dst.set_name)
            op = os.path.join(dst.set_path, 'labels')
            txt_files = os.listdir(op)
            cn_dic = get_txt_cate(txt_files, op)
            print(cn_dic)
            dst_sets_dic['name'] = dst.set_name
            dst_sets_dic['path'] = dst.set_path
            dst_sets_dic['cate_num'] = cn_dic
            dst_sets_dic['num'] = len(txt_files)
            dst_sets_list.append(dst_sets_dic)
        return render_template('client/splitTest.html', data=locals())
    else:
        return redirect(url_for('login'))


@app.route('/client_task')
def client_task():
    if 'username' in session and session['level'] == 4:
        username = session['username']
        target_users = db.session.query(User.name).filter(User.level == 1).all()
        check_users = db.session.query(User.name).filter(User.level == 2).all()
        cates = db.session.query(Category).all()
        n_paths = db.session.query(InitDataSet).filter(InitDataSet.status == 'N').all()
        tasks = db.session.query(InitTargetTask).all()
        return render_template('client/task_distribution.html', data=locals())
    else:
        return redirect(url_for('login'))


@app.route('/client_user_info')
def client_user_info():
    if 'username' in session and session['level'] == 4:
        username = session['username']
        users = db.session.query(User).filter(User.level != 4).all()
        return render_template('client/userInfo.html', data=locals())
    else:
        return redirect(url_for('login'))


@app.route('/client_evaluating')
def client_evaluating():
    if 'username' in session and session['level'] == 4:
        username = session['username']
        return render_template('client/evaluating.html', data=locals())
    else:
        return redirect(url_for('login'))


@app.route('/client_server')
def client_server():
    if 'username' in session and session['level'] == 4:
        username = session['username']
        # print(os.walk(init_base_path))
        dir_list = [dirs for root, dirs, files in os.walk(init_base_path)]
        lis = os.listdir(init_base_path)
        ddd_list = []
        for i in lis:
            ddd = {}
            dd = {}
            lis2 = os.listdir(os.path.join(init_base_path, i))
            for j in lis2:
                lis3 = os.listdir(os.path.join(init_base_path, i, j))
                dd[j] = len(lis3)
            ddd['name'] = i
            ddd['dir_num'] = dd
            ddd['path'] = os.path.join(init_base_path, i)
            ddd_list.append(ddd)
        print(ddd_list)

        return render_template('client/localServer.html', data=locals())
    else:
        return redirect(url_for('login'))


@app.route('/client_des')
def client_des():
    if 'username' in session and session['level'] == 4:
        username = session['username']
        return render_template('client/evaluating.html', data=locals())
    else:
        return redirect(url_for('login'))


@app.route('/')
@app.route('/client_index')
def client_index():
    if 'username' in session and session['level'] == 4:
        username = session['username']
        fields = db.session.query(Field).all()
        # fs = db.session.query(SourceFile).all()
        logs = db.session.query(SourceLog).all()
        # return render_template('client/index.html', data=locals())
        return render_template('client/clientIndex.html', data=locals())
    else:
        return redirect(url_for('login'))


@app.route('/client_import_data')
def client_import_data():
    if 'username' in session and session['level'] == 4:
        username = session['username']
        base_path = init_base_path
        fields = db.session.query(Field).all()
        cate_tables = db.session.query(InitDataSet).all()
        ss_list = []
        for c in cate_tables:
            path = os.path.join(c.set_path, 'images')
            files = os.listdir(path)
            ss_list.append(
                {'name': c.set_name, 'path': c.set_path, 'cate': c.set_cate, 'num': len(files), 'status': c.status})

        return render_template('client/dataImport.html', data=locals())
    else:
        return redirect(url_for('login'))


@app.route('/add_field', methods=['GET', 'POST'])
def add_field():
    if request.method == 'POST':
        result = {'status': 200, 'msg': {}}
        field = request.form.get('field')
        data = db.session.query(Field).filter(Field.field_name == field).first()
        if data:
            result['status'] = 300
        else:
            db.session.add(Field(field_name=field))
            db.session.commit()
            new_data = db.session.query(Field).filter(Field.field_name == field).first()
            result['msg'] = {'field_id': new_data.id, 'field_name': new_data.field_name}
        return jsonify(result)


@app.route('/jt', methods=['GET', 'POST'])
def jt():
    if request.method == 'POST':
        path = request.form.get('path')
        json_path = os.path.join(path, 'json')
        labels_path = os.path.join(path, 'labels')
        if not os.path.exists(labels_path): os.makedirs(labels_path)
        if os.path.exists(json_path):
            files = os.listdir(json_path)
            if files:
                jst = threading.Thread(target=json_poly_to_txt, args=(json_path, labels_path,))
                jst.start()
                jst.join()
                ini_set = db.session.query(InitDataSet).filter(InitDataSet.set_path == path).first()
                if ini_set:
                    cate_num = get_txt_cate(files, labels_path)
                    ini_set.set_cate = json.dumps(cate_num)
                    ini_set.status = 'Y'
                    db.session.commit()
                return jsonify(200)
            else:
                return jsonify(404)
        else:
            return jsonify(404)


@app.route('/path_check', methods=['GET', 'POST'])
def path_check():
    if request.method == 'POST':
        path = request.form.get('path')
        print(path)
        if os.path.exists(path):
            data = db.session.query(InitDataSet).filter(InitDataSet.set_path == path).first()
            if data:
                return jsonify(300)
            else:
                return jsonify(200)
        else:
            return jsonify(404)


@app.route('/name_check', methods=['GET', 'POST'])
def name_check():
    if request.method == 'POST':
        name = request.form.get('name')
        data = db.session.query(InitDataSet).filter(InitDataSet.set_name == name).first()
        if data:
            return jsonify(300)
        else:
            return jsonify(200)


@app.route('/add_init_data_set', methods=['GET', 'POST'])
def add_init_data_set():
    if request.method == 'POST':
        path = request.form.get('path')
        name = request.form.get('name')
        field = request.form.get('field')
        try:
            new_path = os.path.join(path, 'labels')
            files = os.listdir(new_path)
            if len(files) > 0:
                ret = get_txt_cate(files, new_path)
                db.session.add(
                    InitDataSet(set_name=name, set_path=path, set_cate=json.dumps(ret), field_id=int(field),
                                status='Y'))
            else:
                db.session.add(
                    InitDataSet(set_name=name, set_path=path, set_cate='', field_id=int(field), status='N'))
            db.session.commit()
            return jsonify(200)
        except FileNotFoundError:
            print('====')
            db.session.add(
                InitDataSet(set_name=name, set_path=path, set_cate='', field_id=int(field), status='N'))
            db.session.commit()
            return jsonify(200)
        except Exception as e:
            print(e)
            return jsonify('接收错误')


############################################################################################################
@app.route('/get_ini_data_set', methods=['GET', 'POST'])
def get_ini_data_set():
    if request.method == 'POST':
        field = request.form.get('field')
        try:
            cate_tables = db.session.query(InitDataSet).filter(InitDataSet.field_id == int(field),
                                                               InitDataSet.status == 'Y').all()
            ss_list = []
            for c in cate_tables:
                kk_list = [{'name': c.set_name, 'cate': k, 'num': v} for k, v in json.loads(c.set_cate).items()]
                ss_list.append({'key': kk_list})
            return jsonify(ss_list)
        except Exception as e:
            return jsonify('error')


# @app.route('/get_dst_data_set', methods=['GET', 'POST'])
# def get_dst_data_set():
#     try:
#         cate_tables = db.session.query(DstDataSet).all()
#         ss_list = []
#         for c in cate_tables:
#             path = os.path.join(dst_base_path, c.set_name, 'labels')
#             files = os.listdir(path)
#             c_list = {}
#             for i in files:
#                 with open(os.path.join(path, i), 'r') as f:
#                     sh = json.loads(f.read())['shapes']
#                     lm = [k['label'] for k in sh]
#                     for k in set(lm):
#                         if k not in c_list.keys():
#                             c_list[k] = 1
#                         else:
#                             c_list[k] = c_list[k] + 1
#             # kk_list = [{'name': c.set_name, 'cate': k, 'num': v} for k, v in c_list.items()]
#             ss_list.append({'name': c.set_name, 'cate': json.dumps(c_list)})
#         print(ss_list)
#         return jsonify(ss_list)
#     except Exception as e:
#         return jsonify('error')


def find_images(a_img, s_img):
    img_list = []
    for img in a_img:
        for i in s_img:
            if i.split('.')[0] == img.split('.')[0]:
                img_list.append(img)
    print(img_list)
    print(len(img_list))
    return img_list


# def write_source_file(files, old_cate, new_cate, labels_path, set_name):
#     for file in files:
#         cfi = purification(file, old_cate, new_cate, labels_path)  # 提纯
#         # print(cfi)
#         # 制作过程表中已存在标注文件
#         ex_s = db.session.query(SourceFile).filter(SourceFile.set_name == set_name).first()
#         if ex_s:
#             ex = db.session.query(SourceFile).filter(SourceFile.set_name == set_name, SourceFile.name == file).first()
#             if ex:
#                 load_data = json.loads(ex.con.decode()) + cfi
#                 ex.con = json.dumps(load_data).encode()
#                 db.session.commit()
#             else:
#                 db.session.add(
#                     SourceFile(name=set_name + '_' + file, con=json.dumps(cfi).encode(), set_name=set_name))
#                 db.session.commit()
#         else:
#             db.session.add(SourceFile(name=file, con=json.dumps(cfi).encode(), set_name=set_name))
#             db.session.commit()


@app.route('/dst_data_config', methods=['GET', 'POST'])
def dst_data_config():
    if request.method == 'POST':
        # num = request.form.get('num')  # 数量
        n_cate = request.form.get('new_cate')  # 新类别
        o_cate = request.form.get('old_cate')  # 原类别
        n_name = request.form.get('name')  # 数据集名
        if o_cate and n_name:
            tf = db.session.query(InitDataSet).filter(InitDataSet.set_name == n_name).first()
            labels_path = os.path.join(tf.set_path, 'labels')  # 标注文件路径
            images_path = os.path.join(tf.set_path, 'images')  # 原图路径
            save_img_path = os.path.join(copy_path, n_name, 'images')  # 拷贝图片过程路径(用各数据集名当主目录,筛选同数据集同名图片)
            save_label_path = os.path.join(copy_path, n_name, 'labels')  # 拷贝标注文件过程路径(用各数据集名当主目录,筛选同数据集同名图片)
            if not os.path.exists(save_img_path): os.makedirs(save_img_path)  # 创建copy文件夹
            if not os.path.exists(save_label_path): os.makedirs(save_label_path)  # 创建copy文件夹

            label_files = os.listdir(labels_path)  # 所有标注文件
            image_files = os.listdir(images_path)  # 所有原始图片

            s_files = screen_txt_cate(label_files, labels_path, o_cate)  # 所有选中类别标注文件
            print(s_files)
            # print(len(select_cate_files))
            # 找出对应 s_files 标注文件的原始图片
            s_images = find_images(image_files, s_files)

            # copy_label_file(s_files, o_cate, n_cate, labels_path, save_label_path)
            # 复制图片
            t1 = threading.Thread(target=copy_img_file, args=(s_images, images_path, save_img_path,))
            t1.start()
            t1.join()
            t2 = threading.Thread(target=copy_label_file, args=(s_files, o_cate, n_cate, labels_path, save_label_path,))
            t2.start()
            t2.join()
            db.session.add(SourceLog(dat_name=n_name, old_cate=o_cate, new_cate=n_cate, num=len(s_files)))
            db.session.commit()
            return jsonify({'name': n_name, 'o_cate': o_cate, 'n_cate': n_cate, 'num': len(s_files)})
        else:
            return jsonify('error')


@app.route('/clear_sf')
def clear_sf():
    # db.session.query(SourceFile).delete()
    db.session.query(SourceLog).delete()
    # db.session.delete(SourceFile)
    db.session.commit()
    if os.path.exists(copy_path): shutil.rmtree(copy_path)
    os.makedirs(copy_path)
    return redirect(url_for('client_index'))


@app.route('/clear_dst')
def clear_dst():
    if os.path.exists(dst_base_path): shutil.rmtree(dst_base_path)
    time.sleep(1)
    os.makedirs(dst_base_path)
    return redirect(url_for('client_index'))


def remove_rename_img_file(set_paths, new_path, name):
    for s_path in set_paths:
        cp = os.path.join(copy_path, s_path, 'images')
        img_files = os.listdir(cp)
        ex_files = os.listdir(new_path)
        print(ex_files)
        # print(img_files)
        # print(len(img_files))
        for file in img_files:
            ini_path = os.path.join(cp, file)
            if file in ex_files:
                re_save_path = os.path.join(new_path, name + '_' + file)
                shutil.copyfile(ini_path, re_save_path)
            else:
                save_path = os.path.join(new_path, file)
                shutil.copyfile(ini_path, save_path)


def remove_rename_label_file(set_paths, new_path, name):
    for s_path in set_paths:
        cp = os.path.join(copy_path, s_path, 'labels')
        img_files = os.listdir(cp)
        ex_files = os.listdir(new_path)
        print(ex_files)
        # print(img_files)
        # print(len(img_files))
        for file in img_files:
            ini_path = os.path.join(cp, file)
            if file in ex_files:
                re_save_path = os.path.join(new_path, name + '_' + file)
                shutil.copyfile(ini_path, re_save_path)
            else:
                save_path = os.path.join(new_path, file)
                shutil.copyfile(ini_path, save_path)


def make_label_files(dss, path):
    for d in dss:
        # print(json.loads(d.con.decode()))
        shapes = json.loads(d.con.decode())
        with open(os.path.join(path, d.name), 'w+') as f:
            for i in shapes:
                f.write(i + '\n')


@app.route('/create_dst_set', methods=['GET', 'POST'])
def create_dst_set():
    if request.method == 'POST':
        name = request.form.get('name')
        # print(name)
        is_ex = db.session.query(DstDataSet).filter(DstDataSet.set_name == name).first()
        if is_ex:
            return jsonify(303)
        else:
            save_images_path = os.path.join(dst_base_path, name, 'images')  # 保存图片文件的路径
            save_labels_path = os.path.join(dst_base_path, name, 'labels')  # 保存标注文件的路径
            # print(save_images_path)
            if not os.path.exists(save_images_path): os.makedirs(save_images_path)
            if not os.path.exists(save_labels_path): os.makedirs(save_labels_path)
            sets = os.listdir(copy_path)  # 获取copy原始数据集的文件夹
            # print(sets)
            # remove_rename_img_file(sets, save_images_path, name)
            # 保存图片到目标数据集
            rt1 = threading.Thread(target=remove_rename_img_file, args=(sets, save_images_path, name,))
            rt1.start()
            rt1.join()
            # 保存标注文件到目标数据集
            rt1 = threading.Thread(target=remove_rename_label_file, args=(sets, save_labels_path, name,))
            rt1.start()
            rt1.join()
            db.session.add(DstDataSet(set_name=name, set_path=os.path.join(dst_base_path, name)))
            db.session.commit()
            return jsonify(200)


import numpy as np
from PIL import Image


def sp_file(files, op, ct, cv, name):
    train_list = []
    val_list = []
    # np.random.shuffle(images)  # 打乱文件列表
    for i in range(ct):
        train_list.append(files[i])

    for i in range(ct, ct + cv):
        val_list.append(files[i])
    index_path = os.path.join(dst_base_path, name, 'index')
    if not os.path.exists(index_path): os.makedirs(index_path)
    file = open(os.path.join(index_path, 'train.txt'), 'w')
    for i in range(0, len(train_list)):
        path = os.path.join(op, train_list[i])
        file.write(path + '\n')
    file.close()

    file = open(os.path.join(index_path, 'val.txt'), 'w')
    for i in range(len(val_list)):
        path = os.path.join(op, val_list[i])
        file.write(path + '\n')
    file.close()


@app.route('/split_data', methods=['GET', 'POST'])
def split_data():
    if request.method == 'POST':
        name = request.form.get('name')
        print(name)

        num = request.form.get('num')
        print(num)
        img_path = os.path.join(dst_base_path, name, 'images')
        images = os.listdir(img_path)
        np.random.shuffle(images)  # 打乱文件列表
        if '%' in num:
            ratio_train = int(num.split('%')[0]) / 100  # 百分比转换int类型或者float类型
            cnt_train = round(len(images) * ratio_train, 0)  # 训练集数量
            cnt_val = len(images) - cnt_train  # 测试集数量
            sp_file(images, img_path, cnt_train, cnt_val, name)
        else:
            cnt_train = int(num)  # 训练集数量
            cnt_val = len(images) - cnt_train  # 测试集数量
            sp_file(images, img_path, cnt_train, cnt_val, name)

        # cnt_train = round(len(images) * ratio_train, 0)  # 训练集数量
        # cnt_val = len(images) - cnt_train  # 测试集数量

        # train_list = []
        # val_list = []
        # # np.random.shuffle(images)  # 打乱文件列表
        # for i in range(int(cnt_train)):
        #     train_list.append(images[i])
        #
        # for i in range(int(cnt_train), int(cnt_train + cnt_val)):
        #     val_list.append(images[i])
        # index_path = os.path.join(dst_base_path, name, 'index')
        # if not os.path.exists(index_path): os.makedirs(index_path)
        # file = open(os.path.join(index_path, 'train.txt'), 'w')
        # for i in range(0, len(train_list)):
        #     path = os.path.join(img_path, train_list[i])
        #     file.write(path + '\n')
        # file.close()
        #
        # file = open(os.path.join(index_path, 'val.txt'), 'w')
        # for i in range(len(val_list)):
        #     path = os.path.join(img_path, val_list[i])
        #     file.write(path + '\n')
        # file.close()
        return jsonify('ok')


##################################################################################################################
@app.route('/add_cate', methods=['GET', 'POST'])
def add_cate():
    if request.method == 'POST':
        cate = request.form.get('cate')
        data = db.session.query(Category).filter(Category.category_name == cate).first()
        if data:
            return jsonify('该类别已存在')
        else:
            db.session.add(Category(category_name=cate))
            db.session.commit()
            return jsonify('ok')


# ########################任务分配模块########################################################################
@app.route('/create_task', methods=['GET', 'POST'])
def create_task():
    if request.method == 'POST':
        addr = request.form.get('addr')
        cus = request.form.get('ck')
        name_list = json.loads(request.form.get('nameList'))
        cate_list = request.form.get('cateList')
        count = json.loads(request.form.get('count'))
        print(count)
        image_path = os.path.join(addr, 'images')
        # print(image_path)
        dis_task_path = os.path.join(addr, 'tasks')
        if count:
            tus = create_task_dir_yes(image_path, name_list, dis_task_path)
            db.session.add(InitTargetTask(task_path=dis_task_path, target_user=','.join(tus), check_user=cus,
                                          cates=cate_list, is_repeat='Y'))
        else:
            create_task_dir_no(image_path, name_list, dis_task_path)
            db.session.add(InitTargetTask(task_path=dis_task_path, target_user=','.join(name_list), check_user=cus,
                                          cates=cate_list, is_repeat='N'))
        db.session.commit()
        return jsonify('ok')


@app.route('/delete_task', methods=['GET', 'POST'])
def delete_task():
    if request.method == 'POST':
        path = request.form.get('path')
        if os.path.exists(path):
            shutil.rmtree(path)
            f = db.session.query(InitTargetTask).filter(InitTargetTask.task_path == path).first()
            db.session.delete(f)
            db.session.commit()
            return jsonify(200)
        else:
            return jsonify(100)


# #######################################任务表格筛选##################################################################
@app.route('/filter_name', methods=['GET', 'POST'])
def filter_name():
    if request.method == 'POST':
        try:
            name = request.form.get('name')
            tasks = db.session.query(InitTargetTask).filter(InitTargetTask.check_user == name).all()
            task_list = [
                [task.addtime, task.task_path, task.target_user, task.check_user, task.task_status, task.is_repeat] for
                task in tasks]
            return jsonify(task_list)
        except Exception as e:
            print(e)
            return jsonify('error')


@app.route('/filter_time', methods=['GET', 'POST'])
def filter_time():
    if request.method == 'POST':
        try:
            sy, sm, sd = request.form.get('s_time').split('-')
            ey, em, ed = request.form.get('e_time').split('-')

            start = date(year=int(sy), month=int(sm), day=int(sd))
            end = date(year=int(ey), month=int(em), day=int(ed))
            tasks = db.session.query(InitTargetTask.addtime, InitTargetTask.task_path, InitTargetTask.target_user,
                                     InitTargetTask.check_user, InitTargetTask.task_status,
                                     InitTargetTask.is_repeat).filter(
                InitTargetTask.addtime >= start).filter(InitTargetTask.addtime <= end).all()

            return jsonify(tasks)
        except Exception:
            return jsonify('error')


# #######################################标注人员页面########################################################
@app.route('/common_index')
def common_index():
    # if request.method == 'GET':
    if 'username' in session and session['level'] == 1:
        username = session['username']
        # user = db.session.query(User).filter(User.name == username).first()
        tasks = db.session.query(InitTargetTask).all()
        print(tasks)
        user_task_list = [task for task in tasks if username in task.target_user]
        print(user_task_list)
        # task_list = []
        # for i in tasks:
        #     if i.is_repeat == 'N':
        #         if username in i.target_user:
        #             task_list.append(i)
        #     elif i.is_repeat=='Y':
        #         print(i)
        #     tu = i.target_user.split(',')
        #     td = {}
        #     for t in tu:
        #         if t.split('_')[0] == username:
        #             td['id'] = i.id
        #             td['addtime'] = i.addtime
        #             td['task_name'] = i.task_name
        #             td['task_path'] = i.task_path
        #             td['file_num'] = i.file_num
        #             td['task_name'] = i.task_name
        #             td['check_user'] = i.check_user
        #             td['target_status'] = t
        #     task_list.append(td)
        # return render_template('commonPage/index.html', data=locals())
        return render_template('target-check/targetIndex.html', data=locals())
    else:
        return redirect(url_for('login'))


# ###############################################检查人员页面#################################################
@app.route('/check_index')
def check_index():
    if 'username' in session and session['level'] == 2:
        username = session['username']
        uts = db.session.query(InitTargetTask).all()
        task_list = db.session.query(InitTargetTask).filter(InitTargetTask.check_user == username).order_by(
            InitTargetTask.id.desc()).all()
        print(task_list)
        return render_template('target-check/checkIndex.html', data=locals())
    else:
        return redirect(url_for('login'))


# ####################################登录/注册/修改密码/删除用户#####################################################
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        return_data = {'status': 200}
        user = request.form.get('user')
        pwd = request.form.get('pwd')
        level = request.form.get('level')
        u = db.session.query(User).filter(User.name == user).first()
        if u:
            return_data['status'] = 101
            return_data['msg'] = '账号已存在,请重新输入!'
            return jsonify(return_data)
        m = hashlib.md5((pwd + user).encode())
        db.session.add(User(name=user, pwd=m.hexdigest(), level=level))
        db.session.commit()
        return_data['msg'] = '注册成功!'
        return_data['res_time'] = datetime.datetime.now()
        return_data['res_name'] = user
        return_data['res_pwd'] = m.hexdigest()
        return_data['res_level'] = 1
        return jsonify(return_data)
    return render_template('register.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        user = request.form.get('user')
        pwd = request.form.get('pwd')
        mp = hashlib.md5((str(pwd) + str(user)).encode())
        u = db.session.query(User).filter(User.name == user).first()
        if u:
            if u.pwd == mp.hexdigest():
                session['username'] = user
                session['level'] = u.level
                if u.level == 1:
                    return jsonify('/common_index')
                elif u.level == 2:
                    return jsonify('/check_index')
                elif u.level == 3:
                    return jsonify('/index')
                else:
                    return jsonify('/client_index')
            else:
                return jsonify(102)
        else:
            return jsonify(101)
    return render_template('login/login.html')


@app.route('/logout', methods=['GET', 'POST'])
def logout():
    session.clear()
    return redirect(url_for('login'))


@app.route('/update_pwd', methods=['GET', 'POST'])
def update_pwd():
    if request.method == 'POST':
        nid = request.form.get('nid')
        pwd = request.form.get('new_pwd')
        u = db.session.query(User).filter(User.id == nid).first()
        m = hashlib.md5((pwd + u.name).encode())
        u.pwd = m.hexdigest()
        db.session.commit()
        return jsonify('修改成功!')


@app.route('/delete_user', methods=['GET', 'POST'])
def delete_user():
    if request.method == 'POST':
        try:
            nid = request.form.get('nid')
            db.session.query(User).filter(User.id == nid).delete()
            db.session.commit()
            return jsonify('删除成功!')
        except Exception as e:
            return jsonify('未知错误!')


# ################################# labelme打开方式 #####################################################
@app.route('/labelme')
def labelme():
    # print(os.system('net use \\172.17.252.74\labelme /user:administrator Whu123'))
    print('jdhfgd')
    os.system(r'notepad')
    return 'ok'


@app.route('/open_label', methods=['GET', 'POST'])
def open_label():
    if request.method == 'POST':
        path = request.form.get('path')
        # print(os.system('net use \\172.17.252.74\labelme /user:administrator Whu123'))
        os.system(r'labelme ' + path)
        # os.system(r'labelme C:\Users\Whu\Desktop\images')
        return 'ok'


##################################################################################################################
@app.route('/finished', methods=['GET', 'POST'])
def finished():
    if request.method == 'POST':
        user = session['username']
        ini_path = request.form.get('ini_path')
        # print(ini_path)
        dst_path = request.form.get('dst_path')
        # print(dst_path)
        img_path = request.form.get('img_path')
        repeat = request.form.get('repeat')
        ini_set_path = '\\'.join(dst_path.split('\\')[0:-1])
        re_path = os.path.join(ini_set_path, 'transit-json')
        ini_img_path = os.path.join(ini_set_path, 'images')
        if not os.path.exists(re_path): os.makedirs(re_path)

        json_files = os.listdir(ini_path)
        img_files = os.listdir(img_path)

        if len(json_files) != len(img_files):
            return jsonify(103)
        else:
            if repeat == 'Y':
                merge_json_y(json_files, ini_path, re_path, user, ini_img_path)
            else:
                merge_json_n(json_files, ini_path, re_path, user, ini_img_path)
            task = db.session.query(InitTargetTask).filter(InitTargetTask.task_path == dst_path).first()
            task.target_usr_status = 'Y'
            db.session.commit()
            return jsonify('ok')


def remove_file(file_list, old_path, new_path):
    '''
    复制文件到另一个文件夹
    :param file_list: 需要复制的文件名列表
    :param old_path: 上述文件的初始路径
    :param new_path: 复制的文件的目标路径
    :return:
    '''
    for file in file_list:
        src = os.path.join(old_path, file)
        dst = os.path.join(new_path, file)
        try:
            shutil.copyfile(src, dst)
        except Exception as e:
            print(e)


def dir_exists(path):
    '''
    判断文件夹是否存在，存在则删除后创建，不存在则直接创建
    :param path: 文件夹路径
    :return:
    '''
    if not os.path.exists(path):
        os.makedirs(path)
    else:
        shutil.rmtree(path, ignore_errors=True)
        os.makedirs(path)


# def create_task(path, name_list):
#     base_file_name = path.split('\\')[-1]  # 基础文件夹名字
#     files = os.listdir(path)
#     dir_num = int(len(files) / len(name_list))
#     n = len(files) % len(name_list)
#     num = 1
#     name_a, name_b = (0, 1)
#     task_list = []
#     for i in range(0, len(files), dir_num):
#         dn = dir_num + i
#         task_dic = {}
#         if dn <= len(files):
#             split_file_list = files[i:dn]
#             base_n = base_file_name + str(num)
#             if name_b < len(name_list):
#                 task_a = os.path.join(path, name_list[name_a] + '-' + base_n)
#                 task_b = os.path.join(path, name_list[name_b] + '-' + base_n)
#                 task_dic[tuple(split_file_list)] = [task_a, task_b]
#                 dir_exists(task_a)
#                 dir_exists(task_b)
#                 save_task(name_list[name_a], name_list[name_b], task_a, task_b, path, base_n)
#             else:
#                 task_a = os.path.join(path, name_list[name_a] + '-' + base_file_name + str(num))
#                 task_b = os.path.join(path, name_list[0] + '-' + base_file_name + str(num))
#                 task_dic[tuple(split_file_list)] = [task_a, task_b]
#                 dir_exists(task_a)
#                 dir_exists(task_b)
#                 save_task(name_list[name_a], name_list[0], task_a, task_b, path, base_n)
#             num += 1
#         else:
#             last_list = files[-n:]
#             task_a = os.path.join(path, name_list[len(name_list) - 1] + '-' + base_file_name + str(len(name_list)))
#             task_b = os.path.join(path, name_list[0] + '-' + base_file_name + str(len(name_list)))
#             task_dic[tuple(last_list)] = [task_a, task_b]
#         name_a += 1
#         name_b += 1
#         task_list.append(task_dic)
#     return task_list


# def copy_dir():
#     new_name = addr.split('\\')[-1]


def rm_label_user(files, path):
    for file in files:
        op = os.path.join(path, file)
        with open(op, 'r') as f1:
            con = json.loads(f1.read())
            # print('old-con:::', con)
            for label in con['shapes']:
                label['label'] = label['label'].split('_')[-1]

            # print('new-con:::', con)
        with open(op, 'w') as f2:
            f2.write(json.dumps(con))


@app.route('/submit_task', methods=['GET', 'POST'])
def submit_task():
    if request.method == 'POST':
        path = request.form.get('path')
        base_path = '\\'.join(path.split('\\')[0:-1])
        tran_json_path = os.path.join(base_path, 'transit-json')
        labels_path = os.path.join(base_path, 'labels')
        images_path = os.path.join(base_path, 'images')
        print(labels_path)
        if not os.path.exists(labels_path): os.makedirs(labels_path)

        files = os.listdir(tran_json_path)
        img_files = os.listdir(images_path)
        if len(files) == len(img_files):
            rm_th = threading.Thread(target=rm_label_user, args=(files, tran_json_path,))
            rm_th.start()
            rm_th.join()
            jt_th = threading.Thread(target=json_poly_to_txt, args=(tran_json_path, labels_path,))
            jt_th.start()
            jt_th.join()
            t_files = os.listdir(labels_path)
            # print(t_files)
            cate_num = get_txt_cate(t_files, labels_path)
            # print(cate_num)
            task = db.session.query(InitTargetTask).filter(InitTargetTask.task_path == path).first()
            task.task_status = 'finished'
            dat_set = db.session.query(InitDataSet).filter(InitDataSet.set_path == base_path).first()
            dat_set.set_cate = json.dumps(cate_num)
            dat_set.status = 'Y'
            db.session.commit()
            return jsonify(200)
        else:
            return jsonify(103)


# ###################################################客户端#################################################################
# @app.route('/client_import_data')
# def client_import_data():
#     if 'username' in session and session['level'] == 5:
#         username = session['username']
#
#         fields = db.session.query(Field).all()
#         data_logs = db.session.query(SourceLog).all()
#
#         cate_tables = db.session.query(InitDataSet).filter(InitDataSet.set_field == fields[0].id).all()
#         dst_data = db.session.query(DstDataSet).all()
#         kk_dic = {}
#         for dst in dst_data:
#             tts = db.session.query(DstDataFile).filter(DstDataFile.dat_set == dst.set_name).all()
#             if tts:
#                 nit_dic = {}
#                 for zz in tts:
#                     for k in zz.cate.split(','):
#                         if k not in nit_dic.keys():
#                             nit_dic[k] = 1
#                         else:
#                             nit_dic[k] = nit_dic[k] + 1
#                 kk_dic[dst.set_name] = nit_dic
#
#         d_dic = {}
#         for c in cate_tables:
#             if fields[0].id == c.set_field:
#                 t_files = db.session.query(InitTargetFile).filter(InitTargetFile.dat_set == c.set_name).all()
#                 c_list = {}
#                 for i in t_files:
#                     for k in i.target_file_cate.split(','):
#                         if k not in c_list.keys():
#                             c_list[k] = 1
#                         else:
#                             c_list[k] = c_list[k] + 1
#                 d_dic[c.set_name] = c_list
#
#         # return render_template('client/index.html', data=locals())
#         return render_template('client/数据集展示.html', data=locals())
#     else:
#         return redirect(url_for('login'))


def rc_dir(path):
    shutil.rmtree(path, ignore_errors=True)
    time.sleep(1)
    os.makedirs(path)


@app.route('/ini_img_upload', methods=['GET', 'POST'])
def ini_img_upload():
    if request.method == 'POST':
        try:
            file = request.files.get('file')
            ft = file.read()
            if os.path.exists(os.path.join(now_dir, 'import_img')):
                with open('./import_img/' + os.path.basename(file.filename), 'wb') as f:
                    f.write(ft)
            else:
                os.makedirs(os.path.join(now_dir, 'import_img'))
                with open('./import_img/' + os.path.basename(file.filename), 'wb') as f:
                    f.write(ft)
            return jsonify('ok')
        except Exception as e:
            print('上传原始失败 -- 错误信息:', e)
            return jsonify(100)


@app.route('/ini_file_upload', methods=['GET', 'POST'])
def ini_file_upload():
    if request.method == 'POST':
        try:
            file = request.files.get('file')
            ft = file.read()
            if os.path.exists(os.path.join(now_dir, 'import_target')):
                with open('./import_target/' + os.path.basename(file.filename), 'wb') as f:
                    f.write(ft)
            else:
                os.makedirs(os.path.join(now_dir, 'import_target'))
                with open('./import_target/' + os.path.basename(file.filename), 'wb') as f:
                    f.write(ft)
            # global nn
            # nn += 1
            return jsonify('success')
        except Exception as e:
            print('上传标注文件失败 -- 错误信息:', e)
            return jsonify(100)


def upload_ini_img(path, data_list, dat_name):
    for data in data_list:
        with open(os.path.join(path, data), 'rb') as f:
            text = f.read()
        db.session.add(InitImg(img_name=data, img_binary_text=text, dat_set=dat_name))
        db.session.commit()
    rc_dir(os.path.join(now_dir, 'import_img'))


def upload_ini_file(path, data_list, dat_name):
    for data in data_list:
        cate_list = []
        with open(os.path.join(path, data), 'r') as f:
            text = json.loads(f.read())
            for w in text['shapes']:
                cate_list.append(w['label'])
            db.session.add(InitTargetFile(target_file_name=data, target_file_text=json.dumps(text).encode(),
                                          target_file_cate=','.join(set(cate_list)), dat_set=dat_name))
        db.session.commit()

    rc_dir(os.path.join(now_dir, 'import_target'))


@app.route('/all_info', methods=['GET', 'POST'])
def all_info():
    if request.method == 'POST':
        su = request.form.get('su')
        field = request.form.get('field')
        name = request.form.get('name')
        img_path = os.path.join(now_dir, 'import_img')
        target_path = os.path.join(now_dir, 'import_target')
        img_files = os.listdir(img_path)
        target_files = os.listdir(target_path)
        is_exit = db.session.query(InitDataSet).filter(InitDataSet.set_name == name).first()
        if not is_exit:
            if su == 'true':
                if img_files and target_files:
                    t_img = threading.Thread(target=upload_ini_img, args=(img_path, img_files, name,))
                    t_file = threading.Thread(target=upload_ini_file, args=(target_path, target_files, name,))
                    t_file.start()
                    t_img.start()
                else:
                    rc_dir(img_path)
                    rc_dir(target_path)
                    return jsonify(500)
            else:
                if img_files:
                    t_img = threading.Thread(target=upload_ini_img, args=(img_path, img_files, name,))
                    t_img.start()
                else:
                    rc_dir(target_path)
                    return jsonify(500)
            db.session.add(InitDataSet(set_name=name, set_field=field, t_status=su))
            db.session.commit()
            return jsonify('ok')
        else:
            return jsonify(100)


@app.route('/config_upload', methods=['GET', 'POST'])
def config_upload():
    if request.method == 'POST':
        file = request.files.get('file')
        file_text = file.read()
        db.session.add(ConfigFile(config_file_name=file.filename, config_file_text=file_text))
        db.session.commit()
        return jsonify('ok')


def write_img(data_list, name):
    for data in data_list:
        db.session.add(DstDataImg(name=data.name, text=data.text, dat_set=name))
        db.session.commit()


def write_file(data_list, name):
    for data in data_list:
        cate_list = []
        dt = json.loads(data.text.decode())
        for w in dt['shapes']:
            cate_list.append(w['label'])

        db.session.add(DstDataFile(name=data.name, text=data.text, cate=','.join(set(cate_list)), dat_set=name))
        db.session.commit()


@app.route('/run_eval', methods=['GET', 'POST'])
def run_eval():
    if request.method == 'POST':
        gt = request.form.get('gt')
        pre = request.form.get('pre')
        ct = request.form.get('ct')
        eval_hbb(gt, pre, ct)

        return jsonify(200)


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
    # root.mainloop()
