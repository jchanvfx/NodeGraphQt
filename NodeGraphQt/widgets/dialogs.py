import os

from Qt import QtWidgets, QtGui, QtCore

_current_user_directory = os.path.expanduser('~')


def _set_dir(file):
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
            _set_dir(file)
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
            _set_dir(file)
        return file_dlg


class BaseDialog(object):

    @staticmethod
    def message_dialog(parent=None, text='', title='Message', dialog_icon=None,
                       custom_icon=None):
        dlg = QtWidgets.QMessageBox(parent=parent)
        dlg.setWindowTitle(title)
        dlg.setInformativeText(text)
        dlg.setStandardButtons(QtWidgets.QMessageBox.Ok)

        if custom_icon:
            pixmap = QtGui.QPixmap(custom_icon).scaledToHeight(
                32, QtCore.Qt.SmoothTransformation
            )
            dlg.setIconPixmap(pixmap)
        else:
            if dialog_icon == 'information':
                dlg.setIcon(dlg.Information)
            elif dialog_icon == 'warning':
                dlg.setIcon(dlg.Warning)
            elif dialog_icon == 'critical':
                dlg.setIcon(dlg.Critical)

        dlg.exec_()

    @staticmethod
    def question_dialog(parent=None, text='', title='Are you sure?',
                        dialog_icon=None, custom_icon=None):
        dlg = QtWidgets.QMessageBox(parent=parent)
        dlg.setWindowTitle(title)
        dlg.setInformativeText(text)
        dlg.setStandardButtons(
            QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No
        )

        if custom_icon:
            pixmap = QtGui.QPixmap(custom_icon).scaledToHeight(
                32, QtCore.Qt.SmoothTransformation
            )
            dlg.setIconPixmap(pixmap)
        else:
            if dialog_icon == 'information':
                dlg.setIcon(dlg.Information)
            elif dialog_icon == 'warning':
                dlg.setIcon(dlg.Warning)
            elif dialog_icon == 'critical':
                dlg.setIcon(dlg.Critical)

        result = dlg.exec_()
        return bool(result == QtWidgets.QMessageBox.Yes)
