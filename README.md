# Cell-Type Vocabulary Diff

Diff the cell-type label vocabulary between two stages of the Virtual Embryo
Challenge data, and get candidate renames for labels that appear in only one
side, so you spend your time checking a short candidate list instead of
manually eyeballing two label sets against each other.

## Why this exists

Cell-type vocabulary isn't harmonized across stages (see the companion
[Data Gotchas](https://github.com/Shashwat-srivastav/virtualembryo-data-gotchas) repo). Applied
to the actual published E8.5/E9.5 label sets
(`data/metadata/t1_composition.json`), only 11 of ~18-21 labels per stage
are shared verbatim, but several of the "unmatched" ones are plausible
renames, not real absences: `LV-CM`/`RV-CM` at E8.5 vs `V-CM` at E9.5, or
`Endothelium` at E8.5 vs `Endocardium`/`Epithelium` at E9.5.

**This tool makes no biological claim about which renames are correct**. It
only uses string similarity (Python's stdlib `difflib`, no extra
dependencies) to narrow which labels are worth a human looking at. Every
suggestion is explicitly marked "VERIFY, not confirmed." A label with no
lexical match might still be a real rename under a completely different
name, and a suggested candidate might still be lexically similar by
coincidence. This only handles the mechanical part (surfacing candidates),
not the biology.

## Usage

With two `.h5ad` files that have an `obs['celltype']` column:

```bash
python vocab_diff.py --a stageA.h5ad --b stageB.h5ad
```

Or with plain label lists, no `anndata` dependency needed:

```bash
python vocab_diff.py \
    --labels-a "Endothelium,Foregut,LV-CM" \
    --labels-b "Endocardium,BEC,Foregut,V-CM"
```

```
Shared labels (1): ['Foregut']

Only in A (2):
  'Endothelium' -- possible rename candidates in B: ['Endocardium']  (VERIFY, not confirmed)
  'LV-CM' -- possible rename candidates in B: ['V-CM']  (VERIFY, not confirmed)

Only in B (2):
  'Endocardium' -- possible rename candidates in A: ['Endothelium']  (VERIFY, not confirmed)
  'BEC' -- no close lexical match in A, may be a genuine absence
```

`--cutoff` (default 0.6) controls the `difflib` similarity threshold:
lower it to surface more (noisier) candidates, raise it to see only very
close matches.

## Tests

`test_vocab_diff.py` covers basic diff behavior plus a real check against
the actual published E8.5/E9.5 vocabulary, confirming the shared-label count
matches `t1_composition.json`'s own documented `n_shared_types: 11`. Run
with:

```bash
python test_vocab_diff.py
```

## Limitations

- Purely lexical (string similarity), with no biological knowledge, so it
  cannot confirm that two labels actually refer to the same or related
  population. Always verify a candidate against the actual literature or
  marker genes before relying on it.
- Won't catch renames that share no substring at all (e.g. two completely
  different names for the same population).
- No dependency needed for the `--labels-a`/`--labels-b` mode; `--a`/`--b`
  (direct `.h5ad` input) needs `anndata` installed.

## License

MIT. See [LICENSE](LICENSE).

---

Filed as a Community Contribution to the NeurIPS 2026 Virtual Embryo Challenge.
