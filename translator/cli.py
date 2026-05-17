from __future__ import annotations

import argparse
import os
from concurrent.futures import ThreadPoolExecutor

from translator.export import export_xlsx
from translator.parser import collect_input_files
from translator.processor import process_file


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Translate DNA sequences and detect ORFs.")
    parser.add_argument("--input", "-i", help="Input .txt, .csv, .fasta/.fa file or folder")
    parser.add_argument("--export", "-e", help="Path to an .xlsx export file")
    parser.add_argument(
        "--translation",
        choices=("both", "rna", "protein"),
        default="both",
        help="Choose RNA, protein, or both outputs",
    )
    parser.add_argument("--min-aa", type=int, default=0, help="Minimum protein length in amino acids")
    parser.add_argument("--complete", action="store_true", help="Keep only complete ORFs with a stop codon")
    parser.add_argument("--longest", action="store_true", help="Keep only the longest protein per sequence")
    parser.add_argument("--folder", action="store_true", help="Treat --input as a folder")
    return parser


def run_cli(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    if not args.input:
        parser.print_help()
        return 2

    input_type = "folder" if args.folder or os.path.isdir(args.input) else "file"
    files = collect_input_files(args.input, input_type)
    if not files:
        print("No supported input files found.")
        return 1

    if len(files) == 1:
        name, path = next(iter(files.items()))
        results = {
            name: process_file(
                path,
                args.translation,
                min_amino_acids=max(args.min_aa, 0),
                complete_only=args.complete,
                longest_only=args.longest,
            )
        }
    else:
        with ThreadPoolExecutor() as executor:
            futures = {
                name: executor.submit(
                    process_file,
                    path,
                    args.translation,
                    max(args.min_aa, 0),
                    args.complete,
                    args.longest,
                )
                for name, path in files.items()
            }
            results = {name: future.result() for name, future in futures.items()}

    _print_summary(results)

    if args.export:
        if export_xlsx(results, args.export):
            print(f"Exported Excel results to {args.export}")
        else:
            return 1

    return 0


def _print_summary(results: dict) -> None:
    for filename, data in results.items():
        stats = data.get("Stats")
        if not data.get("Valid", False):
            print(f"{filename}: no valid DNA sequence found")
            continue
        print(
            f"{filename}: {stats.length} bp, GC {stats.gc_percent}%, "
            f"{len(data['ORFs'])}/{len(data['AllORFs'])} ORFs shown, "
            f"longest {stats.longest_protein_length} aa"
        )
