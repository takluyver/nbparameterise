import ast

import astcheck
import astsearch

from io import StringIO
import tokenize

from ..code import Parameter

__all__ = ['extract_definitions', 'build_definitions']

def check_list(node):
    def bool_check(node):
        return isinstance(node, ast.NameConstant) and (node.value in (True, False))
    def neg_check(node):
        return isinstance(node.operand, ast.Num) if isinstance(node, ast.UnaryOp) else False
    return all([(isinstance(n, (ast.Num, ast.Str)) 
                 or bool_check(n) or neg_check(n)) for n in node.elts])

def check_fillable_node(node, path):
    if isinstance(node, (ast.Num, ast.Str)):
        return
    elif isinstance(node, ast.UnaryOp) and isinstance(node.operand, ast.Num):
        return
    elif (isinstance(node, ast.List) 
          and isinstance(node.ctx, ast.Load) and check_list(node)):
        return
    elif isinstance(node, ast.NameConstant) and (node.value in (True, False)):
        return
    elif isinstance(node, ast.List):
        for n in node.elts:
            check_fillable_node(n, path)
        return
    elif isinstance(node, ast.Dict):
        for n in node.keys:
            check_fillable_node(n, path)
        for n in node.values:
            check_fillable_node(n, path)
        return
    
    raise astcheck.ASTMismatch(path, node, 'number, string, boolean, list or dict')

definition_pattern = ast.Assign(targets=[ast.Name()], value=check_fillable_node)

def type_and_value(node, comments={}):
    comment = comments.get(node.lineno, None)
    if isinstance(node, ast.Num):
        # int or float
        return type(node.n), node.n, comment
    elif isinstance(node, ast.Str):
        return str, node.s, comment
    elif isinstance(node, ast.List):
        return list, [type_and_value(n)[1] for n in node.elts], comment
    elif isinstance(node, ast.NameConstant) and (node.value in (True, False)):
        return bool, node.value, comment
    elif isinstance(node, ast.Dict):
        return dict, {type_and_value(node.keys[i])[1]: type_and_value(node.values[i])[1] for i in range(len(node.keys))}, comment
    elif isinstance(node, ast.UnaryOp):
        def apply_op(v, op):
            if isinstance(op, ast.USub):
               return -v
            elif isinstance(op, ast.UAdd):
               return v
            elif isinstance(op, ast.Not):
               return not v
            elif isinstance(op, ast.Invert):
               return ~v
        return type(node.operand.n), apply_op(node.operand.n, node.op), comment
    return bool, node.value, comment

def extract_comments(cell: str):
    comments = {}
    tokens = tokenize.generate_tokens(StringIO(cell).readline)
    for ttype, tstr, rowcol, _, _ in tokens:
        if ttype == tokenize.COMMENT:
           comments[rowcol[0]] = tstr
    return comments

def extract_definitions(cell):
    cell_ast = ast.parse(cell)
    comments = extract_comments(cell)
    for assign in astsearch.ASTPatternFinder(definition_pattern).scan_ast(cell_ast):
        typ, val, comment = type_and_value(assign.value, comments)
        yield Parameter(assign.targets[0].id, typ, val, comment=comment)

def build_definitions(inputs, comments=True):
    defs = []
    for param in inputs:
        s = f"{param.name} = {param.value!r}"
        if comments and param.comment:
            comment = param.comment if param.comment.startswith('#') \
                else '# ' + param.comment.lstrip()
            s +=     f"  {comment}"
        defs.append(s)
    return "\n".join(defs)
