# -*- coding: utf-8 -*-

"""
Winframe.py
~~~~~~~~~~~~~~~~~~~~~~~~~

Winframe处理模块
"""

from tkinter import *
import copy
import tkinter.messagebox
from tkinter import ttk
from tkinter import filedialog
import xlwt
from datetime import datetime
import Log
from Log import logger
from Ebbinghaus import Ebbinghaus

photo = None


def update_item(winframe, sub_frame,item_id, name, content, remark):
    winframe.algo_eb.update_item(item_id, name, content, remark)
    sub_frame.destroy()


def tree_click(event, tree, winframe):
    sub_frame = Tk()
    sub_frame.title("Modify Item")  # 设置窗口名字
    screenwidth = sub_frame.winfo_screenwidth()
    screenheight = sub_frame.winfo_screenheight()
    size = '%dx%d+%d+%d' % (500, 220, (screenwidth - 500) / 2, (screenheight - 220) / 3)
    sub_frame.geometry(size)

    for item in tree.selection():
        item_text = tree.item(item, "values")
        print(item_text[2])  # 输出所选行的第一列的值

    box_frame = Frame(sub_frame)
    box_frame.pack(side=TOP, fill=BOTH, expand=NO)

    # Name标签
    text_label_name = Label(box_frame, text='Task Name:')
    text_label_name.grid(row=0, column=0)

    # 输入框
    logger.info(item_text[1])
    input_box = Entry(box_frame, show=None, font=('Arial', 9), width=50)
    input_box.insert(END, item_text[1])
    input_box.grid(row=0, column=1)

    # Content标签
    text_label_content = Label(box_frame, text='Task Content:')
    text_label_content.grid(row=1, column=0)

    # 文本框
    text_box = Text(box_frame, width=50, height=5, font=('Arial', 9))
    text_box.insert(INSERT, item_text[3])
    text_box.grid(row=1, column=1)

    # Content标签
    remark_label_content = Label(box_frame, text='Remark:')
    remark_label_content.grid(row=2, column=0)

    remark_box = Text(box_frame, width=50, height=5, font=('Arial', 9))
    remark_box.insert(INSERT, item_text[4])
    remark_box.grid(row=2, column=1)

    # 新建button_frame
    button_frame = Frame(sub_frame)
    button_frame.pack(side=TOP, expand=NO)

    # 按钮
    button_box_r = Button(button_frame, text='Save', width=5, height=1,
                          command=lambda: update_item(winframe, sub_frame, item_text[0], input_box.get(),
                                                      text_box.get(1.0, END), remark_box.get(1.0, END)))
    button_box_r.grid(row=0, column=1)

    sub_frame.mainloop()


