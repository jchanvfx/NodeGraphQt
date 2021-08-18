Node Embedded Widgets
#####################

Node embedded widgets are the widgets that can be embedded into a
:class:`NodeGraphQt.BaseNode` and displayed in the node graph.

See :ref:`Embedding Custom Widgets` example to adding your own widget into a node.

NodeBaseWidget
**************

.. autoclass:: NodeGraphQt.NodeBaseWidget
    :members:
    :exclude-members: node, setToolTip, type_, value, widget

-----

Below are builtin node widgets inherited from :class:`NodeGraphQt.NodeBaseWidget`

NodeCheckBox
************

.. autoclass:: NodeGraphQt.widgets.node_widgets.NodeCheckBox
    :members:
    :exclude-members: widget, type_

NodeComboBox
************

.. autoclass:: NodeGraphQt.widgets.node_widgets.NodeComboBox
    :members:
    :exclude-members: widget, type_

NodeLineEdit
************

.. autoclass:: NodeGraphQt.widgets.node_widgets.NodeLineEdit
    :members:
    :exclude-members: widget, type_

NodeFilePath
************

.. autoclass:: NodeGraphQt.widgets.node_widgets.NodeFilePath
    :members:
    :exclude-members: widget, type_

NodeFloatEdit
*************

.. autoclass:: NodeGraphQt.widgets.node_widgets.NodeFloatEdit
    :members:
    :exclude-members: widget, type_

NodeIntEdit
***********

.. autoclass:: NodeGraphQt.widgets.node_widgets.NodeIntEdit
    :members:
    :exclude-members: widget, type_
