from __future__ import annotations

from dataclasses import dataclass

from translator.dna_utils import base_counts, complement_dna, dna_to_rna, gc_content, reverse_complement
from translator.protein_translation import ORF, START_CODON, STOP_CODONS, detect_orfs, filter_orfs


@dataclass(frozen=True)
class SequenceStats:
    length: int
    gc_percent: float
    base_counts: dict[str, int]
    start_codon_count: int
    stop_codon_count: int
    longest_protein_length: int


def codon_positions(rna: str, targets: set[str] | frozenset[str]) -> list[int]:
    return [
        index + 1
        for index in range(0, max(len(rna) - 2, 0))
        if rna[index:index + 3] in targets
    ]


def calculate_stats(dna: str, orfs: list[ORF] | None = None) -> SequenceStats:
    rna = dna_to_rna(dna)
    detected_orfs = orfs if orfs is not None else detect_orfs(dna)
    longest = max((orf.protein_length for orf in detected_orfs), default=0)
    return SequenceStats(
        length=len(dna),
        gc_percent=gc_content(dna),
        base_counts=base_counts(dna),
        start_codon_count=len(codon_positions(rna, {START_CODON})),
        stop_codon_count=len(codon_positions(rna, STOP_CODONS)),
        longest_protein_length=longest,
    )


def process_sequence(
    dna: str,
    translation_type: str = "both",
    min_amino_acids: int = 0,
    complete_only: bool = False,
    longest_only: bool = False,
) -> dict:
    rna = dna_to_rna(dna)
    all_orfs = detect_orfs(dna)
    filtered_orfs = filter_orfs(
        all_orfs,
        min_amino_acids=min_amino_acids,
        complete_only=complete_only,
        longest_only=longest_only,
    )

    return {
        "Valid": True,
        "DNA": dna,
        "RNA": rna if translation_type in ("both", "rna") else "",
        "Complement": complement_dna(dna),
        "ReverseComplement": reverse_complement(dna),
        "ORFs": filtered_orfs if translation_type in ("both", "protein") else [],
        "AllORFs": all_orfs,
        "Stats": calculate_stats(dna, all_orfs),
        "StartPositions": codon_positions(rna, {START_CODON}),
        "StopPositions": codon_positions(rna, STOP_CODONS),
    }
