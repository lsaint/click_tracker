# -*- coding: utf-8 -*-

import argparse, time
from datetime import datetime, date

import sqlalchemy
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, scoped_session



def getargs():
    parse = argparse.ArgumentParser(epilog = "coMMon task confiG fiLe Parser -- L\'")
    parse.add_argument('-m', metavar = "mysql_login_info", required = True,
                        help = "user_name:password@host/database")
    group = parse.add_mutually_exclusive_group(required=True)
    group.add_argument('-p', metavar = 'task_pkg.txt', help="taskpkg file")
    group.add_argument('-t', metavar = 'task.txt', help="task file")
    group.add_argument('-a', metavar = 'action.txt', help="action file")
    args = parse.parse_args()
    return vars(args)
ARGS = getargs()


engine = create_engine("mysql://%s" % ARGS["m"], convert_unicode=True)
S = scoped_session(sessionmaker(autocommit=False, autoflush=False, bind=engine))
Base = declarative_base(engine)


def clean():
    Base.metadata.reflect(engine)
    for name, table in Base.metadata.tables.items():
        if name.endswith("_new"):
            print "drop table", name
            table.drop()


def clone():
    engine.execute("CREATE TABLE `taskpkg_new` LIKE `taskpkg`")
    engine.execute("CREATE TABLE `task_new` LIKE `task`")
    engine.execute("CREATE TABLE `action_new` LIKE `action`")


clean()
clone()


def t(s):
    return datetime.strptime(s, "%Y/%m/%d")

def today():
    return date.today()

def u(s):
    return s.decode("gbk")


def checkRange(x, a, b):
    return x in range(a, b+1)



#+------------------------+----------------------+------+-----+---------------------+
#| Field                  | Type                 | Null | Key | Default             |
#+------------------------+----------------------+------+-----+---------------------+
#| task_pkg_id            | int(10) unsigned     | NO   | PRI | NULL                |
#| name                   | varchar(256)         | NO   |     | NULL                |
#| activation_conditions  | int(10) unsigned     | NO   |     | NULL                |
#| repeat_type            | tinyint(3) unsigned  | NO   |     | NULL                |
#| repeat_cycle           | int(10) unsigned     | NO   |     | 0                   |
#| effect_begin_timestamp | timestamp            | NO   |     | CURRENT_TIMESTAMP   |
#| effect_end_timestamp   | timestamp            | NO   |     | 0000-00-00 00:00:00 |
#| task_pkg_index         | smallint(5) unsigned | NO   |     | NULL                |
#| ctime                  | timestamp            | NO   |     | 0000-00-00 00:00:00 |
#| mtime                  | timestamp            | NO   |     | 0000-00-00 00:00:00 |
#| expand                 | mediumtext           | YES  |     | NULL                |
#+------------------------+----------------------+------+-----+---------------------+
class Pkg(Base):
    __tablename__ = 'taskpkg_new'
    __table_args__ = {'autoload':True}


# 任务包ID    标题    激活条件    有效开始时间    有效结束时间    周期间隔    排序索引
def pkg_section_process(lt):
    p = Pkg()
    p.task_pkg_id = int(lt[0])
    p.name = u(lt[1])
    p.activation_conditions = int(lt[2])
    p.effect_begin_timestamp = lt[3] or today()
    p.effect_end_timestamp = t(lt[4])
    p.repeat_cycle = int(lt[5])
    p.task_pkg_index = int(lt[6])

    p.repeat_type = 0
    p.ctime = today()
    p.mtime = today()

    if p.effect_begin_timestamp > p.effect_end_timestamp:
        print "[ERROR]effect_begin_timestamp must early than effect_end_timestamp"
        exit(1)
    if not checkRange(p.activation_conditions, 1, 2):
        print "[ERROR]activation_conditions must in 1-2" 
        exit(1)


    print "pkg {0} parsed".format(p.task_pkg_id)
    return p


#+-------------------------+----------------------+------+-----+---------------------+
#| Field                   | Type                 | Null | Key | Default             |
#+-------------------------+----------------------+------+-----+---------------------+
#| task_id                 | int(10) unsigned     | NO   | PRI | NULL                |
#| task_pkg_id             | int(10) unsigned     | NO   |     | NULL                |
#| name                    | varchar(256)         | NO   |     | NULL                |
#| task_description        | varchar(1024)        | NO   |     | NULL                |
#| prompt                  | varchar(256)         | NO   |     | NULL                |
#| award_type              | smallint(5) unsigned | NO   |     | NULL                |
#| award_amount            | int(10) unsigned     | NO   |     | NULL                |
#| award_detail            | varchar(256)         | NO   |     | NULL                |
#| activation_conditions   | smallint(5) unsigned | NO   |     | NULL                |
#| activation_prev_task_id | int(10) unsigned     | NO   |     | NULL                |
#| effect_begin_timestamp  | timestamp            | NO   |     | CURRENT_TIMESTAMP   |
#| effect_end_timestamp    | timestamp            | NO   |     | 0000-00-00 00:00:00 |
#| repeat_type             | tinyint(3) unsigned  | NO   |     | NULL                |
#| repeat_cycle            | int(10) unsigned     | NO   |     | 0                   |
#| task_handle_type        | smallint(5) unsigned | NO   |     | 0                   |
#| task_type               | smallint(5) unsigned | NO   |     | 0                   |
#| task_index              | smallint(5) unsigned | NO   |     | NULL                |
#| ctime                   | timestamp            | NO   |     | CURRENT_TIMESTAMP   |
#| mtime                   | timestamp            | NO   |     | 0000-00-00 00:00:00 |
#| expand                  | mediumtext           | YES  |     | NULL                |
#+-------------------------+----------------------+------+-----+---------------------+
class Task(Base):
    __tablename__ = 'task_new'
    __table_args__ = {'autoload':True}



