# -*- coding:utf-8 -*-
# @FileName :gen_fg_imgs_by_rectangle_item.py
# @Author   :Deyu He
# @Time     :2022/12/19 17:35

from functools import partial
from pathlib import Path

from loguru import logger

from data_aug.data_package import crop_rectangle_items_for_folder


def filter_func(label_item):
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


margin_tblr = [20, 20, 20, 20]
# src_dirs = [
#     # 标准测试版
#     r"D:\data\AutoProgram\obj_det\raw\stb\stb_rc_15um_without_01005",
#     r"D:\data\AutoProgram\obj_det\raw\stb\stb_led",
#     r"D:\data\AutoProgram\obj_det\raw\stb\stb_sot",
#     r"D:\data\AutoProgram\obj_det\raw\stb\stb_8p4r",
# ]
# dst_dirs = [
#     r"D:\data\AutoProgram\obj_det\fg\STB_RC",
#     r"D:\data\AutoProgram\obj_det\fg\STB_LED",
#     r"D:\data\AutoProgram\obj_det\fg\STB_SOT",
#     r"D:\data\AutoProgram\obj_det\fg\STB_8P4R",
# ]

crop_rectangle_items_for_folder(
    src_dir=r"D:\data\AutoProgram\obj_det\raw\stb\stb_rc_15um_without_01005",
    dst_dir=r"D:\data\AutoProgram\obj_det\fg\STB_RC",
    filter_func=filter_func_only_with_pad,
    margin_tblr=margin_tblr,
)
#
# crop_rectangle_items_for_folder(
#         src_dir=r"D:\data\AutoProgram\obj_det\raw\stb\stb_led",
#         dst_dir=r"D:\data\AutoProgram\obj_det\fg\STB_LED",
#         filter_func=filter_func_only_led_with_pad,
#         margin_tblr=margin_tblr,
#     )
#
# crop_rectangle_items_for_folder(
#         src_dir=r"D:\data\AutoProgram\obj_det\raw\stb\stb_sot",
#         dst_dir=r"D:\data\AutoProgram\obj_det\fg\STB_SOT",
#         filter_func=filter_func_only_sot_with_pad,
#         margin_tblr=margin_tblr,
#     )
#
# crop_rectangle_items_for_folder(
#         src_dir=r"D:\data\AutoProgram\obj_det\raw\stb\stb_8p4r",
#         dst_dir=r"D:\data\AutoProgram\obj_det\fg\STB_8P4R",
#         filter_func=filter_func_only_8p4r_with_pad,
#         margin_tblr=margin_tblr,
#     )


crop_info_map = {
    "STB": [
        r"D:\data\AutoProgram\obj_det\raw\stb\stb_led",
        r"D:\data\AutoProgram\obj_det\raw\stb\stb_sot",
        r"D:\data\AutoProgram\obj_det\raw\stb\stb_8p4r",
    ],
    "BLS": [
        r"D:\data\AutoProgram\obj_det\raw\BeiLaiSheng\468_49--5531_M_D01-T",
        r"D:\data\AutoProgram\obj_det\raw\BeiLaiSheng\5085657-825-T",
        r"D:\data\AutoProgram\obj_det\raw\BeiLaiSheng\cadimage",
        r"D:\data\AutoProgram\obj_det\raw\BeiLaiSheng\iterate_20221215",
        r"D:\data\AutoProgram\obj_det\raw\BeiLaiSheng\iterate_20221220",
    ],
}
#
component_types = ["RC", "LED", "SOT", "8P4R", "IC"]
dst_dir_root = r"D:\data\AutoProgram\obj_det\fg"
for name, src_dir_list in crop_info_map.items():
    for src_dir in src_dir_list:
        for component_type in component_types:
            logger.info(f"gen {component_type} from {str(Path(src_dir).name)}")
            dst_dir_name = name + "_" + component_type
            dst_dir = str(Path(dst_dir_root) / dst_dir_name)
            crop_rectangle_items_for_folder(
                src_dir=src_dir,
                dst_dir=dst_dir,
                filter_func=partial(
                    filter_func_only_xxx_with_pad, component_type=component_type
                ),
                margin_tblr=margin_tblr,
            )
#
crop_rectangle_items_for_folder(
    src_dir=r"D:\data\AutoProgram\obj_det\raw\BeiLaiSheng\iterate_20221215_temp",
    dst_dir=r"D:\data\AutoProgram\obj_det\fg\BLS_TEMP",
    filter_func=filter_func,
    margin_tblr=margin_tblr,
)
