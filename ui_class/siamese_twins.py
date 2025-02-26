import os
from hashlib import md5
from itertools import combinations
from PyQt5.QtCore import QThread, pyqtSignal, Qt
from PyQt5.QtWidgets import QWidget, QFileDialog, QListWidgetItem
from loguru import logger
from qfluentwidgets import StateToolTip
from config import cfg
from ui_tools.siamese.color_histogram_similarity import color_predict
from ui_tools.siamese.merge_pic import merge_pic
from ui_tools.siamese.resent50_predict import load_resent_model, resent_predict
from ui_tools.siamese.shape_texture_similarity import shape_texture_predict
from ui_tools.siamese.vgg16_predict import load_vgg_model, vgg_predict
from ui import ui_saimese_twin
from PyQt5.QtGui import QPixmap
from ui_tools.qt_tools.infobar import createWarningInfoBar, createSuccessInfoBar, createErrorInfoBar


class Predict_Auto_Thread(QThread):
    response = pyqtSignal(dict)

    def __init__(self):
        super().__init__()
        self.pic_path_list = None
        self.base_path = None
        self.model_type = None

        self.model = None

    def run(self) -> None:

        # 使用combinations函数获取所有可能的两两组合
        for combo in combinations(self.pic_path_list, 2):
            try:
                main_pic_path, sup_pic_path = combo
                if self.model_type == 'vgg16':
                    similarity_score = vgg_predict(main_pic_path, sup_pic_path, self.model)
                elif self.model_type == 'resent50':
                    similarity_score = resent_predict(main_pic_path, sup_pic_path, self.model)
                elif self.model_type == 'texture':
                    similarity_score = shape_texture_predict(main_pic_path, sup_pic_path)
                elif self.model_type == 'color':
                    similarity_score = color_predict(main_pic_path, sup_pic_path)
                else:
                    raise '未知模型'

                self.response.emit({
                    'status': 'success',
                    'image': {
                        'source': similarity_score
                    },
                    'index': {
                        'main': int(self.pic_path_list.index(main_pic_path)),
                        'sup': int(self.pic_path_list.index(sup_pic_path))
                    }
                })
            except Exception as e:
                self.response.emit({'status': 'errors', 'msg': str(e)})

        self.response.emit({'status': 'all_success'})


class Predict_Thread(QThread):
    response = pyqtSignal(dict)

    def __init__(self):
        super().__init__()
        self.main_pic_path = None
        self.sup_pic_path = None
        self.model_type = None
        self.clip_labels = None
        self.model = None

    def run(self) -> None:
        try:
            if self.model_type == 'vgg16':
                similarity_score = vgg_predict(self.main_pic_path, self.sup_pic_path, self.model)
            elif self.model_type == 'resent50':
                similarity_score = resent_predict(self.main_pic_path, self.sup_pic_path, self.model)
            elif self.model_type == 'texture':
                similarity_score = shape_texture_predict(self.main_pic_path, self.sup_pic_path)
            elif self.model_type == 'color':
                similarity_score = color_predict(self.main_pic_path, self.sup_pic_path)
            else:
                raise '未知模型'

            self.response.emit({'status': 'success', 'image': {
                'source': similarity_score
            }})
        except Exception as e:
            self.response.emit({'status': 'errors', 'msg': str(e)})


class Load_Model(QThread):
    response = pyqtSignal(dict)

    def __init__(self):
        super().__init__()
        self.model_type = None
        self.model_path = None

    def run(self):
        try:
            if self.model_type == 'vgg16':
                det = load_vgg_model(self.model_path)
            elif self.model_type == 'resent50':
                det = load_resent_model(self.model_path)
            elif self.model_type == 'texture':
                det = 'texture'
            elif self.model_type == 'color':
                det = 'color'
            else:
                raise '未知模型'

            self.response.emit({'status': 'success', 'model': det})
        except Exception as e:
            self.response.emit({'status': 'errors', 'msg': str(e)})

