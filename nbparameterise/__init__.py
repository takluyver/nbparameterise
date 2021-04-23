"""Re-run a notebook substituting input parameters in the first cell."""

__version__ = '0.4'

from .code import (
    Parameter, extract_parameters, replace_definitions, parameter_values,
)
