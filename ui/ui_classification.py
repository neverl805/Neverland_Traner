# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'classification.ui'
#
# Created by: PyQt5 UI code generator 5.15.9
#
# WARNING: Any manual changes made to this file will be lost when pyuic5 is
# run again.  Do not edit this file unless you know what you are doing.


from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_Form(object):
    def setupUi(self, Form):
        Form.setObjectName("Form")
        Form.resize(898, 750)
        self.verticalLayout = QtWidgets.QVBoxLayout(Form)
        self.verticalLayout.setObjectName("verticalLayout")
        self.SimpleCardWidget_2 = SimpleCardWidget(Form)
        self.SimpleCardWidget_2.setMinimumSize(QtCore.QSize(780, 90))
        self.SimpleCardWidget_2.setMaximumSize(QtCore.QSize(16777215, 100))
        self.SimpleCardWidget_2.setObjectName("SimpleCardWidget_2")
        self.horizontalLayout_8 = QtWidgets.QHBoxLayout(self.SimpleCardWidget_2)
        self.horizontalLayout_8.setObjectName("horizontalLayout_8")
        self.horizontalLayout_5 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_5.setObjectName("horizontalLayout_5")
        self.verticalLayout_8 = QtWidgets.QVBoxLayout()
        self.verticalLayout_8.setObjectName("verticalLayout_8")
        self.import_model_btn = PrimaryPushButton(self.SimpleCardWidget_2)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.import_model_btn.sizePolicy().hasHeightForWidth())
        self.import_model_btn.setSizePolicy(sizePolicy)
        self.import_model_btn.setMaximumSize(QtCore.QSize(200, 16777215))
        self.import_model_btn.setObjectName("import_model_btn")
        self.verticalLayout_8.addWidget(self.import_model_btn)
        self.set_word_label_btn = PrimaryPushButton(self.SimpleCardWidget_2)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.set_word_label_btn.sizePolicy().hasHeightForWidth())
        self.set_word_label_btn.setSizePolicy(sizePolicy)
        self.set_word_label_btn.setMaximumSize(QtCore.QSize(200, 16777215))
        self.set_word_label_btn.setObjectName("set_word_label_btn")
        self.verticalLayout_8.addWidget(self.set_word_label_btn)
        self.horizontalLayout_5.addLayout(self.verticalLayout_8)
        self.verticalLayout_7 = QtWidgets.QVBoxLayout()
        self.verticalLayout_7.setObjectName("verticalLayout_7")
        self.yolo_cls_radio_btn = RadioButton(self.SimpleCardWidget_2)
        self.yolo_cls_radio_btn.setObjectName("yolo_cls_radio_btn")
        self.verticalLayout_7.addWidget(self.yolo_cls_radio_btn)
        self.panddle_onnx_radio_btn = RadioButton(self.SimpleCardWidget_2)
        self.panddle_onnx_radio_btn.setObjectName("panddle_onnx_radio_btn")
        self.verticalLayout_7.addWidget(self.panddle_onnx_radio_btn)
        self.horizontalLayout_5.addLayout(self.verticalLayout_7)
        self.horizontalLayout_8.addLayout(self.horizontalLayout_5)
        self.VerticalSeparator = VerticalSeparator(self.SimpleCardWidget_2)
        self.VerticalSeparator.setObjectName("VerticalSeparator")
        self.horizontalLayout_8.addWidget(self.VerticalSeparator)
        self.horizontalLayout_7 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_7.setObjectName("horizontalLayout_7")
        self.verticalLayout_6 = QtWidgets.QVBoxLayout()
        self.verticalLayout_6.setObjectName("verticalLayout_6")
        self.panddle_radio_btn = RadioButton(self.SimpleCardWidget_2)
        self.panddle_radio_btn.setChecked(True)
        self.panddle_radio_btn.setObjectName("panddle_radio_btn")
        self.verticalLayout_6.addWidget(self.panddle_radio_btn)
        self.clip_radio_btn = RadioButton(self.SimpleCardWidget_2)
        self.clip_radio_btn.setChecked(False)
        self.clip_radio_btn.setObjectName("clip_radio_btn")
        self.verticalLayout_6.addWidget(self.clip_radio_btn)
        self.horizontalLayout_7.addLayout(self.verticalLayout_6)
        self.verticalLayout_5 = QtWidgets.QVBoxLayout()
        self.verticalLayout_5.setObjectName("verticalLayout_5")
        self.auto_tbtn = ToggleButton(self.SimpleCardWidget_2)
        self.auto_tbtn.setObjectName("auto_tbtn")
        self.verticalLayout_5.addWidget(self.auto_tbtn)
        self.half_auto_tbtn = ToggleButton(self.SimpleCardWidget_2)
        self.half_auto_tbtn.setChecked(True)
        self.half_auto_tbtn.setObjectName("half_auto_tbtn")
        self.verticalLayout_5.addWidget(self.half_auto_tbtn)
        self.horizontalLayout_7.addLayout(self.verticalLayout_5)
        self.horizontalLayout_8.addLayout(self.horizontalLayout_7)
        self.VerticalSeparator_3 = VerticalSeparator(self.SimpleCardWidget_2)
        self.VerticalSeparator_3.setObjectName("VerticalSeparator_3")
        self.horizontalLayout_8.addWidget(self.VerticalSeparator_3)
        self.verticalLayout_4 = QtWidgets.QVBoxLayout()
        self.verticalLayout_4.setObjectName("verticalLayout_4")
        self.Confidence_label = BodyLabel(self.SimpleCardWidget_2)
        self.Confidence_label.setObjectName("Confidence_label")
        self.verticalLayout_4.addWidget(self.Confidence_label)
        self.horizontalLayout_6 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_6.setObjectName("horizontalLayout_6")
        self.Identification_label = BodyLabel(self.SimpleCardWidget_2)
        self.Identification_label.setObjectName("Identification_label")
        self.horizontalLayout_6.addWidget(self.Identification_label)
        self.text_label_edit = LineEdit(self.SimpleCardWidget_2)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.text_label_edit.sizePolicy().hasHeightForWidth())
        self.text_label_edit.setSizePolicy(sizePolicy)
        self.text_label_edit.setObjectName("text_label_edit")
        self.horizontalLayout_6.addWidget(self.text_label_edit)
        self.verticalLayout_4.addLayout(self.horizontalLayout_6)
        self.horizontalLayout_8.addLayout(self.verticalLayout_4)
        self.VerticalSeparator_4 = VerticalSeparator(self.SimpleCardWidget_2)
        self.VerticalSeparator_4.setObjectName("VerticalSeparator_4")
        self.horizontalLayout_8.addWidget(self.VerticalSeparator_4)
        self.horizontalLayout_4 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_4.setObjectName("horizontalLayout_4")
        self.verticalLayout_9 = QtWidgets.QVBoxLayout()
        self.verticalLayout_9.setObjectName("verticalLayout_9")
        self.load_model_btn = PrimaryPushButton(self.SimpleCardWidget_2)
        self.load_model_btn.setObjectName("load_model_btn")
        self.verticalLayout_9.addWidget(self.load_model_btn)
        self.start_predict_btn = ToggleButton(self.SimpleCardWidget_2)
        self.start_predict_btn.setObjectName("start_predict_btn")
        self.verticalLayout_9.addWidget(self.start_predict_btn)
        self.horizontalLayout_4.addLayout(self.verticalLayout_9)
        self.verticalLayout_3 = QtWidgets.QVBoxLayout()
        self.verticalLayout_3.setObjectName("verticalLayout_3")
        self.impor_dataset_btn = PrimaryPushButton(self.SimpleCardWidget_2)
        self.impor_dataset_btn.setObjectName("impor_dataset_btn")
        self.verticalLayout_3.addWidget(self.impor_dataset_btn)
        self.load_clip_labels_btn = PrimaryPushButton(self.SimpleCardWidget_2)
        self.load_clip_labels_btn.setMaximumSize(QtCore.QSize(96, 16777215))
        self.load_clip_labels_btn.setObjectName("load_clip_labels_btn")
        self.verticalLayout_3.addWidget(self.load_clip_labels_btn)
        self.horizontalLayout_4.addLayout(self.verticalLayout_3)
        self.horizontalLayout_8.addLayout(self.horizontalLayout_4)
        self.verticalLayout.addWidget(self.SimpleCardWidget_2)
        self.SimpleCardWidget = SimpleCardWidget(Form)
        self.SimpleCardWidget.setMinimumSize(QtCore.QSize(100, 300))
        self.SimpleCardWidget.setObjectName("SimpleCardWidget")
        self.horizontalLayout_3 = QtWidgets.QHBoxLayout(self.SimpleCardWidget)
        self.horizontalLayout_3.setObjectName("horizontalLayout_3")
        self.horizontalLayout_2 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_2.setObjectName("horizontalLayout_2")
        self.verticalLayout_2 = QtWidgets.QVBoxLayout()
        self.verticalLayout_2.setObjectName("verticalLayout_2")
        self.CardWidget_2 = CardWidget(self.SimpleCardWidget)
        self.CardWidget_2.setMinimumSize(QtCore.QSize(200, 0))
        self.CardWidget_2.setObjectName("CardWidget_2")
        self.horizontalLayout = QtWidgets.QHBoxLayout(self.CardWidget_2)
        self.horizontalLayout.setContentsMargins(5, -1, -1, -1)
        self.horizontalLayout.setSpacing(5)
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.PixmapLabel = PixmapLabel(self.CardWidget_2)
        self.PixmapLabel.setObjectName("PixmapLabel")
        self.horizontalLayout.addWidget(self.PixmapLabel)
        self.verticalLayout_2.addWidget(self.CardWidget_2)
        self.CardWidget = CardWidget(self.SimpleCardWidget)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.CardWidget.sizePolicy().hasHeightForWidth())
        self.CardWidget.setSizePolicy(sizePolicy)
        self.CardWidget.setMinimumSize(QtCore.QSize(100, 50))
        self.CardWidget.setMaximumSize(QtCore.QSize(10000, 50))
        self.CardWidget.setObjectName("CardWidget")
        self.horizontalLayout_10 = QtWidgets.QHBoxLayout(self.CardWidget)
        self.horizontalLayout_10.setObjectName("horizontalLayout_10")
        self.skip_btn = PrimaryPushButton(self.CardWidget)
        self.skip_btn.setMaximumSize(QtCore.QSize(200, 50))
        self.skip_btn.setObjectName("skip_btn")
        self.horizontalLayout_10.addWidget(self.skip_btn)
        self.save_btn = PrimaryPushButton(self.CardWidget)
        self.save_btn.setMaximumSize(QtCore.QSize(200, 50))
        self.save_btn.setObjectName("save_btn")
        self.horizontalLayout_10.addWidget(self.save_btn)
        self.verticalLayout_2.addWidget(self.CardWidget)
        self.horizontalLayout_2.addLayout(self.verticalLayout_2)
        self.image_path_list = ListWidget(self.SimpleCardWidget)
        self.image_path_list.setMaximumSize(QtCore.QSize(200, 16777215))
        self.image_path_list.setObjectName("image_path_list")
        self.horizontalLayout_2.addWidget(self.image_path_list)
        self.horizontalLayout_3.addLayout(self.horizontalLayout_2)
        self.verticalLayout.addWidget(self.SimpleCardWidget)

        self.retranslateUi(Form)
        QtCore.QMetaObject.connectSlotsByName(Form)

    def retranslateUi(self, Form):
        _translate = QtCore.QCoreApplication.translate
        Form.setWindowTitle(_translate("Form", "Form"))
        self.import_model_btn.setText(_translate("Form", "导入模型"))
        self.set_word_label_btn.setText(_translate("Form", "飞浆设置"))
        self.yolo_cls_radio_btn.setText(_translate("Form", "自定义yolo-cls"))
        self.panddle_onnx_radio_btn.setText(_translate("Form", "自定义paddle-onnx"))
        self.panddle_radio_btn.setText(_translate("Form", "panddle_ocr"))
        self.clip_radio_btn.setText(_translate("Form", "clip"))
        self.auto_tbtn.setText(_translate("Form", "全自动模式"))
        self.half_auto_tbtn.setText(_translate("Form", "半自动模式"))
        self.Confidence_label.setText(_translate("Form", "置信度: 0"))
        self.Identification_label.setText(_translate("Form", "识别标签:"))
        self.load_model_btn.setText(_translate("Form", "加载模型"))
        self.start_predict_btn.setText(_translate("Form", "开启识别"))
        self.impor_dataset_btn.setText(_translate("Form", "导入数据集"))
        self.load_clip_labels_btn.setText(_translate("Form", "加载clip标签"))
        self.skip_btn.setText(_translate("Form", "跳过"))
        self.save_btn.setText(_translate("Form", "保存"))
from qfluentwidgets import BodyLabel, CardWidget, LineEdit, ListWidget, PixmapLabel, PrimaryPushButton, RadioButton, SimpleCardWidget, ToggleButton, VerticalSeparator
