# -*- coding:utf-8 -*-
# @FileName :test_data_package.py
# @Author   :Deyu He
# @Time     :2022/11/29 17:18

from pathlib import Path
from unittest import TestCase

from data_aug import DataPackage


class TestDataPackage(TestCase):
    def test_create_from_label_path(self):
        dp = DataPackage.create_from_label_path(r"./test_data/C0402_15um_black.json")
        dp.visualize()

    def test_create_from_img_path(self):
        dp = DataPackage.create_from_img_path(r"./test_data/C0402_15um_black.bmp")
        dp.visualize()

    def test_save_label(self):
        dp = DataPackage.create_from_img_path(r"./test_data/C0603_15um_black.bmp")
        dp.visualize()
        dp.save_label()

    def test_crop(self):
        dp = DataPackage.create_from_label_path(r"./test_data/C0402_15um_black.json")
        # dp.visualize()

        new_dp = dp.crop(
            500,
            1000,
            1500,
            1000,
            img_path=r"./test_output/C0402_15um_black_test_crop.bmp",
        )
        new_dp.visualize()

    def test_crop_rectangle_item(self):
        dp = DataPackage.create_from_label_path(r"./test_data/C0402_15um_black.json")
        dp.visualize()

        new_dp = dp.crop_rectangle_item(
            dict(
                label="x",
                points=[[500, 1000], [2000, 2000]],
                group_id=None,
                shape_type="rectangle",
                flags={},
            )
        )
        new_dp.visualize()

    def test_crop_rectangle_items_1(self):
        dp = DataPackage.create_from_label_path(r"./test_data/C0402_15um_black.json")
        dst_dir = r"./test_output/crop/"
        Path(dst_dir).mkdir(parents=True, exist_ok=True)
        dp.crop_rectangle_items(dst_dir)

    def test_crop_rectangle_items_2(self):
        dp = DataPackage.create_from_label_path(r"./test_data/C0402_15um_black.json")
        dst_dir = r"./test_output/crop/"
        Path(dst_dir).mkdir(parents=True, exist_ok=True)
        dp.crop_rectangle_items(dst_dir, exclude_labels=["C0402_15um_black"])
