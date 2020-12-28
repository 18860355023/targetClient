import pymysql
import datetime
from flask_sqlalchemy import SQLAlchemy
from flask import Flask
import hashlib, os, json

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "mysql+pymysql://root:123456@localhost:3306/objectDetection?charset=utf8mb4"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = True

db = SQLAlchemy(app, use_native_unicode='utf8mb4')


# ##################################################################bibei#############################################
class User(db.Model):
    # 用户表
    __tablename__ = "user"
    __table_args__ = {'extend_existing': True}
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)  # 编号
    name = db.Column(db.String(20), nullable=False)  # 用户名
    pwd = db.Column(db.String(100), nullable=False)  # 密码
    level = db.Column(db.Integer, nullable=False, default=1)
    register_time = db.Column(db.DateTime, default=datetime.datetime.now())  # 注册时间

    def __repr__(self):
        return "<User %r>" % self.name


class Category(db.Model):
    # 数据集类别（可能用不上）
    __tablename__ = "category"
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)  # 编号
    category_name = db.Column(db.String(100), nullable=False)  # 类别名称

    def __repr__(self):
        return "<Category %r>" % self.category_name


class Field(db.Model):
    # 原始数据集所属领域
    __tablename__ = "field"
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)  # 编号
    field_name = db.Column(db.String(100), nullable=False)  # 类别名称

    def __repr__(self):
        return "<Field %r>" % self.field_name


class ConfigFile(db.Model):
    # 网络结构文件表
    __tablename__ = "config_file"
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    config_file_name = db.Column(db.String(100), nullable=False)  # 网络结构文件名
    config_file_text = db.Column(db.LargeBinary(65536))  # 网络结构文件内容

    def __repr__(self):
        return "<ConfigFile %r>" % self.config_file_name


class InitDataSet(db.Model):
    # 原始数据集
    __tablename__ = "init_data_set"
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)  # 编号
    set_name = db.Column(db.String(200), nullable=False)  # 数据集名字
    set_path = db.Column(db.String(600), nullable=False)  # 数据集路径
    set_cate = db.Column(db.String(800), nullable=True)  # 数据集类别
    field_id = db.Column(db.Integer, nullable=False)  # 数据集所属领域
    # end_s = db.Column(db.String(50))  # 标注格式
    status = db.Column(db.String(100), nullable=False)  # 是否存在标注文件(Y/N)

    def __repr__(self):
        return "<InitDataSet %r>" % self.set_name


class InitTargetFile(db.Model):
    __tablename__ = "init_target_file"
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)  # 编号
    target_file_name = db.Column(db.String(200), nullable=False)  # 标注文件名字
    target_file_text = db.Column(db.LargeBinary(65536))  # 文件二进制内容
    target_file_cate = db.Column(db.String(200), nullable=True)  # 标注文件类别
    dat_set = db.Column(db.String(200), nullable=False)  # 数据集名字

    def __repr__(self):
        return "<InitTargetFile %r>" % self.target_file_name


class SourceLog(db.Model):
    # 数据集文件选中过程日志表
    __tablename__ = "source_log"
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)  # 编号
    dat_name = db.Column(db.String(200), nullable=False)  # 数据集名称
    old_cate = db.Column(db.String(200))  # 选中类别
    new_cate = db.Column(db.String(200))  # 设置类别
    num = db.Column(db.String(200), nullable=False)  # 数量

    def __repr__(self):
        return "<SourceLog %r>" % self.dat_name


class SourceFile(db.Model):
    # 数据集文件选中过程日志表
    __tablename__ = "source_file"
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)  # 编号
    con = db.Column(db.LargeBinary(65536))  # 内容
    name = db.Column(db.String(200))  # 名字
    set_name = db.Column(db.String(200))  # 数据集名字

    def __repr__(self):
        return "<SourceFile %r>" % self.name


class InitTargetTask(db.Model):
    # 根据人数分出来的文件夹
    __tablename__ = "init_target_task"
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)  # 编号
    # task_name = db.Column(db.String(100), nullable=False)  # 任务文件名
    task_path = db.Column(db.String(100), nullable=False)  # 任务路径
    addtime = db.Column(db.DateTime, default=datetime.datetime.now)  # 添加时间
    task_status = db.Column(db.String(100), nullable=False, default='unfinished')  # 任务状态
    # file_num = db.Column(db.Integer, nullable=False)  # 文件数量
    target_user = db.Column(db.String(800), nullable=False)
    cates = db.Column(db.String(800), nullable=False)
    target_user_status = db.Column(db.String(20), nullable=False, default='N')
    check_user = db.Column(db.String(100))
    is_repeat = db.Column(db.String(100))
    # initial_path_id = db.Column(db.Integer, nullable=False)

    def __repr__(self):
        return "<InitTargetTask %r>" % self.task_path


