#!/usr/bin/env python3
"""Example of using nbparameterise API to substitute variables in 'batch mode'
"""

from nbparameterise import extract_parameters, parameter_values, replace_definitions
import nbformat

stock_names = ['YHOO', 'MSFT', 'GOOG']

with open("Stock display.ipynb") as f:
    nb = nbformat.read(f, as_version=4)

orig_parameters = extract_parameters(nb)

for name in stock_names:
    print("Running for stock", name)

    # Update the parameters and run the notebook
    params = parameter_values(orig_parameters, stock=name)
    new_nb = replace_definitions(nb, params)

    # Save
    with open("Stock display %s.ipynb" % name, 'w') as f:
        nbformat.write(new_nb, f)
