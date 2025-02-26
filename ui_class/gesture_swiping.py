import json
import os
from datetime import datetime
from PyQt5.QtCore import Qt, QPoint
from PyQt5.QtWidgets import QWidget, QFileDialog, QListWidgetItem
from loguru import logger
from qfluentwidgets import FluentIcon as FIF, ColorDialog
from qfluentwidgets import StateToolTip
from config import cfg
from ui import ui_swiping
from PyQt5.QtGui import QPixmap, QPainter, QPen, QCursor, QColor, QBrush

from ui_tools.qt_tools.infobar import createWarningInfoBar, createSuccessInfoBar, createErrorInfoBar
from ui_tools.qt_tools.load_images_thread import Load_Images


class Swiping_Class(QWidget):

    def __init__(self, ui_class=ui_swiping.Ui_Form, parent=None):
        super().__init__(parent=parent)

        self.ui = ui_class()
        self.ui.setupUi(self)
        self.setObjectName('Swiping_Class')

        self.arg_init()
        self.ui_init()
        self.btn_init()

    def arg_init(self):

        self.image_files_list = None  # 图片数据集列表
        self.datasets_base_path = None  # 存放图片的路径
        self.current_pic_index = None  # 当前选中的图片的索引
        self.current_image_path = None  # 当前选中的图片名
        self.start_sign = False  # 开始识别标志
        self.use_model = None  # 使用中的模型
        self.model_list = []  # 模型的列表
        self.main_save_path = None # 保存的路径
        # 新增绘图变量
        self.pen_color = QColor("#b2ff0d66")
        self.pen_color.setAlphaF(0.5)
        self.drawing = False  # 是否正在绘制
        self.lastPoint = QPoint()  # 上一点的位置
        self.currentPoint = QPoint()  # 当前点的位置
        self.trace_points = []  # 存储轨迹点坐标
        self.imageDrawings = {}  # key为图片路径，value为绘制点的列表
        self.selectedLineIndex = None  # 选中的轨迹线索引

        self.scale_x = 0.8
        self.scale_y = 0.8
        self.scale_x_use = False
        self.scale_y_use = False

    def ui_init(self):
        self.ui.image_path_list.keyPressEvent = self.keyReleaseEvent
        self.ui.draw_tbtn.setIcon(FIF.EDIT)
        self.ui.draw_tbtn.setToolTip('绘图模式')
        self.ui.color_chosse_btn.setIcon(FIF.PALETTE)
        self.ui.color_chosse_btn.setToolTip('画笔颜色')

    def btn_init(self):
        self.ui.impor_dataset_btn.clicked.connect(self.import_datasets)
        self.ui.image_path_list.currentRowChanged.connect(self.show_images)

        self.ui.load_model_btn.clicked.connect(self.load_model)
        self.ui.start_predict_btn.clicked.connect(self.start_task)

        self.ui.auto_tbtn.clicked.connect(self.auto_tbtn_event)
        self.ui.half_auto_tbtn.clicked.connect(self.half_auto_tbtn_event)
        self.ui.save_btn.clicked.connect(self.save_text_img)
        self.ui.skip_btn.clicked.connect(self.next_pic)

        self.ui.draw_tbtn.clicked.connect(self.enable_drawing)
        self.ui.color_chosse_btn.clicked.connect(self.showColorDialog)

    def setCircleCursor(self):
        # 创建一个透明的QPixmap，大小为32x32
        pixmap = QPixmap(16, 16)
        pixmap.fill(Qt.transparent)

        # 创建一个QPainter来绘制圆形
        painter = QPainter(pixmap)
        # painter.setRenderHint(QPainter.Antialiasing)  # 启用抗锯齿
        painter.setPen(Qt.NoPen)  # 不需要外边框
        painter.setBrush(QBrush(self.pen_color))  # 设置填充颜色，可以根据需要修改
        painter.drawEllipse(0, 0, 16, 16)  # 绘制圆形
        painter.end()

        # 创建一个QCursor对象
        self.drawing_cursor = QCursor(pixmap)

    def showColorDialog(self):
        def __onCustomColorChanged(color):
            self.pen_color = color

        def accept_response():
            w.close()
            self.ui.color_chosse_btn.setChecked(False)
            self.setFocus()

        w = ColorDialog(QColor("#50e42581"), 'Choose color', self, True)
        w.colorChanged.connect(__onCustomColorChanged)
        w.accepted.connect(accept_response)
        w.show()

    def auto_tbtn_event(self):
        self.ui.half_auto_tbtn.setChecked(False)
        self.ui.start_predict_btn.setChecked(True)
        self.ui.start_predict_btn.setText('开启识别')

    def half_auto_tbtn_event(self):
        self.ui.auto_tbtn.setChecked(False)
        self.ui.start_predict_btn.setChecked(False)
        self.ui.start_predict_btn.setText('开启识别')

    def load_model(self):

        def response(infos):
            if infos['status'] == 'errors':
                self.stateTooltip.setContent('模型加载失败 ┭┮﹏┭┮')
                createErrorInfoBar(self, infos['msg'])
            else:
                self.stateTooltip.setContent('模型加载成功 😆')
                self.use_model = infos['model']

            self.stateTooltip.setState(True)

        createWarningInfoBar(self, '暂无可用模型')
        return
        if self.ui.start_predict_btn.isChecked():
            createWarningInfoBar(self, '请先关闭识别')
            return

        if self.ui.panddle_radio_btn.isChecked() and 'paddle' not in self.model_list:
            self.model_list.clear()
            self.model_list.append('paddle')
        elif self.ui.panddle_radio_btn.isChecked() and 'paddle' in self.model_list:
            createWarningInfoBar(self, '目前已经是paddle模型了')
            return

        self.stateTooltip = StateToolTip('正在初始化加载模型', '客官请耐心等待哦~~', self)
        self.stateTooltip.move(0, 30)
        self.stateTooltip.show()

        self.load_model_thread = Load_Model()
        self.load_model_thread.model_type = self.model_list[0]
        self.load_model_thread.response.connect(response)
        self.load_model_thread.start()

    def import_datasets(self):
        def response(data):
            if data['type'] == 'add':
                item = QListWidgetItem(data['item'])
                self.ui.image_path_list.addItem(item)
            elif data['type'] == 'finish':
                self.image_files_list = data['image_files_list']
                pixmap = QPixmap(os.path.join(self.datasets_base_path, self.image_files_list[0]))
                scaled_pixmap = pixmap.scaled(595, 529, Qt.AspectRatioMode.KeepAspectRatio)
                self.ui.PixmapLabel.setPixmap(scaled_pixmap)
                self.ui.image_path_list.setCurrentRow(0)

                self.t = datetime.now().strftime('%Y%m%d%H%M%S')
                createSuccessInfoBar(self, '已导入图片数据')
            else:
                logger.error(data['msg'])
                createErrorInfoBar(self, '导入图片数据失败')

        folder_path = QFileDialog.getExistingDirectory(self, 'Select Folder',
                                                       f'{os.getcwd()}\image')
        if not folder_path:
            createWarningInfoBar(self, '请选择文件保存路径')
            return
        self.ui.image_path_list.clear()
        self.datasets_base_path = folder_path

        self.load_image_taread = Load_Images()
        self.load_image_taread.folder_path = folder_path
        self.load_image_taread.response.connect(response)
        self.load_image_taread.start()

    def update_list_view(self):
        self.ui.image_path_list.clear()
        for stand in self.image_files_list:
            item = QListWidgetItem(stand)
            self.ui.image_path_list.addItem(item)

        pixmap = QPixmap(os.path.join(self.datasets_base_path, self.image_files_list[0]))
        scaled_pixmap = pixmap.scaled(595, 529, Qt.AspectRatioMode.KeepAspectRatio)
        self.ui.PixmapLabel.setPixmap(scaled_pixmap)
        self.ui.image_path_list.setCurrentRow(0)

        self.t = datetime.now().strftime('%Y%m%d%H%M%S')

    def show_images(self):
        self.current_pic_index = self.ui.image_path_list.currentIndex().row()
        self.current_image_path = self.image_files_list[self.current_pic_index]
        img_path = os.path.join(self.datasets_base_path, self.current_image_path)
        current_pixmap = QPixmap(img_path)
        self.imagePixmap = current_pixmap.scaled(595, 529, Qt.AspectRatioMode.KeepAspectRatio)
        self.ui.PixmapLabel.setPixmap(self.imagePixmap)

        # 检查并重绘之前的轨迹
        if self.current_image_path in self.imageDrawings:

            painter = QPainter(self.imagePixmap)
            painter.setPen(QPen(self.pen_color, 8, Qt.SolidLine))
            current_trace_points = self.imageDrawings[self.current_image_path]
            for point_pair_coup in current_trace_points:

                for index, point_pair in enumerate(point_pair_coup):
                    if index + 1 == len(point_pair_coup):
                        break
                    painter.drawLine(point_pair[0], point_pair[1], point_pair_coup[index + 1][0],
                                     point_pair_coup[index + 1][1])

        if self.ui.half_auto_tbtn.isChecked() and self.start_sign:
            self.start_predict_task()

    def start_task(self):
        if self.current_pic_index == None:
            createWarningInfoBar(self, '请先导入数据')
            self.ui.start_predict_btn.setChecked(False)
            return

        if self.use_model == None:
            createWarningInfoBar(self, '请先加载模型')
            self.ui.start_predict_btn.setChecked(False)
            return

        if self.ui.auto_tbtn.isChecked():
            self.start_auto_predict_task()
            self.ui.start_predict_btn.setChecked(True)
        elif self.ui.half_auto_tbtn.isChecked() and self.ui.start_predict_btn.isChecked():
            self.start_sign = True
            self.start_predict_task()
        elif not self.ui.auto_tbtn.isChecked() and not self.ui.half_auto_tbtn.isChecked():
            createWarningInfoBar(self, '请选择识别模式')
            self.ui.start_predict_btn.setChecked(False)
            return

        if self.ui.start_predict_btn.isChecked() and not self.ui.auto_tbtn.isChecked():
            self.ui.start_predict_btn.setText('关闭识别')
        else:
            self.ui.start_predict_btn.setText('开启识别')
            self.start_sign = False

    def save_text_img(self):
        """
        把标签结合到图片命名中保存
        """
        self.main_save_path = cfg.get(cfg.pic_label_save_Folder)

        if self.current_pic_index is not None:

            save_path = os.path.join(self.main_save_path, self.current_image_path.split('.')[0] + '.json')
            save_infos = self.imageDrawings[self.current_image_path]
            with open(save_path, 'a', encoding='utf8') as f:
                for i in save_infos:
                    for ii in i:
                        ii[0] = ii[0] * 0.46
                        ii[1] = ii[1] * 0.46
                json.dump({'points': save_infos}, f)

            createSuccessInfoBar(self, f"手势滑动轨迹已保存到 {save_path}")
            if self.current_pic_index == len(self.image_files_list) - 1:
                createSuccessInfoBar(self, '图片已经遍历一轮')
            else:
                self.next_pic()

    def enable_drawing(self):
        """
        开启绘画模式
        :return:
        """
        self.drawing = self.ui.draw_tbtn.isChecked()
        self.setFocus()
        if self.drawing:
            self.setCircleCursor()
            self.ui.PixmapLabel.setCursor(self.drawing_cursor)
        else:
            self.ui.PixmapLabel.setCursor(QCursor(Qt.CursorShape.ArrowCursor))

    def next_pic(self):
        self.ui.image_path_list.setCurrentRow(self.ui.image_path_list.currentIndex().row() + 1)

    def mousePressEvent(self, event):
        self.setFocus()
        if self.drawing and event.button() == Qt.LeftButton:
            global_point = event.globalPos()
            self.trace_points = []
            # 转换坐标
            self.lastPoint = self.convertToImageCoordinates(global_point)

    def mouseMoveEvent(self, event):
        if (event.buttons() & Qt.LeftButton) and self.drawing:
            global_point = event.globalPos()
            # 转换坐标
            self.currentPoint = self.convertToImageCoordinates(global_point)
            self.trace_points.append([self.currentPoint.x(), self.currentPoint.y()])
            self.drawOnPixmap()

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.LeftButton and self.drawing:
            global_point = event.globalPos()
            self.drawing = False
            self.ui.draw_tbtn.click()
            release_pos = self.convertToImageCoordinates(global_point)
            self.trace_points.append([release_pos.x(), release_pos.y()])
            if self.current_image_path not in self.imageDrawings:
                self.imageDrawings[self.current_image_path] = []
            self.imageDrawings[self.current_image_path].append(self.trace_points)
            logger.info(f'已绘制轨迹: {self.trace_points}')
            self.drawOnPixmap()

    def convertToImageCoordinates(self, global_point):

        local_pos = self.ui.PixmapLabel.mapFromGlobal(global_point)
        # 根据缩放比例调整坐标
        adjusted_x, adjusted_y = self.gen_point(local_pos)
        adjusted_pos = QPoint(int(adjusted_x), int(adjusted_y))
        return adjusted_pos

    def drawOnPixmap(self):
        """在QPixmap上绘制轨迹线条"""
        if not self.imagePixmap.isNull() and self.drawing:
            painter = QPainter(self.imagePixmap)
            painter.setPen(QPen(self.pen_color, 8, Qt.SolidLine))
            if self.lastPoint and self.currentPoint:
                painter.drawLine(self.lastPoint, self.currentPoint)
            self.lastPoint = self.currentPoint

            # 立即更新QLabel显示
            self.ui.PixmapLabel.setPixmap(self.imagePixmap.scaled(self.ui.PixmapLabel.size(), Qt.KeepAspectRatio))

    def gen_point(self, local_pos):
        if self.scale_x_use:
            adjusted_x = local_pos.x() / self.scale_x
        else:
            adjusted_x = local_pos.x()

        if self.scale_y_use:
            adjusted_y = local_pos.y() / self.scale_y
        else:
            adjusted_y = local_pos.y()
        return adjusted_x, adjusted_y

    def keyPressEvent(self, event):
        """
        键盘事件
        :param event:
        :return:
        """
        if event.key() == Qt.Key.Key_S:
            self.save_text_img()
        elif event.key() == Qt.Key.Key_W:
            self.drawing = True
            self.ui.draw_tbtn.click()
        elif event.key() == Qt.Key_Delete:
            del self.imageDrawings[self.current_image_path]
            self.show_images()
