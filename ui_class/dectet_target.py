import os
import time
from datetime import datetime
from PyQt5.QtCore import QThread, pyqtSignal, Qt, QSize, QRect, QPoint
from PyQt5.QtWidgets import QWidget, QFileDialog, QListWidgetItem
from loguru import logger
from ddddocr import DdddOcr
from qfluentwidgets import StateToolTip
from qfluentwidgets import FluentIcon as FIF
from ruamel.yaml import YAML
from config import cfg
from ui import ui_dectet_target
from PyQt5.QtGui import QPixmap, QCursor, QPainter, QPen, QFont
from ui_tools.dectet.dddd_woker import dddd_dectet
from ui_tools.qt_tools.infobar import createWarningInfoBar, createSuccessInfoBar, createErrorInfoBar
from ui_tools.dectet.yolo import load_model, yolo_predict
from ui_tools.qt_tools.labelDialog import LabelDialog
from ui_tools.qt_tools.load_images_thread import Load_Images


class Predict_Auto_Thread(QThread):
    response = pyqtSignal(dict)

    def __init__(self):
        super().__init__()
        self.pic_path_list = None
        self.base_path = None
        self.model_type = None
        self.model = None
        self.main_save_path = None
        self.yolo_labels = []

    def run(self) -> None:

        for index, i in enumerate(self.pic_path_list):
            try:
                if self.model_type == 'dddd':
                    image_list, width, height = dddd_dectet(self.model, os.path.join(self.base_path, i))
                elif self.model_type == 'yolo_world' or self.model_type == 'yolo_self':
                    image_list = yolo_predict(self.model, os.path.join(self.base_path, i))

                else:
                    image_list = []

                if not image_list:
                    self.response.emit({'status': 'success', 'msg': '无Object_detection结果', 'index': index})
                    continue

                self.response.emit({
                    'status': 'success',
                    'image': image_list,
                    'index': index})
            except Exception as e:
                self.response.emit({'status': 'errors', 'msg': str(e), 'index': index})

        self.response.emit({'status': 'all_success'})


class Predict_Thread(QThread):
    response = pyqtSignal(dict)

    def __init__(self):
        super().__init__()
        self.pic_path = None
        self.model_type = None
        self.model = None

    def run(self) -> None:
        try:
            if self.model_type == 'dddd':
                image_list, width, height = dddd_dectet(self.model, self.pic_path)
            elif self.model_type == 'yolo_world' or self.model_type == 'yolo_self':
                image_list = yolo_predict(self.model, self.pic_path)
            else:
                image_list = []

            self.response.emit({'status': 'success', 'image': image_list})
        except Exception as e:
            self.response.emit({'status': 'errors', 'msg': str(e)})


class Load_Model(QThread):
    response = pyqtSignal(dict)

    def __init__(self):
        super().__init__()
        self.model_type = None
        self.model_path = None
        self.yolo_labels = None

    def run(self):
        try:
            if self.model_type == 'dddd':
                det = DdddOcr(det=True, show_ad=False)
            elif self.model_type == 'yolo_world':
                det = load_model('base', labels=self.yolo_labels)
            else:
                det = load_model(self.model_type, self.model_path)
            if det:
                self.response.emit({'status': 'success', 'model': det})
            else:
                self.response.emit({'status': 'errors', 'msg': '模型加载失败,请检查路径是否正确'})
        except Exception as e:
            self.response.emit({'status': 'errors', 'msg': str(e)})


