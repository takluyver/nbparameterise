import os.path
import sys


import IPython.nbformat as nbformat
import tornado.ioloop
import tornado.web

from .code import extract_parameters, replace_definitions, execute_and_render
from .htmlform import build_form

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
        
        replace_definitions(self.application.nb, defined)
        html = execute_and_render(self.application.nb)
        self.write(html)


class NbparameteriseApplication(tornado.web.Application):
    def __init__(self, path):
        self.path = path
        with open(path) as f:
            self.nb = nbformat.read(f, as_version=4)
        
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
    application.listen(8888)
    print("Visit http://localhost:8888/")
    tornado.ioloop.IOLoop.instance().start()

if __name__ == "__main__":
    main()
