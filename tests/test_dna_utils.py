from translator.dna_utils import base_counts, clean_dna, dna_to_rna, gc_content, reverse_complement, validate_dna


def test_dna_to_rna_transcribes_thymine_to_uracil():
    assert dna_to_rna("atgcTA") == "AUGCUA"


def test_clean_and_validate_dna():
    assert clean_dna("a t-gx\nc") == "ATGC"
    assert validate_dna("ATGC")
    assert not validate_dna("ATGX")
    assert not validate_dna("")


def test_reverse_complement():
    assert reverse_complement("ATGAAATAA") == "TTATTTCAT"


def test_gc_content_and_base_counts():
    assert gc_content("ATGCGC") == 66.67
    assert base_counts("AATCGG") == {"A": 2, "T": 1, "C": 1, "G": 2}
