# Paper Package (Evidence-Linked)

This folder contains the paper draft and a minimal reproducibility surface for the PoR / Silence-as-Control claims.

## Scope

This package is intentionally conservative:

- It does **not** introduce new benchmark claims.
- It does **not** retune thresholds mid-run.
- It maps paper claims to tracked repository artifacts.

## Structure

- `main.tex` — paper draft.
- `references.bib` — bibliography.
- `evidence_manifest.md` — claim-to-artifact mapping.
- `appendix_protocol.md` — fixed-threshold protocol and metric definitions.
- `figures/` — generated CSV and LaTeX table fragments used by the paper.
- `cases/` — exported boundary-pocket cases for paper packaging.

## Reproducibility commands

From repo root:

```bash
python scripts/aggregate_paper_results.py
python scripts/make_paper_figures.py
python scripts/export_boundary_cases.py
```

These commands read tracked artifacts under `reports/` and regenerate:

- `paper/figures/results_by_run_scale.csv`
- `paper/figures/results_1000_threshold_sweep.csv`
- `paper/figures/table_run_scale.tex`
- `paper/figures/table_threshold_sweep.tex`
- `paper/cases/borderline_maybe_short_regen.csv`
- `paper/cases/borderline_maybe_short_regen_summary.json`
