# -*- coding:utf-8 -*-
# @FileName :crop_rectangle_labels.py
# @Author   :Deyu He
# @Time     :2022/8/24 14:43

# import copy
# from itertools import product
from pathlib import Path

# import cvutils
# import numpy as np
import pyutils
from loguru import logger  # noqa: F401
from tqdm import tqdm

from data_aug import DataPackage


def batch_crop_rectangle_labels(
    src_dir,
    dst_dir,
    include_labels=None,
    exclude_labels=None,
):
    Path(dst_dir).mkdir(parents=True, exist_ok=True)
    label_path_list = list(pyutils.glob_dir(src_dir, include_patterns=["*.json"]))
    for label_path in tqdm(label_path_list, desc="..."):
        dp = DataPackage.create_from_label_path(label_path)
        dp.crop_rectangle_items(dst_dir, include_labels, exclude_labels)


if __name__ == "__main__":
    src_dir = r"D:\data\stb\stb_rc_15um_without_01005"
    dst_dir = r"D:\code\data_aug\tests\test_output\crop"
    batch_crop_rectangle_labels(src_dir, dst_dir, exclude_labels=["R_body", "C_body"])
