import ast

import astcheck
import astsearch
from IPython.nbconvert.exporters.html import HTMLExporter
from IPython.nbconvert.preprocessors.execute import ExecutePreprocessor

class Input(object):
    def __init__(self, name, vtype, value=None):
        self.name = name
        self.type = vtype
        self.value = value

    def with_value(self, value):
        """Returns a copy with value set to a new value."""
        return type(self)(self.name, self.type, value)

def check_fillable_node(node, path):
    if isinstance(node, (ast.Num, ast.Str)):
        return
    elif isinstance(node, ast.NameConstant) and (node.value in (True, False)):
        return
    
    raise astcheck.ASTMismatch(path, node, 'number, string or boolean')

definition_pattern = ast.Assign(targets=[ast.Name()], value=check_fillable_node)

def type_and_value(node):
    if isinstance(node, ast.Num):
        # int or float
        return type(node.n), node.n
    elif isinstance(node, ast.Str):
        return str, node.s
    return (bool, node.value)

def first_code_cell(nb):
    for cell in nb.worksheets[0].cells:
        if cell.cell_type == 'code':
            return cell

def extract_definitions(cell):
    cell_ast = ast.parse(cell)
    for assign in astsearch.ASTPatternFinder(definition_pattern).scan_ast(cell_ast):
        yield Input(assign.targets[0].id, *type_and_value(assign.value))

def extract_cell1_definitions(nb):
    return extract_definitions(first_code_cell(nb).input)

def build_definitions(inputs):
    return "\n".join("{0.name} = {0.value!r}".format(i) for i in inputs)

def replace_definitions(nb, values):
    first_code_cell(nb).input = build_definitions(values)

def execute_and_render(nb):
    resources = {}
    nb, resources = ExecutePreprocessor().preprocess(nb, resources)
    output, resources = HTMLExporter().from_notebook_node(nb, resources)
    return output