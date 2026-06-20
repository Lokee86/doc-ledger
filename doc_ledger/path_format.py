from __future__ import annotations

from pathlib import PurePath


def posix_relative_path(target_path: PurePath, base_path: PurePath) -> str:
    return target_path.relative_to(base_path).as_posix()
