# -*- coding: utf-8 -*-
"""
Created on 2018-07-18 18:24
---------
@summary: 加密python代码为pyd/so
---------
@author: Boris
"""
import os
import re
import shutil
import tarfile
import tempfile
from distutils.command.build_py import build_py
from distutils.core import setup
from typing import Union, List

from Cython.Build import cythonize

from jmcode.log import logger


def get_package_dir(*args, **kwargs):
    return ""


# 重写get_package_dir， 否者生成的so文件路径有问题
build_py.get_package_dir = get_package_dir


class TemporaryDirectory(object):
    def __enter__(self):
        self.name = tempfile.mkdtemp()
        return self.name

    def __exit__(self, exc_type, exc_value, traceback):
        shutil.rmtree(self.name)


def search(content, regexs):
    if isinstance(regexs, str):
        return re.search(regexs, content)

    for regex in regexs:
        if re.search(regex, content):
            return True


def walk_file(file_path):
    if os.path.isdir(file_path):
        for current_path, sub_folders, files_name in os.walk(file_path):
            for file in files_name:
                file_path = os.path.join(current_path, file)
                yield file_path

    else:
        yield file_path


def is_within_path(path, directory):
    path = os.path.abspath(path)
    directory = os.path.abspath(directory)
    try:
        return os.path.commonpath([path, directory]) == directory
    except ValueError:
        return False


def clean_output_path(output_path):
    if not output_path:
        return
    if os.path.isdir(output_path):
        shutil.rmtree(output_path)
    elif os.path.exists(output_path):
        os.remove(output_path)


def normalize_ignore_files(ignore_files):
    if ignore_files is None:
        return []
    if isinstance(ignore_files, str):
        return [ignore_files]
    return list(ignore_files)


def add_ignore_path(ignore_files, input_file_path, output_file_path):
    ignore_files = normalize_ignore_files(ignore_files)
    if not os.path.isdir(input_file_path) or not output_file_path:
        return ignore_files

    input_abs = os.path.abspath(input_file_path)
    output_abs = os.path.abspath(output_file_path)
    if is_within_path(output_abs, input_abs):
        rel_path = os.path.relpath(output_abs, input_abs)
        if rel_path not in (".", "") and rel_path not in ignore_files:
            ignore_files.append(rel_path)
    return ignore_files


def remove_build_dirs(root_path):
    if not root_path or not os.path.isdir(root_path):
        return
    for current_path, sub_dirs, _ in os.walk(root_path):
        for sub_dir in list(sub_dirs):
            if sub_dir == "build":
                build_path = os.path.join(current_path, sub_dir)
                shutil.rmtree(build_path)
                sub_dirs.remove(sub_dir)


def copy_files(src_path, dst_path):
    if os.path.isdir(src_path):
        clean_output_path(dst_path)

        abs_dst = os.path.abspath(dst_path)

        def callable(src, names: list):
            ignore = []
            for name in names:
                full_name = os.path.abspath(os.path.join(src, name))
                if name in ["dist", ".git", "venv", ".idea", "__pycache__", "build"]:
                    ignore.append(name)
                    continue
                if full_name == abs_dst or is_within_path(abs_dst, full_name) or is_within_path(full_name, abs_dst):
                    ignore.append(name)
            return ignore

        shutil.copytree(src_path, dst_path, ignore=callable)
    else:
        if not os.path.exists(dst_path):
            os.makedirs(dst_path)
        shutil.copyfile(src_path, os.path.join(dst_path, os.path.basename(src_path)))


def copy_file_list(src_path, src_files, dst_path):
    total_count = len(src_files)
    for i, src_f in enumerate(src_files):
        full_dst_path = os.path.join(dst_path, src_f)
        full_dst_dir = os.path.dirname(full_dst_path)
        if not os.path.exists(full_dst_dir):
            os.makedirs(full_dst_dir)
        shutil.copyfile(os.path.join(src_path, src_f), full_dst_path)
        logger.debug("正在复制 {}/{},  {}".format(i + 1, total_count, src_f))

def get_py_files(files, ignore_files: Union[List, str, None] = None):
    """
    @summary:
    ---------
    @param files: 文件列表
    #param ignore_files: 忽略的文件，支持正则
    ---------
    @result:
    """
    for file in files:
        if file.endswith(".py"):
            if ignore_files and search(file, regexs=ignore_files):  # 该文件是忽略的文件
                pass
            else:
                yield file


def filter_cannot_encrypted_py(files, except_main_file):
    """
    过滤掉不能加密的文件，如 log.py __main__.py 以及包含 if __name__ == "__main__": 的文件
    Args:
        files:

    Returns:

    """
    _files = []
    pattern = re.compile(r'^\s*#.*$', re.MULTILINE)
    for file in files:
        if search(file, regexs="__.*?.py"):
            continue

        if except_main_file:
            with open(file, "r", encoding="utf-8") as f:
                content = f.read()
                content = pattern.sub('', content)
                if search(content, regexs="__main__"):
                    continue

        _files.append(file)

    return _files


def encrypt_py(py_files: list):
    encrypted_py = []

    with TemporaryDirectory() as td:
        total_count = len(py_files)
        for i, py_file in enumerate(py_files):
            try:
                dir_name = os.path.dirname(py_file)
                file_name = os.path.basename(py_file)

                os.chdir(dir_name)

                logger.debug("正在加密 {}/{},  {}".format(i + 1, total_count, file_name))

                setup(
                    ext_modules=cythonize([file_name], quiet=True, language_level=3),
                    script_args=["build_ext", "-t", td, "--inplace"],
                )

                encrypted_py.append(py_file)
                logger.debug("加密成功 {}".format(file_name))

            except Exception as e:
                logger.exception("加密失败 {} , error {}".format(py_file, e))
                temp_c = py_file.replace(".py", ".c")
                if os.path.exists(temp_c):
                    os.remove(temp_c)

        return encrypted_py


