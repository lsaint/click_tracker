# -*- coding: utf-8 -*-

from datetime import datetime, date

from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, scoped_session


def t(s):
    return datetime.strptime(s, "%Y/%m/%d")

def today():
    return date.today()

def u(s):
    return s.decode("gbk")


engine = create_engine("mysql://root:111333@localhost/CommonTaskSys_TaskInfo_appid", convert_unicode=True)
S = scoped_session(sessionmaker(autocommit=False, autoflush=False, bind=engine))
Base = declarative_base(engine)


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
    __tablename__ = 'taskpkg'
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

    S.add(p)

#+-------------------------+----------------------+------+-----+---------------------+
#| Field                   | Type                 | Null | Key | Default             |
#+-------------------------+----------------------+------+-----+---------------------+
#| task_id                 | int(10) unsigned     | NO   | PRI | NULL                |
#| task_pkg_id             | int(10) unsigned     | NO   |     | NULL                |
#| name                    | varchar(256)         | NO   |     | NULL                |
#| task_description        | varchar(1024)        | NO   |     | NULL                |
#| prompt                  | varchar(256)         | NO   |     | NULL                |
#| action_type             | smallint(5) unsigned | NO   |     | 0                   |
#| handle_type             | smallint(5) unsigned | NO   |     | NULL                |
#| action_description      | varchar(1024)        | NO   |     | NULL                |
#| need_done_count         | int(10) unsigned     | NO   |     | NULL                |
#| action_expand           | varchar(1024)        | YES  |     | NULL                |
#| have_other_actions      | tinyint(1)           | NO   |     | 0                   |
#| award_type              | smallint(5) unsigned | NO   |     | NULL                |
#| award_amount            | int(10) unsigned     | NO   |     | NULL                |
#| award_detail            | varchar(256)         | NO   |     | NULL                |
#| activation_conditions   | int(10) unsigned     | NO   |     | NULL                |
#| activation_prev_task_id | int(10) unsigned     | NO   |     | NULL                |
#| effect_begin_timestamp  | timestamp            | NO   |     | CURRENT_TIMESTAMP   |
#| effect_end_timestamp    | timestamp            | NO   |     | 0000-00-00 00:00:00 |
#| repeat_type             | tinyint(3) unsigned  | NO   |     | NULL                |
#| repeat_cycle            | int(10) unsigned     | NO   |     | 0                   |
#| task_handle_type        | smallint(5) unsigned | NO   |     | 0                   |
#| task_type               | smallint(5) unsigned | NO   |     | 0                   |
#| task_index              | smallint(5) unsigned | NO   |     | NULL                |
#| ctime                   | timestamp            | NO   |     | 0000-00-00 00:00:00 |
#| mtime                   | timestamp            | NO   |     | 0000-00-00 00:00:00 |
#| expand                  | mediumtext           | YES  |     | NULL                |
#+-------------------------+----------------------+------+-----+---------------------+
class Task(Base):
    __tablename__ = 'task'
    __table_args__ = {'autoload':True}



#任务ID	任务包ID	任务名称	任务描述	任务提示	激活条件	有效开始时间	有效结束时间	周期间隔	前置任务ID	奖励数量	奖励描述	奖励类型	处理类型	排序索引	任务分类
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
    task.repeat_cycle = int(lt[8])
    task.activation_prev_task_id = int(lt[9])
    task.award_amount = int(lt[10])
    task.award_detail = u(lt[11])
    task.award_type = int(lt[12])
    task.task_index = int(lt[13])
    task.task_type = int(lt[14])

    task.action_type = 0
    task.handle_type = 0
    task.action_description = ""
    task.need_done_count = 0
    task.have_other_actions = 0
    task.repeat_type = 0
    task.task_handle_type = 0
    task.ctime = today()
    task.mtime = today()

    S.add(task)



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
    __tablename__ = 'action'
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

    S.add(a)



def parse_file(f):
    with open(f, 'r') as f:
        lines = f.readlines()
        meta = lines[0]

        lines = lines[2:]

        for line in lines:
            lt = line.split("\t")
            lt = [x.strip() for x in lt]
            print lt

            #pkg_section_process(lt)
            #action_section_process(lt)
            task_section_process(lt)

            S.commit()


if __name__ == "__main__":
    #parse_file("task_pkg.txt")
    #parse_file("action.txt")
    parse_file("task.txt")



