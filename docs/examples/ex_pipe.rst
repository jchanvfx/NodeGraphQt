Pipe Overview
#############

Layout Styles
*************

.. image:: ../_images/pipe_layout_types.gif
        :width: 650px

The :class:`NodeGraphQt.NodeGraph` class has 3 different pipe layout styles as
shown above this can be set easily with the :meth:`NodeGraphQt.NodeGraph.set_pipe_style`
function.

|
| Here's a example snippet for setting the pipe layout style to be "angled".

.. code-block:: python
    :linenos:

    from NodeGraphQt import NodeGraph
    from NodeGraphQt.constants import PipeLayoutEnum

    graph = NodeGraph()
    graph.set_pipe_style(PipeLayoutEnum.ANGLE.value)

| There are 3 different pipe layout styles see: :attr:`NodeGraphQt.constants.PipeLayoutEnum`

.. note::

    If you've set up your node graph with the :meth:`NodeGraph.set_context_menu_from_file`
    function and the example
    `example JSON <https://github.com/jchanvfx/NodeGraphQt/blob/master/examples/hotkeys/hotkeys.json>`_
    then you'll already have the actions to set the pipe layout under the
    "Pipes" menu.

    .. image:: ../_images/pipe_layout_menu.png


Layout Direction
****************

The :class:`NodeGraphQt.NodeGraph` pipes can also be set with a vertical layout
direction with the  :meth:`NodeGraphQt.NodeGraph.set_layout_direction` function.

.. image:: ../_images/vertical_layout.png
