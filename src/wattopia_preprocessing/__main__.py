"""``python -m wattopia_preprocessing``: zie ``wattopia_preprocessing.pijplijn`` voor de opdrachtregel."""

import sys

from .pijplijn import main

if __name__ == "__main__":
    sys.exit(main())
