#!/usr/bin/env python3
"""Copy external audio dirs into repo-local sources/ (real files, not symlinks)."""

from __future__ import annotations

import argparse
import shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parent
SOURCES_ROOT = ROOT / "sources"

COPY_TARGETS = [
    ("google_ru_male", "google/ru_male"),
    ("google_ru_female", "google/ru_female"),
    ("our_ru_male", "our/ru_male"),
    ("our_ru_female", "our/ru_female"),
]


def copy_tree(src: Path, dst: Path) -> int:
    if not src.is_dir():
        print(f"Warning: source missing, skipped: {src}")
        return 0

    if dst.exists():
        shutil.rmtree(dst)

    count = 0

    def _copy(src_path: str, dst_path: str) -> str:
        nonlocal count
        shutil.copy2(src_path, dst_path)
        count += 1
        return dst_path

    shutil.copytree(src, dst, copy_function=_copy, symlinks=False)
    print(f"Copied {count} files: {src} -> {dst}")
    return count


def copy_ru_text_files(original_src: Path | None, normalized_src: Path | None, dst: Path) -> int:
    dst.mkdir(parents=True, exist_ok=True)
    count = 0

    if original_src and original_src.is_file():
        shutil.copy2(original_src, dst / "original.txt")
        count += 1
        print(f"Copied: {original_src} -> {dst / 'original.txt'}")
    elif original_src:
        print(f"Warning: missing ru original text, skipped: {original_src}")

    norm_file: Path | None = None
    if normalized_src:
        norm_file = normalized_src / "normalized.txt" if normalized_src.is_dir() else normalized_src
    if norm_file and norm_file.is_file():
        shutil.copy2(norm_file, dst / "normalized.txt")
        count += 1
        print(f"Copied: {norm_file} -> {dst / 'normalized.txt'}")
    elif normalized_src:
        print(f"Warning: missing ru normalized text, skipped: {normalized_src}")

    return count


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)

    for arg_name, _ in COPY_TARGETS:
        parser.add_argument(f"--{arg_name}", type=Path, required=False)
    parser.add_argument("--ru_original", type=Path, required=False)
    parser.add_argument("--our_ru_normalized", type=Path, required=False)
    args = parser.parse_args()

    total = 0
    for arg_name, rel_dst in COPY_TARGETS:
        if not getattr(args, arg_name):
            continue
        src = getattr(args, arg_name).resolve()
        dst = SOURCES_ROOT / rel_dst
        total += copy_tree(src, dst)

    if args.ru_original or args.our_ru_normalized:
        total += copy_ru_text_files(
            args.ru_original.resolve() if args.ru_original else None,
            args.our_ru_normalized.resolve() if args.our_ru_normalized else None,
            SOURCES_ROOT / "our/ru_text",
        )

    print(f"Done. {total} files copied under {SOURCES_ROOT}")


if __name__ == "__main__":
    main()
