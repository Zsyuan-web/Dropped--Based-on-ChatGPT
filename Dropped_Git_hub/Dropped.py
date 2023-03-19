# -*- coding: utf-8 -*-
from Dropped_UI import *
import sys
from PyQt5.QtWidgets import QApplication, QMainWindow
import openai
import os
import re
from PyQt5.QtCore import pyqtSlot, QThread, pyqtSignal
import threading
import json
import multiprocessing as mult
import time
import threading

class FileHandler:
    def __init__(self, file_path):
        self.file_path = file_path

    def read_file(self):
        try:
            with open(self.file_path, 'r', encoding="utf-8") as f:
                return json.load(f)
        except FileNotFoundError:
            print(f"File {self.file_path} not found.")

    def write_file(self, content):
        with open(self.file_path, 'w', encoding="utf-8") as f:
            json.dump(content, f)

class ChatGPT(QThread):
    # 次线程任务
    finished = pyqtSignal(str)  # 自定义信号，表示线程完成任务
    def __init__(self, ip,api_key, message,timeout=30):
        super(ChatGPT, self).__init__()
        self.ip=ip
        self.api_key = api_key
        self.message = message
        self.timeout = timeout  # 超时时间，单位为秒
        os.environ["HTTP_PROXY"] = self.ip
        os.environ["HTTPS_PROXY"] = self.ip

    def run(self):
        def timeout_handler():
            # 超时处理函数
            self.finished.emit('请求超时，请添加代理IP或重试!')
        try:
            start_time = time.time()  # 获取开始时间
            # 创建一个 Timer 对象
            timer = threading.Timer(self.timeout, timeout_handler)
            timer.start()  # 启动定时器
            openai.api_key = self.api_key
            completion = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[{"role": "user", "content": f"{self.message}"}]
            )
            text = completion.choices[0].message.content
            # 取消定时器
            timer.cancel()
            self.finished.emit(text)  # 发送完成信号和程序执行结果
        except Exception as e:
            self.finished.emit('请求失败,请检查API和代理设置！')





    def get_response(self):
        self.start()

