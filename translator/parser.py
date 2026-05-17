from __future__ import annotations

import csv
import os


SUPPORTED_EXTENSIONS = (".txt", ".csv", ".fasta", ".fa")


def read_file(filepath: str) -> str:
    ext = os.path.splitext(filepath)[1].lower()
    try:
        with open(filepath, "r", encoding="utf-8") as file:
            if ext in (".txt", ".fasta", ".fa"):
                lines = [line.strip() for line in file if not line.startswith(">")]
                return "".join(lines)
            if ext == ".csv":
                reader = csv.reader(file)
                return "\n".join(row[0] for row in reader if row)
    except OSError as exc:
        print(f"[read_file] Could not read '{filepath}': {exc}")
    return ""


def collect_input_files(path: str, input_type: str) -> dict[str, str]:
    if input_type == "file":
        return {os.path.basename(path): path}

    supported = [
        filename
        for filename in os.listdir(path)
        if filename.lower().endswith(SUPPORTED_EXTENSIONS)
    ]
    return {filename: os.path.join(path, filename) for filename in sorted(supported)}
