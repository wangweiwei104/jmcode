import os

from jmcode.encrypt_pys import cpsrcfiles


def test_cpsrc_copies_sources_without_encrypting(tmp_path):
    src_dir = tmp_path / "src"
    src_dir.mkdir()
    (src_dir / "demo.py").write_text('print("hello")\n', encoding="utf-8")
    (src_dir / "pkg").mkdir()
    (src_dir / "pkg" / "util.py").write_text('x = 1\n', encoding="utf-8")

    out_dir = tmp_path / "out"
    result = cpsrcfiles(str(src_dir), [], str(out_dir), None, 1, None)

    assert result == str(out_dir)
    assert (out_dir / "demo.py").exists()
    assert (out_dir / "pkg" / "util.py").exists()
    assert not any(p.suffix in {".so", ".pyd"} for p in out_dir.rglob("*"))
