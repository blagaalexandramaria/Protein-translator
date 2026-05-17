from __future__ import annotations

from collections import Counter

VALID_BASES = frozenset("ATCG")
COMPLEMENT_TABLE = str.maketrans("ATCG", "TAGC")


def clean_dna(dna_input: str) -> str:
    """Keep only canonical DNA bases and normalize to uppercase."""
    return "".join(base for base in dna_input.upper() if base in VALID_BASES)


def validate_dna(dna: str) -> bool:
    return bool(dna) and VALID_BASES.issuperset(dna.upper())


def dna_to_rna(dna: str) -> str:
    return dna.upper().replace("T", "U")


def complement_dna(dna: str) -> str:
    return dna.upper().translate(COMPLEMENT_TABLE)


def reverse_complement(dna: str) -> str:
    return complement_dna(dna)[::-1]


def base_counts(dna: str) -> dict[str, int]:
    counts = Counter(dna.upper())
    return {base: counts.get(base, 0) for base in "ATCG"}


def gc_content(dna: str) -> float:
    cleaned = dna.upper()
    if not cleaned:
        return 0.0
    gc_count = cleaned.count("G") + cleaned.count("C")
    return round((gc_count / len(cleaned)) * 100, 2)
