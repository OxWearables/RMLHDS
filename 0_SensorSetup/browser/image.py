import re
from datetime import datetime
from glob import glob
from multiprocessing import Pool
from pathlib import Path

import pandas as pd
import pytz


def check_img_root_dir(img_root_dir):
    img_path_format = img_root_dir + "/P*/*.JPG"

    img_fps = glob(img_path_format)
    if len(img_fps) == 0:
        return False

    return True


def process_imgs(img_path_format: str, n_processes: int = 3) -> pd.DataFrame:
    """
    Assumes images are of format B00000000_21I507_20141003_121214E.JPG.
    Returns a pandas dataframe of participant IDs, filepaths to images and times those images were taken at.
    """
    img_fps = glob(img_path_format)
    # code that extracts ID and time stamp

    img_infos = []
    with Pool(n_processes) as p:
        img_infos = p.map(extract_img_info, img_fps)

    img_df = pd.DataFrame(img_infos, columns=["time", "id", "path"])
    return img_df


def extract_img_info(filepath: str) -> list[datetime, int, str]:
    parts = Path(filepath).parts
    # part ID
    part_id = int(parts[-2][1:])  # e.g. P123

    # time that photo was taken - we assume these are in UK time, and we want to convert to UTC
    pattern = re.compile(r"(\d{8}_\d{6})")  # e.g. 20150621_105702
    naive_img_time = datetime.strptime(
        pattern.search(parts[-1]).group(0), "%Y%m%d_%H%M%S"
    )  # without time zone
    local_img_time = pytz.timezone("Europe/London").localize(naive_img_time)
    utc_img_time = local_img_time.astimezone(pytz.utc)

    return [utc_img_time, part_id, filepath]
