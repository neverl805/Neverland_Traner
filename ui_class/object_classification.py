import os
import shutil
from datetime import datetime

from PyQt5 import QtWidgets, QtCore
from PyQt5.QtCore import QThread, pyqtSignal, Qt
from PyQt5.QtWidgets import QWidget, QFileDialog, QListWidgetItem
from loguru import logger
from paddleocr import PaddleOCR
from qfluentwidgets import StateToolTip, MessageBox, SubtitleLabel, LineEdit, PrimaryPushButton, Flyout, FlyoutView
from config import cfg
from ui import ui_classification
from PyQt5.QtGui import QPixmap

from ui_tools.classification.clip_predict import load_clip_model, clip_predict
from ui_tools.classification.paddle_onnx import WordOcr
from ui_tools.classification.yolo_cls import load_model, yolo_predict
from ui_tools.qt_tools.infobar import createWarningInfoBar, createSuccessInfoBar, createErrorInfoBar
from ui_tools.classification.panddleocr import paddle_ocr_det_text
from ui_tools.qt_tools.load_images_thread import Load_Images


class Predict_Auto_Thread(QThread):
    response = pyqtSignal(dict)

    def __init__(self):
        super().__init__()
        self.pic_path_list = None
        self.base_path = None
        self.model_type = None
        self.clip_labels = None
        self.model = None

    def run(self) -> None:

        for index, i in enumerate(self.pic_path_list):
            try:
                if self.model_type == 'clip':
                    model, tokenizer, preprocess = self.model
                    result = clip_predict(os.path.join(self.base_path, i), self.clip_labels, model, tokenizer,
                                          preprocess)
                elif self.model_type == 'paddle':
                    result = paddle_ocr_det_text(self.model, os.path.join(self.base_path, i))
                elif self.model_type == 'yolo_cls':
                    result = yolo_predict(self.model, os.path.join(self.base_path, i))
                elif self.model_type == 'paddle_onnx':
                    result = self.model.predict_ocr(os.path.join(self.base_path, i))

                if not result:
                    self.response.emit({'status': 'success', 'msg': '无识别结果', 'index': index})
                    continue

                self.response.emit({
                    'status': 'success',
                    'image': result,
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
        self.clip_labels = None
        self.model = None

    def run(self) -> None:
        try:
            if self.model_type == 'clip':
                model, tokenizer, preprocess = self.model
                result = clip_predict(self.pic_path, self.clip_labels, model, tokenizer, preprocess)
            elif self.model_type == 'paddle':
                result = paddle_ocr_det_text(self.model, self.pic_path)
            elif self.model_type == 'yolo_cls':
                result = yolo_predict(self.model, self.pic_path)
            elif self.model_type == 'paddle_onnx':
                result = self.model.predict_ocr(self.pic_path)

            self.response.emit({'status': 'success', 'image': result})
        except Exception as e:
            self.response.emit({'status': 'errors', 'msg': str(e)})


class Load_Model(QThread):
    response = pyqtSignal(dict)

    def __init__(self):
        super().__init__()
        self.model_type = None
        self.model_path = None
        self.word_path = None
        self.onnx_params = None

    def run(self):
        try:
            path = cfg.get(cfg.model_downloadFolder)
            if not path:
                path = os.path.join(os.path.dirname(__file__), 'model')

            if self.model_type == 'clip':
                det = load_clip_model(path)
            elif self.model_type == 'paddle':
                det = PaddleOCR(lang="ch",
                                use_angle_cls=False,
                                det_model_dir=f"{path}\paddle\det\ch\ch_PP-OCRv4_det_infer",
                                cls_model_dir=f"{path}\paddle\cls\ch\ch_PP-OCRv4_cls_infer",
                                rec_model_dir=f"{path}\paddle\\rec\ch\ch_PP-OCRv4_rec_infer"
                                )
            elif self.model_type == 'yolo_cls':
                det = load_model(self.model_path)
            elif self.model_type == 'paddle_onnx':
                det = WordOcr(self.model_path,self.word_path,self.onnx_params)

            self.response.emit({'status': 'success', 'model': det})
        except Exception as e:
            self.response.emit({'status': 'errors', 'msg': str(e)})




class Target_Class(QWidget):

    def __init__(self, ui_class=ui_classification.Ui_Form, parent=None):
        super().__init__(parent=parent)

        self.ui = ui_class()
        self.ui.setupUi(self)
        self.setObjectName('classification')

        self.arg_init()
        self.ui_init()
        self.btn_init()

    def arg_init(self):
        self.image_files_list = None  # 图片数据集列表
        self.datasets_base_path = None  # 存放图片的路径
        self.current_pic_index = None  # 当前选中的图片的索引
        self.clip_label_path = None  # clip标签路径
        self.paddle_label_path = None  # paddle标签路径
        self.yolo_cls_path = None  # yolo-cls模型路径
        self.paddle_onnx_path = None  # paddle onnx 模型路径
        self.start_sign = False  # 开始识别标志
        self.use_model = None  # 使用中的模型
        self.model_list = []  # 模型的列表
        self.onnx_parmas = [3,640,640]
        self.main_save_path = None  # 保存的路径

    def onnx_arguments_init(self,flyou):
        try:
            c = int(self.LineEdit.text().strip())
        except:
            c = 3

        try:
            h = int(self.LineEdit_2.text().strip())
        except:
            h = 640

        try:
            w = int(self.LineEdit_3.text().strip())
        except:
            w = 640

        self.onnx_parmas = [c, h, w]
        flyou.close()

    def onnx_dialog(self):
        self.onnx_view = FlyoutView(
            title='onnx模型输入调整',
            content="请根据模型训练时输入图片的尺寸调整以下参数",
            isClosable=True
        )
        self.layoutWidget = QtWidgets.QWidget(self.onnx_view)
        self.layoutWidget.setGeometry(QtCore.QRect(20, 140, 221, 35))
        self.layoutWidget.setObjectName("layoutWidget")
        self.horizontalLayout_2 = QtWidgets.QHBoxLayout(self.layoutWidget)
        self.horizontalLayout_2.setContentsMargins(0, 0, 0, 0)
        self.horizontalLayout_2.setObjectName("horizontalLayout_2")
        self.SubtitleLabel_2 = SubtitleLabel(self.layoutWidget)
        self.SubtitleLabel_2.setObjectName("SubtitleLabel_2")
        self.horizontalLayout_2.addWidget(self.SubtitleLabel_2)
        self.LineEdit_2 = LineEdit(self.layoutWidget)
        self.LineEdit_2.setObjectName("LineEdit_2")
        self.horizontalLayout_2.addWidget(self.LineEdit_2)
        self.layoutWidget_2 = QtWidgets.QWidget(self.onnx_view)
        self.layoutWidget_2.setGeometry(QtCore.QRect(20, 190, 221, 35))
        self.layoutWidget_2.setObjectName("layoutWidget_2")
        self.horizontalLayout_3 = QtWidgets.QHBoxLayout(self.layoutWidget_2)
        self.horizontalLayout_3.setContentsMargins(0, 0, 0, 0)
        self.horizontalLayout_3.setObjectName("horizontalLayout_3")
        self.SubtitleLabel_3 = SubtitleLabel(self.layoutWidget_2)
        self.SubtitleLabel_3.setObjectName("SubtitleLabel_3")
        self.horizontalLayout_3.addWidget(self.SubtitleLabel_3)
        self.LineEdit_3 = LineEdit(self.layoutWidget_2)
        self.LineEdit_3.setObjectName("LineEdit_3")
        self.horizontalLayout_3.addWidget(self.LineEdit_3)
        self.import_word_label_btn = PrimaryPushButton('导入word文本')
        self.import_word_label_btn.setGeometry(QtCore.QRect(20, 10, 111, 32))
        self.import_word_label_btn.setObjectName("import_word_label_btn")
        self.word_path_label = SubtitleLabel(self.onnx_view)
        self.word_path_label.setGeometry(QtCore.QRect(20, 50, 119, 28))
        self.word_path_label.setText("")
        self.word_path_label.setObjectName("word_path_label")
        self.widget = QtWidgets.QWidget(self.onnx_view)
        self.widget.setGeometry(QtCore.QRect(20, 90, 221, 35))
        self.widget.setObjectName("widget")
        self.horizontalLayout = QtWidgets.QHBoxLayout(self.widget)
        self.horizontalLayout.setContentsMargins(0, 0, 0, 0)
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.SubtitleLabel = SubtitleLabel(self.widget)
        self.SubtitleLabel.setObjectName("SubtitleLabel")
        self.horizontalLayout.addWidget(self.SubtitleLabel)
        self.LineEdit = LineEdit(self.widget)
        self.LineEdit.setObjectName("LineEdit")
        self.horizontalLayout.addWidget(self.LineEdit)
        self.SubtitleLabel_2.setText("高度值:")
        self.SubtitleLabel_3.setText("宽度值:")
        self.SubtitleLabel.setText("通道数:")

        self.LineEdit.setText(str(self.onnx_parmas[0]))

        self.LineEdit_2.setText(str(self.onnx_parmas[1]))

        self.LineEdit_3.setText(str(self.onnx_parmas[2]))

        self.word_path_label.setText(self.paddle_label_path)

        self.onnx_view.addWidget(self.import_word_label_btn)
        self.onnx_view.addWidget(self.word_path_label)
        self.onnx_view.addWidget(self.layoutWidget, align=Qt.AlignCenter)
        self.onnx_view.addWidget(self.layoutWidget_2, align=Qt.AlignCenter)
        self.onnx_view.addWidget(self.widget, align=Qt.AlignCenter)

        # add button to view
        self.onnx_set_btn = PrimaryPushButton('确认')
        self.onnx_set_btn.setFixedWidth(120)

        self.import_word_label_btn.clicked.connect(lambda: self.import_predict_tool('paddle_label'))
        self.onnx_view.addWidget(self.onnx_set_btn, align=Qt.AlignRight)

        # adjust layout (optional)
        self.onnx_view.widgetLayout.insertSpacing(1, 5)
        self.onnx_view.widgetLayout.addSpacing(5)

    def ui_init(self):
        self.ui.image_path_list.keyPressEvent = self.keyPressEvent


    def btn_init(self):
        self.ui.impor_dataset_btn.clicked.connect(self.import_datasets)
        self.ui.image_path_list.currentRowChanged.connect(self.show_images)

        self.ui.load_model_btn.clicked.connect(self.load_model)
        self.ui.load_clip_labels_btn.clicked.connect(lambda: self.import_predict_tool('clip_label'))
        self.ui.import_model_btn.clicked.connect(lambda: self.import_predict_tool('model'))
        self.ui.set_word_label_btn.clicked.connect(self.show_onnx_init)
        self.ui.start_predict_btn.clicked.connect(self.start_task)

        self.ui.auto_tbtn.clicked.connect(self.auto_tbtn_event)
        self.ui.half_auto_tbtn.clicked.connect(self.half_auto_tbtn_event)
        self.ui.save_btn.clicked.connect(lambda: self.save_text_img(True))
        self.ui.skip_btn.clicked.connect(self.next_pic)

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

        if self.ui.start_predict_btn.isChecked():
            createWarningInfoBar(self, '请先关闭识别')
            return

        if self.ui.yolo_cls_radio_btn.isChecked() and self.yolo_cls_path == None:
            createWarningInfoBar(self,'请先导入yolo-cls模型')
            return

        if self.ui.yolo_cls_radio_btn.isChecked() and 'yolo_cls' not in self.model_list:
            self.model_list.clear()
            self.model_list.append('yolo_cls')
        elif self.ui.yolo_cls_radio_btn.isChecked() and 'yolo_cls' in self.model_list:
            pass

        if self.ui.panddle_onnx_radio_btn.isChecked() and (self.paddle_label_path == None or self.paddle_onnx_path == None):
            createWarningInfoBar(self, '请先导入onnx模型以及word文本')
            return

        if self.ui.panddle_onnx_radio_btn.isChecked() and 'paddle_onnx' not in self.model_list:
            self.model_list.clear()
            self.model_list.append('paddle_onnx')
        elif self.ui.panddle_onnx_radio_btn.isChecked() and 'paddle_onnx' in self.model_list:
            pass


        if self.ui.panddle_radio_btn.isChecked() and 'paddle' not in self.model_list:
            self.model_list.clear()
            self.model_list.append('paddle')
        elif self.ui.panddle_radio_btn.isChecked() and 'paddle' in self.model_list:
            createWarningInfoBar(self, '目前已经是paddle模型了')
            return

        if self.ui.clip_radio_btn.isChecked() and 'clip' not in self.model_list:
            self.model_list.clear()
            self.model_list.append('clip')
        elif self.ui.clip_radio_btn.isChecked() and 'clip' in self.model_list:
            createWarningInfoBar(self, '目前已经是clip模型了')
            return

        self.stateTooltip = StateToolTip('正在初始化加载模型', '客官请耐心等待哦~~', self)
        self.stateTooltip.move(0, 30)
        self.stateTooltip.show()

        self.load_model_thread = Load_Model()
        self.load_model_thread.model_type = self.model_list[0]
        self.load_model_thread.model_path = self.yolo_cls_path if self.ui.yolo_cls_radio_btn.isChecked() else self.paddle_onnx_path
        self.load_model_thread.word_path = self.paddle_label_path
        self.load_model_thread.onnx_params = self.onnx_parmas
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

    def import_predict_tool(self, types):
        """
        导入自定义yolo
        :return:
        """
        folder_path, t = QFileDialog.getOpenFileName(self, 'Select File')

        if not folder_path:
            createWarningInfoBar(self, '请选择正确的路径')
            return

        if types == 'model' and folder_path.endswith('onnx'):
            self.paddle_onnx_path = folder_path
            createSuccessInfoBar(self, r'已导入paddle模型')

        if types == 'model' and folder_path.endswith('pt'):
            self.yolo_cls_path = folder_path
            createSuccessInfoBar(self, r'已导入yolo-cls模型')

        if types == 'clip_label' and folder_path.endswith('txt'):
            self.clip_label_path = folder_path
            createSuccessInfoBar(self, '导入clip_label完成')

        if types == 'paddle_label' and folder_path.endswith('txt'):
            self.paddle_label_path = folder_path
            createSuccessInfoBar(self, '导入paddle_label完成')

    def show_images(self):
        self.current_pic_index = self.ui.image_path_list.currentIndex().row()
        img_path = os.path.join(self.datasets_base_path, self.image_files_list[self.current_pic_index])
        current_pixmap = QPixmap(img_path)
        self.scaled_pixmap = current_pixmap.scaled(595, 529, Qt.AspectRatioMode.KeepAspectRatio)

        self.ui.PixmapLabel.setPixmap(self.scaled_pixmap)

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

        if self.ui.clip_radio_btn.isChecked() and (
                not self.clip_label_path or not os.path.exists(self.clip_label_path)):
            createWarningInfoBar(self, '请先新建label.txt或加载你的label文件')
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
        def response(infos):
            logger.info(infos)
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
                for i in infos['image']:
                    text, confiddence = i
                    self.ui.Confidence_label.setText(f'置信度: {str(float(confiddence))}')
                    self.ui.text_label_edit.setText(text)

        if self.ui.clip_radio_btn.isChecked():
            with open(self.clip_label_path, encoding='utf8') as f:
                clip_labels = [i.strip() for i in f.readlines()]
        else:
            clip_labels = []

        pic_path = os.path.join(self.datasets_base_path, self.image_files_list[self.current_pic_index])
        self.predict_thread = Predict_Thread()
        self.predict_thread.pic_path = pic_path
        self.predict_thread.model_type = self.model_list[0]
        self.predict_thread.model = self.use_model
        self.predict_thread.clip_labels = clip_labels
        self.predict_thread.paddle_labels = self.paddle_label_path
        self.predict_thread.response.connect(response)
        self.predict_thread.start()

    def start_auto_predict_task(self):
        def response(infos):
            if infos['status'] == 'all_success':
                createSuccessInfoBar(self, '图片识别成功')
                return

            self.current_pic_index = infos['index']
            if infos['status'] == 'errors':
                createErrorInfoBar(self, '图片识别失败')

                self.ui.image_path_list.setCurrentIndex(
                    self.ui.image_path_list.model().index(self.current_pic_index, 0))
                return

            if 'image' not in infos:
                createSuccessInfoBar(self, '图片识别成功,结果为空')
                self.ui.image_path_list.setCurrentIndex(
                    self.ui.image_path_list.model().index(self.current_pic_index, 0))
                return
            else:
                self.ui.image_path_list.setCurrentIndex(
                    self.ui.image_path_list.model().index(self.current_pic_index, 0))

                for i in infos['image']:
                    text, confiddence = i
                    self.ui.Confidence_label.setText(f'置信度: {str(float(confiddence))}')
                    self.ui.text_label_edit.setText(text)
                    if confiddence > 0.7:
                        self.save_text_img(True)
                    else:
                        self.save_text_img(False)

        if self.ui.clip_radio_btn.isChecked():
            with open(self.clip_label_path, encoding='utf8') as f:
                clip_labels = [i.strip() for i in f.readlines()]
        else:
            clip_labels = []

        self.predict_thread = Predict_Auto_Thread()
        self.predict_thread.pic_path_list = self.image_files_list
        self.predict_thread.base_path = self.datasets_base_path
        self.predict_thread.model_type = self.model_list[0]
        self.predict_thread.model = self.use_model
        self.predict_thread.clip_labels = clip_labels
        self.predict_thread.paddle_labels = self.paddle_label_path
        self.predict_thread.response.connect(response)
        self.predict_thread.start()

    def save_text_img(self, save_type):
        """
        把标签结合到图片命名中保存
        """
        self.main_save_path = cfg.get(cfg.pic_label_save_Folder)

        if self.current_pic_index is not None:
            text = self.ui.text_label_edit.text()
            if not text:
                createSuccessInfoBar(self, "当前图片识别结果为空")
                return
            if not save_type:
                text = '未知类别'

            if not os.path.exists(self.main_save_path + f'/{text}'):
                os.mkdir(self.main_save_path + f'/{text}')

            img_path = self.image_files_list[self.current_pic_index]
            total_img_path = os.path.join(self.datasets_base_path, img_path)
            save_path = os.path.join(self.main_save_path + f'/{text}', text + '_' + img_path)
            if os.path.exists(save_path):
                w = MessageBox('提示消息', '当前图片已保存过了，是否进行覆盖?', self)
                if w.exec():
                    pass
                else:
                    return

            shutil.copy(total_img_path, save_path)

            createSuccessInfoBar(self, f"图片分类已保存到 {save_path}")
            if self.current_pic_index == len(self.image_files_list) - 1:
                createSuccessInfoBar(self, '图片已经遍历一轮')
            else:
                self.next_pic()

    def next_pic(self):
        self.current_pic_index += 1
        self.ui.image_path_list.setCurrentRow(self.ui.image_path_list.model().index(self.current_pic_index, 0))


    def show_onnx_init(self):
        self.onnx_dialog()
        # show view
        w = Flyout.make(self.onnx_view, self.ui.set_word_label_btn, self)
        self.onnx_view.closed.connect(w.close)
        self.onnx_set_btn.clicked.connect(lambda :self.onnx_arguments_init(w))



    def keyPressEvent(self, event):
        """
        键盘事件
        :param event:
        :return:
        """
        if event.key() == Qt.Key.Key_S:
            self.save_text_img(True)

        elif event.key() == Qt.Key.Key_D:
            self.current_pic_index += 1
            self.ui.image_path_list.setCurrentIndex(self.ui.image_path_list.model().index(self.current_pic_index, 0))

        elif event.key() == Qt.Key.Key_A:
            self.current_pic_index -= 1
            self.ui.image_path_list.setCurrentIndex(self.ui.image_path_list.model().index(self.current_pic_index, 0))

    def mousePressEvent(self, event):
        self.setFocus()

