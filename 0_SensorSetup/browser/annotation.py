import pandas as pd


def create_annot_table(img_df: pd.DataFrame, labels: list[str]) -> pd.DataFrame:
    """
    Initialises a table to store the annotations. This table is of the form:
    ```
    time            | id    | path  | comments  | label0        | label1        | ...   | label N       |
    np.datetime64   | int   | str   | str       | float [0,1]   | ditto label0  | ...   | ditto label0  |
    ```
    where time id and path is taken from img_df and label0 to labelN are taken from labels.
    """
    annot_df = img_df.copy()
    annot_df["comment"] = ""
    for label in labels:
        annot_df[label] = 0.0
    return annot_df


def save_annot_table(annot_df: pd.DataFrame, filepath: str) -> bool:
    """
    Saves the annotation table as a csv file.
    """
    annot_df.to_csv(filepath, index=False)
    return True


def load_annot_table(filepath: str) -> pd.DataFrame:
    """
    Loads the annotation table from a csv file.
    """
    return pd.read_csv(filepath)
