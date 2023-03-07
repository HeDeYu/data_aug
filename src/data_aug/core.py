# -*- coding:utf-8 -*-
# @FileName :core.py
# @Author   :Deyu He
# @Time     :2023/3/7 19:10

import random
from pathlib import Path


def get_next_img_and_path(iter, img_list, img_path_list, label_list):
    idx = next(iter)
    return idx, img_list[idx].copy(), Path(img_path_list[idx]), label_list[idx]


# 根据给定的目标roi尺寸与图像尺寸给出随机合法roi的左上角坐标
def get_random_roi_tl(img_shape, output_shape):
    H, W = img_shape[:2]
    if output_shape is not None:
        tl_x = random.randrange(0, W - output_shape[1])
        tl_y = random.randrange(0, H - output_shape[0])
        return tl_x, tl_y
    return 0, 0


# 根据给定的目标roi尺寸与源图像，给出随机裁剪后的roi
def get_random_roi_from_img(img, output_shape):
    bg_tl_x, bg_tl_y = get_random_roi_tl(img.shape, output_shape)
    if len(img.shape) == 3:
        img = img[
            bg_tl_y : bg_tl_y + output_shape[0],
            bg_tl_x : bg_tl_x + output_shape[1],
            :,
        ].copy()
    else:
        img = img[
            bg_tl_y : bg_tl_y + output_shape[0],
            bg_tl_x : bg_tl_x + output_shape[1],
        ].copy()
    return img
