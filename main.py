"""Entrypoint legado — delega para o pacote startup_validator.

O app em si vive em src/startup_validator. Este arquivo existe apenas
para manter compatibilidade com quem invoca `python main.py`.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent / "src"))

from startup_validator.cli import main  # noqa: E402

if __name__ == "__main__":
    main()