def delete_files(files_path):
    """
    @summary: 删除文件
    ---------
    @param files_path: 文件路径 py 及 c 文件
    ---------
    @result:
    """
    try:
        # 删除python文件及c文件
        for file in files_path:
            os.remove(file)  # py文件
            os.remove(file.replace(".py", ".c"))  # c文件

    except Exception as e:
        pass


def rename_excrypted_file(output_file_path):
    files = walk_file(output_file_path)
    for file in files:
        if file.endswith(".pyd") or file.endswith(".so"):
            new_filename = re.sub("(.*)\..*\.(.*)", r"\1.\2", file)
            os.rename(file, new_filename)


def archive_directory(source_dir, archive_path):
    source_dir = os.path.abspath(source_dir)
    archive_path = os.path.abspath(archive_path)
    if os.path.exists(archive_path):
        os.remove(archive_path)
    os.makedirs(os.path.dirname(archive_path) or ".", exist_ok=True)
    with tarfile.open(archive_path, "w:gz") as tar:
        tar.add(source_dir, arcname=os.path.basename(source_dir))


def prepare_output_target(input_file_path, output_file_path):
    input_file_path = os.path.abspath(input_file_path)
    if output_file_path is None:
        if os.path.isdir(input_file_path):
            output_dir = os.path.join(input_file_path, "dist", os.path.basename(input_file_path))
        else:
            output_dir = os.path.join(os.path.dirname(input_file_path), "dist")
        return output_dir, None

    output_file_path = os.path.abspath(output_file_path)
    if output_file_path.endswith(".tar.gz"):
        archive_name = os.path.basename(output_file_path)[:-7]
        output_dir = os.path.join(os.path.dirname(output_file_path), archive_name)
        return output_dir, output_file_path

    return output_file_path, None


def start_encrypt(
    input_file_path,
    input_files: str = None,
    output_file_path: str = None,
    ignore_files: Union[List, str, None] = None,
    except_main_file: int = 1,
    output_file: str = None,
):
    assert input_file_path, "input_file_path cannot be null"
    input_files = input_files or []
    input_file_path = os.path.abspath(input_file_path)

    if output_file_path is not None:
        output_file_path = os.path.abspath(output_file_path)
        assert input_file_path != output_file_path, "output_file_path must be diffent with input_file_path"
        if os.path.isfile(output_file_path):
            raise ValueError("output_file_path need a dir path")

    if output_file is not None:
        output_file = os.path.abspath(output_file)

    output_dir = output_file_path
    if output_dir is None:
        if os.path.isdir(input_file_path):
            output_dir = os.path.join(input_file_path, "dist", os.path.basename(input_file_path))
        else:
            output_dir = os.path.join(os.path.dirname(input_file_path), "dist")
    output_dir = os.path.abspath(output_dir)

    clean_output_path(output_dir)
    if output_file is not None:
        clean_output_path(output_file)

    if len(input_files) == 0:
        copy_files(input_file_path, output_dir)
    else:
        copy_file_list(input_file_path, input_files, output_dir)

    files = walk_file(output_dir)
    py_files = get_py_files(files, ignore_files)
    need_encrypted_py = filter_cannot_encrypted_py(py_files, except_main_file)
    encrypted_py = encrypt_py(need_encrypted_py)

    delete_files(encrypted_py)
    rename_excrypted_file(output_dir)
    remove_build_dirs(output_dir)

    if output_file is not None:
        archive_directory(output_dir, output_file)

    logger.debug(
        "加密完成 total_count={}, success_count={}, 生成到 {}".format(
            len(need_encrypted_py), len(encrypted_py), output_file or output_dir
        )
    )
    return output_file or output_dir


def cpsrcfiles(
    input_file_path,
    input_files: str = None,
    output_file_path: str = None,
    ignore_files: Union[List, str, None] = None,
    except_main_file: int = 1,
    output_file: str = None,
):
    """Copy source files as-is, preserving the original directory structure.

    Unlike jmpro, cpsrc is not an encryption command. It simply copies the specified
    source files/directories to output_dir without invoking Cython or creating
    compiled binary artifacts.
    """
    assert input_file_path, "input_file_path cannot be null"
    input_files = input_files or []
    input_file_path = os.path.abspath(input_file_path)

    if output_file_path is not None:
        output_file_path = os.path.abspath(output_file_path)
        assert input_file_path != output_file_path, "output_file_path must be diffent with input_file_path"
        if os.path.isfile(output_file_path):
            raise ValueError("output_file_path need a dir path")

    if output_file is not None:
        output_file = os.path.abspath(output_file)

    output_dir = output_file_path
    if output_dir is None:
        if os.path.isdir(input_file_path):
            output_dir = os.path.join(input_file_path, "dist", os.path.basename(input_file_path))
        else:
            output_dir = os.path.join(os.path.dirname(input_file_path), "dist")
    output_dir = os.path.abspath(output_dir)

    clean_output_path(output_dir)
    if output_file is not None:
        clean_output_path(output_file)

    if len(input_files) == 0:
        copy_files(input_file_path, output_dir)
    else:
        copy_file_list(input_file_path, input_files, output_dir)

    if output_file is not None:
        archive_directory(output_dir, output_file)

    logger.debug("复制完成，保留源代码原结构，生成到 %s", output_file or output_dir)
    return output_file or output_dir

