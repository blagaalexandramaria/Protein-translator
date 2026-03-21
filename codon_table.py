# organizare pe aminoacizi
AMINOACIDS = {
    "Phe": ["UUU", "UUC"],
    "Leu": ["UUA", "UUG", "CUU", "CUC", "CUA", "CUG"],
    "Ile": ["AUU", "AUC", "AUA"],
    "Met": ["AUG"],

    "Val": ["GUU", "GUC", "GUA", "GUG"],

    "Ser": ["UCU", "UCC", "UCA", "UCG", "AGU", "AGC"],
    "Pro": ["CCU", "CCC", "CCA", "CCG"],
    "Thr": ["ACU", "ACC", "ACA", "ACG"],
    "Ala": ["GCU", "GCC", "GCA", "GCG"],

    "Tyr": ["UAU", "UAC"],
    "STOP": ["UAA", "UAG", "UGA"],

    "His": ["CAU", "CAC"],
    "Gln": ["CAA", "CAG"],
    "Asn": ["AAU", "AAC"],
    "Lys": ["AAA", "AAG"],

    "Asp": ["GAU", "GAC"],
    "Glu": ["GAA", "GAG"],

    "Cys": ["UGU", "UGC"],
    "Trp": ["UGG"],

    "Arg": ["CGU", "CGC", "CGA", "CGG", "AGA", "AGG"],
    "Gly": ["GGU", "GGC", "GGA", "GGG"]
}


# generăm automat CODON_TABLE
CODON_TABLE = {}

for aminoacid, codons in AMINOACIDS.items():
    for codon in codons:
        CODON_TABLE[codon] = aminoacid