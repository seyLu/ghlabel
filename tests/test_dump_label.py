import logging
import shutil
from pathlib import Path

import pytest

from scripts.dump_label import DumpLabel

logger = logging.getLogger("root")
logger.setLevel(logging.ERROR)


@pytest.fixture
def tmp_dir(tmp_path: str) -> Path:
    _tmp_dir: Path = Path(tmp_path, "tmp_labels")
    _tmp_dir.mkdir()
    yield _tmp_dir
    shutil.rmtree(_tmp_dir)


def test_init_dir(tmp_dir: Path) -> None:
    dir: Path = tmp_dir

    tmp_file: Path = Path(dir, "tmp_file.txt")
    tmp_file.touch()

    DumpLabel._init_dir(dir=str(dir))

    assert len(list(dir.iterdir())) == 0


def test_dump(tmp_dir: Path) -> None:
    dir: Path = tmp_dir
    new: bool = True
    ext: str = "yaml"

    DumpLabel.dump(dir=str(dir), new=new, ext=ext)

    assert Path(dir, "_remove_labels.yaml").exists()
    assert Path(dir, "default_labels.yaml").exists()
