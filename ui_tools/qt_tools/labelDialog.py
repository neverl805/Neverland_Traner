from PyQt5.QtCore import QRegExp, QStringListModel, Qt, QPoint
from PyQt5.QtGui import QRegExpValidator, QCursor
from PyQt5.QtWidgets import QDialogButtonBox, QDialog, QCompleter, QVBoxLayout
from qfluentwidgets import LineEdit, ListWidget

BB = QDialogButtonBox


def trimmed(text):
    return text.strip()

def label_validator():
    return QRegExpValidator(QRegExp(r'^[^ \t].+'), None)

class LabelDialog(QDialog):

    def __init__(self, text="Enter object label", parent=None, list_item=None):
        super(LabelDialog, self).__init__(parent)

        self.edit = LineEdit()
        self.setStyleSheet("""
            background-color: rgb(39, 39, 39);
        """)
        self.edit.setText(text)
        self.edit.setValidator(label_validator())
        self.edit.editingFinished.connect(self.post_process)

        model = QStringListModel()
        model.setStringList(list_item)
        completer = QCompleter()
        completer.setModel(model)
        self.edit.setCompleter(completer)

        layout = QVBoxLayout()
        layout.addWidget(self.edit)
        self.button_box = bb = BB(BB.Ok | BB.Cancel, Qt.Horizontal, self)
        bb.setStyleSheet("""
            QPushButton {
        background-color: #7e6baa;
        color: white;
        border: none;
        padding: 5px 10px;
        font-size: 16px;
        border-radius: 8px;
        }
        QPushButton:hover {
            background-color: #8c71aa;
        }
        QPushButton:pressed {
            background-color: #6a5681;
        }
        """)
        bb.accepted.connect(self.validate)
        bb.rejected.connect(self.reject)
        layout.addWidget(bb)

        self.list_widget = ListWidget(self)
        for item in list_item:
            self.list_widget.addItem(item)
        self.list_widget.itemClicked.connect(self.list_item_click)
        self.list_widget.itemDoubleClicked.connect(self.list_item_double_click)
        layout.addWidget(self.list_widget)

        self.setLayout(layout)

    def validate(self):
        if trimmed(self.edit.text()):
            self.accept()

    def post_process(self):
        self.edit.setText(trimmed(self.edit.text()))

    def add_item(self,item):
        self.list_widget.addItem(item)

    def pop_up(self, text='', move=True):
        """
        Shows the dialog, setting the current text to `text`, and blocks the caller until the user has made a choice.
        If the user entered a label, that label is returned, otherwise (i.e. if the user cancelled the action)
        `None` is returned.
        """
        self.edit.setText(text)
        self.edit.setSelection(0, len(text))
        self.edit.setFocus(Qt.PopupFocusReason)
        if move:
            cursor_pos = QCursor.pos()
            parent_bottom_right = self.parentWidget().geometry()
            max_x = parent_bottom_right.x() + parent_bottom_right.width() - self.sizeHint().width()
            max_y = parent_bottom_right.y() + parent_bottom_right.height() - self.sizeHint().height()
            max_global = self.parentWidget().mapToGlobal(QPoint(max_x, max_y))
            if cursor_pos.x() > max_global.x():
                cursor_pos.setX(max_global.x())
            if cursor_pos.y() > max_global.y():
                cursor_pos.setY(max_global.y())
            self.move(cursor_pos)
        return trimmed(self.edit.text()) if self.exec_() else None

    def list_item_click(self, t_qlist_widget_item):
        text = trimmed(t_qlist_widget_item.text())
        self.edit.setText(text)

    def list_item_double_click(self, t_qlist_widget_item):
        self.list_item_click(t_qlist_widget_item)
        self.validate()
