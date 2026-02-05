from importlib.metadata import version

from .models import AddOp, CopyOp, RemoveOp, ReplaceOp, TestOp

__version__ = version(__name__)

__all__ = ["__version__", "AddOp", "CopyOp", "RemoveOp", "ReplaceOp", "TestOp"]
