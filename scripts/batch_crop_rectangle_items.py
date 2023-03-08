# -*- coding:utf-8 -*-
# @FileName :batch_crop_rectangle_labels.py
# @Author   :Deyu He
# @Time     :2023/3/6 14:43


from loguru import logger  # noqa: F401

from data_aug.tools import batch_crop_rectangle_labels

if __name__ == "__main__":
    src_dir = r"E:\data\raw\chip_stb_15um_without_01005"
    dst_dir = r"E:\data\fg\chip_stb"
    batch_crop_rectangle_labels(src_dir, dst_dir, exclude_labels=["R_body", "C_body"])

    src_dir = r"E:\data\raw\sot_stb"
    dst_dir = r"E:\data\fg\sot_stb"
    batch_crop_rectangle_labels(src_dir, dst_dir, exclude_labels=["SOT_body"])

    src_dir = r"E:\data\raw\8p4r_stb"
    dst_dir = r"E:\data\fg\8p4r_stb"
    batch_crop_rectangle_labels(src_dir, dst_dir, exclude_labels=["8P4R_body"])

    src_dir = r"E:\data\raw\led_stb"
    dst_dir = r"E:\data\fg\led_stb"
    batch_crop_rectangle_labels(src_dir, dst_dir, exclude_labels=["LED_body"])
