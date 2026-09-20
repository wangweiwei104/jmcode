# -*- coding:utf-8 -*-
"""
Created on 11/22/23 10:41 AM
@author  : WangWei
@contact : ww_geophy@126.com
@desc    :
"""
# -*- coding: utf-8 -*-
"""
Created on 2020/6/17 6:55 下午
---------
@summary:
---------
@author: Boris
"""
import getopt
import sys

import yaml

from jmcode.encrypt_pys import cpsrcfiles


def usage():
    """
python代码 复制|备份
参数说明：
    -i | --input_dir    yaml配置文件路径
    yaml文件中支持：
        input_dir
        input_files
        output_dir  # 必选，输出目录
        output_file # 可选，输出tar.gz压缩包完整路径
    """


def execute():
    try:
        options, args = getopt.getopt(
            sys.argv[1:],
            "hi:",
            [
                "help",
                "input_dir=",
            ],
        )
        input_file_path = ""
        ignore_files = ""
        except_main_file = 1

        for name, value in options:
            if name in ("-h", "--help"):
                print(usage.__doc__)
                sys.exit()
            elif name in ("-i", "--input_dir"):
                input_file_path = value

        if not input_file_path:
            print("需指定-i 或 input_dir")
            print(usage.__doc__)
            sys.exit()

        with open(input_file_path, encoding="utf-8") as f:
            try:
                args = yaml.safe_load(f) or {}
                input_dir = args.get('input_dir') or args.get('input_file_path')
                input_files = args.get('input_files', [])
                output_dir = args.get('output_dir') or args.get('output_file_path')
                output_file = args.get('output_file')
                if not output_dir:
                    raise ValueError("yaml中必须提供 output_dir")
            except (yaml.YAMLError, ValueError) as e:
                print(e)
                return

        if input_dir is None:
            input_dir = input_file_path

        cpsrcfiles(input_dir, input_files, output_dir,
                   ignore_files, except_main_file,
                   output_file=output_file)

    except getopt.GetoptError:
        print(usage.__doc__)
        sys.exit()