class DstDataSet(db.Model):
    # 目标数据集
    __tablename__ = "dst_data_set"
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    set_name = db.Column(db.String(200), nullable=False)  # 数据集名字
    set_path = db.Column(db.String(200), nullable=False)  # 数据集路径
    # set_cate = db.Column(db.String(200), nullable=False)  # 数据集存在类别

    def __repr__(self):
        return "<DstDataSet %r>" % self.set_name


class DstDataImg(db.Model):
    # 目标数据集
    __tablename__ = "dst_data_img"
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(200), nullable=False)  # 图片名
    text = db.Column(db.LargeBinary(65536))  # 文件二进制内容
    dat_set = db.Column(db.String(200), nullable=False)  # 目标数据集名字

    def __repr__(self):
        return "<DstDataImg %r>" % self.name


class DstDataFile(db.Model):
    # 目标数据集
    __tablename__ = "dst_data_file"
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(200), nullable=False)  # 标注文件名
    cate = db.Column(db.String(200), nullable=False)  # 类别名
    text = db.Column(db.LargeBinary(65536))  # 文件二进制内容
    dat_set = db.Column(db.String(200), nullable=False)  # 目标数据集名字

    def __repr__(self):
        return "<DstDataFile %r>" % self.name


class DstTrain(db.Model):
    # 目标数据集训练集
    __tablename__ = "dst_train"
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    train_name = db.Column(db.String(200), nullable=False)  # 训练集名字
    dst_set_id = db.Column(db.Integer, nullable=False)

    def __repr__(self):
        return "<DstTrain %r>" % self.train_name


class DstTest(db.Model):
    # 目标数据集训练集
    __tablename__ = "dst_test"
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    test_name = db.Column(db.String(200), nullable=False)  # 训练集名字
    dst_set_id = db.Column(db.Integer, nullable=False)

    def __repr__(self):
        return "<DstTest %r>" % self.test_name


class TestImg(db.Model):
    # 目标数据集训练集
    __tablename__ = "test_img"
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    test_img_name = db.Column(db.String(200), nullable=False)  # 训练集原图名字
    test_id = db.Column(db.Integer, nullable=False)

    def __repr__(self):
        return "<DstTest %r>" % self.test_name


class TargetFile(db.Model):
    # 标注文件存储表
    __tablename__ = "target_file"
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    t_file_name = db.Column(db.String(100), nullable=False)
    # t_file_path = db.Column(db.Binary(length=1024), nullable=False)
    t_file_text = db.Column(db.LargeBinary, nullable=False)
    # initial_id = db.Column(db.Integer, nullable=False)
    target_user = db.Column(db.String(100), nullable=False)
    task_id = db.Column(db.Integer, nullable=False)

    # uid = db.Column(db.Integer, db.ForeignKey(User.id))

    def __repr__(self):
        return "<TargetFile %r>" % self.file_name


class DstFile(db.Model):
    # 最终确认文件存储表
    __tablename__ = "dst_file"
    __table_args__ = {'extend_existing': True}
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    d_name = db.Column(db.String(100), nullable=False)
    # t_file_path = db.Column(db.Binary(length=1024), nullable=False)
    d_text = db.Column(db.LargeBinary, nullable=False)
    initial_id = db.Column(db.Integer, nullable=False)
    check_user = db.Column(db.Integer, nullable=False)
    target_cate = db.Column(db.String(500), nullable=False)

    # uid = db.Column(db.Integer, db.ForeignKey(User.id))

    def __repr__(self):
        return "<DstFile %r>" % self.file_nam


class SaveCate(db.Model):
    # 最终确认文件存储表
    __tablename__ = "save_cate"
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    category = db.Column(db.String(100), nullable=False)
    # t_file_path = db.Column(db.Binary(length=1024), nullable=False)
    target_user = db.Column(db.String(100), nullable=False)
    dst_file_name = db.Column(db.String(200), nullable=False)

    # uid = db.Column(db.Integer, db.ForeignKey(User.id))

    def __repr__(self):
        return "<SaveCate %r>" % self.dst_file_name