class Path_List_Update(QThread):
    response = pyqtSignal(dict)

    def __init__(self):
        super().__init__()
        self.pic_path_list = None

    def run(self):
        try:
            for stand in self.pic_path_list:
                self.response.emit({
                    'status':'success',
                    'item':stand
                })
            self.response.emit({
                'status': 'total_success'
            })
        except Exception as e:
            self.response.emit({'status': 'errors', 'msg': str(e)})



class Target_Class(QWidget):

    def __init__(self, ui_class=ui_saimese_twin.Ui_Form, parent=None):
        super().__init__(parent=parent)

        self.ui = ui_class()
        self.ui.setupUi(self)
        self.setObjectName('siamese_twins')

        self.arg_init()
        self.ui_init()
        self.btn_init()

    def arg_init(self):
        self.image_files_list = None  # 图片数据集列表
        self.datasets_base_path = None  # 存放图片的路径
        self.current_pic_index = 0  # 当前选中的图片的索引
        self.sup_pic_index = 0  # 副图的图片索引
        self.start_sign = False  # 开始识别标志
        self.use_model = None  # 使用中的模型
        self.model_list = []  # 模型的列表
        self.main_save_path = None  # 保存的路径
        self.main_pic_path = None
        self.sup_pic_path = None

    def ui_init(self):
        self.ui.main_pic_pixmap.keyPressEvent = self.keyReleaseEvent
        self.ui.subplot_pic_pixmap.keyPressEvent = self.keyReleaseEvent
        self.ui.image_path_list.keyPressEvent = self.keyReleaseEvent

    def btn_init(self):
        self.ui.impor_dataset_btn.clicked.connect(self.import_datasets)
        self.ui.image_path_list.currentRowChanged.connect(self.show_main_image)

        self.ui.load_model_btn.clicked.connect(self.load_model)
        self.ui.start_predict_btn.clicked.connect(self.start_task)

        self.ui.auto_tbtn.clicked.connect(self.auto_tbtn_event)
        self.ui.half_auto_tbtn.clicked.connect(self.half_auto_tbtn_event)

        self.ui.different_class_btn.clicked.connect(lambda: self.marking_pic('different'))
        self.ui.same_class_btn.clicked.connect(lambda: self.marking_pic('same'))
        self.ui.change_sup_pic_btn.clicked.connect(self.next_main_pic)



    def next_main_pic(self):
        self.sup_pic_index += 1
        self.show_sup_image()

    def auto_tbtn_event(self):
        self.ui.half_auto_tbtn.setChecked(False)
        self.ui.start_predict_btn.setChecked(False)
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

                self.ui.current_use_label.setText(f'当前使用的算法: {self.model_list[0]}')

            self.stateTooltip.setState(True)

        if self.ui.start_predict_btn.isChecked():
            createWarningInfoBar(self, '请先关闭识别')
            return

        if 'vgg16' not in self.model_list and self.ui.vgg_radio_btn.isChecked():
            self.model_list.clear()
            self.model_list.append('vgg16')
        elif 'vgg16' in self.model_list and self.ui.vgg_radio_btn.isChecked():
            createWarningInfoBar(self, '目前已经是vgg16模型了')
            return

        if 'resent50' not in self.model_list and self.ui.resent_radio_btn.isChecked():
            self.model_list.clear()
            self.model_list.append('resent50')
        elif 'resent50' in self.model_list and self.ui.resent_radio_btn.isChecked():
            createWarningInfoBar(self, '目前已经是resent50模型了')
            return

        if 'texture' not in self.model_list and self.ui.edge_texture_radio_btn.isChecked():
            self.model_list.clear()
            self.model_list.append('texture')
        elif 'texture' in self.model_list and self.ui.edge_texture_radio_btn.isChecked():
            createWarningInfoBar(self, '目前已经是边缘纹理算法了')
            return

        if 'color' not in self.model_list and self.ui.color_radio_btn.isChecked():
            self.model_list.clear()
            self.model_list.append('color')
        elif 'color' in self.model_list and self.ui.color_radio_btn.isChecked():
            createWarningInfoBar(self, '目前已经是颜色直方图对比算法了')
            return

        self.stateTooltip = StateToolTip('正在初始化加载模型', '客官请耐心等待哦~~', self)
        self.stateTooltip.move(0, 30)
        self.stateTooltip.show()

        self.load_model_thread = Load_Model()
        self.load_model_thread.model_type = self.model_list[0]
        self.load_model_thread.model_path = cfg.get(cfg.model_downloadFolder)
        self.load_model_thread.response.connect(response)
        self.load_model_thread.start()

    def import_datasets(self):

        folder_path = QFileDialog.getExistingDirectory(self, 'Select Folder',
                                                       f'{os.getcwd()}\image')
        if not folder_path:
            createWarningInfoBar(self, '请选择文件保存路径')
            return

        self.datasets_base_path = folder_path
        self.image_files_list = [f for f in os.listdir(folder_path) if
                                 f.lower().endswith(('png', 'jpg', 'jpeg', 'webp', 'bmp'))]

        if not self.image_files_list:
            createWarningInfoBar(self, '文件夹没有图片数据哦')
            return

        self.update_list_view()
        createSuccessInfoBar(self, '已导入图片数据')

    def update_list_view(self):
        def response(infos):
            logger.info(infos)
            if infos['status'] == 'errors':
                createErrorInfoBar(self, infos['msg'])
            elif infos['status'] == 'success':
                item = QListWidgetItem(infos['item'])
                self.ui.image_path_list.addItem(item)
            else:
                self.ui.image_path_list.setCurrentRow(0)
                if self.sup_pic_index == self.current_pic_index:
                    self.sup_pic_index += 1
                self.main_pic_path = os.path.join(self.datasets_base_path,
                                                  self.image_files_list[self.current_pic_index])

                main_pixmap = QPixmap(self.main_pic_path)

                main_scaled_pixmap = main_pixmap.scaled(291, 543, Qt.AspectRatioMode.KeepAspectRatio)

                self.ui.main_pic_pixmap.setPixmap(main_scaled_pixmap)

                self.show_sup_image()

        # print(self.image_files_list)
        self.ui.image_path_list.clear()
        self.update_list_thread = Path_List_Update()
        self.update_list_thread.pic_path_list = self.image_files_list
        self.update_list_thread.response.connect(response)
        self.update_list_thread.start()

    def show_sup_image(self):
        if self.sup_pic_index >= len(self.image_files_list):
            self.sup_pic_index = 0
        self.sup_pic_path = os.path.join(self.datasets_base_path, self.image_files_list[self.sup_pic_index])
        sup_pixmap = QPixmap(self.sup_pic_path)
        sup_scaled_pixmap = sup_pixmap.scaled(291, 543, Qt.AspectRatioMode.KeepAspectRatio)
        self.ui.subplot_pic_pixmap.setPixmap(sup_scaled_pixmap)

        if self.ui.half_auto_tbtn.isChecked() and self.start_sign:
            self.start_predict_task()

    def show_main_image(self):
        self.current_pic_index = self.ui.image_path_list.currentIndex().row()
        self.main_pic_path = os.path.join(self.datasets_base_path, self.image_files_list[self.current_pic_index])
        current_pixmap = QPixmap(self.main_pic_path)
        scaled_pixmap = current_pixmap.scaled(291, 543, Qt.AspectRatioMode.KeepAspectRatio)

        self.ui.main_pic_pixmap.setPixmap(scaled_pixmap)

        if self.ui.half_auto_tbtn.isChecked() and self.start_sign:
            self.start_predict_task()

    def start_task(self):
        if self.current_pic_index == None:
            createWarningInfoBar(self, '请先导入数据')
            self.ui.start_predict_btn.setChecked(False)
            return

        if len(self.image_files_list) < 2:
            createWarningInfoBar(self, '请先导入足够的数据')
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
                confiddence = str("%.5f" % infos['image']['source'])
                self.ui.iden_label_edit.setText(confiddence)


        logger.info(self.model_list[0])
        self.predict_thread = Predict_Thread()
        self.predict_thread.main_pic_path = self.main_pic_path
        self.predict_thread.sup_pic_path = self.sup_pic_path
        self.predict_thread.model_type = self.model_list[0]
        self.predict_thread.model = self.use_model
        self.predict_thread.response.connect(response)
        self.predict_thread.start()

    def start_auto_predict_task(self):
        def response(infos):
            if infos['status'] == 'all_success':
                createSuccessInfoBar(self, '图片识别成功')
                return

            self.current_pic_index = infos['index']['main']
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
                confiddence = str("%.5f" % infos['image']['source'])
                self.ui.iden_label_edit.setText(confiddence)

                if self.ui.image_path_list.currentIndex().row() != infos['index']['main']:
                    self.ui.image_path_list.setCurrentIndex(
                        self.ui.image_path_list.model().index(infos['index']['main'], 0))
                self.sup_pic_index = infos['index']['sup']
                self.show_sup_image()

                if self.model_list[0] == 'vgg16' or self.model_list[0] == 'resent50':
                    if float(infos['image']['source']) > float(cfg.get(cfg.resent_fraction)):
                        self.marking_pic('same')
                    else:
                        self.marking_pic('different')
                elif self.model_list[0] == 'texture':
                    if float(infos['image']['source']) > float(cfg.get(cfg.texture_fraction)):
                        self.marking_pic('same')
                    else:
                        self.marking_pic('different')
                elif self.model_list[0] == 'color':
                    if float(infos['image']['source']) > float(cfg.get(cfg.color_fraction)):
                        self.marking_pic('same')
                    else:
                        self.marking_pic('different')

        self.marking_pic(None)
        self.predict_thread = Predict_Auto_Thread()
        self.predict_thread.pic_path_list = self.image_files_list
        self.predict_thread.base_path = self.datasets_base_path
        self.predict_thread.model_type = self.model_list[0]
        self.predict_thread.model = self.use_model
        self.predict_thread.response.connect(response)
        self.predict_thread.start()

    def marking_pic(self, static):

        self.main_save_path = cfg.get(cfg.pic_label_save_Folder)
        if not self.main_save_path:
            createWarningInfoBar(self, '请先设置图片保存目录')
            return

        if static is None:
            return

        self.t = md5((self.image_files_list[self.current_pic_index] + self.image_files_list[self.sup_pic_index]).encode()).hexdigest() + '.jpg'

        if self.main_pic_path is not None and self.sup_pic_path is not None:
            new_image = merge_pic(self.main_pic_path, self.sup_pic_path)
            if static == 'same':
                self.t = '1_' + self.t
                save_path = os.path.join(self.main_save_path, self.t)
                new_image.save(save_path)
            elif static == 'different':
                self.t = '0_' + self.t
                save_path = os.path.join(self.main_save_path, self.t)
                new_image.save(save_path)
            createSuccessInfoBar(self, f"合并图片已保存到 {save_path}")

            if self.sup_pic_index == len(self.image_files_list):
                self.current_pic_index += 1
                self.ui.image_path_list.setCurrentIndex(
                    self.ui.image_path_list.model().index(self.current_pic_index, 0))
            else:
                self.sup_pic_index += 1
            self.show_sup_image()
        else:
            createWarningInfoBar(self, '图片数量不足')

    def keyPressEvent(self, event):
        """
        键盘事件
        :param event:
        :return:
        """
        if event.key() == Qt.Key.Key_A:
            self.marking_pic('different')
        if event.key() == Qt.Key.Key_D:
            self.marking_pic('same')

    def mousePressEvent(self,event):
        self.setFocus()