class Target_Class(QWidget):

    def __init__(self, ui_class=ui_dectet_target.Ui_Form, parent=None):
        super().__init__(parent=parent)

        self.ui = ui_class()
        self.ui.setupUi(self)
        self.setObjectName('ui_target-Interface')

        self.arg_init()
        self.ui_init()
        self.btn_init()

    def arg_init(self):
        """
        参数初始化
        :return:
        """
        self.yaml = YAML()
        self.yaml_sign = False  # yaml文件是否保存过
        self.classes_len = 0  # 类别数量
        self.label_dialog = LabelDialog(parent=self, list_item=[])  # 类别标注框
        self.yolo_labels = []  # 保存yolo的类别
        self.last_label = ''  # 类别标注的最后一次值 (缓存记录)
        self.image_files_list = None  # 图片数据集列表
        self.datasets_base_path = None  # 存放图片的路径
        self.current_pic_index = None  # 当前选中的图片的索引
        self.start_sign = False  # 开始标注标志
        self.use_model = None  # 使用中的模型
        self.model_list = []  # 模型的列表
        self.rects = []  # 存储矩形的列表
        self.labels_for_images = {}  # 字典，存储每个图像的矩形标签
        self.selected_rect_index = None  # 当前选中的矩形的索引
        self.drawing = False  # 标注模式
        self.adjust_mode = False  # 调整模式
        self.start_point = QPoint()  # 开始标注的点
        self.current_rect = QRect()  # 当前选中的矩形
        self.rects_for_images = {}  # 字典，存储每个图像的矩形列表
        self.main_save_path = None
        self.original_size = self.size()
        self.scale_x = 0.8
        self.scale_y = 0.8
        self.scale_x_use = False
        self.scale_y_use = False
        self.yolo_self_path = None  # 自定义yolo
        self.yolo_label_path = None  # 自定义yolo标签
        self.t = time.strftime("%Y%m%d%H%M%S", time.localtime())  # 用于保存命名

    def ui_init(self):
        """
        ui组件初始化
        :return:
        """
        self.ui.image_flipview.currentIndexChanged.connect(self.update_path_list)

        self.ui.image_flipview.mousePressEvent = self.mouse_press
        self.ui.image_flipview.mouseReleaseEvent = self.mouse_release
        self.ui.image_flipview.mouseMoveEvent = self.mouse_move
        self.ui.image_flipview.keyPressEvent = self.keyPressEvent

        self.ui.draw_tbtn.setIcon(FIF.FIT_PAGE)
        self.ui.draw_tbtn.setToolTip('绘图模式')

        self.toggle_adjust_mode()

    def btn_init(self):
        """
        按钮绑定函数初始化
        :return:
        """
        self.ui.impor_dataset_btn.clicked.connect(self.import_datasets)
        self.ui.image_path_list.currentRowChanged.connect(self.show_images)

        self.ui.load_model_btn.clicked.connect(self.load_model)
        self.ui.start_predict_btn.clicked.connect(self.start_task)

        self.ui.auto_tbtn.clicked.connect(self.auto_tbtn_event)
        self.ui.half_auto_tbtn.clicked.connect(self.half_auto_tbtn_event)

        self.ui.draw_tbtn.clicked.connect(self.enable_drawing)

        self.ui.save_btn.clicked.connect(self.save_rects_to_yolo)
        self.ui.skip_btn.clicked.connect(self.next_pic)

        self.ui.import_model_btn.clicked.connect(lambda: self.import_self_yolo('yolo'))
        self.ui.yolo_label_btn.clicked.connect(lambda: self.import_self_yolo('label'))

    def toggle_adjust_mode(self):
        """
        调整模式
        :return:
        """
        self.adjust_mode = not self.adjust_mode
        if self.adjust_mode:
            self.drawing = False
            self.ui.draw_tbtn.setChecked(False)
            self.ui.image_flipview.setCursor(QCursor(Qt.CursorShape.ArrowCursor))
        else:
            self.ui.image_flipview.setCursor(QCursor(Qt.CursorShape.CrossCursor))

    def auto_tbtn_event(self):
        """
        全自动按钮事件
        :return:
        """
        self.ui.half_auto_tbtn.setChecked(False)
        self.ui.start_predict_btn.setChecked(False)
        self.ui.start_predict_btn.setText('开启识别')

    def half_auto_tbtn_event(self):
        """
        半自动按钮事件
        :return:
        """
        self.ui.auto_tbtn.setChecked(False)
        self.ui.start_predict_btn.setChecked(False)
        self.ui.start_predict_btn.setText('开启识别')

    def load_model(self):
        """
        加载模型
        :return:
        """

        def response(infos):
            if infos['status'] == 'errors':
                self.stateTooltip.setContent('模型加载失败 ┭┮﹏┭┮')
                createErrorInfoBar(self, infos['msg'])
            else:
                self.stateTooltip.setContent('模型加载成功 😆')
                self.use_model = infos['model']

            self.stateTooltip.setState(True)

        if self.ui.start_predict_btn.isChecked():
            createWarningInfoBar(self, '请先关闭识别')
            return

        if self.ui.myself_radio_btn.isChecked() and 'yolo_self' not in self.model_list:
            self.model_list.clear()
            self.model_list.append('yolo_self')
        elif self.ui.myself_radio_btn.isChecked() and 'yolo_self' in self.model_list:
            pass

        if self.ui.yolo_world_radio_btn.isChecked() and 'yolo_world' not in self.model_list:
            self.model_list.clear()
            self.model_list.append('yolo_world')
        elif self.ui.yolo_world_radio_btn.isChecked() and 'yolo_world' in self.model_list:
            createWarningInfoBar(self, '目前已经是yolo_world模型了')
            return

        if self.ui.dddd_radio_btn.isChecked() and 'dddd' not in self.model_list:
            self.model_list.clear()
            self.model_list.append('dddd')
        elif self.ui.dddd_radio_btn.isChecked() and 'dddd' in self.model_list:
            createWarningInfoBar(self, '目前已经是dddd模型了')
            return

        self.stateTooltip = StateToolTip('正在初始化加载模型', '客官请耐心等待哦~~', self)
        self.stateTooltip.move(0, 30)
        self.stateTooltip.show()

        self.load_model_thread = Load_Model()
        self.load_model_thread.model_type = self.model_list[0]
        self.load_model_thread.model_path = self.yolo_self_path
        self.load_model_thread.yolo_labels = self.yolo_labels
        self.load_model_thread.response.connect(response)
        self.load_model_thread.start()

    def update_path_list(self):
        """
        点击图片列表所触发的事件
        :return:
        """
        index = self.ui.image_flipview.currentIndex()
        self.ui.image_path_list.setCurrentRow(index)

    def import_datasets(self):
        """
        导入图片数据集
        :return:
        """
        def response(data):
            if data['type'] == 'add':
                item = QListWidgetItem(data['item'])
                self.ui.image_path_list.addItem(item)
                self.ui.image_flipview.addImage(os.path.join(self.datasets_base_path, data['item']))
            elif data['type'] == 'finish':
                self.image_files_list = data['image_files_list']
                self.ui.image_path_list.setCurrentRow(0)
                self.t = datetime.now().strftime('%Y%m%d%H%M%S')
                createSuccessInfoBar(self, '已导入图片数据')
            else:
                logger.error(data['msg'])
                createErrorInfoBar(self, '导入图片数据失败')

        folder_path = QFileDialog.getExistingDirectory(self, 'Select Folder',
                                                       f'{os.getcwd()}\image')
        if not folder_path:
            createWarningInfoBar(self, '请选择图片数据集')
            return
        self.ui.image_path_list.clear()
        self.datasets_base_path = folder_path

        self.load_image_taread = Load_Images()
        self.load_image_taread.folder_path = folder_path
        self.load_image_taread.response.connect(response)
        self.load_image_taread.start()

        # self.update_list_view()


    def import_self_yolo(self, types):
        """
        导入自定义yolo
        :return:
        """
        folder_path, t = QFileDialog.getOpenFileName(self, 'Select File')

        if not folder_path:
            createWarningInfoBar(self, '请选择正确的路径')
            return

        if types == 'yolo':
            self.yolo_self_path = folder_path
            createSuccessInfoBar(self, r'已导入yolo模型')
        else:
            with open(folder_path, 'r', encoding='utf8') as f:
                data = [i.strip() for i in f.readlines()]
            self.yolo_labels = data
            self.label_dialog = LabelDialog(parent=self, list_item=self.yolo_labels)
            createSuccessInfoBar(self, r'已导入yolo标签,需要重新加载yoloworld模型哦')



    def show_images(self):
        """
        展示图像
        :return:
        """
        self.current_pic_index = self.ui.image_path_list.currentIndex().row()
        if not self.image_files_list:
            return
        img_path = os.path.join(self.datasets_base_path, self.image_files_list[self.current_pic_index])
        self.current_pixmap = QPixmap(img_path)

        if self.current_pixmap.width() > 800:
            width = self.current_pixmap.width() * self.scale_x
            self.scale_x_use = True
        else:
            self.scale_x_use = False
            width = self.current_pixmap.width()
        if self.current_pixmap.height() > 700:
            height = self.current_pixmap.height() * self.scale_y
            self.scale_y_use = True
        else:
            self.scale_y_use = False
            height = self.current_pixmap.height()

        self.ui.image_flipview.setItemSize(QSize(int(width), int(height)))
        self.ui.image_flipview.setFixedSize(QSize(int(width), int(height)))

        # 清除并重新绘制与当前图像相关的矩形
        self.rects = []
        self.update_image()

        if self.ui.half_auto_tbtn.isChecked() and self.start_sign:
            self.ui.image_flipview.setCurrentIndex(self.current_pic_index)
            self.start_predict_task()
        else:
            self.ui.image_flipview.setCurrentIndex(self.current_pic_index)

    def start_task(self):
        """
        开启识别模式
        :return:
        """
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

    def start_predict_task(self):
        """
        开启半自动识别
        :return:
        """

        def response(infos):
            """
            线程回调函数
            :param infos:
            :return:
            """
            # logger.info(infos)
            if infos['status'] == 'errors':
                createErrorInfoBar(self, '图片识别失败')
                return
            elif infos['status'] == 'all_success':
                createSuccessInfoBar(self, '图片识别成功')
                return
            elif not infos['image']:
                createSuccessInfoBar(self, '图片识别成功,结果为空')
                return
            else:
                img_path = os.path.join(self.datasets_base_path, self.image_files_list[self.current_pic_index])
                if img_path not in self.rects_for_images:
                    self.rects_for_images[img_path] = []
                    self.labels_for_images[img_path] = []

                if self.model_list[0] == 'dddd':
                    for i in infos['image']:
                        x1, y1, x2, y2 = i
                        rect = QRect(x1, y1, x2 - x1, y2 - y1)
                        self.rects_for_images[img_path].append(rect)
                        self.rects.append({'label': 'object', 'rect': rect})
                        self.labels_for_images[img_path].append('object')

                        if 'object' not in self.yolo_labels:
                            self.yolo_labels.append('object')
                            self.label_dialog.add_item('object')

                    self.update_image()
                else:
                    for i in infos['image']:
                        x1, y1, x2, y2 = i['box']
                        rect = QRect(x1, y1, x2 - x1, y2 - y1)
                        self.rects_for_images[img_path].append(rect)
                        self.rects.append({'label': i['label'], 'rect': rect})
                        self.labels_for_images[img_path].append(i['label'])

                        if i['label'] not in self.yolo_labels:
                            self.yolo_labels.append(i['label'])
                            self.label_dialog.add_item(i['label'])

                    self.update_image()

        pic_path = os.path.join(self.datasets_base_path, self.image_files_list[self.current_pic_index])
        self.predict_thread = Predict_Thread()
        self.predict_thread.pic_path = pic_path
        self.predict_thread.model_type = self.model_list[0]
        self.predict_thread.model = self.use_model
        self.predict_thread.response.connect(response)
        self.predict_thread.start()

    def start_auto_predict_task(self):
        """
        开启全自动识别
        :return:
        """

        def response(infos):
            """
            线程回调函数
            :param infos:
            :return:
            """
            if infos['status'] == 'all_success':
                createSuccessInfoBar(self, '图片识别成功')
                return

            self.current_pic_index = infos['index']
            if infos['status'] == 'errors':
                createErrorInfoBar(self, '图片识别失败')
                self.ui.image_flipview.setCurrentIndex(self.current_pic_index)
                return

            if 'image' not in infos:
                createSuccessInfoBar(self, '图片识别成功,结果为空')
                self.ui.image_flipview.setCurrentIndex(self.current_pic_index)
                return
            else:
                self.ui.image_flipview.setCurrentIndex(self.current_pic_index)
                self.ui.image_flipview.setItemImage(self.current_pic_index, infos['image'])
                img_path = os.path.join(self.datasets_base_path, self.image_files_list[self.current_pic_index])
                if img_path not in self.rects_for_images:
                    self.rects_for_images[img_path] = []
                    self.labels_for_images[img_path] = []

                if self.model_list[0] == 'dddd':
                    for i in infos['image']:
                        x1, y1, x2, y2 = i
                        rect = QRect(x1, y1, x2 - x1, y2 - y1)
                        self.rects_for_images[img_path].append(rect)
                        self.rects.append({'label': 'object', 'rect': rect})
                        self.labels_for_images[img_path].append('object')

                        if 'object' not in self.yolo_labels:
                            self.yolo_labels.append('object')
                            self.label_dialog.add_item('object')

                    self.update_image()
                    self.save_rects_to_yolo()
                else:
                    for i in infos['image']:
                        x1, y1, x2, y2 = i['box']
                        rect = QRect(x1, y1, x2 - x1, y2 - y1)
                        self.rects_for_images[img_path].append(rect)
                        self.rects.append({'label': i['label'], 'rect': rect})
                        self.labels_for_images[img_path].append(i['label'])

                        if i['label'] not in self.yolo_labels:
                            self.yolo_labels.append(i['label'])
                            self.label_dialog.add_item(i['label'])

                    self.update_image()
                    self.save_rects_to_yolo()

        self.t = time.strftime("%Y%m%d%H%M%S", time.localtime())
        self.predict_thread = Predict_Auto_Thread()
        self.predict_thread.pic_path_list = self.image_files_list
        self.predict_thread.base_path = self.datasets_base_path
        self.predict_thread.model_type = self.model_list[0]
        self.predict_thread.model = self.use_model
        self.predict_thread.main_save_path = self.main_save_path
        self.predict_thread.yolo_labels = self.yolo_labels
        self.predict_thread.response.connect(response)
        self.predict_thread.start()

    def keyPressEvent(self, event):
        """
        键盘事件
        :param event:
        :return:
        """
        if (
                (event.key() == Qt.Key.Key_Escape or event.key() == Qt.Key.Key_Delete)
                and self.adjust_mode
                and self.selected_rect_index is not None
        ):
            img_path = os.path.join(self.datasets_base_path, self.image_files_list[self.current_pic_index])
            if img_path in self.rects_for_images:
                logger.info('删除成功')
                del self.rects_for_images[img_path][self.selected_rect_index]
                del self.labels_for_images[img_path][self.selected_rect_index]
                self.selected_rect_index = None
                self.update_image()

        elif event.key() == Qt.Key.Key_W:
            self.ui.draw_tbtn.setChecked(True)
            self.enable_drawing()

        elif event.key() == Qt.Key.Key_S:
            self.save_rects_to_yolo()

    def enable_drawing(self):
        """
        开启绘画模式
        :return:
        """
        self.drawing = self.ui.draw_tbtn.isChecked()
        if self.drawing:
            self.adjust_mode = False
            self.ui.image_flipview.setCursor(QCursor(Qt.CursorShape.CrossCursor))
        else:
            self.toggle_adjust_mode()
            self.ui.image_flipview.setCursor(QCursor(Qt.CursorShape.ArrowCursor))

    def update_image(self):
        """
        刷新图像
        :return:
        """
        if self.current_pic_index is not None:
            img_path = os.path.join(self.datasets_base_path, self.image_files_list[self.current_pic_index])
            current_pixmap = QPixmap(img_path)
            painter = QPainter(current_pixmap)
            painter.setPen(QPen(Qt.GlobalColor.red, 2, Qt.PenStyle.SolidLine))
            for index, rect in enumerate(self.rects_for_images.get(img_path, [])):

                if index == self.selected_rect_index:
                    logger.info('选中')
                    # 为选中的矩形使用虚线边框
                    painter.setPen(QPen(Qt.GlobalColor.darkMagenta, 3, Qt.PenStyle.DotLine))
                else:
                    # 为未选中的矩形使用实线边框
                    painter.setPen(QPen(Qt.GlobalColor.red, 3, Qt.PenStyle.SolidLine))
                painter.drawRect(rect)
                if self.labels_for_images.get(img_path):
                    # 绘制文本
                    painter.setPen(QPen(Qt.GlobalColor.red))  # 设置文本颜色为蓝色
                    painter.setFont(QFont("Arial", 15))  # 设置字体和字号
                    if rect.y() - 5 < 10:
                        y = rect.y() + 15
                    else:
                        y = rect.y() - 5
                    painter.drawText(rect.x(), y, self.labels_for_images.get(img_path)[index])

            if self.current_rect is not None and not self.current_rect.isNull():
                painter.setPen(QPen(Qt.GlobalColor.blue, 3, Qt.PenStyle.DotLine))
                painter.drawRect(self.current_rect)
            painter.end()
            self.ui.image_flipview.setItemImage(self.current_pic_index, current_pixmap)

    def get_rect_at_position(self, position):
        """
        获取当前图片所绘制矩形的索引
        :param position:
        :return:
        """
        if not self.image_files_list:
            return None
        img_path = os.path.join(self.datasets_base_path, self.image_files_list[self.current_pic_index])
        for index, rect in enumerate(self.rects_for_images.get(img_path, [])):
            if rect.contains(position):
                return index
        return None

    def mouse_press(self, event):
        """
        鼠标按下事件
        :param event:
        :return:
        """
        self.setFocus()
        if self.drawing and event.button() == Qt.MouseButton.LeftButton:
            # 转换坐标
            global_point = event.globalPos()
            local_pos = self.ui.image_flipview.mapFromGlobal(global_point)
            # 根据缩放比例调整坐标
            adjusted_x, adjusted_y = self.gen_point(local_pos)
            adjusted_pos = QPoint(int(adjusted_x), int(adjusted_y))

            self.start_point = adjusted_pos
            self.current_rect = QRect(self.start_point, QSize())

        if self.adjust_mode and event.button() == Qt.MouseButton.LeftButton:
            global_point = event.globalPos()
            local_pos = self.ui.image_flipview.mapFromGlobal(global_point)
            adjusted_x, adjusted_y = self.gen_point(local_pos)
            adjusted_pos = QPoint(int(adjusted_x), int(adjusted_y))

            self.selected_rect_index = self.get_rect_at_position(adjusted_pos)
            if self.selected_rect_index is not None:
                self.update_image()

    def mouse_move(self, event):
        """
        鼠标移动事件
        :param event:
        :return:
        """
        if self.drawing and event.buttons() & Qt.MouseButton.LeftButton:
            global_point = event.globalPos()
            local_pos = self.ui.image_flipview.mapFromGlobal(global_point)
            adjusted_x, adjusted_y = self.gen_point(local_pos)
            if self.ui.image_flipview.width() > 1000:
                adjusted_x = adjusted_x - 4
                adjusted_y = adjusted_y - 4
            adjusted_pos = QPoint(int(adjusted_x), int(adjusted_y))
            self.current_rect.setBottomRight(adjusted_pos)
            self.update_image()

    def mouse_release(self, event):
        """
        鼠标左键释放事件
        :param event:
        :return:
        """
        if self.drawing and event.button() == Qt.MouseButton.LeftButton:
            global_point = event.globalPos()
            local_pos = self.ui.image_flipview.mapFromGlobal(global_point)
            adjusted_x, adjusted_y = self.gen_point(local_pos)
            adjusted_pos = QPoint(int(adjusted_x), int(adjusted_y))
            self.current_rect.setBottomRight(adjusted_pos)

            text = self.label_dialog.pop_up(self.last_label)
            if text and text not in self.yolo_labels:
                self.yolo_labels.append(text)
                self.label_dialog.add_item(text)
            elif text is None or text == '':
                self.current_rect = None
                self.update_image()
                return

            self.last_label = text
            self.rects.append({'label': text, 'rect': self.current_rect})
            img_path = os.path.join(self.datasets_base_path, self.image_files_list[self.current_pic_index])

            if img_path not in self.rects_for_images:
                self.rects_for_images[img_path] = []
                self.labels_for_images[img_path] = []

            self.rects_for_images[img_path].append(self.current_rect)
            self.labels_for_images[img_path].append(text)
            self.current_rect = QRect()
            self.update_image()
            self.ui.draw_tbtn.setChecked(False)
            self.enable_drawing()

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

    def convert_rect_to_yolo(self, rect_info, img_width, img_height):
        """
        将 QRect 转换为 YOLO 格式的坐标
        """
        rect = rect_info.get('rect')
        label = rect_info.get('label')
        x_center = (rect.left() + rect.right()) / 2 / img_width
        y_center = (rect.top() + rect.bottom()) / 2 / img_height
        width = rect.width() / img_width
        height = rect.height() / img_height
        return label, x_center, y_center, width, height

    def save_rects_to_yolo(self):
        """
        按下保存按钮将矩形坐标保存到 YOLO 格式的 .txt 文件
        :return:
        """
        self.main_save_path = cfg.get(cfg.pic_label_save_Folder)

        if self.current_pic_index is not None:
            img_path = os.path.join(self.datasets_base_path, self.image_files_list[self.current_pic_index])
            img = QPixmap(img_path)
            img_width = img.width()
            img_height = img.height()

            yolo_rects = [self.convert_rect_to_yolo(rect, img_width, img_height) for rect in self.rects]

            save_base_path = self.image_files_list[self.current_pic_index].split('.')[0] + ".txt"

            dataset_path = os.path.join(self.main_save_path, f'detect_dataset_{self.t}')
            if not os.path.exists(dataset_path):
                os.mkdir(dataset_path)

            labels_path = os.path.join(dataset_path, f'labels')
            if not os.path.exists(labels_path):
                os.mkdir(labels_path)

            save_path = os.path.join(labels_path, save_base_path)

            with open(save_path, "w") as file:
                for rect in yolo_rects:
                    index = self.yolo_labels.index(rect[0])
                    file.write(f"{index} {rect[1]} {rect[2]} {rect[3]} {rect[4]}\n")

            if not self.yaml_sign:
                self.classes_len = len(self.yolo_labels)
                with open(f'{dataset_path}/data.yaml', "w", encoding='utf-8') as label_file:
                    self.yaml.dump({'nc': len(self.yolo_labels), 'names': self.yolo_labels}, label_file)
                self.yaml_sign = True
            else:
                if self.classes_len != len(self.yolo_labels):
                    self.classes_len = len(self.yolo_labels)
                    with open(f'{dataset_path}/data.yaml', "w", encoding='utf-8') as label_file:
                        self.yaml.dump({'nc': len(self.yolo_labels), 'names': self.yolo_labels}, label_file)

            createSuccessInfoBar(self, f"矩形坐标已保存到 {save_path}")
            if self.current_pic_index == len(self.image_files_list) - 1:
                createSuccessInfoBar(self, '图片已经遍历一轮')
            else:
                self.next_pic()

    def next_pic(self):
        self.ui.image_path_list.setCurrentRow(self.ui.image_path_list.currentIndex().row() + 1)

    def resizeEvent(self, event):
        # 获取新的窗口尺寸
        new_size = event.size()

        # 计算缩放比例
        x = new_size.width() / self.original_size.width()
        y = new_size.height() / self.original_size.height()
        print(f"窗口缩放比例：{x}, {y}")
        if x > 1.1 and y > 1.1:
            self.scale_x = round(x, 1)
            self.scale_y = round(y, 1)

            self.show_images()
            # 更新原始尺寸（可选）
            self.original_size = new_size

        if x < 0.8 and y < 0.8:
            self.scale_x = self.scale_y = 0.8

            self.show_images()
            # 更新原始尺寸（可选）
            self.original_size = new_size

        # 调用基类的 resizeEvent 处理
        super().resizeEvent(event)
