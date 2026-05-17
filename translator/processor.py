from __future__ import annotations

from translator.analysis import SequenceStats, process_sequence
from translator.dna_utils import clean_dna, validate_dna
from translator.parser import read_file


def process_file(
    filepath: str,
    translation_type: str = "both",
    min_amino_acids: int = 0,
    complete_only: bool = False,
    longest_only: bool = False,
) -> dict:
    content = read_file(filepath)
    if not content:
        return _empty_result()

    dna = clean_dna(content)
    if not validate_dna(dna):
        return _empty_result()

    return process_sequence(
        dna,
        translation_type=translation_type,
        min_amino_acids=min_amino_acids,
        complete_only=complete_only,
        longest_only=longest_only,
    )


def _empty_result() -> dict:
    return {
        "Valid": False,
        "DNA": "",
        "RNA": "",
        "Complement": "",
        "ReverseComplement": "",
        "ORFs": [],
        "AllORFs": [],
        "Stats": SequenceStats(
            length=0,
            gc_percent=0.0,
            base_counts={"A": 0, "T": 0, "C": 0, "G": 0},
            start_codon_count=0,
            stop_codon_count=0,
            longest_protein_length=0,
        ),
        "StartPositions": [],
        "StopPositions": [],
    }
