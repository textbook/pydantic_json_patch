from importlib.metadata import version

from .models import AddOp, RemoveOp

__version__ = version(__name__)

__all__ = ["__version__", "AddOp", "RemoveOp"]
