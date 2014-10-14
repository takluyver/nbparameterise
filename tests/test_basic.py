import os.path
import unittest

from IPython.nbformat import current as nbformat
from nbparameterise import code

samplenb = os.path.join(os.path.dirname(__file__), 'sample.ipynb')

class BasicTestCase(unittest.TestCase):
    def setUp(self):
        with open(samplenb) as f:
            self.nb = nbformat.read(f, 'ipynb')

        self.params = code.extract_parameters(self.nb)

    def test_extract(self):
        a = self.params[0]
        assert a.name == 'a'
        assert a.type == str
        assert a.value == "Some text"

        b = self.params[1]
        assert b.name == 'b'
        assert b.type == int
        assert b.value == 12

        c = self.params[2]
        assert c.name == 'c'
        assert c.type == float
        assert c.value == 14.0
        assert c.metadata['display_name'] == 'Sea'

        d = self.params[3]
        assert d.name == 'd'
        assert d.type == bool
        assert d.value == False

    def test_rebuild(self):
        from_form = [
            self.params[0].with_value("New text"),
            self.params[1].with_value(21),
            self.params[2].with_value(0.25),
            self.params[3].with_value(True),
        ]
        code.replace_definitions(self.nb, from_form)

        ns = {}
        exec(self.nb.worksheets[0].cells[0].input, ns)
        assert ns['a'] == "New text"
        assert ns['b'] == 21
        assert ns['c'] == 0.25
        assert ns['d'] == True
