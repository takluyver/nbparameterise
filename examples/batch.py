#!/usr/bin/env python3
"""Example of using nbparameterise API to substitute variables in 'batch mode'
"""

from nbparameterise import extract_parameters, parameter_values, replace_definitions
import nbformat
from nbconvert.exporters.notebook import NotebookExporter
from nbconvert.writers import FilesWriter

stock_names = ['YHOO', 'MSFT', 'GOOG']

with open("Stock display.ipynb") as f:
    nb = nbformat.read(f, as_version=4)

orig_parameters = extract_parameters(nb)

for name in stock_names:
    print("Running for stock", name)

    params = parameter_values(orig_parameters, stock=name)
    
    nb = replace_definitions(nb, params)

    # Save
    output, resources = NotebookExporter().from_notebook_node(nb, {})
    nbname = "Stock display %s" % name
    FilesWriter().write(output, resources, notebook_name=nbname)
