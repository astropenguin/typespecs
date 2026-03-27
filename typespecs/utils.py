__all__ = ["PANDAS_VERSION"]

# dependencies
import pandas as pd
from packaging import version

# constants
PANDAS_VERSION = version.parse(pd.__version__)
