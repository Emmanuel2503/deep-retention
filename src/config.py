"""Rutas del repositorio y semilla."""
from pathlib import Path
import os

REPO_ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = REPO_ROOT / "data" 
DATA_PATH = DATA_DIR / "Customer-Churn-Records.csv"
MODELS_DIR = REPO_ROOT / "models"
REPORTS_DIR = REPO_ROOT / "reports"
SEED = 42

def portfolio_path() -> Path: 
    env_path = os.getenv("DEEP_RETENTION_PORTFOLIO") 
    if env_path: 
        return Path(env_path) 
    scored_path = MODELS_DIR / "portfolio_scored.csv" 
    if scored_path.exists():
         return scored_path 
    return DATA_DIR / "fixtures" / "portfolio_cases.csv"