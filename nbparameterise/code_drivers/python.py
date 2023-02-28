import ast
import tokenize
from io import StringIO

import astcheck

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

definition_pattern = astcheck.single_assign(target=ast.Name(), value=check_fillable_node)

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

def find_assignments(cell):
    cell_ast = ast.parse(cell)

    # We only want global assignments, so we're not walking the AST here.
    for stmt in cell_ast.body:
        if astcheck.is_ast_like(stmt, definition_pattern):
            if isinstance(stmt, ast.AnnAssign):
                name = stmt.target.id
            else:  # ast.Assign
                name = stmt.targets[0].id
            yield name, stmt

def extract_definitions(cell):
    comments = extract_comments(cell)
    for name, stmt in find_assignments(cell):
        typ, val, comment = type_and_value(stmt.value, comments)
        yield Parameter(name, typ, val, comment=comment)


def build_definitions(params: dict, prev_code):
    """Rebuild code with modified parameters

    This function for Python >= 3.8 (?) preserves the existing code structure
    & comments, only replacing assignment values within the code.
    """
    # [end_]col_offset count UTF-8 bytes, so we encode the code here and decode
    # again after slicing.
    # Stick None in to allow 1-based line indexing
    old_lines = [None] + prev_code.encode().splitlines(keepends=True)
    from_line, from_col = 1, 0
    vars_used = set()
    output = []
    for name, stmt in find_assignments(prev_code):
        if name not in params:
            continue  # Leave the existing value

        vars_used.add(name)

        vn = stmt.value
        if vn.lineno == from_line: # Same line as last value we replaced
            output.append(old_lines[from_line][from_col:vn.col_offset].decode())
        else:  # On a new line
            output.append(old_lines[from_line][from_col:].decode())
            output.extend([l.decode() for l in old_lines[from_line+1 : vn.lineno]])
            output.append(old_lines[vn.lineno][:vn.col_offset].decode())
        from_line, from_col = vn.end_lineno, vn.end_col_offset

        # Substitute in the new value for the variable
        output.append(repr(params[name].value))

    # Copy across any remaining code to the end of the cell
    output.append(old_lines[from_line][from_col:].decode())
    output.extend([l.decode() for l in old_lines[from_line+1 :]])

    # Add in any variables for which we have a value but weren't in the code
    unused_vars = set(params) - vars_used
    if unused_vars:
        output.append('\n\n')
        for name in unused_vars:
            output.append(f"{name} = {params[name].value!r}\n")

    return ''.join(output)

