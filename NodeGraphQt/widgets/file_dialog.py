from .. import QtWidgets
from .stylesheet import STYLE_MESSAGEBOX
import os

current_dir = os.path.expanduser('~')


def set_dir(file):
    global current_dir
    if os.path.isdir(file):
        current_dir = file
    elif os.path.isfile(file):
        current_dir = os.path.split(file)[0]


class file_dialog(object):

    @staticmethod
    def getSaveFileName(parent=None, title="Save File", file_dir=None, ext_filter="*"):
        if not file_dir:
            file_dir = current_dir
        file_dlg = QtWidgets.QFileDialog.getSaveFileName(
            parent, title, file_dir, ext_filter)
        file = file_dlg[0] or None
        if file:
            set_dir(file)
        return file_dlg

    @staticmethod
    def getOpenFileName(parent=None, title="Open File", file_dir=None, ext_filter="*"):
        if not file_dir:
            file_dir = current_dir

        file_dlg = QtWidgets.QFileDialog.getOpenFileName(
            parent, title, file_dir, ext_filter)

        file = file_dlg[0] or None
        if file:
            set_dir(file)

        return file_dlg


def messageBox(text, title , buttons):
    msg = QtWidgets.QMessageBox()
    msg.setStyleSheet(STYLE_MESSAGEBOX)
    msg.setWindowTitle(title)
    msg.setInformativeText(text)
    msg.setStandardButtons(buttons)
    return msg.exec_()