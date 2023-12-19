import copy
import importlib
import re
from warnings import warn


class Parameter(object):
    def __init__(self, name, vtype, value=None, metadata=None, comment=None):
        self.name = name
        self.type = vtype
        self.value = value
        self.metadata = metadata or {}
        self.comment = comment

    def __repr__(self):
        params = [repr(self.name), self.type.__name__]
        if self.value is not None:
            params.append(f"value={self.value!r}")
        if self.metadata:
            params.append(f"metadata={self.metadata!r}")
        if self.comment:
            params.append(f"comment={self.comment!r}")
        return "Parameter(%s)" % ", ".join(params)

    def with_value(self, value):
        """Returns a copy with value set to a new value."""
        return type(self)(
            self.name, self.type, value,  self.metadata or None, self.comment
        )

    def __eq__(self, other):
        if isinstance(other, Parameter):
            return (
                self.name == other.name
                and self.type == other.type
                and self.value == other.value
            )

def get_parameter_cell(nb, tag='parameters'):
    cell = find_first_tagged_cell(nb, tag)
    if cell is None:
        cell = first_code_cell(nb)
    return cell

def find_first_tagged_cell(nb, tag):
    tag = tag.lower()
    for cell in nb.cells:
        if cell.cell_type == 'code':
            tags = cell.get('metadata', {}).get('tags', [])
            if any([i.lower() == tag for i in tags]):
                return cell


def first_code_cell(nb):
    for cell in nb.cells:
        if cell.cell_type == 'code':
            return cell

kernel_name_re = re.compile(r'\w+$')

def get_driver_module(nb, override=None):
    if override:
        module_name = override
    else:
        module_name = nb.metadata.get('language_info', {}).get('name', 'python')
    assert kernel_name_re.match(module_name)
    return importlib.import_module('nbparameterise.code_drivers.%s' % module_name)

def extract_parameter_dict(nb, lang=None, tag='Parameters'):
    """Returns a dictionary of Parameter objects derived from the notebook.

    This looks for assignments (like 'n = 50') in the first code cell of the
    notebook, or the first cell with a 'parameters' tag. The parameters may also
    have some metadata stored in the notebook metadata; this will be attached as
    the .metadata instance on each one.

    *lang* may be used to override the kernel name embedded in the notebook. For
    now, nbparameterise only handles 'python'.

    *tag* specifies the cell tag which it will look for, with case-insensitive
    matching. If no code cell has the tag, it will take the first code cell.
    """
    params = extract_parameters(nb, lang, tag=tag)
    return {p.name: p for p in params}

def extract_parameters(nb, lang=None, tag='Parameters'):
    """Returns a list of Parameter instances derived from the notebook.

    This looks for assignments (like 'n = 50') in the first code cell of the
    notebook, or the first cell with a 'parameters' tag. The parameters may also
    have some metadata stored in the notebook metadata; this will be attached as
    the .metadata instance on each one.

    *lang* may be used to override the kernel name embedded in the notebook. For
    now, nbparameterise only handles 'python'.

    *tag* specifies the cell tag which it will look for, with case-insensitive
    matching. If no code cell has the tag, it will take the first code cell.
    """
    drv = get_driver_module(nb, override=lang)
    cell = get_parameter_cell(nb,tag)

    params = list(drv.extract_definitions(cell.source))

    # Add extra info from notebook metadata
    for param in params:
        param.metadata  = nb.metadata.get('parameterise', {}).get(param.name, {})

    return params

def parameter_values(params, new_values=None, new='ignore', **kwargs):
    """Return a new parameter list/dict, substituting values from kwargs.

    Usage example::

        params = parameter_values(params,
            stock='GOOG',
            days_back=300
        )

    Any parameters not supplied will keep their original value.
    Names not already in params are ignored by default, but can be added with
    ``new='add'`` or cause an error with ``new='error'``.

    This can be used with either a dict from :func:`extract_parameter_dict`
    or a list from :func:`extract_parameters`. It will return the corresponding
    container type.
    """
    if new not in {'ignore', 'add', 'error'}:
        raise ValueError("new= must be one of 'ignore'/'add'/'error'")
    new_values = (new_values or {}).copy()
    new_values.update(kwargs)

    if isinstance(params, dict):
        new_list = parameter_values(params.values(), new_values, new=new)
        return {p.name: p for p in new_list}

    res = [p.with_value(new_values[p.name]) if p.name in new_values else p
           for p in params]

    new_keys = set(new_values) - {p.name for p in params}
    if new == 'error':
        if new_keys:
            raise KeyError(f"Unexpected keys: {sorted(new_keys)}")
    elif new == 'add':
        for k in new_keys:
            value = new_values[k]
            res.append(Parameter(k, type(value), value))

    return res

def replace_definitions(nb, values, execute=False, execute_resources=None,
                        lang=None, *, comments=True, tag='Parameters'):
    """Return a copy of nb with the parameter cell defining the given parameters.

    values should be a dict (from :func:`extract_parameter_dict`) or a list
    (from :func:`extract_parameters`) of :class:`Parameter` objects,
    with their .value attribute set to the desired value.

    If execute is True, the notebook is executed with the new values.
    execute_resources is passed to nbconvert.ExecutePreprocessor; it's a dict,
    and if possible should contain a 'path' key for the working directory in
    which to run the notebook.

    *lang* may be used to override the kernel name embedded in the notebook. For
    now, nbparameterise only handles 'python3' and 'python2'.

    *tag* specifies the cell tag which the parameter cell should have, with
    case-insensitive matching. If no code cell has the tag, it will replace the
    first code cell.
    """
    if isinstance(values, list):
        values = {p.name: p for p in values}

    if not comments:
        warn("comments=False is now ignored", stacklevel=2)

    nb = copy.deepcopy(nb)

    drv = get_driver_module(nb, override=lang)
    cell = get_parameter_cell(nb, tag)
    cell.source = drv.build_definitions(values, prev_code=cell.source)
    if execute:
        warn("execute=True is deprecated, use nbclient instead", stacklevel=2)
        from nbconvert.preprocessors import ExecutePreprocessor
        resources = execute_resources or {}
        nb, resources = ExecutePreprocessor().preprocess(nb, resources)
    return nb
