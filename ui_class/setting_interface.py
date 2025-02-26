# coding:utf-8
from typing import Union

from config import cfg, AUTHOR, VERSION, YEAR
from qfluentwidgets import (SettingCardGroup, SwitchSettingCard, FolderListSettingCard,
                            OptionsSettingCard, RangeSettingCard, PushSettingCard,
                            ColorSettingCard, HyperlinkCard, PrimaryPushSettingCard, ScrollArea,
                            ComboBoxSettingCard, ExpandLayout, Theme, InfoBar, CustomColorSettingCard,
                            setTheme, setThemeColor, isDarkTheme, SettingCard, FluentIconBase, CompactDoubleSpinBox,
                            qconfig)
from qfluentwidgets import FluentIcon as FIF
from PyQt5.QtCore import Qt, pyqtSignal, QUrl, QStandardPaths
from PyQt5.QtGui import QDesktopServices, QIcon
from PyQt5.QtWidgets import QWidget, QLabel, QFontDialog, QFileDialog


class CompactSettingCard(SettingCard):
    """ Setting card with a slider """

    valueChanged = pyqtSignal(int)

    def __init__(self, configItem, icon: Union[str, QIcon, FluentIconBase], title, content=None, parent=None):
        super().__init__(icon, title, content, parent)
        self.configItem = configItem
        self.compactDoubleSpinBox = CompactDoubleSpinBox(self)

        self.hBoxLayout.addStretch(1)
        self.hBoxLayout.addSpacing(6)
        self.hBoxLayout.addWidget(self.compactDoubleSpinBox, 0, Qt.AlignRight)
        self.hBoxLayout.addSpacing(16)
        self.compactDoubleSpinBox.setValue(configItem.value)

        configItem.valueChanged.connect(self.setValue)
        self.compactDoubleSpinBox.valueChanged.connect(self.__onValueChanged)
        self.compactDoubleSpinBox.setSingleStep(0.1)

    def __onValueChanged(self, value: int):
        """ slider value changed slot """
        value = float(str(value).strip())
        self.setValue(value)
        self.valueChanged.emit(value)

    def setValue(self, value):
        qconfig.set(self.configItem, value)
        self.compactDoubleSpinBox.setValue(value)


