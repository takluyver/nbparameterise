Choose input values for a notebook, and nbparameterise will run it and render to HTML

*Experimental, alpha level code*

To use it, create a notebook, where the first code cell contains simple variable
assignments of strings, numbers and booleans. Other cells after this should
do computation based on these values, and display the results. See 'Stock display'
for an example.

At the command line::

    python3 -m nbparameterise "Stock display.ipynb"


Nbparameterise is written in Python 3, but it can handle running notebooks in
Python 2, so long as they were saved by a recent enough version of IPython.