#任务ID	任务包ID	任务名称	任务描述	任务提示	激活条件	有效开始时间	有效结束时间    周期重复类型	周期间隔	前置任务ID	奖励数量	奖励描述	奖励类型	处理类型	排序索引	任务分类
def task_section_process(lt):
    task = Task()
    task.task_id = int(lt[0])
    task.task_pkg_id = int(lt[1])
    task.name = u(lt[2])
    task.task_description = u(lt[3])
    task.prompt = u(lt[4])
    task.activation_conditions = int(lt[5])
    task.effect_begin_timestamp = t(lt[6])
    task.effect_end_timestamp = t(lt[7])
    task.repeat_type = int(lt[8])
    task.repeat_cycle = int(lt[9])
    task.activation_prev_task_id = int(lt[10])
    task.award_amount = int(lt[11])
    task.award_detail = u(lt[12])
    task.award_type = int(lt[13])
    task.task_handle_type = int(lt[14])
    task.task_index = int(lt[15])
    task.task_type = int(lt[16])

    task.ctime = today()
    task.mtime = today()

    if task.effect_begin_timestamp > task.effect_end_timestamp:
        print "[ERROR]effect_begin_timestamp must early than effect_end_timestamp"
        exit(1)
    if not checkRange(task.activation_conditions, 1, 4):
        print "[ERROR]activation_conditions must in 1-4"
        exit(1)
    if not checkRange(task.repeat_type, 0, 1):
        print "[ERROR]repeat_type must in 0-1"
        exit(1)
    if not checkRange(task.task_handle_type, 1, 2):
        print "[ERROR]task_handle_type must in 1-2"
        exit(1)

    print "task id {0} parsed".format(task.task_id)
    return task



#+--------------------+----------------------+------+-----+---------+
#| Field              | Type                 | Null | Key | Default |
#+--------------------+----------------------+------+-----+---------+
#| action_type        | smallint(5) unsigned | NO   | PRI | NULL    |
#| task_id            | int(10) unsigned     | NO   | PRI | NULL    |
#| handle_type        | smallint(5) unsigned | NO   |     | NULL    |
#| action_description | varchar(1024)        | NO   |     | NULL    |
#| need_done_count    | int(10) unsigned     | NO   |     | NULL    |
#| expand             | varchar(1024)        | YES  |     | NULL    |
#+--------------------+----------------------+------+-----+---------+
class Action(Base):
    __tablename__ = 'action_new'
    __table_args__ = {'autoload':True}


# 任务ID    动作描述    动作数量    处理类型    分享URL     动作分类
def action_section_process(lt):
    a = Action()
    a.task_id = int(lt[0])
    a.action_description = u(lt[1])
    a.need_done_count = int(lt[2])
    a.handle_type = int(lt[3])
    a.expand = lt[4]
    a.action_type = lt[5] or 0

    if not checkRange(a.handle_type, 1, 4):
        print "[ERROR]handle_type must in 1-4"
        exit(1)

    print "action type {0} parsed".format(a.action_type)
    return a


def parse_file(f):
    with open(f, 'r') as f:
        print "reading", f.name
        lines = f.readlines()

        lines = lines[2:]

        ret = []
        for line in lines:
            lt = line.split("\t")
            lt = [x.strip() for x in lt]

            ret.append(lt)
            print "id {0} loaded".format(lt[0])

    return ret


def save_pkg(f):
    for lt in parse_file(f):
        S.add(pkg_section_process(lt))
    S.commit()
    print "sql pkg commit sucess"


def save_task(ft):
    ltt = parse_file(ft)
    for lt in ltt:
        S.add(task_section_process(lt))
    S.commit()
    print "sql task commit sucess"


def save_action(fa):
    lta = parse_file(fa)
    for lt in lta:
        S.add(action_section_process(lt))
    S.commit()
    print "sql action commit sucess"



def rename_p():
    engine.execute("RENAME TABLE taskpkg TO taskpkg_{0}".format(int(time.time())))
    engine.execute("RENAME TABLE taskpkg_new TO taskpkg")
    engine.execute("drop table if exists action_new;")
    engine.execute("drop table if exists task_new;")


def rename_t():
    engine.execute("RENAME TABLE task TO task_{0}".format(int(time.time())))
    engine.execute("RENAME TABLE task_new TO task")
    engine.execute("drop table if exists action_new;")
    engine.execute("drop table if exists taskpkg_new;")


def rename_a():
    engine.execute("RENAME TABLE action TO action_{0}".format(int(time.time())))
    engine.execute("RENAME TABLE action_new TO action")
    engine.execute("drop table if exists task_new;")
    engine.execute("drop table if exists taskpkg_new;")



def clean_backup():
    print "clean_backup"


def main():
    f_pkg = ARGS["p"]
    f_task  = ARGS["t"]
    f_action = ARGS["a"]
    if f_pkg:
        save_pkg(f_pkg)
        rename_p()
    elif f_task:
        save_task(f_task)
        rename_t()
    elif f_action:
        save_action(f_action)
        rename_a()


if __name__ == "__main__":
    main()

