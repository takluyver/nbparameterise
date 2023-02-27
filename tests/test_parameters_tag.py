import os.path

import pytest

import nbformat
from nbparameterise import (
    extract_parameters, replace_definitions, Parameter, get_parameter_cell,
)

samplenb = os.path.join(os.path.dirname(__file__), 'sample_parameters_tag.ipynb')

@pytest.fixture()
def tagged_cell_nb():
    return nbformat.read(samplenb, as_version=4)


def test_extract(tagged_cell_nb):
    # Tag is not case-sensitive
    params =  extract_parameters(tagged_cell_nb, tag='paraMeters')
    assert params == [
        Parameter('a', str, "Some text"),
        Parameter('b', int, 12),
        Parameter('b2', int, -7),
        Parameter('c', float, 14.0),
        Parameter('d', bool, False),
        Parameter('e', list, [0, 1.0, True, "text", [0, 1]]),
        Parameter('f', dict, {0: 0, "item": True, "dict": {0: "text"}}),
    ]
    assert params[4].comment == '# comment:bool'
    assert params[6].comment == '# comment:dict'
    assert params[3].metadata == {'display_name': 'Sea'}

def test_rebuild(tagged_cell_nb):
    params = extract_parameters(tagged_cell_nb)
    from_form = [
        params[0].with_value("New text"),
        params[1].with_value(21),
        params[2].with_value(-3),
        params[3].with_value(0.25),
        params[4].with_value(True),
    ]
    nb = replace_definitions(tagged_cell_nb, from_form, execute=False)
    cell = get_parameter_cell(nb, 'ParametErs')  # Not case-sensitive
    assert "# comment:bool" in cell.source

    ns = {}
    exec(cell.source, ns)
    assert ns['a'] == "New text"
    assert ns['b'] == 21
    assert ns['b2'] == -3
    assert ns['c'] == 0.25
    assert ns['d'] == True

