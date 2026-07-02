#!/usr/bin/env python3
"""
Regenerate ru_data.json from repo-local sources/.

Google offline TTS uses 1-based indices (1.wav).
Our model uses 0-based indices (ru-CMOS000.wav).
"""

from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent


def load_config() -> dict:
    with open(ROOT / "config.json", encoding="utf-8") as f:
        return json.load(f)


def resolve_path(path_str: str) -> Path:
    path = Path(path_str)
    if not path.is_absolute():
        path = (ROOT / path).resolve()
    return path


def rel_path(path: Path) -> str:
    return "./" + path.relative_to(ROOT).as_posix()


def audio_entry(src: Path) -> str | None:
    return rel_path(src) if src.exists() else None


def read_line_texts(path: Path) -> list[str]:
    if not path.exists():
        raise FileNotFoundError(f"Missing text file: {path}")
    return [line.strip() for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def build_ru_json(cfg: dict) -> dict:
    naming = cfg["naming"]
    num_items = cfg["num_items"]

    google_male_dir = resolve_path(cfg["google"]["ru_male_dir"])
    google_female_dir = resolve_path(cfg["google"]["ru_female_dir"])
    our_male_dir = resolve_path(cfg["our"]["ru_male_dir"])
    our_female_dir = resolve_path(cfg["our"]["ru_female_dir"])
    ru_text_dir = resolve_path(cfg["our"]["ru_text_dir"])

    raw_texts = read_line_texts(ru_text_dir / "original.txt")
    normalized_texts = read_line_texts(ru_text_dir / "normalized.txt")

    if len(raw_texts) < num_items:
        raise ValueError(f"Expected {num_items} raw texts, got {len(raw_texts)}")
    if len(normalized_texts) < num_items:
        raise ValueError(f"Expected {num_items} normalized texts, got {len(normalized_texts)}")

    result: dict[str, dict] = {}
    for n in range(1, num_items + 1):
        item_id = f"{n:03d}"
        idx = n - 1
        raw_text = raw_texts[idx]
        normalized_text = normalized_texts[idx]

        google_male_wav = google_male_dir / naming["google_wav"].format(n=n)
        google_female_wav = google_female_dir / naming["google_wav"].format(n=n)
        our_male_wav = our_male_dir / naming["our_ru_wav"].format(idx=idx)
        our_female_wav = our_female_dir / naming["our_ru_wav"].format(idx=idx)

        if not google_male_wav.exists():
            raise FileNotFoundError(f"Missing Google ru male audio: {google_male_wav}")
        if not google_female_wav.exists():
            raise FileNotFoundError(f"Missing Google ru female audio: {google_female_wav}")

        result[item_id] = {
            "raw_text": raw_text,
            "normalized_text": normalized_text,
            "male": {
                "google_audio": rel_path(google_male_wav),
                "our_audio": audio_entry(our_male_wav),
            },
            "female": {
                "google_audio": rel_path(google_female_wav),
                "our_audio": audio_entry(our_female_wav),
            },
        }

    return result


def main() -> None:
    cfg = load_config()
    ru_data = build_ru_json(cfg)

    with open(ROOT / "ru_data.json", "w", encoding="utf-8") as f:
        json.dump(ru_data, f, ensure_ascii=False, indent=4)

    ru_missing_male = sum(1 for v in ru_data.values() if not v["male"]["our_audio"])
    ru_missing_female = sum(1 for v in ru_data.values() if not v["female"]["our_audio"])

    print(f"Generated ru_data.json ({len(ru_data)} items)")
    if ru_missing_male:
        print(f"Warning: RU male our audio missing for {ru_missing_male} items.")
    if ru_missing_female:
        print(f"Warning: RU female our audio missing for {ru_missing_female} items.")


if __name__ == "__main__":
    main()
