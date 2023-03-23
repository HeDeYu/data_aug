from pathlib import Path

import pyutils

from data_aug.data_package import gen_data_package_list_from_label_file_for_folder

src_dir = r"D:\data\Short_circuit\ic\vertical"

dst_root = r"D:\data\Short_circuit\ic\rotate"

Path(dst_root).mkdir(exist_ok=True, parents=True)

for dp in gen_data_package_list_from_label_file_for_folder(src_dir):
    dp = dp.rotate_by_multi_90(90)

    dp.update_img_path(pyutils.replace_parent(dp.img_path, dst_root))
    dp.save()
