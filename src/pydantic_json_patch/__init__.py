from importlib.metadata import version

from .models import RemoveOp

__version__ = version(__name__)

__all__ = ["__version__", "RemoveOp"]
