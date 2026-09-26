# jmcode

![](https://img.shields.io/badge/python-3.0-brightgreen)

## 简介

将python代码一键加密为so或pyd。支持单个文件加密，整个项目加密。

Git仓库地址: https://github.com/wangweiwei104/jmcode

## 编译

```
python setup.py bdist_wheel -d dist
```


## 安装

    pip install jmcode

## 使用方法

    cpsrc -i xxx.yaml
    jmcode -i xxx.yaml

加密后的文件默认存储在 dist/project_name/ 下

## 附yaml文件的示例 [args_jmcode.yaml](tests/args_jmcode.yaml)

```yaml
input_dir: . #待加密文件夹路径，可是相对路径或绝对路径
input_files: #待加密文件
  - main.py
  - main_catbin.py
  - main_dataset_view.py
  - main_gen_dataset.py
  - main_getFileNames.py
  - main_split_signal.py
  - main_pth_version.py
  - main_pick_vel.py
  - EventPick.py
  - EventPlot.py
  - csvlog.py
  - data.py
  - dataset_hdf5.py
  - gen_dataset_base.py
  - gen_dataset_bg.py
  - gen_dataset_auto_bg.py
  - option.py
  - option_common.py
  - solver.py
  - train_test.py
  - common.py
  - utils.py
  - visualizer.py
  # - thirty_lib.py
  - AGCgain.py
  # - thirty_libs/libcadzow.so
  - model/__init__.py
  - model/bgnet.py
  - checkpoints/BGNET_pretrained_2023-05-12-08-31-44.pth
  - checkpoints/model-demo/BGNET_0050.pth
  - configs/args_dataset_demo.yaml
  - configs/args_main_demo.yaml
  - configs/args_split_signal_demo.yaml
  - data/demo.segy
#加密后的文件输出路径，默认在input_file_path下创建dist文件夹，存放加密后的文件
output_dir: ./dist/AISeisDenoise
output_file: ./dist/AISeisDenoise.tar.gz
```