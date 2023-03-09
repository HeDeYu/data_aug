# -*- coding:utf-8 -*-
# @FileName :synthesize_by_mosaic_for_obj_det.py
# @Author   :Deyu He
# @Time     :2022/12/14 19:51

import os

from data_aug.data_package import mosaic_mxn_for_folder

data_root = r"D:/data/AutoProgram/obj_det/synthesize_lv1"
dir_list = os.listdir(data_root)
# data_640_list = []
# data_320_list = []
# data_480_list = []


data_480_dict = {
    "ALL_BG_480": 1,
    "ALL_RC_S_480": 1,
    "ALL_RC_M_480": 1,
    "ALL_RC_L_s2_480": 1,
    "ALL_SOT_M_480": 1,
    "ALL_SOT_L_s2_480": 1,
    "ALL_SOT_XL_s4_480": 1,
    "ALL_IC_M_480": 1,
    "ALL_IC_L_s2_480": 1,
    "ALL_IC_XL_s4_480": 1,
}
data_480_list = []
for dir_name, weight in data_480_dict.items():
    for _ in range(weight):
        data_480_list.append(os.path.join(data_root, dir_name))

dst_dir = r"D:\data\temp3"
num_to_gen = 200
suffix_patterns = ["*.bmp"]
dst_size = [960, 960]
mosaic_mxn_for_folder(
    data_480_list, suffix_patterns, dst_dir, dst_size, 2, 2, num_to_gen
)
