# -*- coding:utf-8 -*-
# @FileName :data_package.py
# @Author   :Deyu He
# @Time     :2022/11/29 17:15

import copy
import datetime
import itertools
import random
from pathlib import Path

import cv2
import cvutils
import numpy as np
import pyutils
from loguru import logger
from tqdm import tqdm

__all__ = [
    "DataPackage",
    "gen_data_package_list_from_img_file_for_folder",
    "gen_data_package_list_from_label_file_for_folder",
    "filter_with_size_for_folder",
    "crop_rectangle_items_for_folder",
    "crop_point_items_for_folder",
    "paste_by_iter_for_folder",
]


# 面向labelme软件的标注数据的类
# 重要的数据成员包括图像路径,图像,标注路径,标注内容
# 提供常用的方法,包括生成默认,保存,裁剪
class DataPackage:
    @classmethod
    def gen_default_label(cls, img_path, img_shape, version="4.5.7"):
        """
        根据图像路径（仅有文件名字）与图像宽高生成默认的标注内容
        """
        return dict(
            # todo: remove the hard magic numbers below
            version=version,
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

    def merge(self, other):
        self.label_items.extend(other.label_items)
        return self

    def resize_by_factor(self, fx, fy, interpolation=1):
        """
        给定缩放系数，返回新创建的缩放后的DataPackage对象
        Args:
            fx: x缩放系数
            fy: y缩放系数
            interpolation: 插值方式，默认为1（linear）

        Returns:

        """

        img = cv2.resize(self.img, None, fx=fx, fy=fy, interpolation=interpolation)
        img_shape = img.shape
        img_path = pyutils.append_file_name(
            self.img_path, f"_resize-{img_shape[1]}-{img_shape[0]}"
        )
        ret_dp = DataPackage.gen_default_data_package(img_path, img_shape)
        ret_dp.img = img
        for label_item in self.label_items:
            ret_dp.label_items.append(self.resize_label_item(label_item, fx, fy))
        return ret_dp

    def rotate_by_multi_90(self, rotate_degree):
        """
        将执行对象旋转-90, 90，180或270度，返回新创建的旋转后的DataPackage对象
        Args:
            rotate_degree: 旋转角度，可选取90，-90，180或270度，其中正数表示逆时针旋转。

        Returns:

        """
        assert rotate_degree in [90, 180, 270, -90]
        if rotate_degree == -90:
            rotate_degree = 270
        if rotate_degree == 90:
            rotate_flag = cv2.ROTATE_90_COUNTERCLOCKWISE
        elif rotate_degree == 270:
            rotate_flag = cv2.ROTATE_90_CLOCKWISE
        else:
            rotate_flag = cv2.ROTATE_180
        img = cv2.rotate(self.img, rotate_flag)
        img_shape = img.shape
        img_path = pyutils.append_file_name(self.img_path, f"_rotate-{rotate_degree}")
        ret_dp = DataPackage.gen_default_data_package(img_path, img_shape)
        ret_dp.img = img
        for label_item in self.label_items:
            ret_dp.label_items.append(
                self.rotate_label_item(label_item, self.img.shape, rotate_degree)
            )
            pass
        return ret_dp

    def pad_with_tblr(self, pad_tblr, img_path=None, auto_gen_img_path=True):
        t, b, l, r = pad_tblr
        new_height = self.img.shape[0] + t + b
        new_width = self.img.shape[1] + l + r
        num_channels = len(self.img.shape)
        if num_channels == 1:
            new_img = np.zeros(shape=(new_height, new_width), dtype=self.img.dtype)
            new_img[
                t : t + self.img.shape[0], l : l + self.img.shape[1]
            ] = self.img.copy()
        elif num_channels == 3:
            new_img = np.zeros(shape=(new_height, new_width, 3), dtype=self.img.dtype)
            new_img[
                t : t + self.img.shape[0], l : l + self.img.shape[1], :
            ] = self.img.copy()
        new_label = copy.deepcopy(self.label)
        new_label["imageHeight"] = new_height
        new_label["imageWidth"] = new_width
        new_label["shapes"] = []
        for label_item in self.label_items:
            new_label["shapes"].append(self.translate_label_item(label_item, l, t))
        if img_path is None and auto_gen_img_path:
            dir_path = Path(Path(self.img_path).parent)
            img_path = str(
                dir_path
                / Path(
                    Path(self.img_path).stem
                    + "_tblr-"
                    + str(round(t))
                    + "-"
                    + str(round(b))
                    + "-"
                    + str(round(l))
                    + "-"
                    + str(round(r))
                ).with_suffix(Path(self.img_path).suffix)
            )
            new_label["imagePath"] = str(Path(img_path).name)
        elif img_path is None:
            new_label["imagePath"] = None
        return DataPackage(
            img_path=img_path,
            img=new_img,
            label_path=None,
            label=new_label,
            cat_idx=self.cat_idx,
        )

    def pad_with_dst_size(
        self, dst_size, center=True, img_path=None, auto_gen_img_path=True
    ):
        dst_width, dst_height = dst_size
        assert dst_height >= self.img.shape[0]
        assert dst_width >= self.img.shape[1]
        if center:
            t = (dst_height - self.img.shape[0]) // 2
            b = dst_height - self.img.shape[0] - t
            _l = (dst_width - self.img.shape[1]) // 2
            r = dst_width - self.img.shape[1] - _l
            return self.pad_with_tblr(
                pad_tblr=[t, b, _l, r],
                img_path=img_path,
                auto_gen_img_path=auto_gen_img_path,
            )
        else:
            raise NotImplementedError

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
        img = rect.crop(self.img)

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

        label_ = self.gen_default_label(str(img_path), img.shape)

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
            else:
                continue
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

    def crop_point_item(self, point_item, crop_size, img_path=None, cat_idx=-1):
        """
        输入point类型的label item且包含点数为1(否则返回None),待返回DataPackage对象的img_path与cat_idx属性,调用对象方法crop返回新的DataPackage对象.
        Args:
            point_item: 待裁剪的point类型的label item,通常为执行对象label属性中的某个label item
            crop_size: 待裁剪的矩形区域尺寸
            img_path: 待返回DataPackage对象的img_path,默认为None
            cat_idx: 待返回DataPackage对象的cat_idx,默认为-1

        Returns:

        """
        if (not point_item["shape_type"] == "point") or len(point_item["points"]) != 1:
            return None
        center_x, center_y = point_item["points"][0]
        center_x = round(center_x)
        center_y = round(center_y)
        tl_x = center_x - crop_size[0] // 2
        tl_y = center_y - crop_size[1] // 2
        br_x = tl_x + crop_size[0] - 1
        br_y = tl_y + crop_size[1] - 1
        return self.crop(
            tl_x,
            tl_y,
            br_x,
            br_y,
            img_path=img_path,
            cat_idx=cat_idx,
            append_coords_to_file_name=True,
        )

    def crop_point_items(self, dst_dir=None, crop_size=None, filter_func=None):
        assert crop_size is not None
        raise NotImplementedError

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
            return True
        logger.warning(r"self.img_path is None!")
        return False

    def save_label(self):
        if self.label_path is not None:
            pyutils.dump_json(self.label, self.label_path)
            return True
        logger.warning(r"self.label_path is None!")
        return False

    def save(self):
        save_img = self.save_img()
        save_label = self.save_label()
        return save_img and save_label

    @staticmethod
    def translate_label_item(label_item, x, y):
        """
        对输入标注item的所有点进行x，y平移，其它内容保持不变，返回新创建的标注item
        Args:
            label_item: 需要进行平移的标注条目
            x: x平移量
            y: y平移量

        Returns:

        """
        new_label_item = copy.deepcopy(label_item)
        new_label_item["points"] = []
        for pt in label_item["points"]:
            new_label_item["points"].append([pt[0] + x, pt[1] + y])
        return new_label_item

    @staticmethod
    def resize_label_item(label_item, fx, fy):
        """
        对输入标注item的所有点进行fx，fy的缩放，其它内容保持不变，返回新创建的标注item
        Args:
            label_item: 需要进行缩放的标注条目
            fx: x缩放系数
            fy: y缩放系数

        Returns:

        """
        new_label_item = copy.deepcopy(label_item)
        new_label_item["points"] = []
        for pt in label_item["points"]:
            new_label_item["points"].append([pt[0] * fx, pt[1] * fy])
        return new_label_item

    @staticmethod
    def rotate_label_item(label_item, img_shape, rotate_degree):
        """
        将标注条目旋转90，180或270度，并进行必要的平移。
        Args:
            label_item: 待旋转的标注条目
            img_shape: 旋转后图像的shape
            rotate_degree: 旋转角度，90，180，270

        Returns:

        """
        h, w = img_shape[:2]
        if rotate_degree == 90:
            M = np.array([[0, 1, 0], [-1, 0, w], [0, 0, 1]])
        elif rotate_degree == 270:
            M = np.array([[0, -1, h], [1, 0, 0], [0, 0, 1]])
        else:
            M = np.array([[-1, 0, w], [0, -1, h], [0, 0, 1]])
        new_label_item = copy.deepcopy(label_item)
        new_label_item["points"] = []

        if label_item["shape_type"] == "rectangle":
            pt = label_item["points"][0]
            x1, y1 = np.matmul(M, np.array([pt[0], pt[1], 1])).tolist()[:2]
            pt = label_item["points"][1]
            x2, y2 = np.matmul(M, np.array([pt[0], pt[1], 1])).tolist()[:2]
            new_label_item["points"].append([min(x1, x2), min(y1, y2)])
            new_label_item["points"].append([max(x1, x2), max(y1, y2)])
        else:
            for pt in label_item["points"]:
                new_pt = np.matmul(M, np.array([pt[0], pt[1], 1])).tolist()[:2]
                new_label_item["points"].append([new_pt[0], new_pt[1]])
        return new_label_item

    def paste_to(self, dst_data_package, tl_x, tl_y):
        assert isinstance(dst_data_package, DataPackage)
        num_channels = len(self.img.shape)
        img = dst_data_package.img
        label = dst_data_package.label
        x = tl_x
        y = tl_y
        if num_channels == 1:
            img[y : y + self.img.shape[0], x : x + self.img.shape[1]] = self.img.copy()
        elif num_channels == 3:
            img[
                y : y + self.img.shape[0], x : x + self.img.shape[1], :
            ] = self.img.copy()
        new_label = copy.deepcopy(label)
        for label_item in self.label_items:
            new_label["shapes"].append(self.translate_label_item(label_item, x, y))
        return DataPackage(
            img_path=dst_data_package.img_path,
            img=img,
            label_path=dst_data_package.label_path,
            label=new_label,
        )

    def paste(self, dst_data_package, tl_x, tl_y):
        self.paste_to(dst_data_package, tl_x, tl_y)

    def paste_by(self, src_data_package, tl_x, tl_y, in_place=False):
        """
        将源对象粘贴到本对象上，不进行label item重叠冲突处理，不进行越界处理，返回新创建的DataPackage对象或执行对象本身。
        Args:
            src_data_package: 源对象
            tl_x: 源对象粘贴到执行对象时的左上点x坐标
            tl_y: 源对象粘贴到执行对象时的左上点y坐标
            in_place: 是否原地操作，默认为False

        Returns:

        """
        assert isinstance(src_data_package, DataPackage)
        paste_height, paste_width = src_data_package.img.shape[:2]

        if in_place:
            ret = self
        else:
            ret = self.copy()

        ret.img[
            tl_y : tl_y + paste_height, tl_x : tl_x + paste_width, :
        ] = src_data_package.img.copy()
        for label_item_to_append in src_data_package.label_items:
            ret.label_items.append(
                ret.translate_label_item(label_item_to_append, tl_x, tl_y)
            )

        return ret

    def paste_by_iter(
        self,
        src_data_package_iter,
        num_to_paste=1,
        allow_overlap=False,
        num_max_try=1,
        overlap_margin=0,
        in_place=False,
    ):
        """
        给定源对象迭代器，粘贴次数，是否允许重叠，不允许重叠时单个源对象的最大尝试粘贴次数，判断是否重合时的余量，将源对象粘贴到执行对象，
        返回新创建的DataPackage对象或执行对象本身。
        Args:
            src_data_package_iter: 源对象迭代器
            num_to_paste: 执行对象上最大粘贴源对象数量
            allow_overlap: 是否允许源对象的标注条目与执行对象当时的标注条目发生重合，默认为False
            num_max_try: 不允许发生重合时同一个源对象的最大尝试粘贴次数
            overlap_margin: 判断是否发生重合时的雨量，默认为0
            in_place: 是否原地操作，默认为False

        Returns:

        """

        num_pasted = 0
        if in_place:
            ret = self
        else:
            ret = self.copy()
        while num_pasted < num_to_paste:
            try:
                src_data_package = next(src_data_package_iter)
            except StopIteration:
                return ret

            # 对源对象进行基本的增强操作
            assert isinstance(src_data_package, DataPackage)

            rotate_degree = random.randint(0, 3)
            if rotate_degree != 0:
                src_data_package = src_data_package.rotate_by_multi_90(
                    rotate_degree * 90
                )

            stride = 1.0
            scale_range = [0.9 / stride, 1.0 / stride]
            scale_x = (
                random.random() * (scale_range[1] - scale_range[0]) + scale_range[0]
            )
            scale_y = (
                random.random() * (scale_range[1] - scale_range[0]) + scale_range[0]
            )
            src_data_package = src_data_package.resize_by_factor(fx=scale_x, fy=scale_y)

            if allow_overlap:
                # 在合法区域内随机生成粘贴位置左上角坐标
                tl_x = random.randint(
                    0, ret.img.shape[1] - src_data_package.img.shape[1] - 1
                )
                tl_y = random.randint(
                    0, ret.img.shape[0] - src_data_package.img.shape[0] - 1
                )
                # 调用paste_by方法执行当前源对象的粘贴操作。
                ret = ret.paste_by(src_data_package, tl_x, tl_y)
            else:
                num_try = 0
                # 需要考虑重叠冲突处理的场合，循环操作直至生成有效位置，若到达最大尝试次数依然找不到有效位置，粘贴次数自增，跳过当前源对象的粘贴操作。
                while num_try < num_max_try:
                    tl_x = random.randint(
                        0, ret.img.shape[1] - src_data_package.img.shape[1] - 1
                    )
                    tl_y = random.randint(
                        0, ret.img.shape[0] - src_data_package.img.shape[0] - 1
                    )
                    if ret.check_overlap(
                        tl_x - overlap_margin,
                        tl_y - overlap_margin,
                        src_data_package.img.shape[1] + overlap_margin * 2,
                        src_data_package.img.shape[0] + overlap_margin * 2,
                    ):
                        # logger.info("conflict")
                        num_try += 1
                        if num_try == num_max_try:
                            # logger.info("try max")
                            pass
                        continue
                    else:
                        # logger.info("paste")
                        # 调用paste_by方法执行当前源对象的粘贴操作。
                        ret = ret.paste_by(
                            src_data_package, tl_x, tl_y, in_place=in_place
                        )
                        break
            # ret.visualize()
            num_pasted += 1
        return ret

    def check_overlap(self, tl_x, tl_y, width, height):
        """
        检查某个矩形区域是否与任意标注条目出现重合
        Args:
            tl_x: 矩形区域左上角x坐标
            tl_y: 矩形区域左上角y坐标
            width: 矩形区域宽度
            height: 矩形区域高度

        Returns:

        """
        pts = tl_x, tl_y, tl_x + width, tl_y + height
        polygon_roi = cvutils.PolygonROI.create_from_rect_xyxy(*pts)

        for label_item in self.label_items:
            if label_item["shape_type"] == "rectangle":
                pt1, pt2 = label_item["points"]
                pts_ = [*pt1, *pt2]
                polygon_roi_ = cvutils.PolygonROI.create_from_rect_xyxy(*pts_)
                if polygon_roi.overlap(polygon_roi_):
                    return True
        return False

    @classmethod
    def mosaic_mxn(
        cls, data_package_list, dst_size, m=2, n=2, img_path=None, jitter=0, img_val=0
    ):
        """
        给定待拼接的DataPackage对象序列，目标尺寸，以及拼接块的行列数字，生成对象的img_path成员数据，预设像素值
        Args:
            data_package_list:
            dst_size:
            m:
            n:
            img_path:
            jitter:
            img_val:

        Returns:

        """
        # 给定的待拼接对象数量应不大于m*n
        assert len(data_package_list) <= m * n
        # 创建目标尺寸的dp
        width, height = dst_size
        ret_dp = DataPackage.gen_default_data_package(
            img_path=img_path, img_shape=[dst_size[1], dst_size[0], 3], img_val=img_val
        )
        # 计算每个拼接区域的左上角坐标
        y_block_idx_list = list(range(m))
        x_block_idx_list = list(range(n))
        y_offset = height / m
        x_offset = width / n
        ys = [round(y_block_idx * y_offset) for y_block_idx in y_block_idx_list]
        xs = [round(x_block_idx * x_offset) for x_block_idx in x_block_idx_list]
        tl_coord_list = list(itertools.product(xs, ys))

        # 将序列中的对象依次以列优先原则粘贴到待返回对象上。
        for idx, dp in enumerate(data_package_list):
            assert isinstance(dp, DataPackage)
            x, y = tl_coord_list[idx]
            x += random.randint(0, jitter[0])
            y += random.randint(0, jitter[1])
            ret_dp = ret_dp.paste_by(dp, x, y)
        return ret_dp

    @classmethod
    def mosaic_1p5(cls, data_package_list, dst_size, img_path=None, loc=0):
        ret_dp = DataPackage.gen_default_data_package(
            img_path=img_path, img_shape=[dst_size[1], dst_size[0], 3]
        )
        # loc = random.randint(0, 3)
        for idx, dp in enumerate(data_package_list):
            assert isinstance(dp, DataPackage)
            if loc == 0:
                xs = [
                    0,
                    dst_size[0] // 3 * 2,
                    dst_size[0] // 3 * 2,
                    dst_size[0] // 3 * 2,
                    dst_size[0] // 3,
                    0,
                ]
                ys = [
                    0,
                    0,
                    dst_size[0] // 3,
                    dst_size[0] // 3 * 2,
                    dst_size[0] // 3 * 2,
                    dst_size[0] // 3 * 2,
                ]
            elif loc == 1:
                xs = [dst_size[0] // 3, 0, 0, 0, dst_size[0] // 3, dst_size[0] // 3 * 2]
                ys = [
                    0,
                    0,
                    dst_size[0] // 3,
                    dst_size[0] // 3 * 2,
                    dst_size[0] // 3 * 2,
                    dst_size[0] // 3 * 2,
                ]
            elif loc == 2:
                xs = [
                    0,
                    0,
                    dst_size[0] // 3,
                    dst_size[0] // 3 * 2,
                    dst_size[0] // 3 * 2,
                    dst_size[0] // 3 * 2,
                ]
                ys = [dst_size[0] // 3, 0, 0, 0, dst_size[0] // 3, dst_size[0] // 3 * 2]
            elif loc == 3:
                xs = [dst_size[0] // 3, dst_size[0] // 3 * 2, dst_size[0] // 3, 0, 0, 0]
                ys = [dst_size[0] // 3, 0, 0, 0, dst_size[0] // 3, dst_size[0] // 3 * 2]

            ret_dp = dp.paste(ret_dp, xs[idx], ys[idx])
        return ret_dp


def gen_data_package_list_from_img_file_for_folder(dir_path, suffix_patterns):
    if not isinstance(dir_path, list):
        dir_path = [dir_path]
    img_path_list = []
    for dir_path_ in dir_path:
        img_path_list.extend(
            list(
                pyutils.glob_dir(
                    str(Path(dir_path_).absolute()), include_patterns=suffix_patterns
                )
            )
        )
    return [DataPackage.create_from_img_path(img_path) for img_path in img_path_list]


def gen_data_package_list_from_label_file_for_folder(dir_path):
    if not isinstance(dir_path, list):
        dir_path = [dir_path]
    label_path_list = []
    for dir_path_ in dir_path:
        label_path_list.extend(
            list(
                pyutils.glob_dir(
                    str(Path(dir_path_).absolute()), include_patterns=["*.json"]
                )
            )
        )
    return [
        DataPackage.create_from_label_path(label_path) for label_path in label_path_list
    ]


def filter_with_size_for_folder(
    src_dir,
    min_size=[0, 0],
    max_size=[float("inf"), float("inf")],
    min_mode="and",
    max_mode="and",
):
    dp_list = gen_data_package_list_from_label_file_for_folder(src_dir)
    ret = [
        dp
        for dp in dp_list
        if dp.filter_with_size(min_size, max_size, min_mode, max_mode)
    ]
    return ret


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


def crop_point_items_for_folder(src_dir, dst_dir, filter_func=None, crop_size=None):
    raise NotImplementedError


def paste_by_iter_for_folder(
    fg_dir,
    bg_dir,
    dst_dir,
    suffix_patterns,
    dst_size,
    num_to_gen,
    num_to_paste=1,
    allow_overlap=False,
    num_max_try=1,
    overlap_margin=0,
):
    """
    用户给定前景文件夹，背景文件夹，图像后缀，输出目标文件夹，生成图像的尺寸，以及DataPackage类的paste_by_iter方法所需的其他参数，
    从前景文件夹与目标文件夹中选取图片进行粘贴操作。
    Args:
        fg_dir: 前景文件夹路径
        bg_dir: 背景文件夹路径
        dst_dir:
        suffix_patterns:
        dst_size:
        num_to_gen:
        num_to_paste:
        allow_overlap:
        num_max_try:
        overlap_margin:

    Returns:

    """
    pyutils.mkdir(dst_dir)

    fg_data_package_list = gen_data_package_list_from_img_file_for_folder(
        fg_dir, suffix_patterns
    )
    bg_data_package_list = gen_data_package_list_from_img_file_for_folder(
        bg_dir, suffix_patterns
    )
    assert len(fg_data_package_list)
    assert len(bg_data_package_list)
    logger.info(f"fg imgs num: {len(fg_data_package_list)}")
    fg_dp_cyclic_iter = pyutils.make_cyclic_iterator(fg_data_package_list)
    bg_dp_cyclic_iter = pyutils.make_cyclic_iterator(bg_data_package_list)

    for _ in tqdm(
        range(num_to_gen),
        desc=f"synthesizing images (num to generate = {num_to_gen}, num_to_paste = {num_to_paste}): ",
    ):
        # 获取一个背景dp
        bg_dp = next(bg_dp_cyclic_iter)
        assert isinstance(bg_dp, DataPackage)
        # todo: 裁剪背景dp到指定尺寸
        tl_x = random.randint(0, bg_dp.img.shape[1] - dst_size[1] - 1)
        tl_y = random.randint(0, bg_dp.img.shape[0] - dst_size[0] - 1)
        # todo: 若bg图的尺寸小于目标尺寸，执行pad操作
        assert bg_dp.img.shape[0] > dst_size[0] and bg_dp.img.shape[1] > dst_size[1]
        ret = bg_dp.crop(
            tl_x,
            tl_y,
            tl_x + dst_size[1] - 1,
            tl_y + dst_size[0] - 1,
            img_path=bg_dp.img_path,
            append_coords_to_file_name=True,
        )

        # 调用paste_by_iter方法获取粘贴后的dp对象
        ret = ret.paste_by_iter(
            src_data_package_iter=fg_dp_cyclic_iter,
            num_to_paste=num_to_paste,
            allow_overlap=allow_overlap,
            num_max_try=num_max_try,
            overlap_margin=overlap_margin,
            in_place=False,
        )
        # 更新生成的dp对象的路径信息,保存生成的dp对象
        ret_img_path = pyutils.replace_parent(
            pyutils.append_file_name(
                ret.img_path,
                "_paste-" + datetime.datetime.now().strftime("%Y%m%d-%H%M%S-%f"),
            ),
            dst_dir,
        )
        ret.update_img_path(ret_img_path)
        ret.save()


def mosaic_mxn_for_folder(
    mosaic_dir_list, suffix_patterns, dst_dir, dst_size, m, n, num_to_gen, img_val=0
):
    pyutils.mkdir(dst_dir)

    ingredient_iter_list = []
    for mosaic_dir in mosaic_dir_list:
        ingredient_iter_list.append(
            pyutils.make_cyclic_iterator(
                gen_data_package_list_from_img_file_for_folder(
                    mosaic_dir, suffix_patterns
                )
            )
        )

    ingredient_iter_idx_iter = pyutils.make_cyclic_iterator(
        range(len(ingredient_iter_list))
    )

    for _ in tqdm(
        range(num_to_gen), desc=f"mosaic images (num to gen = {num_to_gen}): "
    ):
        ingredient_dp_list = []
        for _ in range(m * n):
            ingredient_dp_list.append(
                next(ingredient_iter_list[next(ingredient_iter_idx_iter)])
            )
        dp_height, dp_width = ingredient_dp_list[0].img.shape[:2]
        jitter_x = (dst_size[0] - (dp_width * n)) // n
        jitter_y = (dst_size[1] - (dp_height * m)) // m
        # logger.info(f"{jitter_x} {jitter_y}")
        ret = DataPackage.mosaic_mxn(
            ingredient_dp_list, dst_size, jitter=[jitter_x, jitter_y], m=m, n=n
        )

        ret.update_img_path(
            Path(dst_dir)
            / (datetime.datetime.now().strftime("%Y%m%d-%H%M%S-%f") + ".bmp")
        )
        # ret.visualize()
        save_success = ret.save()
        import time

        time.sleep(0.1)
        if not save_success:
            logger.info(f"{ret.img_path}, {ret.label_path}")
