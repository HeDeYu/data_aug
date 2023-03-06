# -*- coding:utf-8 -*-
# @FileName :batch_rm_image_data.py
# @Author   :Deyu He
# @Time     :2023/3/6 14:20

import pyutils


# 仅支持原地操作，去除标注文件中的图像内容
def batch_rm_image_data(src_json_dir):
    for src_json_path in pyutils.glob_dir(src_json_dir, include_patterns=["*.json"]):
        json_data = pyutils.load_json(src_json_path)

        json_data["imageData"] = None
        pyutils.dump_json(json_data, src_json_path)


if __name__ == "__main__":
    src_json_dir = r""
    batch_rm_image_data(src_json_dir=src_json_dir)
