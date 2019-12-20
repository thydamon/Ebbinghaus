# -*- coding: utf-8 -*-

"""
Ebbinghaus.py
~~~~~~~~~~~~~~~~~~~~~~~~~

Ebbinghaus处理模块
"""

import Dbconn
import Log
from Log import logger
from datetime import datetime, timedelta
import time
from collections import namedtuple


class Ebbinghaus(object):
    def __init__(self):
        database_path = Dbconn.get_project_root() + "/" + "Ebbinghaus.db"
        self.db_con = Dbconn.DBConn()
        self.db_con.connect("sqlite3", database_path)
        self.content_type = namedtuple('content', ['id', 'name', 'content', 'time', 'ebbinghausid'])

    def today_to_do_list(self):
        """
        生成今天的任务
        # >>> from datetime import datetime
        # >>> cday = datetime.strptime('2017-8-1 18:20:20', '%Y-%m-%d %H:%M:%S')
        # >>> print(cday)
        2017-08-01 18:20:20
        # >>> from datetime import datetime, timedelta
        # >>> now = datetime.now()
        # >>> now
        datetime.datetime(2017, 5, 18, 16, 57, 3, 540997)
        # >>> now + timedelta(hours=10)
        datetime.datetime(2017, 5, 19, 2, 57, 3, 540997)
        # >>> now - timedelta(days=1)
        datetime.datetime(2017, 5, 17, 16, 57, 3, 540997)
        # >>> now + timedelta(days=2, hours=12)
        datetime.datetime(2017, 5, 21, 4, 57, 3, 540997)
        :return:
        """
        # 取初始的任务
        # sql = "select name,content,time,ebbinghausid from items where status = 0"
        # self.db_con.execute(sql)
        # unfinished_rows = self.db_con.fetchall()

        # 取遗忘曲线未完成任务
        sql = "select id,name,content,update_time,ebbinghausid from items where status = 1"
        self.db_con.execute(sql)
        raw_rows = self.db_con.fetchall()

        ebbinghaus_rows = []
        for row in raw_rows:
            # 取时间比较
            db_time = datetime.strptime(row[3], '%Y-%m-%d %H:%M:%S')
            now_time = datetime.now()
            # 计算差值
            interval = now_time - db_time
            interval_day = interval.days
            interval_second = interval.seconds
            interval_time = interval_day + interval_second/(60*60*24)

            # 查询ebbinghaus信息
            sql = "select time from ebbinghaus where id = %d" % row[4]
            self.db_con.execute(sql)
            ebbinghaus_raw_rows = self.db_con.fetchall()
            # 大于遗忘曲线指定时间的都要取出
            logger.info("interval_time[%f]ebbinghaus_time[%f]"%(float(interval_time), float(ebbinghaus_raw_rows[0][0])))
            if float(interval_time) >= float(ebbinghaus_raw_rows[0][0]):
                content = self.content_type._make(list(row))
                ebbinghaus_rows.append(content)

        list_rows = ebbinghaus_rows

        return list_rows

    def register_today_task(self, name, content, remark):
        # 获取当前时间
        """
        :param name:  items类别
        :param content: items内容
        :param remark: 备注选填
        :return:

        times: 完成次数
        status: 1-未完成 2-当天已完成
        """
        now = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
        sql = "insert into items (Name,Content,Remark,Time,Times,EbbinghausId,Status,Update_Time) " \
              "values('%s','%s','%s','%s',%d,%d,%d, '%s')" % \
              (name, content, remark, now, 0, 1, 1, now)
        self.db_con.execute(sql)
        self.db_con.commit()

    def update_today_task(self, item_id, rank, remark):
        """
        更新任务难度
        :param item_id: 任务ID
        :param rank: 1-right[EbbinghausId:8]
                     2-easy[EbbinghausId:5]
                     3-general[EbbinghausId:4]
                     4-difficultly[EbbinghausId:3]
                     5-difficultly[EbbinghausId:2]
        :param remark: 备注
        :return:
        """

        ebbinghaus_id = 0
        if rank == 1:
            ebbinghaus_id = 8
        elif rank == 2:
            ebbinghaus_id = 5
        elif rank == 3:
            ebbinghaus_id = 4
        elif rank == 4:
            ebbinghaus_id = 3
        elif rank == 5:
            ebbinghaus_id = 2

        sql = "select times,rank,update_time from items where id = %d" % item_id
        logger.info(sql)
        self.db_con.execute(sql)
        raw_rows = self.db_con.fetchall()
        times = int(raw_rows[0][0]) + 1  # 次数加一

        # 只有等级调小才重新更新日期，计算时间间隔
        if rank > int(raw_rows[0][1]):
            update_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())   # 当期时间
        else:
            update_time = raw_rows[0][2]  # 原来时间

        sql = "update items set times = %d, ebbinghausid = %d, remark = '%s', Update_Time = '%s' where id = %d" % \
              (times, ebbinghaus_id, remark, update_time, item_id)
        logger.info(sql)
        self.db_con.execute(sql)
        self.db_con.commit()

#
# if __name__ == '__main__':
#     Log.init_logger("./Ebbinghaus.log", "debug")
#     eb = Ebbinghaus()
#     # eb.register_today_task("name3", "content3", "")
#     # eb.update_today_task()
#     rows = eb.today_to_do_list()
#     logger.info("*"*50)
#     logger.info(rows)
#     logger.info("="*50)
#     eb.update_today_task(2, 2, "")
#     # rows = eb.today_to_do_list()
#     logger.info("*" * 50)
#     logger.info(rows)

