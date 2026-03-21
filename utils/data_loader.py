from pathlib import Path

import pandas as pd


DATA_FILE = Path(__file__).resolve().parents[1] / "data" / "sample_regions.csv"


def load_region_data() -> pd.DataFrame:
    """Load the regional dataset from CSV."""
    dataframe = pd.read_csv(DATA_FILE)
    return dataframe


def get_region_names(dataframe: pd.DataFrame) -> list:
    """Return all region names for the dropdown."""
    return sorted(dataframe["region"].unique().tolist())


def get_region_record(dataframe: pd.DataFrame, region_name: str) -> pd.Series:
    """Return a single region row as a pandas Series."""
    region_row = dataframe.loc[dataframe["region"] == region_name]
    if region_row.empty:
        raise ValueError(f"Region '{region_name}' was not found in the dataset.")
    return region_row.iloc[0]
