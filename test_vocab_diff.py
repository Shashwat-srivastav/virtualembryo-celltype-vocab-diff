"""Unit tests for diff_labels(), plus a real-data check against the actual
E8.5 vs E9.5 cell-type vocabulary published in
data/metadata/t1_composition.json (no anndata/file I/O needed -- pure label
lists). Run with: python test_vocab_diff.py
"""
from vocab_diff import diff_labels

# --- basic behavior ---
shared, only_a, only_b = diff_labels(["Foo", "Bar"], ["Bar", "Baz"])
assert shared == ["Bar"], shared
assert set(only_a) == {"Foo"}, only_a
assert set(only_b) == {"Baz"}, only_b
print("basic shared/only-in-one-side: PASS")

# --- fuzzy candidate surfacing: a close rename should be suggested ---
shared, only_a, only_b = diff_labels(["Endothelium"], ["Endocardium"], cutoff=0.5)
assert only_a["Endothelium"] == ["Endocardium"], only_a
print("fuzzy candidate surfacing: PASS")

# --- a genuinely unrelated label should get no candidates ---
shared, only_a, only_b = diff_labels(["Hepatocyte"], ["Neural Tube"], cutoff=0.6)
assert only_a["Hepatocyte"] == [], only_a
print("no-spurious-candidate for unrelated labels: PASS")

# --- real data: E8.5 vs E9.5 cell-type labels (from data/metadata/t1_composition.json) ---
E85 = ["Foregut", "pSHF", "Surface Ectoderm", "OFT/RV-CM", "Endothelium", "JCF", "IFT-CM",
       "Paraxial Mesoderm", "EXEM", "aSHF", "Neural Tube", "Pericardium", "AVC-CM", "RV-CM",
       "LV-CM", "SV-CM", "NCC", "Blood"]
E95 = ["OFT/RV-CM", "Endocardium", "SV-CM", "pPHM", "Hepatocyte", "V-CM", "pSHF", "aSHF",
       "Pericardium", "Proepicardium", "ST", "Foregut", "IFT-CM", "NCC-derived",
       "Surface Ectoderm", "AVC-CM", "BEC", "Epithelium", "aPHM", "Blood", "NCC"]
shared, only_a, only_b = diff_labels(E85, E95)
assert len(shared) == 11, f"expected 11 shared types per t1_composition.json's own n_shared_types, got {len(shared)}"
assert "V-CM" in only_a["LV-CM"], "LV-CM should surface V-CM as a lexical candidate"
print("real E8.5/E9.5 vocabulary check (matches published n_shared_types=11): PASS")

print("\nALL TESTS PASS")
