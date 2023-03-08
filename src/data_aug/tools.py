# -*- coding:utf-8 -*-
# @FileName :tools.py
# @Author   :Deyu He
# @Time     :2023/3/7 14:43

from pathlib import Path

import pyutils
from tqdm import tqdm

from .data_package import DataPackage


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