class WinFrame(object):
    def __init__(self):
        self.algo_eb = Ebbinghaus()
        self.items = self.algo_eb.today_to_do_list()
        self.frame_list = []
        self.win_frame = Tk()
        self.win_frame.title("Ebbinghaus")  # 设置窗口名字
        self.center_window(500, 220)
        # self.win_frame.geometry('500x220')  # 设置窗口大小
        self.set_menu()

    def draw_menu(self, line_frame):
        """
        在菜单下面画线
        :param line_frame:
        :return:
        """
        can = Canvas(line_frame, width=400, height=450)
        can.pack()
        can.create_line((0, 25), (500, 25), width=1)

    def fetch_one_item(self):
        raw_item = copy.deepcopy(self.items)
        fetch_one_item = raw_item.pop()

        return fetch_one_item

    def remove_one_item(self):
        remove_one_item = self.items.pop()

        return remove_one_item

    def set_menu(self):
        menu_bar = Menu(self.win_frame)

        file_menu = Menu(menu_bar, tearoff=0)
        menu_bar.add_cascade(label='File', menu=file_menu)
        file_menu.add_command(label='Insert', command=self.register_task)
        file_menu.add_command(label='Task', command=self.show_task)
        file_menu.add_command(label='List', command=self.list_task)
        file_menu.add_command(label='All', command=self.show_all)
        file_menu.add_command(label='Export', command=self.export_task)

        self.win_frame.config(menu=menu_bar)

    def register_task(self):
        # 清空界面
        self.destroy_frame()

        # 新建frame_box
        box_frame = Frame(self.win_frame)
        self.frame_list.append(box_frame)
        box_frame.pack(side=TOP, fill=BOTH, expand=NO)

        # Name标签
        text_label_name = Label(box_frame, text='Task Name:')
        text_label_name.grid(row=0, column=0)

        # 输入框
        combox_list = ttk.Combobox(box_frame, width=48)
        combox_list['values'] = self.algo_eb.get_item_name()
        combox_list.grid(row=0, column=1)

        # Content标签
        text_label_content = Label(box_frame, text='Task Content:')
        text_label_content.grid(row=1, column=0)

        # 文本框
        text_box = Text(box_frame, width=50, height=5, font=('Arial', 9))
        text_box.grid(row=1, column=1)

        # Content标签
        remark_label_content = Label(box_frame, text='Remark:')
        remark_label_content.grid(row=2, column=0)

        remark_box = Text(box_frame, width=50, height=5, font=('Arial', 9))
        remark_box.grid(row=2, column=1)

        # 新建button_frame
        button_frame = Frame(self.win_frame)
        self.frame_list.append(button_frame)
        button_frame.pack(side=TOP, expand=NO)

        # 按钮
        button_box_r = Button(button_frame, text='Save', width=5, height=1,
                              command=lambda: self.insert_task(combox_list, text_box, remark_box))
        button_box_r.grid(row=0, column=1)

    def show_task(self):
        # 清空界面
        self.destroy_frame()
        if len(self.items) > 0:
            ele_list = self.remove_one_item()
        else:
            tkinter.messagebox.showinfo('Message', 'Task is Empty!')
            return

        # 新建frame_box
        box_frame = Frame(self.win_frame)
        self.frame_list.append(box_frame)
        box_frame.pack(side=TOP, fill=BOTH, expand=NO)

        # Name标签
        text_label_name = Label(box_frame, text='Task Name:')
        text_label_name.grid(row=0, column=0)

        # 输入框
        data_name = StringVar(value=ele_list.name)
        input_box = Entry(box_frame, textvariable=data_name, show=None, font=('Arial', 9), width=50)
        input_box.grid(row=0, column=1)

        # Content标签
        text_label_content = Label(box_frame, text='Task Content:')
        text_label_content.grid(row=1, column=0)

        # 文本框
        text_box = Text(box_frame, width=50, height=5, font=('Arial', 9))
        text_box.insert(INSERT, ele_list.content)
        text_box.grid(row=1, column=1)

        # Content标签
        remark_label_content = Label(box_frame, text='Remark:')
        remark_label_content.grid(row=2, column=0)

        remark_box = Text(box_frame, width=50, height=5, font=('Arial', 9))
        remark_box.grid(row=2, column=1)

        # 新建button_frame
        button_frame = Frame(self.win_frame)
        self.frame_list.append(button_frame)
        button_frame.pack(side=TOP, expand=NO)

        # 按钮
        button_box_r = Button(button_frame, text='R', width=2, height=1,
                              command=lambda: self.update_task(remark_box, ele_list.id, 1))
        button_box_r.grid(row=0, column=1)

        button_box_e = Button(button_frame, text='E', width=2, height=1,
                              command=lambda: self.update_task(remark_box, ele_list.id, 2))
        button_box_e.grid(row=0, column=2)

        button_box_g = Button(button_frame, text='G', width=2, height=1,
                              command=lambda: self.update_task(remark_box, ele_list.id, 3))
        button_box_g.grid(row=0, column=3)

        button_box_d = Button(button_frame, text='D', width=2, height=1,
                              command=lambda: self.update_task(remark_box, ele_list.id, 4))
        button_box_d.grid(row=0, column=4)

        button_box_t = Button(button_frame, text='T', width=2, height=1,
                              command=lambda: self.update_task(remark_box, ele_list.id, 5))
        button_box_t.grid(row=0, column=5)

    def list_task(self):
        self.destroy_frame()
        if len(self.items) == 0:
            tkinter.messagebox.showinfo('Message', 'Task List is Empty!')
            return
        table_frame = Frame(self.win_frame)
        table_frame.pack()
        self.frame_list.append(table_frame)
        columns = ("ID", "Name", "Content", "Remark")
        tree_view = ttk.Treeview(table_frame, show="headings", height=45, columns=columns)

        tree_view.heading("ID", text="ID")
        tree_view.heading("Name", text="Name")
        tree_view.heading("Content", text="Content")
        tree_view.heading("Remark", text="Remark")

        tree_view.column("ID", width=100)
        tree_view.column("Name", width=100)
        tree_view.column("Content", width=100)
        tree_view.column("Remark", width=100)

        for ele in self.items:
            tree_view.insert("", 0, values=ele)

        # 设置滚动条
        scroll_bar = tkinter.Scrollbar(table_frame)
        scroll_bar.pack(side=tkinter.RIGHT, fill=tkinter.Y)
        scroll_bar.config(command=tree_view.yview)

        tree_view.pack()

    def insert_task(self, combox_list, text_box, remark_box):
        self.algo_eb.register_today_task(combox_list.get(), text_box.get(1.0, END), remark_box.get(1.0, END))
        # combox_list.delete(0, END)
        text_box.delete(1.0, END)
        remark_box.delete(1.0, END)

    def show_all(self):
        self.destroy_frame()
        if len(self.items) == 0:
            tkinter.messagebox.showinfo('Message', 'Task List is Empty!')
            return
        table_frame = Frame(self.win_frame)
        table_frame.pack()
        self.frame_list.append(table_frame)
        columns = ("ID", "Name", "Time", "Content", "Remark", "Times", "Ebbinghuasid", "Status", "Update Time")
        tree_view = ttk.Treeview(table_frame, show="headings", height=45, columns=columns)

        tree_view.heading("ID", text="ID")
        tree_view.heading("Name", text="Name")
        tree_view.heading("Time", text="Time")
        tree_view.heading("Content", text="Content")
        tree_view.heading("Remark", text="Remark")
        tree_view.heading("Times", text="Times")
        tree_view.heading("Ebbinghuasid", text="Ebbinghuasid")
        tree_view.heading("Status", text="Status")
        tree_view.heading("Update Time", text="Update Time")

        tree_view.column("ID", width=100)
        tree_view.column("Name", width=100)
        tree_view.column("Time", width=100)
        tree_view.column("Content", width=100)
        tree_view.column("Remark", width=100)
        tree_view.column("Times", width=100)
        tree_view.column("Ebbinghuasid", width=100)
        tree_view.column("Status", width=100)
        tree_view.column("Update Time", width=100)

        for ele in self.algo_eb.list_all():
            tree_view.insert("", 0, values=ele)

        tree_view.bind('<Double-Button-1>', lambda event: tree_click(event, tree_view, self))

        # 设置滚动条
        scroll_bar = tkinter.Scrollbar(table_frame)
        scroll_bar.pack(side=tkinter.RIGHT, fill=tkinter.Y)
        scroll_bar.config(command=tree_view.yview)

        tree_view.pack()

    def export_task(self):
        book = xlwt.Workbook()
        sheet = book.add_sheet('sheet')

        alignment = xlwt.Alignment()  # 创建居中
        alignment.horz = xlwt.Alignment.HORZ_CENTER
        alignment.vert = xlwt.Alignment.VERT_CENTER
        style = xlwt.XFStyle()  # 创建样式
        style.alignment = alignment  # 给样式添加文字居中属性
        style.font.height = 200  # 设置字体大小

        col_name = [('ID', 'Name', 'Content', 'Time', 'EbbinghausID')]

        for row, line in enumerate(col_name):
            logger.info(line)
            for col, value in enumerate(line):
                logger.info(value)
                sheet.write(row, col, value, style)

        for row, line in enumerate(self.items):
            row = row + 1
            logger.info(line)
            for col, value in enumerate(line):
                logger.info(value)
                sheet.write(row, col, value)

        date_time = datetime.now().strftime('%Y-%m-%d')
        xml_file = filedialog.asksaveasfilename()
        book.save('%s_%s.xls' % (xml_file, date_time))

    def update_task(self, remark_box, item_id, rank):
        self.algo_eb.update_today_task(item_id, rank, remark_box.get(1.0, END))
        self.show_task()

    def center_window(self, width, height):
        screenwidth = self.win_frame.winfo_screenwidth()
        screenheight = self.win_frame.winfo_screenheight()
        size = '%dx%d+%d+%d' % (width, height, (screenwidth - width) / 2, (screenheight - height) / 3)
        self.win_frame.geometry(size)

    def destroy_frame(self):
        while len(self.frame_list) > 0:
            ele = self.frame_list.pop(0)
            ele.destroy()

    def show_wind(self):
        self.win_frame.mainloop()


if __name__ == "__main__":
    Log.init_logger("./Ebbinghaus.log", "debug")
    wf = WinFrame()
    wf.show_wind()
