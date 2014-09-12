import os.path
import sys


from IPython.nbformat import current as nbformat
import tornado.ioloop
import tornado.web

from .code import extract_cell1_definitions, replace_definitions, execute_and_render
from .htmlform import build_form

static_path = os.path.join(os.path.dirname(__file__), 'static')


class MainHandler(tornado.web.RequestHandler):
    def get(self):
        self.write(str(build_form(self.application.definitions, 
                                  self.application.nbname)))

class SubmissionHandler(tornado.web.RequestHandler):
    def post(self):
        names_values = []
        for name, valtype in self.application.definitions:
            if valtype is bool:
                value = (self.get_argument(name, default='off') == 'on')
            else:
                value = valtype(self.get_argument(name))
            names_values.append((name, value))
        
        replace_definitions(self.application.nb, names_values)
        html = execute_and_render(self.application.nb)
        self.write(html)


class NbparameteriseApplication(tornado.web.Application):
    def __init__(self, path):
        self.path = path
        with open(path) as f:
            self.nb = nbformat.read(f, 'ipynb')
        
        basename = os.path.basename(path)
        assert basename.endswith('.ipynb')
        self.nbname = basename[:-6]
        self.definitions = list(extract_cell1_definitions(self.nb))
        super().__init__([
            (r"/", MainHandler),
            (r"/submit", SubmissionHandler)
        ], static_path=static_path)


def main():
    application = NbparameteriseApplication(sys.argv[1])
    application.listen(8888)
    tornado.ioloop.IOLoop.instance().start()

if __name__ == "__main__":
    main()