class Dropped_window(QMainWindow):
    def __init__(self):
        super().__init__()
        self.ui=Ui_MainWindow()
        self.ui.setupUi(self)
        self.setWindowFlag(QtCore.Qt.FramelessWindowHint)
        self.setAttribute(QtCore.Qt.WA_TranslucentBackground)

        # 设置默认ip为空
        self.ip = ""
        # 备用文件创建实例
        self.file_handler = FileHandler('back file.txt')
        # 读取备用文件
        self.content = self.file_handler.read_file()
        # 页面跳转链接
        self.ui.pushButton_main.clicked.connect(self.display_page1)
        self.ui.pushButton_set.clicked.connect(self.display_page2)

        # 设置页面“确认(key)”按钮链接
        self.ui.pushButton_key.clicked.connect(self.PB_kye)

        # 设置页面“设为备用(key)”按钮链接
        self.ui.pushButton_key_3.clicked.connect(self.PB_kye_back)

        # 设置页面“确认(ip)”按钮链接
        self.ui.pushButton_ip.clicked.connect(self.PB_ip)

        # 设置页面“设为备用(ip)”按钮链接
        self.ui.pushButton_ip_2.clicked.connect(self.PB_ip_back)

        # 设置页面“圆形”按钮默认状态
        self.ui.radioButton.setChecked(self.content["raButton_key"][0])
        self.ui.radioButton_2.setChecked(self.content["raButton_key"][1])
        self.ui.radioButton_3.setChecked(self.content["raButton_key"][2])
        self.ui.radioButton_4.setChecked(self.content["raButton_ip"][0])
        self.ui.radioButton_6.setChecked(self.content["raButton_ip"][1])

        if self.content["raButton_key"][1]:
            if self.content["api_key"][-1][:3]== "sk-" and len(self.content["api_key"][-1]) == 51:
                self.api_key = self.content["api_key"][-1]
                self.ui.lineEdit.setText("API key已设置为备用1")
            else:
                self.ui.lineEdit.setText("当前备用不可用")
        if self.content["raButton_key"][2]:
            if self.content["api_key"][-2][:3]== "sk-" and len(self.content["api_key"][-2]) == 51:
                self.api_key = self.content["api_key"][-2]
                self.ui.lineEdit.setText("API key已设置为备用2")
            else:
                self.ui.lineEdit.setText("当前备用不可用")
        if self.content["raButton_ip"][1]:
            if len(self.content["ip"][-1][:self.content["ip"][-1].index(":")]) <= 15 and self.content["ip"][-1][:self.content["ip"][-1].index(":")].count(".") == 3 and len(self.content["ip"][-1][self.content["ip"][-1].index(":")+1:]) == 5 and self.content["ip"][-1][self.content["ip"][-1].index(":")+1:].isdigit():
                self.ip = self.content["ip"][-1]
                self.ui.lineEdit_2.setText("代理IP已设置")
                self.ui.lineEdit_3.setText("已设置")
            else:
                self.ui.lineEdit_2.setText("代理IP不可用")
                self.ui.lineEdit_3.setText("不可用")

        # 设置页面“圆形”按钮处于非“无”时，输入文本框显示当前key和ip  链接
        self.ui.radioButton.toggled.connect(self.text_input_key)
        self.ui.radioButton_2.toggled.connect(self.text_input_key)
        self.ui.radioButton_3.toggled.connect(self.text_input_key)
        self.ui.radioButton_4.toggled.connect(self.text_input_ip)
        self.ui.radioButton_6.toggled.connect(self.text_input_ip)

        # 主页面文本框内容接收
        # 主页面”改写“按钮 链接
        self.ui.pushButton_2.clicked.connect(self.PB_Rewrite)
        # 主页面”进一步改写“按钮 链接
        self.ui.pushButton_5.clicked.connect(self.PB_Fu_Rewrite)
        # 主页面”扩写“按钮 链接
        self.ui.pushButton_4.clicked.connect(self.PB_Ex_Rewrite)
        # 主页面”缩写“按钮 链接
        self.ui.pushButton.clicked.connect(self.PB_Ab_Rewrite)
        # 主页面”语法检查“按钮 链接
        self.ui.pushButton_6.clicked.connect(self.PB_Gr_Rewrite)

        # 主页面”清空“按钮 链接
        self.ui.pushButton_3.clicked.connect(self.PB_Rewrite_clear)


        # 窗口显示
        self.show()

    # 设置页面“确认(key)”按钮功能
    def PB_kye(self):
        key_text= self.ui.lineEdit.text()
        self.file_handler.write_file(self.content)  # “圆形”按钮的默认状态将写入备用文件
        # 确保输入格式正确
        if key_text == "无" or key_text == "请输入API key……" or key_text == "API key已存在……"or key_text == "":
            self.ui.lineEdit.setText("请输入API key……")
        elif key_text[:3]!= "sk-" or len(key_text) != 51:
            self.ui.lineEdit.setText("请输入正确的API key，形如”sk-××××“的51位字符串")
        else:
            self.api_key = key_text
            self.ui.lineEdit.setText("API key已设置")


    # 设置页面“设为备用(key)”按钮功能
    def PB_kye_back(self):
        key_text = self.ui.lineEdit.text()
        if key_text == "无" or key_text == "请输入API key……" or  key_text == "":
            self.ui.lineEdit.setText("请输入API key……")
        elif key_text[:3] != "sk-" or len(key_text) != 51:
            self.ui.lineEdit.setText("请输入正确的API key，形如”sk-××××“的51位字符串")
        elif key_text in self.content["api_key"] :
            self.ui.lineEdit.setText("API key已存在……")
        else:
            self.content["api_key"].append(key_text)
            # 写入备用文件
            self.file_handler.write_file(self.content)
            self.ui.lineEdit.setText("API key已设为备用")

    # 设置页面“确认(ip)”按钮功能
    def PB_ip(self):
        self.file_handler.write_file(self.content)  # “圆形”按钮的默认状态将写入备用文件
        ip_text_0 = self.ui.lineEdit_2.text()
        ip_text_1 = self.ui.lineEdit_3.text()
        ip_text = ip_text_0 + ":" + ip_text_1
        if ip_text == ":":
            self.ip = ""
            self.ui.lineEdit_2.setText("代理IP已设置")
            self.ui.lineEdit_3.setText("已设置")
        elif ip_text == "无:无" or ip_text == "请输入代理IP:端口"or ip_text == "代理IP已存在:端口已存在":
            self.ui.lineEdit_2.setText("请输入代理IP")
            self.ui.lineEdit_3.setText("端口")

        elif len(ip_text_0)>15 or ip_text_0.count(".") != 3 or len(ip_text_1)!= 5 or ip_text_1.isdigit()!= True:
            self.ui.lineEdit_2.setText("请输入正确代理IP")
            self.ui.lineEdit_3.setText("端口")
        else:
            self.ip = ip_text
            self.ui.lineEdit_2.setText("代理IP已设置")
            self.ui.lineEdit_3.setText("已设置")


    # 设置页面“设为备用(ip)”按钮功能
    def PB_ip_back(self):
        ip_text_0 = self.ui.lineEdit_2.text()
        ip_text_1 = self.ui.lineEdit_3.text()
        ip_text = ip_text_0+":"+ip_text_1
        if ip_text == "无:无" or ip_text == "请输入代理IP:端口" or ip_text == ":":
            self.ui.lineEdit_2.setText("请输入代理IP")
            self.ui.lineEdit_3.setText("端口")
        elif len(ip_text_0) > 15 or ip_text_0.count(".") != 3 or len(ip_text_1) != 5 or ip_text_1.isdigit() != True:
            self.ui.lineEdit_2.setText("请输入正确代理IP")
            self.ui.lineEdit_3.setText("端口")
        elif ip_text in self.content["ip"]:
            self.ui.lineEdit_2.setText("代理IP已存在")
            self.ui.lineEdit_3.setText("端口已存在")
        else:
            self.content["ip"].append(ip_text)
            # 写入备用文件
            self.file_handler.write_file(self.content)
            self.ui.lineEdit_2.setText("代理IP与端口已设为备用")
            self.ui.lineEdit_3.setText("端口")

    # 设置页面“圆形”按钮处于非“无”时，输入文本框显示当前key  功能
    def text_input_key(self):
        if self.ui.radioButton.isChecked():
            self.ui.lineEdit.clear()
            self.content["raButton_key"][0] = 1  # 保证“圆形”按钮只有一个是默认选中状态
            self.content["raButton_key"][1] = 0
            self.content["raButton_key"][2] = 0
        if self.ui.radioButton_2.isChecked():
            self.ui.lineEdit.clear()
            self.content["raButton_key"][0] = 0  # 保证“圆形”按钮只有一个是默认选中状态
            self.content["raButton_key"][1] = 1
            self.content["raButton_key"][2] = 0
            self.ui.lineEdit.setText(self.content["api_key"][-1])
        if self.ui.radioButton_3.isChecked():
            self.ui.lineEdit.clear()
            self.content["raButton_key"][0] = 0 # 保证“圆形”按钮只有一个是默认选中状态
            self.content["raButton_key"][1] = 0
            self.content["raButton_key"][2] = 1
            self.ui.lineEdit.setText(self.content["api_key"][-2])

    # 设置页面“圆形”按钮处于非“无”时，输入文本框显示当前IP  功能
    def text_input_ip(self):
        if self.ui.radioButton_4.isChecked():
            self.ui.lineEdit_2.clear()
            self.ui.lineEdit_3.clear()
            self.content["raButton_ip"][0] = 1  # 保证“圆形”按钮只有一个是默认选中状态
            self.content["raButton_ip"][1] = 0
        if self.ui.radioButton_6.isChecked():
            self.ui.lineEdit_2.clear()
            self.ui.lineEdit_3.clear()
            self.content["raButton_ip"][0] = 0  # 保证“圆形”按钮只有一个是默认选中状态
            self.content["raButton_ip"][1] = 1
            self.ui.lineEdit_2.setText(self.content["ip"][-1][:self.content["ip"][-1].index(":")])
            self.ui.lineEdit_3.setText(self.content["ip"][-1][self.content["ip"][-1].index(":")+1:])

    # 主页面”改写“按钮 功能
    def PB_Rewrite(self):
        Rewrite_text = self.ui.textEdit.toPlainText()
        if Rewrite_text != "":
            self.ui.textEdit_2.setText("请稍后，正在进行改写……")
            reRewrite_text= "请对下面这段文字进行一定程度的改写，注意，只需给出改写后的内容。\n"+Rewrite_text
            self.ChatGPT = ChatGPT(self.ip,self.api_key, reRewrite_text)
            # 次线程任务结束后执行（）内的函数，并将该线程的结果传给该函数
            self.ChatGPT.finished.connect(self.on_rewritten)
            self.ChatGPT.get_response() # 次线程任务开始
        else:
            self.ui.textEdit_2.setText("请输入文本……")

        # 主页面”改写“按钮 功能

    # 主页面”进一步改写“按钮 功能
    def PB_Fu_Rewrite(self):
        Rewrite_text = self.ui.textEdit.toPlainText()
        if Rewrite_text != "":
            self.ui.textEdit_2.setText("请稍后，正在进行进一步的改写……")
            reRewrite_text = "在不改变原有语义的基础上，请对下面这段文字进行较大程度的改写，并对这段文字的名词进行适当的同义词替换。注意，只需给出改写后的内容。\n" + Rewrite_text
            self.ChatGPT = ChatGPT(self.ip,self.api_key, reRewrite_text)
            # 次线程任务结束后执行（）内的函数，并将该线程的结果传给该函数
            self.ChatGPT.finished.connect(self.on_rewritten)
            self.ChatGPT.get_response()  # 次线程任务开始
        else:
            self.ui.textEdit_2.setText("请输入文本……")

    # 主页面”扩写“按钮 功能
    def PB_Ex_Rewrite(self):
        Rewrite_text = self.ui.textEdit.toPlainText()
        if Rewrite_text != "":
            self.ui.textEdit_2.setText("请稍后，正在进行进扩写……")
            reRewrite_text = "在不改变原有语义的基础上，请对下面这段文字进行扩写。注意，只需给出改写后的内容。\n" + Rewrite_text
            self.ChatGPT = ChatGPT(self.ip,self.api_key, reRewrite_text)
            # 次线程任务结束后执行（）内的函数，并将该线程的结果传给该函数
            self.ChatGPT.finished.connect(self.on_rewritten)
            self.ChatGPT.get_response()  # 次线程任务开始
        else:
            self.ui.textEdit_2.setText("请输入文本……")

    # 主页面”缩写“按钮 功能
    def PB_Ab_Rewrite(self):
        Rewrite_text = self.ui.textEdit.toPlainText()
        if Rewrite_text != "":
            self.ui.textEdit_2.setText("请稍后，正在进行进缩写……")
            reRewrite_text = "在不改变原有语义的基础上，请对下面这段文字进行缩写。注意，只需给出改写后的内容。\n" + Rewrite_text
            self.ChatGPT = ChatGPT(self.ip,self.api_key, reRewrite_text)
            # 次线程任务结束后执行（）内的函数，并将该线程的结果传给该函数
            self.ChatGPT.finished.connect(self.on_rewritten)
            self.ChatGPT.get_response()  # 次线程任务开始
        else:
            self.ui.textEdit_2.setText("请输入文本……")

    # 主页面”语法检查“按钮 功能
    def PB_Gr_Rewrite(self):
        Rewrite_text = self.ui.textEdit.toPlainText()
        if Rewrite_text != "":
            self.ui.textEdit_2.setText("请稍后，正在进行进语法检查……")
            reRewrite_text = "请对下面这段文字进行语法检查和错别字检查，并给出修改意见和修改后的句子。\n" + Rewrite_text
            self.ChatGPT = ChatGPT(self.ip,self.api_key, reRewrite_text)
            # 次线程任务结束后执行（）内的函数，并将该线程的结果传给该函数
            self.ChatGPT.finished.connect(self.on_rewritten)
            self.ChatGPT.get_response()  # 次线程任务开始
        else:
            self.ui.textEdit_2.setText("请输入文本……")

    # 次线程任务结束后执行的函数，参数由次线程程序的结果直接附于
    def on_rewritten(self, rewritten_text):
        rewritten_text = re.sub(r"\s+", "", rewritten_text) # 去除空格
        self.ui.textEdit_2.setText(rewritten_text)

    # 主页面”清空“按钮 功能
    def PB_Rewrite_clear(self):
        self.ui.textEdit.clear()

    # 页面跳转功能
    def display_page1(self):
        self.ui.stackedWidget.setCurrentIndex(0)
    def display_page2(self):
        self.ui.stackedWidget.setCurrentIndex(1)

    def toggle_maximize(self):
        if self.isMaximized():
            self.showNormal()
        else:
            self.showMaximized()


    # 拖动
    def mousePressEvent(self, event):
        if event.button() == QtCore.Qt.LeftButton and self.isMaximized() == False:
            self.m_flag = True
            self.m_Position = event.globalPos() - self.pos()  # 获取鼠标相对窗口的位置
            event.accept()
            self.setCursor(QtGui.QCursor(QtCore.Qt.OpenHandCursor))  # 更改鼠标图标

    def mouseMoveEvent(self, mouse_event):
        if QtCore.Qt.LeftButton and self.m_flag:
            self.move(mouse_event.globalPos() - self.m_Position)  # 更改窗口位置
            mouse_event.accept()

    def mouseReleaseEvent(self, mouse_event):
        self.m_flag = False
        self.setCursor(QtGui.QCursor(QtCore.Qt.ArrowCursor))


if __name__ == '__main__':
    # 创建窗口实例
    app = QApplication(sys.argv)
    # 为main_window类和login_window类创建对象
    main_window = Dropped_window()
    # 关闭程序，释放资源
    sys.exit(app.exec_())