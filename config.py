# coding:utf-8
from enum import Enum
import os,json
from PyQt5.QtCore import Qt, QLocale
from qfluentwidgets import (qconfig, QConfig, ConfigItem, OptionsConfigItem, BoolValidator,
                            ColorConfigItem, OptionsValidator, RangeConfigItem, RangeValidator,
                            FolderListValidator, EnumSerializer, FolderValidator, ConfigSerializer, __version__)


class Language(Enum):
    """ Language enumeration """

    CHINESE_SIMPLIFIED = QLocale(QLocale.Chinese, QLocale.China)
    CHINESE_TRADITIONAL = QLocale(QLocale.Chinese, QLocale.HongKong)
    ENGLISH = QLocale(QLocale.English)
    AUTO = QLocale()


class LanguageSerializer(ConfigSerializer):
    """ Language serializer """

    def serialize(self, language):
        return language.value.name() if language != Language.AUTO else "Auto"

    def deserialize(self, value: str):
        return Language(QLocale(value)) if value != "Auto" else Language.AUTO


class Config(QConfig):
    """ Config of application """

    # folders
    model_downloadFolder = ConfigItem(
        "Folders", "Model_Download", "model", FolderValidator())
    pic_label_save_Folder = ConfigItem(
        "Folders", "Pic_Label_save", "pic_label", FolderValidator())

    texture_fraction = RangeConfigItem(
        "MainWindow", "Texture_fraction", 2, RangeValidator(0, 10))

    color_fraction = RangeConfigItem(
        "MainWindow", "Color_fraction", 2, RangeValidator(0, 10))
    model_fraction = RangeConfigItem(
        "MainWindow", "Model_fraction", 0.8, RangeValidator(0, 1))


    # main window
    enableAcrylicBackground = ConfigItem(
        "MainWindow", "EnableAcrylicBackground", False, BoolValidator())
    minimizeToTray = ConfigItem(
        "MainWindow", "MinimizeToTray", True, BoolValidator())
    playBarColor = ColorConfigItem("MainWindow", "PlayBarColor", "#225C7F")
    recentPlaysNumber = RangeConfigItem(
        "MainWindow", "RecentPlayNumbers", 300, RangeValidator(10, 300))
    dpiScale = OptionsConfigItem(
        "MainWindow", "DpiScale", "Auto", OptionsValidator([1, 1.25, 1.5, 1.75, 2, "Auto"]), restart=True)
    language = OptionsConfigItem(
        "MainWindow", "Language", Language.AUTO, OptionsValidator(Language), LanguageSerializer(), restart=True)


YEAR = 2024
AUTHOR = "Neverland"
VERSION = __version__

cfg = Config()
qconfig.load('config/config.json', cfg)
with open('config/config.json',encoding='utf8')as f:
    json_file = json.load(f)

if not json_file.get('Folders').get('Pic_Download'):
    cfg.pic_label_save_Folder.value = os.path.join(os.getcwd(), 'pic_label')
if not json_file.get('Folders').get('Model_Download'):
    cfg.model_downloadFolder.value = os.path.join(os.getcwd(), 'model')

if __name__ == '__main__':
    print(cfg.get(cfg.pic_label_save_Folder))