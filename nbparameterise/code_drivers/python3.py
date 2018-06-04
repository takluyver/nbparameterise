  GNU nano 2.3.1                               File: ../../../karabo/extern/lib/python3.4/site-packages/nbparameterise/code_drivers/python3.py                                                                     

import ast

import astcheck
import astsearch

from io import BytesIO
import tokenize

from ..code import Parameter

__all__ = ['extract_definitions', 'build_definitions']

def check_list(node):
    def bool_check(node):
        return isinstance(node, ast.NameConstant) and (node.value in (True, False))
    return all([(isinstance(n, (ast.Num, ast.Str))
                 or bool_check(n)) for n in node.elts])

def check_fillable_node(node, path):
    if isinstance(node, (ast.Num, ast.Str)):
        return
    elif (isinstance(node, ast.List)
          and isinstance(node.ctx, ast.Load) and check_list(node)):
        return
    elif isinstance(node, ast.NameConstant) and (node.value in (True, False)):
        return

    raise astcheck.ASTMismatch(path, node, 'number, string, list or boolean')

definition_pattern = ast.Assign(targets=[ast.Name()], value=check_fillable_node)

def type_and_value(node, comments={}):
    comment = comments.get(node.lineno, None)
    if isinstance(node, ast.Num):
        # int or float
        return type(node.n), node.n, comment
    elif isinstance(node, ast.Str):
        return str, node.s, comment
    elif isinstance(node, ast.List):
        return list, [type_and_value(n)[1] for n in node.elts]
    return bool, node.value, comment

def extract_comments(tokens):
    comments = {}
    for ttype, tstr, rowcol, _, _ in tokens:
        if ttype == tokenize.COMMENT:
           comments[rowcol[0]] = tstr
    return comments

def extract_definitions(cell):
    cell_ast = ast.parse(cell)
    cell_tokens = tokenize.tokenize(BytesIO(cell.encode('utf-8')).readline)
    comments = extract_comments(cell_tokens)
    for assign in astsearch.ASTPatternFinder(definition_pattern).scan_ast(cell_ast):
        yield Parameter(assign.targets[0].id, *type_and_value(assign.value, comments))

def build_definitions(inputs):
    return "\n".join("{0.name} = {0.value!r}".format(i) for i in inputs)