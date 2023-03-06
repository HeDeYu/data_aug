# -*- coding:utf-8 -*-
# @FileName :test_data_package.py
# @Author   :Deyu He
# @Time     :2022/11/29 17:18

from unittest import TestCase

from data_aug import DataPackage


class TestDataPackage(TestCase):
    def test_crop(self):
        pass
        # dp = DataPackage.create_from_img_path(
        #     r"D:\data\2DAOI\AutoProgram\obj_det\raw\stb_15um_black\C0805_15um_black.bmp"
        # )
        # dp.visualize()
        # new_dp = dp.crop(500, 500, 1000, 500)
        # new_dp.visualize()
        # new_dp = dp.crop(500, 500, 1500, 1000, img_path=r"D:11\a.bmp", label_itself=True, label="x", flags={})
        # new_dp.visualize()

        # new_dp = dp.crop_rectangle_item(
        #     dict(
        #         label="x",
        #         points=[[500, 500], [1500, 1000]],
        #         group_id=None,
        #         shape_type="rectangle",
        #         flags={},
        #     )
        # )
        # new_dp.visualize()

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
