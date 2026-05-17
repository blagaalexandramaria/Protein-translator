from __future__ import annotations

from dataclasses import dataclass
from functools import lru_cache

from codon_table import CODON_TABLE
from translator.dna_utils import dna_to_rna, reverse_complement

START_CODON = "AUG"
STOP_CODONS = frozenset({"UAA", "UAG", "UGA"})


@dataclass(frozen=True)
class ORF:
    direction: str
    frame: str
    start_position: int
    stop_position: int | None
    end_position: int
    length_nt: int
    protein_length: int
    protein: str
    codon_pairs: tuple[tuple[str, str], ...]
    stop_codon: str | None
    complete: bool


@lru_cache(maxsize=128)
def translate_rna_codon(codon: str) -> str:
    return CODON_TABLE.get(codon.upper(), "?")


def _protein_from_pairs(pairs: list[tuple[str, str]]) -> str:
    return "-".join(aminoacid for _, aminoacid in pairs)


def _forward_position(index: int, _sequence_length: int) -> int:
    return index + 1


def _reverse_position(index: int, sequence_length: int) -> int:
    return sequence_length - index


def detect_orfs(dna: str, include_reverse: bool = True) -> list[ORF]:
    """Detect AUG-started ORFs in all forward frames and optionally reverse frames."""
    sequence = dna.upper()
    orientations = [("forward", sequence, _forward_position)]
    if include_reverse:
        orientations.append(("reverse", reverse_complement(sequence), _reverse_position))

    orfs: list[ORF] = []
    sequence_length = len(sequence)

    for direction, oriented_dna, position_mapper in orientations:
        sign = "+" if direction == "forward" else "-"
        for offset in range(3):
            frame = f"{sign}{offset + 1}"
            index = offset

            while index <= len(oriented_dna) - 3:
                codon = dna_to_rna(oriented_dna[index:index + 3])
                if codon != START_CODON:
                    index += 3
                    continue

                pairs: list[tuple[str, str]] = []
                stop_codon: str | None = None
                stop_index: int | None = None
                scan_index = index

                while scan_index <= len(oriented_dna) - 3:
                    scan_codon = dna_to_rna(oriented_dna[scan_index:scan_index + 3])
                    aminoacid = translate_rna_codon(scan_codon)
                    if aminoacid == "STOP":
                        stop_codon = scan_codon
                        stop_index = scan_index
                        break
                    pairs.append((scan_codon, aminoacid))
                    scan_index += 3

                if pairs:
                    complete = stop_index is not None
                    if complete:
                        length_nt = stop_index + 3 - index
                        end_index = stop_index + 2
                        stop_position = position_mapper(stop_index, sequence_length)
                    else:
                        length_nt = len(pairs) * 3
                        end_index = index + length_nt - 1
                        stop_position = None

                    orfs.append(
                        ORF(
                            direction=direction,
                            frame=frame,
                            start_position=position_mapper(index, sequence_length),
                            stop_position=stop_position,
                            end_position=position_mapper(end_index, sequence_length),
                            length_nt=length_nt,
                            protein_length=len(pairs),
                            protein=_protein_from_pairs(pairs),
                            codon_pairs=tuple(pairs),
                            stop_codon=stop_codon,
                            complete=complete,
                        )
                    )

                index += 3

    return orfs


def filter_orfs(
    orfs: list[ORF],
    min_amino_acids: int = 0,
    complete_only: bool = False,
    longest_only: bool = False,
) -> list[ORF]:
    filtered = [
        orf
        for orf in orfs
        if orf.protein_length >= min_amino_acids and (orf.complete or not complete_only)
    ]
    if longest_only and filtered:
        return [max(filtered, key=lambda item: (item.protein_length, item.length_nt))]
    return filtered


def rna_to_protein_all(rna: str) -> list[tuple[str, list[tuple[str, str]], str | None]]:
    """Compatibility wrapper for the original RNA translation shape."""
    dna = rna.upper().replace("U", "T")
    proteins = []
    for orf in detect_orfs(dna, include_reverse=False):
        proteins.append((orf.protein, list(orf.codon_pairs), orf.stop_codon))
    return proteins


def translate_dna(dna: str) -> tuple[str, list[tuple[str, list[tuple[str, str]], str | None]]]:
    rna = dna_to_rna(dna)
    return rna, rna_to_protein_all(rna)
