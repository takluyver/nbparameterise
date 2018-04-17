import copy
import importlib
import re

from nbconvert.preprocessors import ExecutePreprocessor

class Parameter(object):
    def __init__(self, name, vtype, value=None, metadata=None):
        self.name = name
        self.type = vtype
        self.value = value
        self.metadata = metadata or {}

    def __repr__(self):
        params = [repr(self.name), self.type.__name__]
        if self.value is not None:
            params.append("value=%r" % self.value)
        return "Parameter(%s)" % ", ".join(params)

    def with_value(self, value):
        """Returns a copy with value set to a new value."""
        return type(self)(self.name, self.type, value, self.metadata or None)

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

def extract_parameters(nb, lang=None):
    """Returns a list of Parameter instances derived from the notebook.

    This looks for assignments (like 'n = 50') in the first code cell of the
    notebook. The parameters may also have some metadata stored in the notebook
    metadata; this will be attached as the .metadata instance on each one.

    lang may be used to override the kernel name embedded in the notebook. For
    now, nbparameterise only handles 'python3' and 'python2'.
    """
    drv = get_driver_module(nb, override=lang)
    params = list(drv.extract_definitions(first_code_cell(nb).source))

    # Add extra info from notebook metadata
    for param in params:
        param.metadata  = nb.metadata.get('parameterise', {}).get(param.name, {})

    return params

def parameter_values(params, **kwargs):
    """Return a copy of the parameter list, substituting values from kwargs.

    Usage example::

        params = parameter_values(params,
            stock='GOOG',
            days_back=300
        )

    Any parameters not supplied will keep their original value.
    """
    res = []
    for p in params:
        if p.name in kwargs:
            res.append(p.with_value(kwargs[p.name]))
        else:
            res.append(p)
    return res

def replace_definitions(nb, values, execute=True, execute_resources=None,
                        lang=None):
    """Return a copy of nb with the first code cell defining the given parameters.

    values should be a list of Parameter objects (as returned by extract_parameters),
    with their .value attribute set to the desired value.

    If execute is True, the notebook is executed with the new values.
    execute_resources is passed to nbconvert.ExecutePreprocessor; it's a dict,
    and if possible should contain a 'path' key for the working directory in
    which to run the notebook.

    lang may be used to override the kernel name embedded in the notebook. For
    now, nbparameterise only handles 'python3' and 'python2'.
    """
    nb = copy.deepcopy(nb)
    drv = get_driver_module(nb, override=lang)
    first_code_cell(nb).source = drv.build_definitions(values)
    if execute:
        resources = execute_resources or {}
        nb, resources = ExecutePreprocessor().preprocess(nb, resources)
    return nb
