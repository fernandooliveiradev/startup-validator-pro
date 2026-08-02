"""Configuração e leitura de variáveis de ambiente do Startup Validator Pro."""

import os
from pathlib import Path

from dotenv import load_dotenv

from startup_validator import __version__

# Carrega as variáveis de ambiente do .env do diretório do projeto.
load_dotenv()

# Diretório raiz do repositório (um nível acima de src/).
ROOT_DIR = Path(__file__).resolve().parents[2]
TMP_DIR = ROOT_DIR / "tmp"
DB_FILE = TMP_DIR / "validations.db"
SESSION_TABLE = "validations"

APP_NAME = "Startup Validator Pro"
APP_VERSION = __version__
APP_TAGLINE = "Validação de ideias com DeepSeek V4"

MODEL_ID = os.getenv("MODEL_ID", "deepseek-v4-flash")
REASONING_EFFORT = os.getenv("REASONING_EFFORT", "high")
# Habilita o "thinking" do DeepSeek (formato OpenAI: {"thinking": {"type": "enabled"}}).
THINKING_ENABLED = os.getenv("THINKING_ENABLED", "true").lower() in {"1", "true", "yes"}


def ensure_dirs() -> None:
    """Cria diretórios de runtime, se necessário."""
    TMP_DIR.mkdir(exist_ok=True)


def get_deepseek_api_key() -> str | None:
    return os.getenv("DEEPSEEK_API_KEY")


def get_tavily_api_key() -> str | None:
    return os.getenv("TAVILY_API_KEY")
