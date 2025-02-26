from PyQt5.QtCore import Qt
from qfluentwidgets import InfoBar, InfoBarPosition


def createWarningInfoBar(self, text: str, time=1000, postion=InfoBarPosition.TOP):
    InfoBar.warning(
        title='警告',
        content=text,
        orient=Qt.Orientation.Horizontal,
        isClosable=True,  # disable close button
        position=postion,
        duration=time,
        parent=self
    )


def createSuccessInfoBar(self, info, time=1000, postion=InfoBarPosition.TOP):
    # convenient class mothod
    InfoBar.success(
        title='成功',
        content=info,
        orient=Qt.Orientation.Horizontal,
        isClosable=True,
        position=postion,
        duration=time,
        parent=self
    )


def createErrorInfoBar(self, info, time=1000, postion=InfoBarPosition.TOP):
    InfoBar.error(
        title='错误',
        content=info,
        orient=Qt.Orientation.Horizontal,
        isClosable=True,
        position=postion,
        duration=time,  # won't disappear automatically
        parent=self
    )