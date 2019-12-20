# -*- coding: utf-8 -*-

"""
pub.DBConn
~~~~~~~~~~~~~~~~

该模块提供数据库访问方法
"""

import cx_Oracle
import sqlite3
import os


class DBConn(object):
    def __init__(self):
        self.conn = None
        self.cursor = None

    def connect(self, db_type, *args):
        try:
            if db_type == "Oracle":
                self.conn = cx_Oracle.connect(*args)
                self.cursor = self.conn.cursor()
            elif db_type == "sqlite3":
                self.conn = sqlite3.connect(*args)
                self.cursor = self.conn.cursor()
        except Exception as e:
            print(str.format("数据库连接异常:{0}", e))

    def execute(self, sql):
        self.cursor.execute(sql)

    def fetchone(self):
        row = self.cursor.fetchone()

        return row

    def fetchall(self):
        rows = self.cursor.fetchall()

        return rows

    def commit(self):
        self.conn.commit()

    def __del__(self):
        self.cursor.close()
        self.conn.close()


def get_project_root():
    path = os.path.abspath(os.curdir)

    return path


def get_data_from_database(database, filename, sql):
    db = DBConn()
    database_path = get_project_root()+filename
    print(database_path)
    print(database_path)
    db.connect(database, database_path)
    db.execute(sql)
    rows = db.fetchall()

    return rows


def get_data(data, index):
    data_list = []
    for e in data:
        data_list.append(e[index])

    return data_list



