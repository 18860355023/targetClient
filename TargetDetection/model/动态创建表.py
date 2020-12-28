# targets = db.session.query(User).filter(User.level == 1).all()
# checks = db.session.query(User).filter(User.level == 2).all()
# for tar in targets:
#     # __tablename__ = tar.name + '_target'
#     colums = []
#     colums.append(tar.name + '_target')
#     colums.append(db.Column('id', db.Integer, primary_key=True, autoincrement=True, comment="ID"))
#     colums.append(db.Column('f_name', db.String(255), nullable=False, comment=u"文件名"))
#     colums.append(db.Column('f_content', db.LargeBinary, nullable=False, comment=u"文件内容"))
#     colums.append(db.Column('task_id', db.Integer, comment=u"任务ID"))
#     db.Table(*colums, extend_existing=True)
#     db.create_all()
#
# for ch in checks:
#     # __tablename__ = ch.name + '_dst'
#     colums = []
#     colums.append(ch.name + '_dst')
#     colums.append(db.Column('id', db.Integer, primary_key=True, autoincrement=True, comment="ID"))
#     colums.append(db.Column('f_name', db.String(255), nullable=False, comment=u"文件名"))
#     colums.append(db.Column('f_content', db.LargeBinary, nullable=False, comment=u"文件内容"))
#     colums.append(db.Column('task_id', db.Integer, comment=u"任务ID"))
#     colums.append(db.Column('target_user', db.String(100), comment=u"标注人"))
#     db.Table(*colums, extend_existing=True)
#     db.create_all()
