import os.path
import sys


from IPython.nbformat import current as nbformat
import tornado.ioloop
import tornado.web

from .code import extract_cell1_definitions, replace_definitions, execute_and_render
from .htmlform import build_form

static_path = os.path.join(os.path.dirname(__file__), 'static')

def make_application(filename):    
    with open(filename) as f:
        nb = nbformat.read(f, 'ipynb')
    basename = os.path.basename(filename)
    assert basename.endswith('.ipynb')
    nbname = basename[:-6]
    
    definitions = list(extract_cell1_definitions(nb))
    
    class MainHandler(tornado.web.RequestHandler):
        def get(self):
            self.write(str(build_form(definitions, nbname)))
    
    class SubmissionHandler(tornado.web.RequestHandler):
        def post(self):
            names_values = []
            for name, valtype in definitions:
                if valtype is bool:
                    value = (self.get_argument(name, default='off') == 'on')
                else:
                    value = valtype(self.get_argument(name))
                names_values.append((name, value))
            
            replace_definitions(nb, names_values)
            html = execute_and_render(nb)
            self.write(html)
    
    return tornado.web.Application([
        (r"/", MainHandler),
        (r"/submit", SubmissionHandler)
    ], static_path=static_path)

def main():
    application = make_application(sys.argv[1])
    application.listen(8888)
    tornado.ioloop.IOLoop.instance().start()

if __name__ == "__main__":
    main()