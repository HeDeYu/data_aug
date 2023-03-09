# -*- coding:utf-8 -*-
# @FileName :data_package.py
# @Author   :Deyu He
# @Time     :2022/11/29 17:15

import copy
from pathlib import Path

import cvutils
import numpy as np
import pyutils
from loguru import logger

__all__ = [
    "DataPackage",
]


# 面向labelme软件的标注数据的类
# 重要的数据成员包括图像路径,图像,标注路径,标注内容
# 提供常用的方法,包括生成默认,保存,裁剪
class DataPackage:
    @classmethod
    def gen_default_label(cls, img_path, img_shape):
        """
        根据图像路径（仅有文件名字）与图像宽高生成默认的标注内容
        """
        return dict(
            # todo: remove the hard magic numbers below
            version="4.5.7",
            flags={},
            shapes=[],
            imagePath=img_path,
            imageData=None,
            imageHeight=img_shape[0],
            imageWidth=img_shape[1],
        )

    @classmethod
    def gen_default_data_package(cls, img_path, img_shape, img_val=0):
        """
        根据图像路径生成默认图像，并使用默认标注内容，返回dp对象
        """
        img_val = int(img_val)
        if img_val < 0:
            img_val = 0
        elif img_val > 255:
            img_val = 255
        img = np.ones(shape=img_shape, dtype=np.uint8) * img_val
        label = cls.gen_default_label(img_path, img_shape[:2])
        return DataPackage(img_path, img, None, label)

    @classmethod
    def create_from_img_path(cls, img_path, cat_idx=-1):
        """
        类方法,通过图像路径(并生成绝对路径)创建DataPackage对象,通过默认同名方式获取标注路径,若标注文件存在,校验载入的标注内容中的imagePath,
        imageWidth与imageHeight(但不会修改本地标注文件),若标注文件不存在,创建默认标注内容.
        Args:
            img_path:
            cat_idx:

        Returns:

        """
        assert img_path is not None
        img_path = str(Path(img_path).absolute())
        img = cvutils.imread(img_path)
        img = img[:, :, :3]
        label_path = Path(img_path).with_suffix(".json")
        if Path(label_path).exists():
            # 若标注文件存在，载入标注，并校验标注文件中图像文件的正确性。
            label = pyutils.load_json(label_path)
            if label["imagePath"] != str(Path(img_path).name):
                logger.warning(
                    f"{img_path} and {label_path} does not match in imagePath"
                )
                label["imagePath"] = str(Path(img_path).name)
            if label["imageHeight"] != img.shape[0]:
                logger.warning(
                    f"{img_path} and {label_path} does not match in imageHeight"
                )
                label["imageHeight"] = img.shape[0]
            if label["imageWidth"] != img.shape[1]:
                logger.warning(
                    f"{img_path} and {label_path} does not match in imageWidth"
                )
                label["imageWidth"] = img.shape[1]
        else:
            # 若标注文件不存在，构造默认标注内容，写入实际的图像路径与尺寸。
            label = cls.gen_default_label(img_path, img.shape)
        return cls(img_path, img, label_path, label, cat_idx)

    @classmethod
    def create_from_label_path(cls, label_path, cat_idx=-1):
        """
        类方法，通过标注路径生成对象，其中图像路径通过标注内容获取
        """
        assert label_path is not None
        label_path = str(Path(label_path).absolute())
        label = pyutils.load_json(label_path)
        img_path = Path(label_path).parent / label["imagePath"]
        img = cvutils.imread(img_path)
        img = img[:, :, :3]
        return cls(img_path, img, label_path, label, cat_idx)

    def __init__(self, img_path, img, label_path, label, cat_idx=-1):
        """
        初始化方法,由用户显式提供数据成员
        """
        if img_path is not None:
            img_path = str(Path(img_path).absolute())
        if label_path is not None:
            label_path = str(Path(label_path).absolute())
        self.img = img
        self.img_path = img_path
        if label_path is not None:
            self.label_path = label_path
        else:
            self.label_path = (
                str(Path(img_path).with_suffix(".json"))
                if img_path is not None
                else None
            )
        self.label = copy.deepcopy(label)
        self.cat_idx = cat_idx

    def copy(self):
        return DataPackage(
            img_path=self.img_path,
            img=self.img.copy(),
            label_path=self.label_path,
            label=copy.deepcopy(self.label),
            cat_idx=self.cat_idx,
        )

    def update_img_path(self, img_path, update_label_path_by_default=True):
        """
        更新执行对象的img_path数据成员（以及label数据成员中的imagePath字段），并根据参数默认更新label_path数据成员。
        Args:
            img_path: 新的img_path
            update_label_path_by_default: 是否采用默认方式更新执行对象的label_path数据成员

        Returns:

        """
        self.img_path = img_path
        self.label["imagePath"] = str(Path(img_path).name)
        if update_label_path_by_default:
            self.label_path = str(Path(img_path).with_suffix(".json"))

    def filter_with_size(
        self,
        min_size=[0, 0],
        max_size=[float("inf"), float("inf")],
        min_mode="and",
        max_mode="and",
    ):
        """
        给定尺寸范围与模式（and或者or），返回执行对象是否满足给定尺寸范围
        Args:
            min_size:
            max_size:
            min_mode:
            max_mode:

        Returns:

        """
        h, w = self.img.shape[:2]
        if min_mode == "and":
            fit_min = h >= min_size[1] and w >= min_size[0]
        else:
            fit_min = h >= min_size[1] or w >= min_size[0]
        if max_mode == "and":
            fit_max = h < max_size[1] and w < max_size[0]
        else:
            fit_max = h < max_size[1] or w < max_size[0]
        return fit_min and fit_max

    # 给定左上角坐标与宽高，裁剪图像与标注
    def crop(
        self,
        tl_x,
        tl_y,
        width,
        height,
        img_path=None,
        cat_idx=-1,
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
                # 若源标注rect完整落入目标图像中，则保留其标注到目标标注中（带取整操作）
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
        # width, height = round(rectangle_item["points"][1][0]) - round(
        #     rectangle_item["points"][0][0]
        # ), round(rectangle_item["points"][1][1]) - round(rectangle_item["points"][0][1])
        width = br_x - tl_x
        height = br_y - tl_y
        return self.crop(
            tl_x,
            tl_y,
            width,
            height,
            img_path=img_path,
            cat_idx=cat_idx,
        )

    def crop_rectangle_items(self, dst_dir, include_labels=None, exclude_labels=None):
        for idx, item in enumerate(self.label["shapes"]):
            # 若给定了有效标注名字列表，则不考虑不在有效标注名字列表中的标注
            if include_labels is not None and item["label"] not in include_labels:
                continue
            # 若给定了无效标注名字列表，则不考虑无效标注名字列表中的标注
            if exclude_labels is not None and item["label"] in exclude_labels:
                continue

            if item["shape_type"] == "rectangle":
                pt = [*item["points"][0], *item["points"][1]]
                pt_name = [round(pt_) for pt_ in pt]
                # 以裁剪的左上右下坐标追加到源的图像名字中作为裁剪图像的名字
                saved_img_path = Path(dst_dir) / Path(
                    self.img_path.stem + "_" + "_".join([str(pt_) for pt_ in pt_name])
                ).with_suffix(".bmp")

                cropped_dp = self.crop_rectangle_item(
                    item, img_path=str(saved_img_path)
                )

                cropped_dp.save_img()

                cropped_dp.save_label()

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
