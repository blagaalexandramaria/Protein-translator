from translator.protein_translation import detect_orfs, filter_orfs, translate_rna_codon


def test_translate_rna_codon():
    assert translate_rna_codon("AUG") == "Met"
    assert translate_rna_codon("UAA") == "STOP"
    assert translate_rna_codon("NNN") == "?"


def test_detects_complete_forward_orf_with_positions():
    orfs = detect_orfs("ATGGCTTAA", include_reverse=False)

    assert len(orfs) == 1
    orf = orfs[0]
    assert orf.frame == "+1"
    assert orf.direction == "forward"
    assert orf.start_position == 1
    assert orf.stop_position == 7
    assert orf.length_nt == 9
    assert orf.protein == "Met-Ala"
    assert orf.stop_codon == "UAA"
    assert orf.complete


def test_detects_forward_frame_two_orf():
    orfs = detect_orfs("CATGAAATAA", include_reverse=False)

    assert len(orfs) == 1
    assert orfs[0].frame == "+2"
    assert orfs[0].start_position == 2
    assert orfs[0].stop_position == 8


def test_detects_reverse_complement_orf():
    orfs = detect_orfs("TTATTTCAT")
    reverse_orfs = [orf for orf in orfs if orf.direction == "reverse"]

    assert len(reverse_orfs) == 1
    orf = reverse_orfs[0]
    assert orf.frame == "-1"
    assert orf.start_position == 9
    assert orf.stop_position == 3
    assert orf.protein == "Met-Lys"


def test_filters_by_length_completion_and_longest():
    orfs = detect_orfs("ATGAAATAAATGCCCTAG", include_reverse=False)

    filtered = filter_orfs(orfs, min_amino_acids=2, complete_only=True, longest_only=True)

    assert len(filtered) == 1
    assert filtered[0].protein_length == 2
    assert filtered[0].complete
