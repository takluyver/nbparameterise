"""Re-run a notebook substituting input parameters in the first cell."""

__version__ = '0.3'

from .code import (Parameter, extract_parameters, replace_definitions,
                    parameter_values,
                  )
