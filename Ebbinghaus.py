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


def cal_time_interval(time_start, now_time):
    db_time = datetime.strptime(time_start, '%Y-%m-%d %H:%M:%S')
    # now_time = datetime.now()
    # 计算差值
    interval = now_time - db_time
    interval_day = interval.days
    interval_second = interval.seconds
    interval_time = interval_day + interval_second / (60 * 60 * 24)

    return interval_time


class Ebbinghaus(object):
    def __init__(self):
        database_path = Dbconn.get_project_root() + "/" + "Ebbinghaus.db"
        self.db_con = Dbconn.DBConn()
        self.db_con.connect("sqlite3", database_path)
        self.content_type = namedtuple('content', ['id', 'name', 'content', 'time', 'ebbinghausid'])

    def today_to_do_list(self):
        """
        生成今天的任务
        :return:
        """
        # 取遗忘曲线未完成任务
        sql = "select id,name,content,update_time,ebbinghausid from items where status = 1"
        self.db_con.execute(sql)
        raw_rows = self.db_con.fetchall()

        ebbinghaus_rows = []
        for row in raw_rows:
            # 计算差值
            interval_time = cal_time_interval(row[3], datetime.now())

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
        now_time = datetime.strptime(now, '%Y-%m-%d %H:%M:%S')
        delta = timedelta(days=0.5)
        review_time = (now_time+delta).strftime('%Y-%m-%d %H:%M:%S')
        sql = "insert into items (Name,Content,Remark,Time,Times,EbbinghausId,Status,Update_Time,Review_Time) " \
              "values('%s','%s','%s','%s',%d,%d,%d, '%s','%s')" % \
              (name, content.strip(), remark.strip(), now, 0, 1, 1, now, review_time)
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

        sql = "select times,ebbinghausid,update_time from items where id = %d" % item_id
        logger.info(sql)
        self.db_con.execute(sql)
        raw_rows = self.db_con.fetchall()
        times = int(raw_rows[0][0]) + 1  # 次数加一
        # rank = int(raw_rows[0][1])

        # 只有等级调小才重新更新日期，计算时间间隔
        # if ebbinghaus_id < int(raw_rows[0][1]):
        #     update_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())   # 当期时间
        # else:
        #     update_time = raw_rows[0][2]  # 原来时间
        #
        # # 未按期完成的，重新开始计算
        rank_days = self.get_day_by_rank_id(rank)
        # interval_time = cal_time_interval(update_time, datetime.now())  # 任务完成时间间隔
        # logger.info("update_time[%s],now[%s],interval_time[%f]ebbbinghaus_interval[%f]"
        #             % (update_time, datetime.now(), interval_time, rank_days))
        # if interval_time > rank_days:   # 任务完成时间间隔大于ebbinghuas时间间隔
        #     update_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
        # 更新时间都取最新时间
        update_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())  # 当期时间

        now = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
        now_time = datetime.strptime(now, '%Y-%m-%d %H:%M:%S')
        delta = timedelta(days=rank_days)
        review_time = (now_time+delta).strftime('%Y-%m-%d %H:%M:%S')

        sql = "update items set times = %d, ebbinghausid = %d, remark = '%s', update_time = '%s', review_time= '%s' " \
              "where id = %d" % (times, ebbinghaus_id, remark.strip(), update_time, review_time, item_id)
        logger.info(sql)
        self.db_con.execute(sql)
        self.db_con.commit()

    def get_day_by_rank_id(self, rank):
        sql = "select time from ebbinghaus,rank where rank.ebbinghausId = ebbinghaus.id and rank = %d" % rank
        logger.info(sql)
        self.db_con.execute(sql)
        raw_row = self.db_con.fetchall()

        return int(raw_row[0][0])

    def get_item_name(self):
        sql = "SELECT DISTINCT name FROM items"
        logger.info(sql)
        self.db_con.execute(sql)
        raw_row = self.db_con.fetchall()

        ret_row = []
        for ele in raw_row:
            ret_row.append(ele[0])

        return tuple(ret_row)

    def list_all(self):
        sql = "SELECT * FROM items ORDER BY ID DESC"
        logger.info(sql)
        self.db_con.execute(sql)
        raw_rows = self.db_con.fetchall()

        item_type = namedtuple('item', ['id', 'name', 'time', 'content', 'remark', 'times', 'ebbinghuasid', 'status',
                                        'update_time', 'review_time'])

        ret_rows = []
        for row in raw_rows:
                item = item_type._make(list(row))
                ret_rows.append(item)

        return ret_rows

    def list_all_by_query(self, query_string):
        sql = "SELECT * FROM items WHERE Name = '%s' ORDER BY ID DESC" % query_string
        logger.info(sql)
        self.db_con.execute(sql)
        raw_rows = self.db_con.fetchall()

        item_type = namedtuple('item', ['id', 'name', 'time', 'content', 'remark', 'times', 'ebbinghuasid', 'status',
                                        'update_time', 'review_time'])

        ret_rows = []
        for row in raw_rows:
                item = item_type._make(list(row))
                ret_rows.append(item)

        return ret_rows

    def update_item(self, item_id, name, content, remark):
        sql = "update items set name = '%s', content = '%s', remark = '%s' where id = %d" % \
              (name, content.strip(), remark.strip(), int(item_id))
        logger.info(sql)
        self.db_con.execute(sql)
        self.db_con.commit()


if __name__ == '__main__':
    # Log.init_logger("./Ebbinghaus.log", "debug")
    # eb = Ebbinghaus()
    # eb.register_today_task("name3", "content3", "")
    # eb.update_today_task()
    # rows = eb.today_to_do_list()
    # logger.info("*"*50)
    # logger.info(rows)
    # logger.info("="*50)
    # eb.update_today_task(2, 2, "")
    # rows = eb.today_to_do_list()
    # rows = eb.list_all()
    # print(rows)
    # logger.info("*" * 50)
    # logger.info(rows)
    a = cal_time_interval("2019-12-25 21:20:55", datetime.now())
    print(a)
