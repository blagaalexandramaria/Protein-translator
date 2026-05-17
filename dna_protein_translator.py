from __future__ import annotations

import sys

from translator import (
    base_counts,
    clean_dna,
    complement_dna,
    detect_orfs,
    dna_to_rna,
    filter_orfs,
    gc_content,
    reverse_complement,
    rna_to_protein_all,
    translate_dna,
    translate_rna_codon,
    validate_dna,
)
from translator.export import export_xlsx
from translator.parser import read_file
from translator.processor import process_file

__all__ = [
    "base_counts",
    "clean_dna",
    "complement_dna",
    "detect_orfs",
    "dna_to_rna",
    "export_xlsx",
    "filter_orfs",
    "gc_content",
    "process_file",
    "read_file",
    "reverse_complement",
    "rna_to_protein_all",
    "translate_dna",
    "translate_rna_codon",
    "validate_dna",
]


def run_gui() -> None:
    import tkinter as tk

    from translator.gui import ProteinTranslatorGUI

    root = tk.Tk()
    ProteinTranslatorGUI(root)
    root.mainloop()


if __name__ == "__main__":
    if len(sys.argv) > 1:
        from translator.cli import run_cli

        raise SystemExit(run_cli())
    run_gui()
