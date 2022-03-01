import os.path
import unittest

import nbformat
from nbparameterise import code, Parameter,get_parameter_cell

samplenb = os.path.join(os.path.dirname(__file__), 'sample_parameters_tag.ipynb')

class BasicParameterTestCase(unittest.TestCase):
    def setUp(self):
        with open(samplenb) as f:
            self.nb = nbformat.read(f, as_version=4)

        self.params = code.extract_parameters(self.nb)

    def test_extract(self):
        assert self.params == [
            Parameter('a', str, "Some text"),
            Parameter('b', int, 12),
            Parameter('b2', int, -7),
            Parameter('c', float, 14.0),
            Parameter('d', bool, False),
            Parameter('e', list, [0, 1.0, True, "text", [0, 1]]),
            Parameter('f', dict, {0: 0, "item": True, "dict": {0: "text"}}),
        ]
        assert self.params[4].comment == '# comment:bool'
        assert self.params[6].comment == '# comment:dict'
        assert self.params[3].metadata == {'display_name': 'Sea'}

    def test_rebuild(self):
        from_form = [
            self.params[0].with_value("New text"),
            self.params[1].with_value(21),
            self.params[2].with_value(-3),
            self.params[3].with_value(0.25),
            self.params[4].with_value(True),
        ]
        nb = code.replace_definitions(self.nb, from_form, execute=False)
        cell = get_parameter_cell(nb, 'ParametErs')  # Not case sensitive
        assert "# comment:bool" in cell.source

        ns = {}
        exec(cell.source, ns)
        assert ns['a'] == "New text"
        assert ns['b'] == 21
        assert ns['b2'] == -3
        assert ns['c'] == 0.25
        assert ns['d'] == True

