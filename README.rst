This is a tool to run notebooks with input values. When you write the notebook,
these are defined in the first code cell - or a cell with a 'parameters' cell
tag - with regular assignments like this:

.. code-block:: python

    stock = 'YHOO'
    days_back = 600

Nbparameterise handles finding and extracting these parameters, and replacing
them with input values. You can then run the notebook with the new values.
This can be used for:

- Batch processing: run the same code on a list of different inputs. See
  ``examples/batch.py``.
- Simple user interfaces: build an input form based on the parameters, and run
  the notebook when the user submits the form. See ``examples/webapp.py`` for
  an implementation of this with an HTML form.

Nbparameterise can identify and replace numbers, strings, booleans (True/False),
lists and dicts - the types which can be represented in JSON (apart from None).
It's designed to change parameter values but keep their types, although this
isn't enforced.

Extra information about the parameters, such as names to display in a user
interface, can be stored in notebook metadata.

Nbparameterise is written in Python 3, but it can handle notebooks that use
Python 2.

Usage:

.. code-block:: python

    import nbclient
    import nbformat
    from nbparameterise import (
        extract_parameters, replace_definitions, parameter_values
    )

    with open("Stock display.ipynb") as f:
        nb = nbformat.read(f, as_version=4)

    # Get a list of Parameter objects
    orig_parameters = extract_parameters(nb)

    # Update one or more parameters
    params = parameter_values(orig_parameters, stock='GOOG')

    # Make a notebook object with these definitions
    new_nb = replace_definitions(nb, params)

    # Execute the notebook with the new parameters
    nbclient.execute(new_nb)

If you are interested in using your parameterized Jupyter notebooks through a command line interface, have a look at `nbclick <https://github.com/ssciwr/nbclick>`_.

Changes
-------

0.6.1
~~~~~

2024-05-15

- nbparameterise no longer requires `nbconvert <https://pypi.org/project/nbconvert/>`_,
  and loads it only if you pass the deprecated ``execute=True`` option.

0.6
~~~

2023-02-28

- The parameters cell no longer needs to be the first code cell: if you add a cell tag
  'parameters' to another cell, parameters will be extracted from and replaced in that
  cell. Capitalisation doesn't matter. (`PR #27
  <https://github.com/takluyver/nbparameterise/pull/27>`_).
- Only the parameter values are replaced: other code in the parameter cell  will now be
  preserved unchanged (`PR #19 <https://github.com/takluyver/nbparameterise/pull/19>`_).
  The ``comment=`` parameter now has no effect, and it may be removed in a future
  version.
- The ``execute=`` parameter for ``replace_definitions()`` is now deprecated.
  Please use `nbclient <https://nbclient.readthedocs.io/en/latest/>`_ to execute
  your notebook after substituting parameters.
- nbparameterise now requires Python 3.8 or above.
