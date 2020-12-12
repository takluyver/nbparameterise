#!/usr/bin/env python3
"""Example of using nbparameterise API to substitute variables in 'batch mode'
"""

from nbclient import execute
import nbformat
from nbparameterise import extract_parameters, parameter_values, replace_definitions

stock_names = ['AAPL', 'MSFT', 'GOOG']

nb = nbformat.read("Stock display.ipynb", as_version=4)

orig_parameters = extract_parameters(nb)

for name in stock_names:
    print("Running for stock", name)

    # Update the parameters and run the notebook
    params = parameter_values(orig_parameters, stock=name)
    new_nb = replace_definitions(nb, params)
    execute(new_nb)

    # Save
    with open("Stock display %s.ipynb" % name, 'w') as f:
        nbformat.write(new_nb, f)
