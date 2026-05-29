import pandas as pd
from pathlib import Path

def read_csv_checked(path: Path) -> pd.DataFrame:
    if not path.exists():
        raise FileNotFoundError(f" The CSV file NOT fOUND: {path}")
    return pd.read_csv(path)