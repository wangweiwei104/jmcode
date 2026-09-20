import os

from jmcode.encrypt_pys import start_encrypt


def test_nested_output_dir_is_encrypted(tmp_path):
    src_dir = tmp_path / "proj"
    src_dir.mkdir()
    (src_dir / "demo.py").write_text('print("hello")\n', encoding="utf-8")

    output_dir = src_dir / "out"
    result = start_encrypt(str(src_dir), [], str(output_dir), None, 0)

    assert result == str(output_dir)
    assert output_dir.exists()
    output_files = list(output_dir.iterdir())
    assert any(f.suffix in {".so", ".pyd"} for f in output_files), output_files
    assert not any(f.suffix == ".py" for f in output_files), output_files
