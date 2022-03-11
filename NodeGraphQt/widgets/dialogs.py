import os

from .stylesheet import STYLE_MESSAGEBOX
from Qt import QtWidgets

current_dir = os.path.expanduser('~')


def set_dir(file):
    global current_dir
    if os.path.isdir(file):
        current_dir = file
    elif os.path.isfile(file):
        current_dir = os.path.split(file)[0]


class FileDialog(object):

    @staticmethod
    def getSaveFileName(parent=None, title='Save File', file_dir=None,
                        ext_filter='*'):
        if not file_dir:
            file_dir = current_dir
        file_dlg = QtWidgets.QFileDialog.getSaveFileName(
            parent, title, file_dir, ext_filter)
        file = file_dlg[0] or None
        if file:
            set_dir(file)
        return file_dlg

    @staticmethod
    def getOpenFileName(parent=None, title='Open File', file_dir=None,
                        ext_filter='*'):
        if not file_dir:
            file_dir = current_dir

        file_dlg = QtWidgets.QFileDialog.getOpenFileName(
            parent, title, file_dir, ext_filter)

        file = file_dlg[0] or None
        if file:
            set_dir(file)

        return file_dlg


class BaseDialog(object):

    @staticmethod
    def message_dialog(text, title):
        dlg = QtWidgets.QMessageBox()
        dlg.setStyleSheet(STYLE_MESSAGEBOX)
        dlg.setWindowTitle(title)
        dlg.setInformativeText(text)
        dlg.setStandardButtons(QtWidgets.QMessageBox.Ok)
        return dlg.exec_()

    @staticmethod
    def question_dialog(text, title):
        dlg = QtWidgets.QMessageBox()
        dlg.setStyleSheet(STYLE_MESSAGEBOX)
        dlg.setWindowTitle(title)
        dlg.setInformativeText(text)
        dlg.setStandardButtons(
            QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No
        )
        result = dlg.exec_()
        return bool(result == QtWidgets.QMessageBox.Yes)
