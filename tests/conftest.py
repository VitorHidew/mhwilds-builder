"""Keep imports and persistence tests away from the real application storage."""
import atexit
import os
from pathlib import Path
import shutil
from tempfile import gettempdir
from uuid import uuid4


_temporary_root = Path(gettempdir()).resolve()
_storage = _temporary_root / f"mhwilds-tests-{uuid4().hex}"
_storage.mkdir()
os.environ["MHWILDS_STORAGE_DIR"] = str(_storage)


def _cleanup():
    if _storage.resolve().parent == _temporary_root:
        shutil.rmtree(_storage, ignore_errors=True)


atexit.register(_cleanup)
