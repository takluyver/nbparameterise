"""Example of using nbparameterise API to substitute variables in 'batch mode'
"""

from nbparameterise import code
import nbformat
from nbconvert.preprocessors.execute import ExecutePreprocessor
from nbconvert.exporters.notebook import NotebookExporter
from nbconvert.writers import FilesWriter

stock_names = ['YHOO', 'MSFT', 'GOOG']

with open("Stock display.ipynb") as f:
    nb = nbformat.read(f, as_version=4)

definitions = code.extract_parameters(nb)

for name in stock_names:
    print("Rendering for stock", name)

    defined = []
    for inp in definitions:
        if inp.name =='stock':
            # Fill in the current value
            defined.append(inp.with_value(name))
        else:
            defined.append(inp)
    
    code.replace_definitions(nb, defined)

    # Run
    resources = {}
    nb, resources = ExecutePreprocessor().preprocess(nb, resources)

    # Save
    output, resources = NotebookExporter().from_notebook_node(nb, resources)
    nbname = "Stock display %s" % name
    FilesWriter().write(output, resources, notebook_name=nbname)
