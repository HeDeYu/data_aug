# -*- coding:utf-8 -*-
# @FileName :synthesize_by_paste_for_obj_det.py
# @Author   :Deyu He
# @Time     :2022/12/14 19:57

import os

from data_aug.data_package import mosaic_mxn_online

fg_root = r"D:\data\obj_det\fg"

# fg_img_dirs_all_all_l = [
#     r"STB_RC_L",
#     r"STB_LED_L",
#     r"STB_SOT_L",
#     r"STB_8P4R_L",
#     r"BLS_RC_L",
#     r"BLS_LED_L",
#     r"BLS_SOT_L",
#     r"BLS_8P4R_L",
# ]
# fg_img_dirs_all_all_l = [os.path.join(fg_root, dir_) for dir_ in fg_img_dirs_all_all_l]

# fg_img_dirs_all_rc_s = [r"STB_RC_S", r"BLS_RC_S"]
# fg_img_dirs_all_rc_s = [os.path.join(fg_root, dir_) for dir_ in fg_img_dirs_all_rc_s]
#
# fg_img_dirs_all_rc_m = [
#     r"STB_RC_M",
#     r"BLS_RC_M",
#     r"STB_LED_M",
#     r"BLS_LED_M",
# ]
# fg_img_dirs_all_rc_m = [os.path.join(fg_root, dir_) for dir_ in fg_img_dirs_all_rc_m]
#
# fg_img_dirs_all_rc_l = [
#     r"STB_RC_L",
#     r"BLS_RC_L",
#     r"STB_LED_L",
#     r"BLS_LED_L",
# ]
# fg_img_dirs_all_rc_l = [os.path.join(fg_root, dir_) for dir_ in fg_img_dirs_all_rc_l]
#
# fg_img_dirs_all_sot_m = [
#     r"STB_SOT_M",
#     r"BLS_SOT_M",
#     r"STB_8P4R_M",
#     r"BLS_8P4R_M",
# ]
# fg_img_dirs_all_sot_m = [os.path.join(fg_root, dir_) for dir_ in fg_img_dirs_all_sot_m]
#
# fg_img_dirs_all_sot_l = [
#     r"STB_SOT_L",
#     r"BLS_SOT_L",
#     r"STB_8P4R_L",
#     r"BLS_8P4R_L",
# ]
# fg_img_dirs_all_sot_l = [os.path.join(fg_root, dir_) for dir_ in fg_img_dirs_all_sot_l]
#
# fg_img_dirs_all_sot_xl = [
#     r"STB_SOT_XL",
#     r"BLS_SOT_XL",
# ]
# fg_img_dirs_all_sot_xl = [
#     os.path.join(fg_root, dir_) for dir_ in fg_img_dirs_all_sot_xl
# ]
#
# fg_img_dirs_all_ic_m = [
#     # r"STB_IC_L",
#     r"BLS_IC_M",
# ]
# fg_img_dirs_all_ic_m = [os.path.join(fg_root, dir_) for dir_ in fg_img_dirs_all_ic_m]
#
# fg_img_dirs_all_ic_l = [
#     # r"STB_IC_L",
#     r"BLS_IC_L",
# ]
# fg_img_dirs_all_ic_l = [os.path.join(fg_root, dir_) for dir_ in fg_img_dirs_all_ic_l]
#
# fg_img_dirs_all_ic_xl = [
#     # r"STB_IC_L",
#     r"BLS_IC_XL",
# ]
# fg_img_dirs_all_ic_xl = [os.path.join(fg_root, dir_) for dir_ in fg_img_dirs_all_ic_xl]

#
# fg_img_dirs_stb_led_sot_8p4r_m = [
#     r"STB_LED_M",
#     r"STB_SOT_M",
#     r"STB_8P4R_M",
# ]
# fg_img_dirs_stb_led_sot_8p4r_m = [
#     os.path.join(fg_root, dir_) for dir_ in fg_img_dirs_stb_led_sot_8p4r_m
# ]
#
# fg_img_dirs_bls_led_sot_8p4r_m = [
#     r"BLS_LED_M",
#     r"BLS_SOT_M",
#     r"BLS_8P4R_M",
# ]
# fg_img_dirs_bls_led_sot_8p4r_m = [
#     os.path.join(fg_root, dir_) for dir_ in fg_img_dirs_bls_led_sot_8p4r_m
# ]


