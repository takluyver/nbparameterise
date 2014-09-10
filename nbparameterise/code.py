import ast
import sys

import astcheck
import astsearch
from IPython.nbconvert.exporters.html import HTMLExporter
from IPython.nbconvert.preprocessors.execute import ExecutePreprocessor
from IPython.nbformat import current as nbformat

def check_fillable_node(node, path):
    if isinstance(node, (ast.Num, ast.Str)):
        return
    elif isinstance(node, ast.NameConstant) and (node.value in (True, False)):
        return
    
    raise astcheck.ASTMismatch(path, node, 'number, string or boolean')

definition_pattern = ast.Assign(targets=[ast.Name()], value=check_fillable_node)

def find_type(node):
    if isinstance(node, ast.Num):
        return type(node.n)
    elif isinstance(node, ast.Str):
        return str
    return bool

def first_code_cell(nb):
    for cell in nb.worksheets[0].cells:
        if cell.cell_type == 'code':
            return cell

def extract_cell1_definitions(nb):
    cell1_ast = ast.parse(first_code_cell(nb).input)
    for assign in astsearch.ASTPatternFinder(definition_pattern).scan_ast(cell1_ast):
        yield assign.targets[0].id, find_type(assign.value)

def build_definitions(names_values):
    return "\n".join("{} = {!r}".format(n, v) for n,v in names_values)

def replace_definitions(nb, values):
    first_code_cell(nb).input = build_definitions(values)

def execute_and_render(nb):
    resources = {}
    nb, resources = ExecutePreprocessor().preprocess(nb, resources)
    output, resources = HTMLExporter().from_notebook_node(nb, resources)
    return output