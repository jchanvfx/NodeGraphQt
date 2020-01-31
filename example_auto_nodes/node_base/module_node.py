import inspect
from .auto_node import AutoNode


def _get_functions_from_module(module, function_dict, max_depth=1, module_name=None):
    funcs = [func for func in dir(module) if not func.startswith('_')]

    if not module_name:
        module_name = module.__name__

    for func in funcs:
        if func in ["sys","os"]:
            continue

        new_module_name = module_name + "." + func

        obj = getattr(module, func)
        if inspect.ismodule(obj):
            if len(new_module_name.split(".")) > max_depth:
                continue
            _get_functions_from_module(obj, function_dict, max_depth, new_module_name)
        else:
            function_dict[new_module_name] = obj


def get_functions_from_module(module, max_depth=1):
    function_dict = {}
    _get_functions_from_module(module, function_dict, max_depth)
    return function_dict


def get_functions_from_type(object_type):
    type_functions = [func for func in dir(object_type) if not func.startswith('_')]
    function_dict = {}
    for func in type_functions:
        function_dict[func] = getattr(object_type, func)
    return function_dict


class ModuleNode(AutoNode):
    """
    module node.
    """

    module_functions = {}

    def __init__(self,defaultInputType=None,defaultOutputType=None):
        super(ModuleNode, self).__init__(defaultInputType,defaultOutputType)
        self.add_combo_menu('funcs', 'Functions', items=list(self.module_functions.keys()))

        # switch math function type
        self.view.widgets['funcs'].value_changed.connect(self.addFunction)
        self.add_output('output')
        self.create_property('output', None)

        self.view.widgets['funcs'].widget.setCurrentIndex(0)
        self.addFunction(None, self.view.widgets['funcs'].widget.currentText())

    def is_function(self,obj):
        if inspect.isfunction(self.func) or inspect.isbuiltin(self.func):
            return True
        elif "method" in type(obj).__name__  or "function" in type(obj).__name__:
            return True

        return False

    def addFunction(self, prop, func):
        """
        Create inputs based on functions arguments.
        """

        self.func = self.module_functions[func]

        args = []
        if self.is_function(self.func):
            try:
                args = inspect.getfullargspec(self.func).args
            except:
                args = []

        self.process_args(args)

    def process_args(self,in_args, out_args = None):
        for arg in in_args:
            if arg not in self.inputs().keys():
                self.add_input(arg)

        for inPort in self.input_ports():
            if inPort.name() in in_args:
                if not inPort.visible():
                    inPort.set_visible(True)
            else:
                inPort.set_visible(False)

        if out_args is None:
            return

        for arg in out_args:
            if arg not in self.outputs().keys():
                self.add_output(arg)

        for outPort in self.output_ports():
            if outPort.name() in out_args:
                if not outPort.visible():
                    outPort.set_visible(True)
            else:
                outPort.set_visible(False)

    def run(self):
        """
        Evaluate all entries, pass them as arguments of the
        chosen function.
        """
        args = []
        for port in self.input_ports():
            if not port.visible():
                continue
            data = self.getInputData(port)
            if data is not None:
                args.append(data)
            elif self.defaultValue is not None:
                return self.defaultValue

        try:
            # Execute function with arguments.
            if self.is_function(self.func):
                data = self.func(*args)
            else:
                data = self.func
            if data is None:
                data = args[0]
            self.set_property('output', data)
        except Exception as error:
            self.error("Error : %s" % str(error))