# fg_img_dirs_sot_stb = [
#     os.path.join(fg_root, dir_) for dir_ in fg_img_dirs_sot_stb
# ]

# bg_root = r"D:\data\obj_det\bg"
# bg_img_dirs = [
#     r"stb_15um_white_bg",
#     r"stb_15um_green_bg",
#     r"stb_15um_red_bg",
#     r"stb_15um_blue_bg",
#     r"stb_15um_black_bg",
#     r"stb_15um_yellow_bg",
# ]
# bg_img_dirs = [os.path.join(bg_root, dir_) for dir_ in bg_img_dirs]

# fg_dir, name, dst_size, num_to_gen, num_to_paste
# candidates = [
#     [fg_img_dirs_sot_stb, "sot_stb", 480, 6, 1],
# ]

# for first_size in np.linspace(480, 240, 13):
#     for fg_img_dirs, name, dst_size, num_to_gen, num_to_paste in candidates:  # type: ignore
#         dst_dir = rf"D:\data\obj_det\synthesize_by_paste\{name}_{str(dst_size)}"
#         logger.info("fg_img_dirs:")
#         logger.info(fg_img_dirs)
#         logger.info("bg_img_dirs:")
#         logger.info(bg_img_dirs)
#         logger.info("dst_dir:")
#         logger.info(dst_dir)
#         paste_by_iter_for_folder(
#             fg_dir=fg_img_dirs,
#             bg_dir=bg_img_dirs,
#             dst_dir=dst_dir,
#             suffix_patterns=["*.bmp"],
#             dst_size=[dst_size, dst_size],
#             num_to_gen=num_to_gen,
#             num_to_paste=num_to_paste,
#             allow_overlap=False,
#             num_max_try=20,
#             overlap_margin=5,
#             first_size=first_size,
#             max_size=None,
#             min_size=None,
#         )

bg_paste_root = r"D:\data\obj_det\bg"
bg_img_dirs = [
    r"stb_15um_white_bg",
    r"stb_15um_green_bg",
    r"stb_15um_red_bg",
    r"stb_15um_blue_bg",
    r"stb_15um_black_bg",
    r"stb_15um_yellow_bg",
]
bg_img_dirs_for_paste = [os.path.join(bg_paste_root, dir_) for dir_ in bg_img_dirs]

fg_img_dirs_rc_stb = [r"rc_stb"]
fg_img_dirs_led_stb = [r"led_stb"]
fg_img_dirs_8p4r_stb = [r"8p4r_stb"]
fg_img_dirs_sot_stb = [r"sot_stb"]
fg_img_dirs_ic_stb = [r"ic_stb"]

fg_img_dir_ll = [
    [os.path.join(fg_root, dir_) for dir_ in fg_img_dirs_rc_stb],
    [os.path.join(fg_root, dir_) for dir_ in fg_img_dirs_led_stb],
    [os.path.join(fg_root, dir_) for dir_ in fg_img_dirs_8p4r_stb],
    [os.path.join(fg_root, dir_) for dir_ in fg_img_dirs_sot_stb],
    [os.path.join(fg_root, dir_) for dir_ in fg_img_dirs_ic_stb],
]
min_size_list = [None, None, 32, 32, 64]

bg_mosaic_root = r"D:\data\obj_det\bg_for_mosaic"
bg_img_dirs_for_mosaic = [
    "bls_bg",
]
bg_img_dirs_for_mosaic = [
    os.path.join(bg_mosaic_root, dir_) for dir_ in bg_img_dirs_for_mosaic
]


mosaic_mxn_online(
    bg_img_dirs_for_paste,
    fg_img_dir_ll,
    bg_img_dirs_for_mosaic,
    [1024, 1024],
    [256, 256],
    4,
    4,
    30,
    r"D:\data\obj_det\temp",
    "*.bmp",
    num_to_paste_for_block=20,
    # max_size_list=max_size_list,
    # min_size_list=min_size_list,
)
