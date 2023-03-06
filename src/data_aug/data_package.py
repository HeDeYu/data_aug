# -*- coding:utf-8 -*-
# @FileName :data_package.py
# @Author   :Deyu He
# @Time     :2022/11/29 17:15


import copy
from pathlib import Path

import cvutils
import pyutils

__all__ = [
    "DataPackage",
]


# 面向labelme软件的标注数据的类
# 重要的数据成员包括图像路径,图像,标注路径,标注内容
# 提供常用的方法,包括生成默认,保存,裁剪
class DataPackage:
    # 根据图像路径（仅有文件名字）与图像宽高生成默认的标注内容
    @classmethod
    def gen_default_label(cls, img_path, shape):
        return dict(
            # todo: remove the hard magic numbers below
            version="4.5.7",
            flags={},
            shapes=[],
            imagePath=img_path,
            imageData=None,
            imageHeight=shape[0],
            imageWidth=shape[1],
        )

    # 通过图像路径生成对象，其中标注路径与图像路径一致，仅替换后缀，仅适用与图像与标注放置在同一文件夹下的情况，若标注文件不存在，生成默认的标注内容
    @classmethod
    def create_from_img_path(cls, img_path, cat_idx=-1):
        img = cvutils.imread(img_path)
        label_path = Path(img_path).with_suffix(".json")
        if Path(label_path).exists():
            label = pyutils.load_json(label_path)
        else:
            label = DataPackage.gen_default_label(
                str(Path(img_path).name), (img.shape[0], img.shape[1])
            )
        return cls(img_path, img, label_path, label, cat_idx)

    # 通过标注路径生成对象，其中图像路径通过标注内容获取
    @classmethod
    def create_from_label_path(cls, label_path, cat_idx=-1):
        label = pyutils.load_json(label_path)
        img_path = Path(label_path).parent / label["imagePath"]
        img = cvutils.imread(img_path)
        return cls(img_path, img, label_path, label, cat_idx)

    # 初始化方法,由用户显式提供数据成员
    def __init__(self, img_path, img, label_path, label, cat_idx=-1):
        self.img_path = img_path
        self.img = img.copy()
        self.label_path = label_path
        self.label = copy.deepcopy(label)
        self.rectangle_items = []
        self.cat_idx = cat_idx
        for shapes_item in self.label["shapes"]:
            if shapes_item["shape_type"] == "rectangle":
                self.rectangle_items.append(
                    cvutils.RectROI.create_from_xyxy(
                        shapes_item["points"][0][0],
                        shapes_item["points"][0][1],
                        shapes_item["points"][1][0],
                        shapes_item["points"][1][1],
                    )
                )

    def crop(
        self,
        tl_x,
        tl_y,
        width,
        height,
        img_path=None,
        label_itself=False,
        cat_idx=-1,
        label=None,
        group_id=None,
        shape_type="rectangle",
        flags=None,
    ):
        rect = cvutils.RectROI.create_from_xywh(tl_x, tl_y, width, height)
        label_path = (
            str(Path(img_path).with_suffix(".json")) if img_path is not None else None
        )
        img = rect.crop(self.img)
        label_ = DataPackage.gen_default_label(
            img_path=str(Path(img_path).name) if img_path is not None else None,
            shape=(img.shape[0], img.shape[1]),
        )

        for shapes_item in self.label["shapes"]:
            if shapes_item["shape_type"] == "rectangle":
                tl_x_, tl_y_ = round(shapes_item["points"][0][0]), round(
                    shapes_item["points"][0][1]
                )
                br_x_, br_y_ = round(shapes_item["points"][1][0]), round(
                    shapes_item["points"][1][1]
                )

                if rect.contain([tl_x_, tl_y_]) and rect.contain([br_x_, br_y_]):
                    tl = [tl_x_ - tl_x, tl_y_ - tl_y]
                    br = [br_x_ - tl_x, br_y_ - tl_y]

                    temp = copy.deepcopy(shapes_item)
                    temp["points"] = [
                        [round(tl[0]), round(tl[1])],
                        [round(br[0]), round(br[1])],
                    ]
                    label_["shapes"].append(temp)

        return DataPackage(img_path, img, label_path, label_, cat_idx)

    def crop_rectangle_item(self, rectangle_item, img_path=None, cat_idx=-1):
        tl_x, tl_y = round(rectangle_item["points"][0][0]), round(
            rectangle_item["points"][0][1]
        )
        br_x, br_y = round(rectangle_item["points"][1][0]), round(
            rectangle_item["points"][1][1]
        )
        # width, height = round(rectangle_item["points"][1][0]) - round(rectangle_item["points"][0][0]), round(rectangle_item["points"][1][1]) - round(rectangle_item["points"][0][1])
        return self.crop(
            tl_x,
            tl_y,
            br_x,
            br_y,
            img_path=img_path,
            label_itself=True,
            cat_idx=cat_idx,
            label=rectangle_item["label"],
            group_id=rectangle_item["group_id"],
            flags=rectangle_item["flags"],
            shape_type="rectangle",
        )

    def visualize(self):
        img = self.img.copy()
        for rectangle_item in self.rectangle_items:
            rectangle_item.draw(img, (0, 0, 255), 1)

        win_name = (
            str(Path(self.img_path).name) if self.img_path is not None else "none"
        )

        cvutils.imshow(img, win_name, 0)

    def save_img(self):
        if self.img_path is not None:
            cvutils.imwrite(self.img_path, self.img)

    def save_label(self):
        if self.label_path is not None:
            pyutils.dump_json(self.label, self.label_path)
