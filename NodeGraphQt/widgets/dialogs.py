import os

from Qt import QtWidgets

_current_user_directory = os.path.expanduser('~')


def set_dir(file):
    global _current_user_directory
    if os.path.isdir(file):
        _current_user_directory = file
    elif os.path.isfile(file):
        _current_user_directory = os.path.split(file)[0]


class FileDialog(object):

    @staticmethod
    def getSaveFileName(parent=None, title='Save File', file_dir=None,
                        ext_filter='*'):
        if not file_dir:
            file_dir = _current_user_directory
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
            file_dir = _current_user_directory
        file_dlg = QtWidgets.QFileDialog.getOpenFileName(
            parent, title, file_dir, ext_filter)
        file = file_dlg[0] or None
        if file:
            set_dir(file)
        return file_dlg


class BaseDialog(object):

    @staticmethod
    def message_dialog(text='', title='Message'):
        dlg = QtWidgets.QMessageBox()
        dlg.setWindowTitle(title)
        dlg.setInformativeText(text)
        dlg.setStandardButtons(QtWidgets.QMessageBox.Ok)
        return dlg.exec()

    @staticmethod
    def question_dialog(text='', title='Are you sure?'):
        dlg = QtWidgets.QMessageBox()
        dlg.setWindowTitle(title)
        dlg.setInformativeText(text)
        dlg.setStandardButtons(
            QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No
        )
        result = dlg.exec()
        return bool(result == QtWidgets.QMessageBox.Yes)
