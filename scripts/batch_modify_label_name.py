# -*- coding:utf-8 -*-
# @FileName :batch_modify_label_name.py
# @Author   :Deyu He
# @Time     :2022/9/3 14:23

# import re
# import copy
from functools import partial  # noqa: F401
from pathlib import Path

import pyutils

map_dict = {
    "C1210_15um_green": "CR_body",
    "C1206_15um_green": "CR_body",
    "C0805_15um_green": "CR_body",
    "C0603_15um_green": "CR_body",
    "C0402_15um_green": "CR_body",
    "C0201_15um_green": "CR_body",
    "C01005_15um_green": "CR_body",
    "R1210_15um_green": "CR_body",
    "R1206_15um_green": "CR_body",
    "R0805_15um_green": "CR_body",
    "R0603_15um_green": "CR_body",
    "R0402_15um_green": "CR_body",
    "R0201_15um_green": "CR_body",
    "R01005_15um_green": "CR_body",
    "8P4R_0402_body": "8P4R_body",
    "8P4R_0603_body": "8P4R_body",
}


def batch_modify_label_name(src_json_dir, output_dir, update_shapes_label_func):
    assert update_shapes_label_func is not None
    assert output_dir is not None
    Path(output_dir).mkdir(parents=True, exist_ok=True)
    for src_json_path in pyutils.glob_dir(src_json_dir, include_patterns=["*.json"]):
        json_data = pyutils.load_json(src_json_path)

        for label_item in json_data["shapes"]:
            update_shapes_label_func(label_item)
        pyutils.dump_json(json_data, Path(output_dir) / Path(src_json_path).name)

        # new_json_data = copy.deepcopy(json_data)
        # new_json_data["shapes"] = []
        # for label_item in json_data["shapes"]:
        #     if not label_item["label"].endswith("with_pad"):
        #         new_json_data["shapes"].append(label_item)
        # pyutils.dump_json(new_json_data, Path(output_dir) / Path(src_json_path).name)


# def delete_last_to_label(label_item):
#     name_keys = label_item["label"].split("_")
#     label_item["label"] = "_".join(name_keys[:-1])
#
#
# def add_postfix_to_label(label_item, postfix):
#     name_keys = label_item["label"].split("_")
#     name_keys.append(str(postfix))
#     label_item["label"] = "_".join(name_keys)
#
#


def remap(label_item):
    # for label_old, label_new in map_dict.items():
    #     if label_old == label_item["label"]:
    #         label_item["label"] = label_new
    #         break
    label = label_item["label"]
    if label.startswith("8P4R"):
        if label.endswith("body"):
            label_item["label"] = "8P4R_body"
        elif label.endswith("with_pad"):
            label_item["label"] = "8P4R_with_pad"
    elif label.startswith("SOT"):
        if label.endswith("body"):
            label_item["label"] = "SOT_body"
        elif label.endswith("with_pad"):
            label_item["label"] = "SOT_with_pad"
    elif label.startswith("LED"):
        if label.endswith("body"):
            label_item["label"] = "LED_body"
        elif label.endswith("with_pad"):
            label_item["label"] = "LED_with_pad"
    elif label.startswith("R"):
        if label.endswith("with_pad"):
            label_item["label"] = "R_with_pad"
        else:
            label_item["label"] = "R_body"
    elif label.startswith("C"):
        if label.endswith("with_pad"):
            label_item["label"] = "C_with_pad"
        else:
            label_item["label"] = "C_body"
    elif label == "land":
        label_item["label"] = "Land"


# def relabel(label_item, label_new):
#     label_item["label"] = label_new
#
#
# def customized_update(label_item):
#     if len(label_item["label"].split("_")) > 1:
#         return
#     label_item["label"] = "SOT_" + label_item["label"][3:] + "_with_pad"


if __name__ == "__main__":
    src_json_dir = r"D:\data\raw\sot_stb"
    output_dir = r"D:\data\raw\temp"

    batch_modify_label_name(
        src_json_dir=src_json_dir,
        output_dir=output_dir,
        update_shapes_label_func=remap,
    )
