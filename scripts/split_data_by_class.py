from pathlib import Path

from loguru import logger

from data_aug.data_package import gen_data_package_list_from_label_file_for_folder

src_dir = r"D:\data\obj_det\fg\all_bls"

dst_root_ = r"D:\data\obj_det\fg"

senario = "bls"

# cls_dst_map = {
#     "R": dst_root / f"rc_{senario}",
#     "C": dst_root / f"rc_{senario}",
#     "RC": dst_root / f"rc_{senario}",
#     "SOT": dst_root / f"sot_{senario}",
#     "LED": dst_root / f"led_{senario}",
# }

for dp in gen_data_package_list_from_label_file_for_folder(src_dir):
    # 正常来说都是 XX_body 和 XX_with_pad
    dst_root = Path(dst_root_)
    if dp.label_items[0]["label"].startswith("R"):
        dst_dir = dst_root / f"rc_{senario}"
    elif dp.label_items[0]["label"].startswith("C"):
        dst_dir = dst_root / f"rc_{senario}"
    elif dp.label_items[0]["label"].startswith("LED"):
        dst_dir = dst_root / f"led_{senario}"
    elif dp.label_items[0]["label"].startswith("SOT"):
        dst_dir = dst_root / f"sot_{senario}"
    elif dp.label_items[0]["label"].startswith("8P4R"):
        dst_dir = dst_root / f"8p4r_{senario}"
    else:
        logger.warning(f"{dp.img_path}: {dp.label_items[0]['label']}")
        continue
    Path(dst_dir).mkdir(parents=True, exist_ok=True)
    dst_img_path = Path(dst_dir) / Path(dp.img_path).name
    dp.update_img_path(dst_img_path)
    dp.save()
