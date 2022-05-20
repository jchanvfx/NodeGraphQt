Node Widgets
############

| Node widgets are the widgets that can be embedded into a
 :class:`NodeGraphQt.BaseNode` and displayed in the node graph.

| To create your own widget embedded in a node see the
 :ref:`Embedding Custom Widgets` example page.

NodeBaseWidget
**************

.. autoclass:: NodeGraphQt.NodeBaseWidget
    :members:
    :exclude-members: node, setToolTip, type_, value, widget

-----

.. note::
    Below are the classes for the :class:`NodeGraphQt.BaseNode` builtin
    functions:

     - ``QCheckBox``: :meth:`NodeGraphQt.BaseNode.add_checkbox`
     - ``QComboBox``: :meth:`NodeGraphQt.BaseNode.add_combo_menu`
     - ``QLineEdit``: :meth:`NodeGraphQt.BaseNode.add_text_input`


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
