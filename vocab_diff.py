"""Diff the cell-type label vocabulary between two stages of the Virtual
Embryo Challenge data, and surface fuzzy-match CANDIDATES for labels that
appear in only one file.

Cell-type vocabulary is not harmonized across stages (see the companion
virtualembryo-data-gotchas repo): a label absent from one stage may just be
a rename, not a true biological absence (e.g. one label at an earlier stage
possibly corresponding to several more specific labels at a later one). This
tool does NOT claim to know which renames are correct -- it only narrows
"which labels should a human even look at" using string similarity, which is
a purely lexical signal with no biological knowledge behind it. Always
verify a suggested candidate yourself before treating it as a real match.

Usage (h5ad files with an obs['celltype'] column):
    python vocab_diff.py --a stageA.h5ad --b stageB.h5ad

Usage (plain label lists, comma-separated, no anndata dependency needed):
    python vocab_diff.py --labels-a "Endothelium,Foregut" --labels-b "Endocardium,BEC,Foregut"
"""
import argparse
import difflib


def diff_labels(labels_a, labels_b, cutoff: float = 0.6, n_candidates: int = 3):
    """Returns (shared, only_a, only_b) where only_a/only_b are
    {label: [candidate matches from the other side, best first]}."""
    set_a, set_b = set(labels_a), set(labels_b)
    shared = sorted(set_a & set_b)
    only_a = sorted(set_a - set_b)
    only_b = sorted(set_b - set_a)

    def candidates(label, pool):
        return difflib.get_close_matches(label, pool, n=n_candidates, cutoff=cutoff)

    only_a_with_candidates = {lbl: candidates(lbl, set_b) for lbl in only_a}
    only_b_with_candidates = {lbl: candidates(lbl, set_a) for lbl in only_b}
    return shared, only_a_with_candidates, only_b_with_candidates


def print_report(name_a, name_b, shared, only_a, only_b):
    print(f"Shared labels ({len(shared)}): {shared}\n")

    print(f"Only in {name_a} ({len(only_a)}):")
    for lbl, cands in only_a.items():
        if cands:
            print(f"  '{lbl}' -- possible rename candidates in {name_b}: {cands}  (VERIFY, not confirmed)")
        else:
            print(f"  '{lbl}' -- no close lexical match in {name_b}, may be a genuine absence")
    print()

    print(f"Only in {name_b} ({len(only_b)}):")
    for lbl, cands in only_b.items():
        if cands:
            print(f"  '{lbl}' -- possible rename candidates in {name_a}: {cands}  (VERIFY, not confirmed)")
        else:
            print(f"  '{lbl}' -- no close lexical match in {name_a}, may be a genuine absence")


def main():
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--a", help="first .h5ad file")
    p.add_argument("--b", help="second .h5ad file")
    p.add_argument("--celltype-key", default="celltype", help="obs column holding cell-type labels")
    p.add_argument("--labels-a", help="comma-separated labels instead of --a")
    p.add_argument("--labels-b", help="comma-separated labels instead of --b")
    p.add_argument("--cutoff", type=float, default=0.6, help="difflib similarity cutoff, 0-1")
    args = p.parse_args()

    if args.labels_a is not None and args.labels_b is not None:
        labels_a = [s.strip() for s in args.labels_a.split(",") if s.strip()]
        labels_b = [s.strip() for s in args.labels_b.split(",") if s.strip()]
        name_a, name_b = "A", "B"
    elif args.a and args.b:
        import anndata as ad
        adata_a = ad.read_h5ad(args.a, backed="r")
        adata_b = ad.read_h5ad(args.b, backed="r")
        labels_a = list(adata_a.obs[args.celltype_key].unique())
        labels_b = list(adata_b.obs[args.celltype_key].unique())
        name_a, name_b = args.a, args.b
    else:
        raise SystemExit("provide either --a/--b (h5ad files) or --labels-a/--labels-b (comma-separated)")

    shared, only_a, only_b = diff_labels(labels_a, labels_b, cutoff=args.cutoff)
    print_report(name_a, name_b, shared, only_a, only_b)


if __name__ == "__main__":
    main()
