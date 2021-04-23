#!/usr/bin/env python3
"""Present an HTML form for the parameters of a notebook, and run it on submission.

To use this example, run::

    python3 webapp.py "Stock display.ipynb"

The form fields are not hardcoded here; they are built from the notebook, so it
should build a suitable form for any notebook you run this with. Try it with
Fibonacci.ipynb as well.
"""
import os.path
import sys

from nbclient import execute
from nbconvert.exporters import HTMLExporter
import nbformat
import tornado.ioloop
import tornado.web

from nbparameterise import extract_parameters, replace_definitions
from htmlform import build_form

static_path = os.path.join(os.path.dirname(__file__), 'static')


class MainHandler(tornado.web.RequestHandler):
    def get(self):
        self.write(str(build_form(self.application.parameters,
                                  self.application.nbname)))

class SubmissionHandler(tornado.web.RequestHandler):
    def post(self):
        defined = []
        for v in self.application.parameters:
            if v.type is bool:
                inp = v.with_value(self.get_argument(v.name, default='off') == 'on')
            else:
                inp = v.with_value(v.type(self.get_argument(v.name)))
            defined.append(inp)

        nb = replace_definitions(self.application.nb, defined)
        nb = execute(nb, cwd=os.path.dirname(self.application.path))
        output, _ = HTMLExporter().from_notebook_node(nb)
        self.write(output)


class NbparameteriseApplication(tornado.web.Application):
    def __init__(self, path):
        self.path = path
        self.nb = nbformat.read(path, as_version=4)
        
        basename = os.path.basename(path)
        assert basename.endswith('.ipynb')
        self.nbname = basename[:-6]
        self.parameters = extract_parameters(self.nb)
        super().__init__([
            (r"/", MainHandler),
            (r"/submit", SubmissionHandler)
        ], static_path=static_path)


def main():
    application = NbparameteriseApplication(sys.argv[1])
    application.listen(3131)
    print("Visit http://localhost:3131/")
    tornado.ioloop.IOLoop.instance().start()

if __name__ == "__main__":
    main()