class SettingInterface(ScrollArea):
    """ Setting interface """

    checkUpdateSig = pyqtSignal()
    musicFoldersChanged = pyqtSignal(list)
    acrylicEnableChanged = pyqtSignal(bool)
    downloadFolderChanged = pyqtSignal(str)
    minimizeToTrayChanged = pyqtSignal(bool)

    def __init__(self, parent=None):
        super().__init__(parent=parent)
        self.setObjectName('ui_setting')
        self.scrollWidget = QWidget()
        self.expandLayout = ExpandLayout(self.scrollWidget)

        # setting label
        self.settingLabel = QLabel(self.tr("Settings"), self)

        # music folders
        self.markInThisPCGroup = SettingCardGroup(
            self.tr("标注配置保存"), self.scrollWidget)

        self.model_downloadFolderCard = PushSettingCard(
            self.tr('Choose folder'),
            FIF.DOWNLOAD,
            self.tr("模型下载目录"),
            cfg.get(cfg.model_downloadFolder),
            self.markInThisPCGroup
        )
        self.pic_downloadFolderCard = PushSettingCard(
            self.tr('Choose folder'),
            FIF.DOWNLOAD,
            self.tr("图片标注保存目录"),
            cfg.get(cfg.pic_label_save_Folder),
            self.markInThisPCGroup
        )

        self.siamese_twin_group = SettingCardGroup(self.tr('孪生标注算法阈值设置'), self.scrollWidget)
        self.model_fraction_card = CompactSettingCard(
            cfg.model_fraction,
            FIF.BOOK_SHELF,
            self.tr("模型识别阈值"),
            self.tr("越近1越相似"),
            parent=self.siamese_twin_group
        )

        self.texture_fraction_card = CompactSettingCard(
            cfg.texture_fraction,
            FIF.BOOK_SHELF,
            self.tr("形状纹理分数阈值"),
            self.tr("越近0越相似"),
            parent=self.siamese_twin_group
        )
        self.color_fraction_card = CompactSettingCard(
            cfg.color_fraction,
            FIF.BOOK_SHELF,
            self.tr("颜色直方图分数阈值"),
            self.tr("越近0越相似"),
            parent=self.siamese_twin_group
        )


        # personalization
        self.personalGroup = SettingCardGroup(self.tr('Personalization'), self.scrollWidget)
        self.enableAcrylicCard = SwitchSettingCard(
            FIF.TRANSPARENT,
            self.tr("Use Acrylic effect"),
            self.tr("Acrylic effect has better visual experience, but it may cause the window to become stuck"),
            configItem=cfg.enableAcrylicBackground,
            parent=self.personalGroup
        )
        self.themeCard = OptionsSettingCard(
            cfg.themeMode,
            FIF.BRUSH,
            self.tr('Application theme'),
            self.tr("Change the appearance of your application"),
            texts=[
                self.tr('Light'), self.tr('Dark'),
                self.tr('Use system setting')
            ],
            parent=self.personalGroup
        )
        self.themeColorCard=CustomColorSettingCard(
            cfg.themeColor,
            FIF.PALETTE,
            self.tr('Theme color'),
            self.tr('Change the theme color of you application'),
            self.personalGroup
        )
        self.zoomCard = OptionsSettingCard(
            cfg.dpiScale,
            FIF.ZOOM,
            self.tr("Interface zoom"),
            self.tr("Change the size of widgets and fonts"),
            texts=[
                "100%", "125%", "150%", "175%", "200%",
                self.tr("Use system setting")
            ],
            parent=self.personalGroup
        )
        self.languageCard = ComboBoxSettingCard(
            cfg.language,
            FIF.LANGUAGE,
            self.tr('Language'),
            self.tr('Set your preferred language for UI'),
            texts=['简体中文', '繁體中文', 'English', self.tr('Use system setting')],
            parent=self.personalGroup
        )


        # main panel
        self.mainPanelGroup = SettingCardGroup(self.tr('Main Panel'), self.scrollWidget)
        self.minimizeToTrayCard = SwitchSettingCard(
            FIF.MINIMIZE,
            self.tr('Minimize to tray after closing'),
            self.tr('window will continue to run in the background'),
            configItem=cfg.minimizeToTray,
            parent=self.mainPanelGroup
        )


        self.__initWidget()

    def __initWidget(self):
        self.resize(1000, 800)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setViewportMargins(0, 120, 0, 20)
        self.setWidget(self.scrollWidget)
        self.setWidgetResizable(True)

        # initialize style sheet
        self.__setQss()

        # initialize layout
        self.__initLayout()
        self.__connectSignalToSlot()

    def __initLayout(self):
        self.settingLabel.move(60, 63)

        self.markInThisPCGroup.addSettingCard(self.model_downloadFolderCard)
        self.markInThisPCGroup.addSettingCard(self.pic_downloadFolderCard)

        self.siamese_twin_group.addSettingCard(self.model_fraction_card)
        self.siamese_twin_group.addSettingCard(self.texture_fraction_card)
        self.siamese_twin_group.addSettingCard(self.color_fraction_card)

        self.personalGroup.addSettingCard(self.enableAcrylicCard)
        self.personalGroup.addSettingCard(self.themeCard)
        self.personalGroup.addSettingCard(self.themeColorCard)
        self.personalGroup.addSettingCard(self.zoomCard)
        self.personalGroup.addSettingCard(self.languageCard)


        self.mainPanelGroup.addSettingCard(self.minimizeToTrayCard)


        # add setting card group to layout
        self.expandLayout.setSpacing(28)
        self.expandLayout.setContentsMargins(60, 10, 60, 0)
        self.expandLayout.addWidget(self.markInThisPCGroup)
        self.expandLayout.addWidget(self.siamese_twin_group)
        self.expandLayout.addWidget(self.personalGroup)
        self.expandLayout.addWidget(self.mainPanelGroup)

    def __setQss(self):
        """ set style sheet """
        self.scrollWidget.setObjectName('scrollWidget')
        self.settingLabel.setObjectName('settingLabel')

        theme = 'dark' if isDarkTheme() else 'light'
        with open(f'resource/qss/{theme}/setting_interface.qss', encoding='utf-8') as f:
            self.setStyleSheet(f.read())

    def __showRestartTooltip(self):
        """ show restart tooltip """
        InfoBar.warning(
            '',
            self.tr('Configuration takes effect after restart'),
            parent=self.window()
        )


    def __model_onDownloadFolderCardClicked(self):
        """ download folder card clicked slot """
        folder = QFileDialog.getExistingDirectory(
            self, self.tr("Choose folder"), "./")
        if not folder or cfg.get(cfg.model_downloadFolder) == folder:
            return

        cfg.set(cfg.model_downloadFolder, folder)
        self.model_downloadFolderCard.setContent(folder)

    def __pic_onDownloadFolderCardClicked(self):
        """ download folder card clicked slot """
        folder = QFileDialog.getExistingDirectory(
            self, self.tr("Choose folder"), "./")
        if not folder or cfg.get(cfg.pic_label_save_Folder) == folder:
            return

        cfg.set(cfg.pic_label_save_Folder, folder)
        self.pic_downloadFolderCard.setContent(folder)


    def __showRestartTooltip(self):
        """ show restart tooltip """
        InfoBar.warning(
            '',
            self.tr('Configuration takes effect after restart'),
            parent=self.window()
        )

    def __onThemeChanged(self, theme: Theme):
        """ theme changed slot """
        # change the theme of qfluentwidgets
        setTheme(theme)

        # chang the theme of setting interface
        self.__setQss()

    def __connectSignalToSlot(self):
        """ connect signal to slot """
        cfg.appRestartSig.connect(self.__showRestartTooltip)
        cfg.themeChanged.connect(self.__onThemeChanged)

        self.model_downloadFolderCard.clicked.connect(
            self.__model_onDownloadFolderCardClicked)
        self.pic_downloadFolderCard.clicked.connect(
            self.__pic_onDownloadFolderCardClicked)

        # personalization
        self.enableAcrylicCard.checkedChanged.connect(
            self.acrylicEnableChanged)
        self.themeColorCard.colorChanged.connect(setThemeColor)


        # main panel
        self.minimizeToTrayCard.checkedChanged.connect(
            self.minimizeToTrayChanged)

