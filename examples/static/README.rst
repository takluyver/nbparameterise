Examples of using nbparameterise:

**webapp** runs a creates an HTML form based on the notebook
to choose input values. When the user clicks 'Run notebook', it renders an HTML
view of the notebook run with their inputs. Run it with::

    # Get the dependencies
    pip install tornado htmlgen
    python3 webapp.py "Stock display.ipynb"

**batch** demonstrates running in batch mode, looping over parameter values.
It saves one ``.ipynb`` file for each input value. Run it with::

    python3 batch.py

