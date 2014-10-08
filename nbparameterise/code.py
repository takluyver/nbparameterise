import importlib
import re

from IPython.nbconvert.exporters.html import HTMLExporter
from IPython.nbconvert.preprocessors.execute import ExecutePreprocessor

class Input(object):
    def __init__(self, name, vtype, value=None):
        self.name = name
        self.type = vtype
        self.value = value

    def __repr__(self):
        params = [repr(self.name), self.type.__name__]
        if self.value is not None:
            params.append("value=%r" % self.value)
        return "Input(%s)" % ", ".join(params)

    def with_value(self, value):
        """Returns a copy with value set to a new value."""
        return type(self)(self.name, self.type, value)

def first_code_cell(nb):
    for cell in nb.worksheets[0].cells:
        if cell.cell_type == 'code':
            return cell

kernel_name_re = re.compile(r'\w+$')

def get_driver_module(nb):
    kernel_name = nb.metadata.get('kernelspec', {}).get('name', 'python3')
    assert kernel_name_re.match(kernel_name)
    return importlib.import_module('nbparameterise.code_drivers.%s' % kernel_name)

def extract_cell1_definitions(nb):
    drv = get_driver_module(nb)
    return list(drv.extract_definitions(first_code_cell(nb).input))

def replace_definitions(nb, values):
    drv = get_driver_module(nb)
    first_code_cell(nb).input = drv.build_definitions(values)

def execute_and_render(nb):
    resources = {}
    nb, resources = ExecutePreprocessor().preprocess(nb, resources)
    output, resources = HTMLExporter().from_notebook_node(nb, resources)
    return output