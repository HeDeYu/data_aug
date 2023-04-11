# -*- coding:utf-8 -*-
# @FileName :gen_fg_imgs_by_rectangle_item.py
# @Author   :Deyu He
# @Time     :2022/12/19 17:35

# from functools import partial
# from pathlib import Path
#
# from loguru import logger

from data_aug.data_package import crop_rectangle_items_for_folder


def filter_all_true(label_item):
    return True


def filter_func_only_with_pad(label_item):
    return label_item["label"].endswith("_with_pad")


def filter_func_only_xxx_with_pad(label_item, component_type):
    return label_item["label"].startswith(component_type) and label_item[
        "label"
    ].endswith("_with_pad")


def filter_func_only_rc_with_pad(label_item):
    return label_item["label"].startswith("RC") and label_item["label"].endswith(
        "_with_pad"
    )


def filter_func_only_led_with_pad(label_item):
    return label_item["label"].startswith("LED") and label_item["label"].endswith(
        "_with_pad"
    )


def filter_func_only_sot_with_pad(label_item):
    return label_item["label"].startswith("SOT") and label_item["label"].endswith(
        "_with_pad"
    )


def filter_func_only_8p4r_with_pad(label_item):
    return label_item["label"].startswith("8P4R") and label_item["label"].endswith(
        "_with_pad"
    )


# =================================================元件检测业务===========================================================
src_dir_root = r"D:\data\obj_det\raw"
dst_dir_root = r"D:\data\obj_det\fg"
default_margin_tblr = [5, 5, 5, 5]

# 标准测试板普通rc元件，15u，排除01005
margin_tblr = default_margin_tblr
filter_func = filter_func_only_with_pad
crop_rectangle_items_for_folder(
    src_dir=src_dir_root + r"\stb\rc_stb_15um_without_01005",
    dst_dir=dst_dir_root + r"\rc_stb",
    filter_func=filter_func,
    margin_tblr=margin_tblr,
)

# 标准测试板led元件，15u
margin_tblr = default_margin_tblr
filter_func = filter_func_only_with_pad
crop_rectangle_items_for_folder(
    src_dir=src_dir_root + r"\stb\led_stb",
    dst_dir=dst_dir_root + r"\led_stb",
    filter_func=filter_func,
    margin_tblr=margin_tblr,
)

# 标准测试板8p4r元件，15u
margin_tblr = default_margin_tblr
filter_func = filter_func_only_with_pad
crop_rectangle_items_for_folder(
    src_dir=src_dir_root + r"\stb\8p4r_stb",
    dst_dir=dst_dir_root + r"\8p4r_stb",
    filter_func=filter_func,
    margin_tblr=margin_tblr,
)

# 标准测试板sot元件（不含sod），15u
margin_tblr = default_margin_tblr
filter_func = filter_func_only_with_pad
crop_rectangle_items_for_folder(
    src_dir=src_dir_root + r"\stb\sot_stb",
    dst_dir=dst_dir_root + r"\sot_stb",
    filter_func=filter_func,
    margin_tblr=margin_tblr,
)

# 标准测试板ic元件，15u
margin_tblr = default_margin_tblr
filter_func = filter_func_only_with_pad
crop_rectangle_items_for_folder(
    src_dir=src_dir_root + r"\stb\ic_stb",
    dst_dir=dst_dir_root + r"\ic_stb",
    filter_func=filter_func,
    margin_tblr=margin_tblr,
)

# 贝莱胜板子
margin_tblr = default_margin_tblr
filter_func = filter_func_only_with_pad
crop_rectangle_items_for_folder(
    src_dir=src_dir_root + r"\BeiLaiSheng",
    dst_dir=dst_dir_root + r"\all_bls",
    filter_func=filter_func,
    margin_tblr=margin_tblr,
)
# =================================================元件检测业务===========================================================
