import sys
from pathlib import Path


def test_setup_metadata_and_entry_points():
    setup_py = Path(__file__).resolve().parents[1] / "setup.py"
    content = setup_py.read_text(encoding="utf-8")

    assert 'name="jmcode"' in content
    assert 'author="wangwei"' in content
    assert 'author_email="ww_geophy@126.com"' in content
    assert 'description="python项目代码一键加密打包"' in content
    assert 'cpsrc = jmcode.cmdline_cpsrc:execute' in content
    assert 'jmcode = jmcode.cmdline_jmpro:execute' in content
    assert 'jmcode.cmdline_cpsrc:execute' in content
    assert 'jmcode.cmdline_jmpro:execute' in content


def test_wheel_python_tag_uses_python_311_boundary():
    setup_py = Path(__file__).resolve().parents[1] / "setup.py"
    content = setup_py.read_text(encoding="utf-8")

    assert 'python_tag = "py311" if version_info >= (3, 11) else "py3"' in content
    assert '"python_tag": python_tag' in content
