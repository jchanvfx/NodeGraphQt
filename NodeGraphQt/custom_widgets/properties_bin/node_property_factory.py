from NodeGraphQt.constants import NodePropWidgetEnum
from .custom_widget_color_picker import PropColorPickerRGB, PropColorPickerRGBA
from .custom_widget_file_paths import PropFilePath, PropFileSavePath
from .custom_widget_slider import PropSlider, PropDoubleSlider
from .custom_widget_value_edit import FloatValueEdit, IntValueEdit
from .custom_widget_vectors import PropVector2, PropVector3, PropVector4
from .prop_widgets_base import (
    PropLabel,
    PropLineEdit,
    PropTextEdit,
    PropComboBox,
    PropCheckBox,
    PropSpinBox,
    PropDoubleSpinBox
)


class NodePropertyWidgetFactory(object):
    """
    Node property widget factory for mapping the corresponding property widget
    to the Properties bin.
    """

    def __init__(self):
        self._widget_mapping = {
            NodePropWidgetEnum.HIDDEN.value: None,
            # base widgets.
            NodePropWidgetEnum.QLABEL.value: PropLabel,
            NodePropWidgetEnum.QLINE_EDIT.value: PropLineEdit,
            NodePropWidgetEnum.QTEXT_EDIT.value: PropTextEdit,
            NodePropWidgetEnum.QCOMBO_BOX.value: PropComboBox,
            NodePropWidgetEnum.QCHECK_BOX.value: PropCheckBox,
            NodePropWidgetEnum.QSPIN_BOX.value: PropSpinBox,
            NodePropWidgetEnum.QDOUBLESPIN_BOX.value: PropDoubleSpinBox,
            # custom widgets.
            NodePropWidgetEnum.COLOR_PICKER.value: PropColorPickerRGB,
            NodePropWidgetEnum.COLOR4_PICKER.value: PropColorPickerRGBA,
            NodePropWidgetEnum.SLIDER.value: PropSlider,
            NodePropWidgetEnum.DOUBLE_SLIDER.value: PropDoubleSlider,
            NodePropWidgetEnum.FILE_OPEN.value: PropFilePath,
            NodePropWidgetEnum.FILE_SAVE.value: PropFileSavePath,
            NodePropWidgetEnum.VECTOR2.value: PropVector2,
            NodePropWidgetEnum.VECTOR3.value: PropVector3,
            NodePropWidgetEnum.VECTOR4.value: PropVector4,
            NodePropWidgetEnum.FLOAT.value: FloatValueEdit,
            NodePropWidgetEnum.INT.value: IntValueEdit,
        }

    def get_widget(self, widget_type=NodePropWidgetEnum.HIDDEN.value):
        """
        Return a new instance of a node property widget.

        Args:
            widget_type (int): widget type index.

        Returns:
            BaseProperty: node property widget.
        """
        if widget_type in self._widget_mapping:
            return self._widget_mapping[widget_type]()
