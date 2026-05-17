from translator.analysis import calculate_stats, process_sequence


def test_calculate_stats_counts_bases_codons_and_longest_protein():
    stats = calculate_stats("ATGGCTTAATGA")

    assert stats.length == 12
    assert stats.gc_percent == 33.33
    assert stats.base_counts == {"A": 4, "T": 4, "C": 1, "G": 3}
    assert stats.start_codon_count == 2
    assert stats.stop_codon_count == 2
    assert stats.longest_protein_length == 2


def test_process_sequence_applies_orf_filters():
    result = process_sequence("ATGAAAGCTTAAATGCCCTAG", min_amino_acids=3)

    assert result["Valid"]
    assert result["Stats"].length == 21
    assert len(result["ORFs"]) == 1
    assert result["ORFs"][0].protein == "Met-Lys-Ala"
