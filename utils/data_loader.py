from pathlib import Path

import pandas as pd


DATA_FILE = Path(__file__).resolve().parents[1] / "data" / "sample_regions.csv"


def load_region_data() -> pd.DataFrame:
    """Load the RESQnet regional dataset from CSV."""
    return pd.read_csv(DATA_FILE)


def get_disaster_types(dataframe: pd.DataFrame) -> list:
    """Return disaster types for the main selector."""
    return dataframe["disaster_type"].drop_duplicates().tolist()


def get_region_names(dataframe: pd.DataFrame) -> list:
    """Return region names from a dataframe subset."""
    return dataframe["region"].drop_duplicates().tolist()


def get_regions_for_disaster(dataframe: pd.DataFrame, disaster_type: str) -> list:
    """Return the regions that match a selected disaster type."""
    filtered = dataframe.loc[dataframe["disaster_type"] == disaster_type, "region"]
    return filtered.drop_duplicates().tolist()


def get_region_record(dataframe: pd.DataFrame, region_name: str) -> pd.Series:
    """Return a single region row as a pandas Series."""
    region_row = dataframe.loc[dataframe["region"] == region_name]
    if region_row.empty:
        raise ValueError(f"Region '{region_name}' was not found in the dataset.")
    return region_row.iloc[0]


def get_disaster_subset(dataframe: pd.DataFrame, disaster_type: str) -> pd.DataFrame:
    """Return the five map points for the selected disaster type."""
    return dataframe.loc[dataframe["disaster_type"] == disaster_type].copy()
