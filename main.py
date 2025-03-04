# coding:utf-8
import os.path
import sys
from PyQt5.QtCore import Qt, QTranslator
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QApplication
from qfluentwidgets import (NavigationItemPosition, MessageBox, MSFluentWindow, setTheme, Theme, FluentTranslator)
from qfluentwidgets import FluentIcon as FIF
from config import cfg
from ui import ui_dectet_target,ui_classification,ui_saimese_twin,ui_swiping
from ui_class import dectet_target,object_classification,siamese_twins,setting_interface,gesture_swiping
# from ultralytics import YOLO, YOLOWorld
# import open_clip
# import torch
# import ruamel.yaml
# import shutil


class Window(MSFluentWindow):

    def __init__(self):
        super().__init__()

        self.setting_ui = setting_interface.SettingInterface(self)

        # create sub interface
        self.homeInterface = dectet_target.Target_Class(ui_dectet_target.Ui_Form, self)
        self.classification = object_classification.Target_Class(ui_classification.Ui_Form, self)
        self.siamese_twins = siamese_twins.Target_Class(ui_saimese_twin.Ui_Form, self)
        self.gesture_swiping = gesture_swiping.Swiping_Class(ui_swiping.Ui_Form, self)

        self.initNavigation()
        self.initWindow()

    def initNavigation(self):
        self.addSubInterface(self.homeInterface, FIF.HOME, '目标检测', FIF.HOME_FILL)
        self.addSubInterface(self.classification, FIF.ROBOT, '物体分类')
        self.addSubInterface(self.siamese_twins, FIF.PEOPLE, '孪生标注')
        self.addSubInterface(self.gesture_swiping, FIF.PENCIL_INK, '手势滑动')
        self.addSubInterface(self.setting_ui, FIF.SETTING, '设置',position=NavigationItemPosition.BOTTOM)

        self.navigationInterface.addItem(
            routeKey='Help',
            icon=FIF.HELP,
            text='帮助',
            onClick=self.showMessageBox,
            selectable=False,
            position=NavigationItemPosition.BOTTOM,
        )

        self.navigationInterface.setCurrentItem(self.homeInterface.objectName())

    def initWindow(self):
        self.resize(1100, 950)
        self.setWindowIcon(QIcon('bitbug_favicon.ico'))
        self.setWindowTitle('Neverland-Trainer')

        # 获取主屏幕
        primary_screen = app.primaryScreen()

        # 获取屏幕尺寸
        screen_geometry = primary_screen.geometry()
        screen_width = screen_geometry.width()
        screen_height = screen_geometry.height()

        # 计算窗口的中心点
        window_width = self.width()
        window_height = self.height()
        center_x = (screen_width - window_width) // 2
        center_y = (screen_height - window_height) // 2

        # 移动窗口到屏幕中心
        self.move(center_x, center_y)

    def showMessageBox(self):
        w = MessageBox(
            '支持作者🥰',
            '个人开发不易，如果这个项目帮助到了您，可以考虑请作者喝一瓶快乐水🥤。您的支持就是作者开发和维护项目的动力🚀\n由于借助了多个深度学习模型 代码整体偏重，可自行做调整二开\nwx: xu970821582 我是小菜鸡 人够可考虑拉群交流 方向 (偏web3 ai)',
            self
        )
        w.yesButton.setText('来啦老弟')
        w.cancelButton.setText('下次一定')
        w.show()



if __name__ == '__main__':
    if cfg.get(cfg.dpiScale) == "Auto":
        QApplication.setHighDpiScaleFactorRoundingPolicy(
            Qt.HighDpiScaleFactorRoundingPolicy.PassThrough)
        QApplication.setAttribute(Qt.AA_EnableHighDpiScaling)
    else:
        os.environ["QT_ENABLE_HIGHDPI_SCALING"] = "0"
        os.environ["QT_SCALE_FACTOR"] = str(cfg.get(cfg.dpiScale))

    QApplication.setHighDpiScaleFactorRoundingPolicy(Qt.HighDpiScaleFactorRoundingPolicy.PassThrough)
    QApplication.setAttribute(Qt.AA_EnableHighDpiScaling)
    QApplication.setAttribute(Qt.AA_UseHighDpiPixmaps)
    # 切换主题
    setTheme(Theme.DARK)

    app = QApplication(sys.argv)
    app.setAttribute(Qt.AA_DontCreateNativeWidgetSiblings)\

    # internationalization
    locale = cfg.get(cfg.language).value
    fluentTranslator = FluentTranslator(locale)
    settingTranslator = QTranslator()
    settingTranslator.load(locale, "settings", ".", "resource/i18n")

    app.installTranslator(fluentTranslator)
    app.installTranslator(settingTranslator)

    w = Window()
    w.show()
    app.exec()
