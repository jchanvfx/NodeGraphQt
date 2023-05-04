Node Widgets
############

| Node widgets are the widgets that can be embedded into a
  :class:`NodeGraphQt.BaseNode` and displayed in the node graph.

| To create your own widget embedded in a node see the
  :ref:`Embedding Custom Widgets` example page.

**Classes:**

.. autosummary::
    NodeGraphQt.NodeBaseWidget
    NodeGraphQt.widgets.node_widgets.NodeCheckBox
    NodeGraphQt.widgets.node_widgets.NodeComboBox
    NodeGraphQt.widgets.node_widgets.NodeLineEdit

NodeBaseWidget
**************

.. autoclass:: NodeGraphQt.NodeBaseWidget
    :members:
    :exclude-members: staticMetaObject, node, setToolTip, type_, value, widget

NodeCheckBox
************

.. autoclass:: NodeGraphQt.widgets.node_widgets.NodeCheckBox
    :members:
    :exclude-members: staticMetaObject, widget, type_

NodeComboBox
************

.. autoclass:: NodeGraphQt.widgets.node_widgets.NodeComboBox
    :members:
    :exclude-members: staticMetaObject, widget, type_

NodeLineEdit
************

.. autoclass:: NodeGraphQt.widgets.node_widgets.NodeLineEdit
    :members:
    :exclude-members: staticMetaObject, widget, type_
