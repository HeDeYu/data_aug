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
from tqdm import tqdm

__all__ = [
    "DataPackage",
    "crop_rectangle_items_for_folder",
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

    @property
    def label_items(self):
        return self.label["shapes"]

    def gen_rectangle_items(self):
        """
        返回标注类型为rectangle的元素列表，元素对象为cvutils.RectROI对象
        """
        rectangle_items = []
        for shapes_item in self.label_items:
            if shapes_item["shape_type"] == "rectangle":
                rectangle_items.append(
                    cvutils.RectROI.create_from_xyxy(
                        shapes_item["points"][0][0],
                        shapes_item["points"][0][1],
                        shapes_item["points"][1][0],
                        shapes_item["points"][1][1],
                    )
                )
        return rectangle_items

    @property
    def rectangle_items(self):
        """
        返回标注类型为rectangle的cvutils.RectROI对象列表，注意只有坐标信息，其余标注信息已丢失
        """
        return self.gen_rectangle_items()

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

    def crop(
        self,
        tl_x,
        tl_y,
        br_x,
        br_y,
        img_path=None,
        cat_idx=-1,
        append_coords_to_file_name=True,
        label_itself=False,
        label=None,
        group_id=None,
        shape_type="rectangle",
        flags=None,
    ):
        """
        输入待裁剪矩形区域的左上点与右下点坐标,输入返回DataPackage对象的img_path与cat_idx属性,
        输入是否将待裁剪矩形区域本身作为新的label item写进返回的DataPackage对象中的标志,以及(若要写进时该label item)相关的字段,
        返回新的DataPackage对象,该对象img属性为裁剪矩形图像,执行对象中被待裁剪矩形区域完全包含的label item,经过恰当平移后写进返回对象中.
        Args:
            tl_x: 待裁剪的矩形区域的左上点x坐标
            tl_y: 待裁剪的矩形区域的左上点y坐标
            br_x: 待裁剪的矩形区域的右下点x坐标
            br_y: 待裁剪的矩形区域的右下点y坐标
            img_path: 返回的DataPackage对象的img_path属性,默认为None
            cat_idx: 返回的DataPackage对象的cat_idx属性,默认为-1
            append_coords_to_file_name: 若img_path不为None且此参数为True,将待裁剪矩形区域的左上右下点坐标追加到img_path中.
            label_itself: 待裁剪的矩形区域本身是否作为新的label item写进返回的DataPackage对象
            label: 待裁剪的矩形区域本身作为新的label item写进返回的DataPackage对象时,该label item的label字段,默认为None
            group_id: 待裁剪的矩形区域本身作为新的label item写进返回的DataPackage对象时,该label item的group_id字段,默认为None
            shape_type: 待裁剪的矩形区域本身作为新的label item写进返回的DataPackage对象时,该label item的shape_type字段, 默认为rectangle
            flags: 待裁剪的矩形区域本身作为新的label item写进返回的DataPackage对象时,该label item的flags字段,默认为None

        Returns:
            返回新创建的DataPackage对象,其img_path与cat_idx由输入参数决定,label_path由img_path通过默认方式确定,
            对label属性,首先创建默认的label属性对象,遍历执行对象的label item,将其中标注类型为rectangle的,
            并被待裁剪矩形区域完全包含的label item写进返回对象的label属性中,
            todo:
            最后根据输入参数决定是否将待裁剪矩形区域与相关信息生成label item,并追加到返回对象的label属性中.
        """
        tl_x = max(0, tl_x)
        tl_y = max(0, tl_y)
        br_x = min(self.img.shape[1], br_x)
        br_y = min(self.img.shape[0], br_y)
        rect = cvutils.RectROI.create_from_xywh(
            tl_x, tl_y, br_x - tl_x + 1, br_y - tl_y + 1
        )
        if img_path is not None and append_coords_to_file_name:
            img_path = str(Path(img_path).absolute())
            img_path = Path(img_path).parent / Path(
                Path(img_path).stem
                + "_"
                + "-".join(
                    [
                        str(round(tl_x)),
                        str(round(tl_y)),
                        str(round(br_x)),
                        str(round(br_y)),
                    ]
                )
            ).with_suffix(Path(img_path).suffix)
        label_path = (
            str(Path(img_path).with_suffix(".json")) if img_path is not None else None
        )
        img = rect.crop(self.img)
        label_ = self.gen_default_label(img_path, img.shape)

        for shapes_item in self.label_items:
            if shapes_item["shape_type"] == "rectangle":
                tl_x_, tl_y_ = round(shapes_item["points"][0][0]), round(
                    shapes_item["points"][0][1]
                )
                br_x_, br_y_ = round(shapes_item["points"][1][0]), round(
                    shapes_item["points"][1][1]
                )
                # 原始标注条目中完整落入裁剪区域中的标注，其他标注信息保留，坐标点经平移调整后写入到新对象的标注中。
                total_contain = rect.contain([tl_x_, tl_y_]) and rect.contain(
                    [br_x_, br_y_]
                )

                if total_contain:
                    tl = [tl_x_ - tl_x, tl_y_ - tl_y]
                    br = [br_x_ - tl_x, br_y_ - tl_y]

                    temp = copy.deepcopy(shapes_item)
                    temp["points"] = [
                        [round(tl[0]), round(tl[1])],
                        [round(br[0]), round(br[1])],
                    ]
                    label_["shapes"].append(temp)

        # todo:
        if label_itself:
            pass

        return DataPackage(img_path, img, label_path, label_, cat_idx)

    def crop_rectangle_item(
        self, rectangle_item, margin_tblr=None, img_path=None, cat_idx=-1
    ):
        """
        输入rectangle类型的label item(否则返回None),待返回DataPackage对象的img_path与cat_idx属性,调用对象方法crop返回新的DataPackage对象.
        Args:
            rectangle_item: 待裁剪的rectangle类型的label item,通常为执行对象label属性中的某个label item.
            margin_tblr: 基于给定rectangle标注的矩形往四个方向上扩展生成的矩形为最终裁剪区域,默认为None
            img_path: 待返回DataPackage对象的img_path,默认为None
            cat_idx: 待返回DataPackage对象的cat_idx,默认为-1
        Returns:

        """
        if not rectangle_item["shape_type"] == "rectangle":
            return None

        if margin_tblr is not None:
            assert len(margin_tblr) == 4

        tl_x, tl_y = round(rectangle_item["points"][0][0]), round(
            rectangle_item["points"][0][1]
        )
        br_x, br_y = round(rectangle_item["points"][1][0]), round(
            rectangle_item["points"][1][1]
        )
        if margin_tblr is not None:
            tl_x -= margin_tblr[2]
            tl_y -= margin_tblr[0]
            br_x += margin_tblr[3]
            br_y += margin_tblr[1]
        return self.crop(
            tl_x,
            tl_y,
            br_x,
            br_y,
            img_path=img_path,
            cat_idx=cat_idx,
            append_coords_to_file_name=True,
            # label_itself=True,
            # cat_idx=cat_idx,
            # label=rectangle_item["label"],
            # group_id=rectangle_item["group_id"],
            # flags=rectangle_item["flags"],
            # shape_type="rectangle",
        )

    def crop_rectangle_items(self, dst_dir=None, margin_tblr=None, filter_func=None):
        """
        裁剪执行对象的所有rectangle标注,返回DataPackage对象序列.
        Args:
            dst_dir: 裁剪生成的DataPackage序列的img_path所在的文件夹,若为None,则选用执行对象本身self.img_path
            margin_tblr: 基于给定rectangle标注的矩形往四个方向上扩展生成的矩形为最终裁剪区域,默认为None
            filter_func: 用户给定的作用于待裁剪标注的筛选条件,满足筛选条件的标注

        Returns:

        """
        if self.img_path is None or dst_dir is None:
            dst_img_path = self.img_path
        else:
            dst_img_path = str(
                Path(Path(dst_dir) / Path(self.img_path).name).absolute()
            )
        ret_list = []
        for label_item in self.label_items:
            if label_item["shape_type"] == "rectangle":
                if (filter_func is not None) and (not filter_func(label_item)):
                    continue
                ret_list.append(
                    self.crop_rectangle_item(
                        rectangle_item=label_item,
                        img_path=dst_img_path,
                        margin_tblr=margin_tblr,
                    )
                )
        return ret_list

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


def crop_rectangle_items_for_folder(
    src_dir, dst_dir, filter_func=None, margin_tblr=None
):
    src_dir = str(Path(src_dir).absolute())
    dst_dir = str(Path(dst_dir).absolute())
    Path(dst_dir).absolute().mkdir(parents=True, exist_ok=True)
    label_path_list = list(pyutils.glob_dir(src_dir, include_patterns=["*.json"]))
    for label_path in tqdm(label_path_list, desc="..."):
        dp = DataPackage.create_from_label_path(label_path)
        cropped_dp_list = dp.crop_rectangle_items(
            dst_dir=dst_dir, filter_func=filter_func, margin_tblr=margin_tblr
        )

        for cropped_dp in cropped_dp_list:
            cropped_dp.save()
