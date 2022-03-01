import os.path
import unittest

import nbformat
from nbparameterise import code, Parameter,get_parameter_cell

samplenb = os.path.join(os.path.dirname(__file__), 'sample.ipynb')

class BasicTestCase(unittest.TestCase):
    def setUp(self):
        with open(samplenb) as f:
            self.nb = nbformat.read(f, as_version=4)

        self.params = code.extract_parameters(self.nb)
        self.param_dict = code.extract_parameter_dict(self.nb)

    def test_extract(self):
        assert self.params == [
            Parameter('a', str, "Some text"),
            Parameter('b', int, 12),
            Parameter('b2', int, -7),
            Parameter('c', float, 14.0),
            Parameter('d', bool, False),
            Parameter('e', list, [0, 1.0, True, "text", [0, 1]]),
            Parameter('f', dict, {0: 0, "item": True, "dict": {0: "text"}}),
            Parameter('café', str, "καφές"),
        ]
        assert self.params[4].comment == '# comment:bool'
        assert self.params[6].comment == '# comment:dict'
        assert self.params[3].metadata == {'display_name': 'Sea'}

    def test_extract_dict(self):
        assert self.param_dict == {
            'a': Parameter('a', str, "Some text"),
            'b': Parameter('b', int, 12),
            'b2': Parameter('b2', int, -7),
            'c': Parameter('c', float, 14.0),
            'd': Parameter('d', bool, False),
            'e': Parameter('e', list, [0, 1.0, True, "text", [0, 1]]),
            'f': Parameter('f', dict, {0: 0, "item": True, "dict": {0: "text"}}),
            'café': Parameter('café', str, "καφές")
        }

    def test_rebuild(self):
        from_form = [
            self.params[0].with_value("New text"),
            self.params[1].with_value(21),
            self.params[2].with_value(-3),
            self.params[3].with_value(0.25),
            self.params[4].with_value(True),
        ]
        nb = code.replace_definitions(self.nb, from_form, execute=False)
        cell = get_parameter_cell(nb)
        assert "# comment:bool" in cell.source

        ns = {}
        exec(cell.source, ns)
        assert ns['a'] == "New text"
        assert ns['b'] == 21
        assert ns['b2'] == -3
        assert ns['c'] == 0.25
        assert ns['d'] == True
        assert ns['café'] == "καφές"

        # Function & non parameter assignment should be preserved
        assert ns['func']() == 0.25
        assert ns['other_assignment'] == 21 ** 2

    def test_rebuild_from_dict(self):
        new_params = self.param_dict.copy()
        new_params['c'] = self.param_dict['c'].with_value(0.75)
        new_params['e'] = self.param_dict['e'].with_value([5, 6, 7, 8])
        new_params['thé'] = Parameter('thé', str, value="चाय")

        nb = code.replace_definitions(self.nb, new_params, execute=False)

        assert "# comment:bool" in nb.cells[0].source

        ns = {}
        exec(nb.cells[0].source, ns)
        assert ns['a'] == "Some text"
        assert ns['b'] == 12
        assert ns['c'] == 0.75
        assert ns['e'] == [5, 6, 7, 8]
        assert ns['café'] == "καφές"
        assert ns['thé'] == "चाय"

        # Function & non parameter assignment should be preserved
        assert ns['func']() == 0.75
        assert ns['other_assignment'] == 12 ** 2

    def test_new_values(self):
        params = code.parameter_values(self.params,
            a = "New text",
            c = 12.0
        )

        assert [p.name for p in params] == ['a', 'b', 'b2', 'c', 'd', 'e', 'f', 'café']

        assert params[0].value == 'New text'
        assert params[1].value == 12
        assert params[3].value == 12.0
        assert isinstance(params[3].value, float)
        assert params[4].value == False

    def test_new_values_dict(self):
        new_dict = code.parameter_values(self.param_dict,
            a = "New text",
            c = 12.0,
            z = 54,  # Extra parameters ignored by default
        )

        assert new_dict == {
            'a': Parameter('a', str, "New text"),
            'b': Parameter('b', int, 12),
            'b2': Parameter('b2', int, -7),
            'c': Parameter('c', float, 12.0),
            'd': Parameter('d', bool, False),
            'e': Parameter('e', list, [0, 1.0, True, "text", [0, 1]]),
            'f': Parameter('f', dict, {0: 0, "item": True, "dict": {0: "text"}}),
            'café': Parameter('café', str, "καφές")
        }

    def test_add_param(self):
        new_dict = code.parameter_values(self.param_dict, z=54, new='add')
        assert set(new_dict) == {'a', 'b', 'b2', 'c', 'd', 'e', 'f', 'café', 'z'}
        assert new_dict['z'] == Parameter('z', int, 54)

    def test_err_new_param(self):
        with self.assertRaises(KeyError):
            new_dict = code.parameter_values(self.param_dict, z=54, new='error')

def test_parameter_repr():
    p = Parameter('days', int, 7, metadata={'foo': 'boo'}, comment='# Days to show')
    p2 = eval(repr(p))  # The repr should eval to an identical Parameter
    assert p2 == p
    assert p2.metadata == p.metadata
    assert p2.comment == p.comment