if __name__ == "__main__":
    db.drop_all()
    db.create_all()
    # m = hashlib.md5((str(123456) + 'kk').encode())
    # db.session.add(User(name='kk', pwd=m.hexdigest(), level=1))
    # path1 = 'C:\\Users\\Whu\\Desktop\\SSDT\\img'
    # path2 = 'C:\\Users\\Whu\\Desktop\\SSDT\\trg'
    # path3 = 'C:\\Users\\Whu\\Desktop\\SSDR\\images'
    # path4 = 'C:\\Users\\Whu\\Desktop\\SSDR\\target'
    # path5 = 'C:\\Users\\Whu\\Desktop\\labelfile\\img'
    # path6 = 'C:\\Users\\Whu\\Desktop\\labelfile\\jsonfile'

    # img1 = os.listdir(path1)
    # img2 = os.listdir(path3)
    # img3 = os.listdir(path5)
    # trg1 = os.listdir(path2)
    # trg2 = os.listdir(path4)
    # trg3 = os.listdir(path6)

    # db.session.add(InitDataSet(set_name='数据集A', set_field=1, t_status='true'))
    # db.session.add(InitDataSet(set_name='数据集B', set_field=1, t_status='true'))
    # db.session.add(InitDataSet(set_name='数据集C', set_field=1, t_status='true'))

    m3 = hashlib.md5((str(123456) + 'zhangsan').encode())
    db.session.add(User(name='zhangsan', pwd=m3.hexdigest(), level=1))

    m4 = hashlib.md5((str(123456) + 'lisi').encode())
    db.session.add(User(name='lisi', pwd=m4.hexdigest(), level=1))

    db.session.add(User(name='target1', pwd=hashlib.md5((str(123456) + 'target1').encode()).hexdigest(), level=1))
    db.session.add(User(name='target2', pwd=hashlib.md5((str(123456) + 'target2').encode()).hexdigest(), level=1))
    db.session.add(User(name='target3', pwd=hashlib.md5((str(123456) + 'target3').encode()).hexdigest(), level=1))
    db.session.add(User(name='target4', pwd=hashlib.md5((str(123456) + 'target4').encode()).hexdigest(), level=1))
    db.session.add(User(name='target5', pwd=hashlib.md5((str(123456) + 'target5').encode()).hexdigest(), level=1))

    db.session.add(User(name='namea', pwd=hashlib.md5((str(123456) + 'namea').encode()).hexdigest(), level=2))
    db.session.add(User(name='nameb', pwd=hashlib.md5((str(123456) + 'nameb').encode()).hexdigest(), level=2))
    db.session.add(User(name='namec', pwd=hashlib.md5((str(123456) + 'namec').encode()).hexdigest(), level=2))
    db.session.add(User(name='named', pwd=hashlib.md5((str(123456) + 'named').encode()).hexdigest(), level=2))
    db.session.add(User(name='client', pwd=hashlib.md5((str(123456) + 'client').encode()).hexdigest(), level=4))

    m2 = hashlib.md5((str(123456) + 'root').encode())
    db.session.add(User(name='root', pwd=m2.hexdigest(), level=3))

    m5 = hashlib.md5((str(123456) + 'administrator').encode())
    db.session.add(User(name='administrator', pwd=m5.hexdigest(), level=3))

    db.session.add(Field(field_name='光学遥感数据'))
    db.session.add(Field(field_name='SAR遥感数据'))
    db.session.add(Field(field_name='光学无人机数据'))
    # db.session.add(Field(field_name='未知数据'))

    db.session.add(Category(category_name='car'))
    db.session.add(Category(category_name='line'))
    db.session.add(Category(category_name='people'))
    db.session.add(Category(category_name='tool'))
    db.session.add(Category(category_name='bus'))
    db.session.add(Category(category_name='bike'))
    db.session.add(Category(category_name='boat'))
    db.session.add(Category(category_name='plane'))
    db.session.add(Category(category_name='bird'))
    db.session.add(Category(category_name='tree'))
    db.session.add(Category(category_name='river'))
    db.session.add(Category(category_name='bridge'))
    db.session.commit()
